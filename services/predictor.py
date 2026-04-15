import json
from pathlib import Path

import joblib
import pandas as pd

from services.mapper import map_dashboard_input_to_model_features
from services.explanations import (
    generate_risk_reasons,
    generate_user_summary,
    generate_admin_summary,
)
from services.medical_rules import evaluate_diagnosis_procedure_consistency

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "xgboost_fraud_algorithm.joblib"
FEATURES_PATH = ARTIFACTS_DIR / "feature_names.json"


class FraudPredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        with open(FEATURES_PATH, "r") as f:
            self.feature_names = json.load(f)

    def align_features(self, mapped_features: dict) -> pd.DataFrame:
        input_df = pd.DataFrame([mapped_features])
        for col in self.feature_names:
            if col not in input_df.columns:
                input_df[col] = 0
        return input_df[self.feature_names]

    def compute_rules_score(self, claim_payload: dict, consistency: dict) -> float:
        score = 0.0

        claim_amount = float(claim_payload.get("claim_amount", 0))
        procedure_count = int(claim_payload.get("procedure_count", 1))
        admission_type = str(claim_payload.get("admission_type", "planned")).lower()
        out_of_pocket = float(claim_payload.get("out_of_pocket", 0))
        age = int(claim_payload.get("age", 0))

        if claim_amount >= 90000:
            score += 0.25
        elif claim_amount >= 50000:
            score += 0.15
        elif claim_amount >= 30000:
            score += 0.08

        if procedure_count >= 5:
            score += 0.20
        elif procedure_count >= 3:
            score += 0.10

        if admission_type == "emergency" and claim_amount >= 40000:
            score += 0.15
        elif admission_type == "emergency":
            score += 0.05

        if out_of_pocket >= 10000:
            score += 0.10
        elif out_of_pocket >= 5000:
            score += 0.05

        if age >= 75:
            score += 0.05

        if not consistency["is_consistent"]:
            if consistency["severity"] == "high":
                score += 0.25
            elif consistency["severity"] == "medium":
                score += 0.15

        return min(score, 1.0)

    def predict(self, claim_payload: dict) -> dict:
        mapped = map_dashboard_input_to_model_features(claim_payload)
        model_input = self.align_features(mapped)

        pred = self.model.predict(model_input)[0]
        base_proba = float(self.model.predict_proba(model_input)[0][1])

        consistency = evaluate_diagnosis_procedure_consistency(
            claim_payload.get("diagnosis_code", ""),
            claim_payload.get("procedure_code", "")
        )

        rules_score = self.compute_rules_score(claim_payload, consistency)

        consistency_score = 0.0
        if not consistency["is_consistent"]:
            consistency_score = 1.0 if consistency["severity"] == "high" else 0.6

        final_score = (
            0.35 * base_proba +
            0.40 * rules_score +
            0.25 * consistency_score
        )

        final_score = min(final_score, 1.0)

        if final_score >= 0.70:
            risk_level = "High Risk"
        elif final_score >= 0.40:
            risk_level = "Medium Risk"
        else:
            risk_level = "Low Risk"

        final_prediction_label = 1 if final_score >= 0.50 else 0
        final_prediction_text = "Fraud" if final_prediction_label == 1 else "No Fraud"

        risk_reasons = generate_risk_reasons(claim_payload, final_score)
        user_summary = generate_user_summary(claim_payload, final_score, risk_level, risk_reasons)
        admin_summary = generate_admin_summary(claim_payload, final_score, risk_level, risk_reasons)

        return {
            "prediction_label": final_prediction_label,
            "prediction_text": final_prediction_text,
            "fraud_probability": final_score,
            "risk_level": risk_level,
            "mapped_features": mapped,
            "risk_reasons": risk_reasons,
            "user_summary": user_summary,
            "admin_summary": admin_summary,
            "consistency_check": consistency,
            "base_model_probability": base_proba,
            "rules_score": rules_score,
            "consistency_score": consistency_score,
        }


_predictor = None


def get_predictor() -> FraudPredictor:
    global _predictor
    if _predictor is None:
        _predictor = FraudPredictor()
    return _predictor