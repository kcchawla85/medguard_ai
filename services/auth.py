import hashlib
import re

import streamlit as st

from services.database import fetch_one, execute_insert


def hash_password(password: str) -> str:
    salt = b"medguard_ai_salt_v1"
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return hashed.hex()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def authenticate_user(email: str, password: str) -> dict | None:
    user = fetch_one("SELECT * FROM users WHERE email = ? AND is_active = 1", (email,))
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def register_user(full_name: str, email: str, password: str, role: str = "user") -> tuple[bool, str]:
    full_name = full_name.strip()
    email = email.strip().lower()

    if len(full_name) < 2:
        return False, "Full name must be at least 2 characters."

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    existing = fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if existing:
        return False, "An account with this email already exists."

    execute_insert(
        """
        INSERT INTO users (full_name, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        """,
        (full_name, email, hash_password(password), role),
    )
    return True, "Registration successful. You can now log in."


def require_login():
    if "user" not in st.session_state or not st.session_state.user:
        st.warning("Please log in from the sidebar.")
        st.stop()


def require_admin():
    require_login()
    if st.session_state.user["role"] != "admin":
        st.error("Admin access only.")
        st.stop()


def require_user():
    require_login()
    if st.session_state.user["role"] not in {"user", "admin"}:
        st.error("User access only.")
        st.stop()


def logout_user():
    st.session_state.user = None


def sidebar_login():
    st.sidebar.title("MedGuard AI")

    if "user" not in st.session_state:
        st.session_state.user = None

    auth_mode = st.sidebar.selectbox("Access", ["Login", "Register"])

    if st.session_state.user:
        user = st.session_state.user
        st.sidebar.success(f"{user['full_name']}")
        st.sidebar.caption(f"Role: {user['role'].title()}")

        role_view = st.sidebar.selectbox(
            "Role View",
            [user["role"].title()],
            disabled=True
        )
        st.sidebar.caption(f"Current role dashboard: {role_view}")

        if user["role"] == "admin":
            st.sidebar.info("Admin pages: Admin Dashboard, All Claims, Claim Review")
        else:
            st.sidebar.info("User pages: User Dashboard, Submit Claim, My Claims")

        if st.sidebar.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()

    else:
        if auth_mode == "Login":
            with st.sidebar.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                user = authenticate_user(email, password)
                if user:
                    st.session_state.user = user
                    st.sidebar.success("Login successful")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid credentials")

            st.sidebar.caption("Default Admin: admin@medguard.ai / admin123")
            st.sidebar.caption("Default User: aman@example.com / user123")

        else:
            with st.sidebar.form("register_form"):
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if password != confirm_password:
                    st.sidebar.error("Passwords do not match.")
                else:
                    ok, message = register_user(full_name, email, password, role="user")
                    if ok:
                        st.sidebar.success(message)
                    else:
                        st.sidebar.error(message)