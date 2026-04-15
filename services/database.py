import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
import json

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "medguard_ai.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def column_exists(conn: sqlite3.Connection, table_name: str, column_name: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r["name"] == column_name for r in rows)


def safe_add_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_type: str) -> None:
    if not column_exists(conn, table_name, column_name):
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            location TEXT NOT NULL,
            diagnosis_code TEXT NOT NULL,
            procedure_code TEXT NOT NULL,
            procedure_count INTEGER NOT NULL,
            admission_type TEXT NOT NULL,
            date_of_service TEXT NOT NULL,
            claim_amount REAL NOT NULL,
            insurance_coverage REAL NOT NULL,
            out_of_pocket REAL NOT NULL,
            billing_date TEXT NOT NULL,
            description TEXT,
            workflow_status TEXT NOT NULL DEFAULT 'ai_reviewed',
            submitted_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            fraud_probability REAL NOT NULL,
            prediction_label INTEGER NOT NULL,
            prediction_text TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            model_version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(claim_id) REFERENCES claims(id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            admin_id INTEGER NOT NULL,
            decision TEXT NOT NULL CHECK(decision IN ('approved', 'rejected')),
            remarks TEXT,
            reviewed_at TEXT NOT NULL,
            FOREIGN KEY(claim_id) REFERENCES claims(id),
            FOREIGN KEY(admin_id) REFERENCES users(id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            event_title TEXT NOT NULL,
            event_description TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(claim_id) REFERENCES claims(id)
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(claim_id) REFERENCES claims(id)
        )
        """)

        safe_add_column(conn, "predictions", "risk_reasons", "TEXT")
        safe_add_column(conn, "predictions", "user_summary", "TEXT")
        safe_add_column(conn, "predictions", "admin_summary", "TEXT")


def seed_default_users() -> None:
    from services.auth import hash_password

    users = [
        ("Admin User", "admin@medguard.ai", hash_password("admin123"), "admin"),
        ("Aman Verma", "aman@example.com", hash_password("user123"), "user"),
    ]

    with get_conn() as conn:
        for full_name, email, password_hash, role in users:
            exists = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            if not exists:
                conn.execute(
                    """
                    INSERT INTO users (full_name, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (full_name, email, password_hash, role, datetime.utcnow().isoformat())
                )


def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def execute_insert(query: str, params: tuple = ()) -> int:
    with get_conn() as conn:
        cursor = conn.execute(query, params)
        return int(cursor.lastrowid)


def create_claim(payload: dict[str, Any], user_id: int) -> int:
    claim_id = execute_insert(
        """
        INSERT INTO claims (
            user_id, full_name, age, gender, hospital_name, provider_name, location,
            diagnosis_code, procedure_code, procedure_count, admission_type,
            date_of_service, claim_amount, insurance_coverage, out_of_pocket,
            billing_date, description, workflow_status, submitted_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            payload["full_name"],
            int(payload["age"]),
            payload["gender"],
            payload["hospital_name"],
            payload["provider_name"],
            payload["location"],
            payload["diagnosis_code"],
            payload["procedure_code"],
            int(payload["procedure_count"]),
            payload["admission_type"],
            payload["date_of_service"],
            float(payload["claim_amount"]),
            float(payload["insurance_coverage"]),
            float(payload["out_of_pocket"]),
            payload["billing_date"],
            payload.get("description", ""),
            "ai_reviewed",
            datetime.utcnow().isoformat(),
        ),
    )

    add_timeline_event(
        claim_id=claim_id,
        event_type="submitted",
        event_title="Claim submitted",
        event_description="The user submitted a new health insurance claim.",
    )
    return claim_id


def create_prediction(claim_id: int, result: dict[str, Any], model_version: str = "xgboost_v2") -> int:
    prediction_id = execute_insert(
        """
        INSERT INTO predictions (
            claim_id, fraud_probability, prediction_label, prediction_text,
            risk_level, model_version, created_at, risk_reasons, user_summary, admin_summary
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            claim_id,
            float(result["fraud_probability"]),
            int(result["prediction_label"]),
            result["prediction_text"],
            result["risk_level"],
            model_version,
            datetime.utcnow().isoformat(),
            json.dumps(result.get("risk_reasons", [])),
            result.get("user_summary", ""),
            result.get("admin_summary", ""),
        ),
    )

    add_timeline_event(
        claim_id=claim_id,
        event_type="ai_reviewed",
        event_title="AI screening completed",
        event_description=f"AI marked this claim as {result['risk_level']} with probability {result['fraud_probability']:.2%}.",
    )
    return prediction_id


def add_timeline_event(claim_id: int, event_type: str, event_title: str, event_description: str = "") -> int:
    return execute_insert(
        """
        INSERT INTO timeline_events (claim_id, event_type, event_title, event_description, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (claim_id, event_type, event_title, event_description, datetime.utcnow().isoformat()),
    )


def create_anomaly_alert(claim_id: int, alert_type: str, severity: str, message: str) -> int:
    return execute_insert(
        """
        INSERT INTO anomaly_alerts (claim_id, alert_type, severity, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (claim_id, alert_type, severity, message, datetime.utcnow().isoformat()),
    )


def get_claim_alerts(claim_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT * FROM anomaly_alerts
        WHERE claim_id = ?
        ORDER BY created_at DESC
        """,
        (claim_id,),
    )


def get_claim_timeline(claim_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT * FROM timeline_events
        WHERE claim_id = ?
        ORDER BY created_at ASC
        """,
        (claim_id,),
    )


def get_user_claims(user_id: int) -> list[dict[str, Any]]:
    claims = fetch_all(
        """
        SELECT
            c.*,
            p.fraud_probability,
            p.prediction_label,
            p.prediction_text,
            p.risk_level,
            p.model_version,
            p.risk_reasons,
            p.user_summary,
            p.admin_summary,
            r.decision,
            r.remarks,
            r.reviewed_at
        FROM claims c
        LEFT JOIN predictions p ON p.claim_id = c.id
        LEFT JOIN reviews r ON r.claim_id = c.id
        WHERE c.user_id = ?
        ORDER BY c.submitted_at DESC
        """,
        (user_id,),
    )

    for claim in claims:
        if claim.get("risk_reasons"):
            try:
                claim["risk_reasons"] = json.loads(claim["risk_reasons"])
            except Exception:
                claim["risk_reasons"] = []
        else:
            claim["risk_reasons"] = []

    return claims


def get_all_claims() -> list[dict[str, Any]]:
    claims = fetch_all(
        """
        SELECT
            c.*,
            u.email,
            p.fraud_probability,
            p.prediction_text,
            p.risk_level,
            p.risk_reasons,
            p.user_summary,
            p.admin_summary,
            r.decision,
            r.remarks,
            r.reviewed_at
        FROM claims c
        JOIN users u ON u.id = c.user_id
        LEFT JOIN predictions p ON p.claim_id = c.id
        LEFT JOIN reviews r ON r.claim_id = c.id
        ORDER BY c.submitted_at DESC
        """
    )

    for claim in claims:
        if claim.get("risk_reasons"):
            try:
                claim["risk_reasons"] = json.loads(claim["risk_reasons"])
            except Exception:
                claim["risk_reasons"] = []
        else:
            claim["risk_reasons"] = []

    return claims


def get_claim_detail(claim_id: int) -> dict[str, Any] | None:
    detail = fetch_one(
        """
        SELECT
            c.*,
            u.email,
            p.fraud_probability,
            p.prediction_label,
            p.prediction_text,
            p.risk_level,
            p.model_version,
            p.risk_reasons,
            p.user_summary,
            p.admin_summary,
            r.decision,
            r.remarks,
            r.reviewed_at
        FROM claims c
        JOIN users u ON u.id = c.user_id
        LEFT JOIN predictions p ON p.claim_id = c.id
        LEFT JOIN reviews r ON r.claim_id = c.id
        WHERE c.id = ?
        """,
        (claim_id,),
    )

    if not detail:
        return None

    if detail.get("risk_reasons"):
        try:
            detail["risk_reasons"] = json.loads(detail["risk_reasons"])
        except Exception:
            detail["risk_reasons"] = []
    else:
        detail["risk_reasons"] = []

    detail["timeline"] = get_claim_timeline(claim_id)
    detail["alerts"] = get_claim_alerts(claim_id)
    return detail


def review_claim(claim_id: int, admin_id: int, decision: str, remarks: str) -> None:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM reviews WHERE claim_id = ?",
            (claim_id,),
        ).fetchone()

        now = datetime.utcnow().isoformat()

        if existing:
            conn.execute(
                """
                UPDATE reviews
                SET admin_id = ?, decision = ?, remarks = ?, reviewed_at = ?
                WHERE claim_id = ?
                """,
                (admin_id, decision, remarks, now, claim_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO reviews (claim_id, admin_id, decision, remarks, reviewed_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (claim_id, admin_id, decision, remarks, now),
            )

        conn.execute(
            "UPDATE claims SET workflow_status = ? WHERE id = ?",
            (decision, claim_id),
        )

    add_timeline_event(
        claim_id=claim_id,
        event_type="reviewed",
        event_title=f"Admin {decision}",
        event_description=remarks or f"The claim was {decision} by the admin.",
    )


def get_admin_stats() -> dict[str, Any]:
    all_claims = get_all_claims()
    total_claims = len(all_claims)
    high_risk = sum(1 for c in all_claims if c.get("risk_level") == "High Risk")
    medium_risk = sum(1 for c in all_claims if c.get("risk_level") == "Medium Risk")
    low_risk = sum(1 for c in all_claims if c.get("risk_level") == "Low Risk")
    pending = sum(1 for c in all_claims if c.get("workflow_status") == "ai_reviewed")
    approved = sum(1 for c in all_claims if c.get("workflow_status") == "approved")
    rejected = sum(1 for c in all_claims if c.get("workflow_status") == "rejected")
    total_users = fetch_one("SELECT COUNT(*) AS cnt FROM users WHERE role = 'user'")["cnt"]

    return {
        "total_claims": total_claims,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "total_users": total_users,
    }


def get_provider_leaderboard(limit: int = 10) -> list[dict[str, Any]]:
    return fetch_all(
        f"""
        SELECT
            c.provider_name,
            COUNT(c.id) AS total_claims,
            ROUND(AVG(COALESCE(p.fraud_probability, 0)), 4) AS avg_fraud_probability,
            SUM(CASE WHEN p.risk_level = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_claims,
            SUM(CASE WHEN c.workflow_status = 'rejected' THEN 1 ELSE 0 END) AS rejected_claims
        FROM claims c
        LEFT JOIN predictions p ON p.claim_id = c.id
        GROUP BY c.provider_name
        ORDER BY avg_fraud_probability DESC, high_risk_claims DESC, total_claims DESC
        LIMIT {int(limit)}
        """
    )


def get_recent_activity(limit: int = 15) -> list[dict[str, Any]]:
    return fetch_all(
        f"""
        SELECT
            t.claim_id,
            t.event_title,
            t.event_description,
            t.created_at,
            c.full_name,
            c.provider_name
        FROM timeline_events t
        JOIN claims c ON c.id = t.claim_id
        ORDER BY t.created_at DESC
        LIMIT {int(limit)}
        """
    )