import pandas as pd
import streamlit as st

from services.auth import require_user, sidebar_login
from services.database import get_user_claims

sidebar_login()
require_user()

user = st.session_state.user
claims = get_user_claims(user["id"])
df = pd.DataFrame(claims)

st.title("User Dashboard")
st.caption("Overview of your submitted claims, AI screening, and review progress")

if df.empty:
    st.info("No claims submitted yet.")
    st.stop()

total = len(df)
approved = (df["workflow_status"] == "approved").sum()
rejected = (df["workflow_status"] == "rejected").sum()
under_review = (df["workflow_status"] == "ai_reviewed").sum()
high_risk = (df["risk_level"] == "High Risk").sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Claims", total)
c2.metric("Under Review", int(under_review))
c3.metric("Approved", int(approved))
c4.metric("Rejected", int(rejected))
c5.metric("High Risk", int(high_risk))

st.subheader("Claim Status Distribution")
status_counts = df["workflow_status"].value_counts()
st.bar_chart(status_counts)

latest = df.iloc[0].to_dict()
st.subheader("Latest AI Message")
st.info(latest.get("user_summary") or "No summary available yet.")

st.subheader("Recent Claims")
show_cols = [
    "id", "hospital_name", "provider_name", "claim_amount",
    "risk_level", "prediction_text", "workflow_status", "submitted_at"
]
st.dataframe(df[show_cols], use_container_width=True, hide_index=True)