import streamlit as st

from services.auth import logout_user, sidebar_login
from services.database import init_db, seed_default_users
from services.ui_helpers import inject_custom_css

st.set_page_config(
    page_title="MedGuard AI",
    page_icon="🛡️",
    layout="wide",
)

init_db()
seed_default_users()
inject_custom_css()
sidebar_login()

st.title("🛡️ MedGuard AI")
st.caption("Real-Time Health Insurance Claim Fraud Detection Dashboard")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    user = st.session_state.user
    st.success(f"Logged in as {user['full_name']} ({user['role']})")
else:
    st.warning("Please log in or register from the sidebar.")

st.markdown("---")
st.markdown(
    """
### Platform Features
- Submit health insurance claims
- AI-powered fraud risk scoring
- Human-readable AI summaries
- Claim timeline tracking
- Admin review workflow
- Provider leaderboard
- Anomaly alerts
"""
)