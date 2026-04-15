import pandas as pd
import streamlit as st

from services.auth import require_user, sidebar_login
from services.database import get_user_claims, get_claim_detail
from services.ui_helpers import inject_custom_css, render_field, render_badge
from services.codebook import get_diagnosis_name, get_procedure_name

sidebar_login()
require_user()
inject_custom_css()

st.title("My Claims")
claims = get_user_claims(st.session_state.user["id"])
df = pd.DataFrame(claims)

if df.empty:
    st.info("You have not submitted any claims yet.")
    st.stop()

status_filter = st.multiselect(
    "Filter by Status",
    options=sorted(df["workflow_status"].dropna().unique().tolist()),
    default=sorted(df["workflow_status"].dropna().unique().tolist()),
)
risk_filter = st.multiselect(
    "Filter by Risk Level",
    options=sorted(df["risk_level"].dropna().unique().tolist()),
    default=sorted(df["risk_level"].dropna().unique().tolist()),
)

filtered = df[df["workflow_status"].isin(status_filter) & df["risk_level"].isin(risk_filter)]

st.dataframe(
    filtered[
        [
            "id", "hospital_name", "provider_name", "claim_amount",
            "risk_level", "prediction_text", "workflow_status",
            "decision", "submitted_at"
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

claim_ids = filtered["id"].tolist()
selected_claim = st.selectbox("Open Claim Detail", claim_ids)

detail = get_claim_detail(selected_claim)

st.markdown(f"## Claim Detail #{selected_claim}")

top1, top2, top3 = st.columns(3)
with top1:
    if detail["risk_level"] == "High Risk":
        render_badge("High Risk", "high")
    elif detail["risk_level"] == "Medium Risk":
        render_badge("Medium Risk", "medium")
    else:
        render_badge("Low Risk", "low")

with top2:
    status = detail["workflow_status"]
    if status == "approved":
        render_badge("Approved", "approved")
    elif status == "rejected":
        render_badge("Rejected", "rejected")
    else:
        render_badge("Under Review", "pending")

with top3:
    st.metric("Fraud Probability", f"{float(detail['fraud_probability'] or 0):.2%}")

left, right = st.columns([1, 1])

with left:
    st.markdown("### Claim Information")
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    render_field("Full Name", detail["full_name"])
    render_field("Age", detail["age"])
    render_field("Gender", detail["gender"])
    render_field("Hospital Name", detail["hospital_name"])
    render_field("Provider Name", detail["provider_name"])
    render_field("Location", detail["location"])
    render_field("Diagnosis", f"{detail['diagnosis_code']} — {get_diagnosis_name(detail['diagnosis_code'])}")
    render_field("Procedure", f"{detail['procedure_code']} — {get_procedure_name(detail['procedure_code'])}")
    render_field("Procedure Count", detail["procedure_count"])
    render_field("Admission Type", detail["admission_type"])
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("### Billing & AI Summary")
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    render_field("Claim Amount", f"₹ {float(detail['claim_amount']):,.2f}")
    render_field("Insurance Coverage", f"₹ {float(detail['insurance_coverage']):,.2f}")
    render_field("Out of Pocket", f"₹ {float(detail['out_of_pocket']):,.2f}")
    render_field("Prediction", detail["prediction_text"])
    render_field("Review Decision", detail.get("decision") or "Pending")
    render_field("Admin Remarks", detail.get("remarks") or "No remarks yet")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("### AI Summary")
st.info(detail.get("user_summary") or "No AI summary available.")

st.markdown("### Risk Reasons")
for reason in detail.get("risk_reasons", []):
    st.write(f"- {reason}")

st.markdown("### Claim Timeline")
for event in detail.get("timeline", []):
    st.markdown(
        f"**{event['event_title']}**  \n"
        f"{event['event_description'] or ''}  \n"
        f"`{event['created_at']}`"
    )

if detail.get("alerts"):
    st.markdown("### Anomaly Alerts")
    for alert in detail["alerts"]:
        if alert["severity"] == "high":
            st.error(alert["message"])
        else:
            st.warning(alert["message"])