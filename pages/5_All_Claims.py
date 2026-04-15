import pandas as pd
import streamlit as st

from services.auth import require_admin, sidebar_login
from services.database import get_all_claims

sidebar_login()
require_admin()

st.title("All Claims")
claims = pd.DataFrame(get_all_claims())

if claims.empty:
    st.info("No claims found.")
    st.stop()

status_options = sorted(claims["workflow_status"].dropna().unique().tolist())
risk_options = sorted(claims["risk_level"].dropna().unique().tolist())

col1, col2, col3 = st.columns(3)
with col1:
    status_filter = st.multiselect("Workflow Status", status_options, default=status_options)
with col2:
    risk_filter = st.multiselect("Risk Level", risk_options, default=risk_options)
with col3:
    search = st.text_input("Search by User / Hospital / Provider")

filtered = claims[
    claims["workflow_status"].isin(status_filter) &
    claims["risk_level"].isin(risk_filter)
].copy()

if search:
    q = search.lower()
    filtered = filtered[
        filtered["full_name"].str.lower().str.contains(q) |
        filtered["hospital_name"].str.lower().str.contains(q) |
        filtered["provider_name"].str.lower().str.contains(q)
    ]

st.dataframe(
    filtered[
        [
            "id", "full_name", "email", "hospital_name", "provider_name",
            "claim_amount", "prediction_text", "risk_level",
            "workflow_status", "decision", "submitted_at"
        ]
    ],
    use_container_width=True,
    hide_index=True,
)