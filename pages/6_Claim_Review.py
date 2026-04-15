import streamlit as st

from services.auth import require_admin, sidebar_login
from services.database import get_all_claims, get_claim_detail, review_claim
from services.ui_helpers import inject_custom_css, render_field, render_badge
from services.codebook import get_diagnosis_name, get_procedure_name

sidebar_login()
require_admin()
inject_custom_css()

st.title("Claim Review")

all_claims = get_all_claims()
if not all_claims:
    st.info("No claims available.")
    st.stop()

claim_ids = [c["id"] for c in all_claims]
selected_claim_id = st.selectbox("Select Claim ID", claim_ids)

detail = get_claim_detail(selected_claim_id)
if not detail:
    st.error("Claim not found.")
    st.stop()

st.markdown(f"## Claim Detail #{selected_claim_id}")

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
    render_field("User", detail["full_name"])
    render_field("Email", detail["email"])
    render_field("Age", detail["age"])
    render_field("Gender", detail["gender"])
    render_field("Hospital", detail["hospital_name"])
    render_field("Provider", detail["provider_name"])
    render_field("Location", detail["location"])
    render_field("Diagnosis", f"{detail['diagnosis_code']} — {get_diagnosis_name(detail['diagnosis_code'])}")
    render_field("Procedure", f"{detail['procedure_code']} — {get_procedure_name(detail['procedure_code'])}")
    render_field("Procedure Count", detail["procedure_count"])
    render_field("Admission Type", detail["admission_type"])
    render_field("Claim Amount", f"₹ {float(detail['claim_amount']):,.2f}")
    render_field("Insurance Coverage", f"₹ {float(detail['insurance_coverage']):,.2f}")
    render_field("Out of Pocket", f"₹ {float(detail['out_of_pocket']):,.2f}")
    render_field("Description", detail["description"] or "N/A")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("### AI Fraud Analysis")
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    render_field("Prediction", detail["prediction_text"])
    render_field("Risk Level", detail["risk_level"])
    render_field("Current Decision", detail.get("decision") or "Pending")
    render_field("Current Remarks", detail.get("remarks") or "No remarks")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Admin Summary")
    st.info(detail.get("admin_summary") or "No admin summary available.")

    st.markdown("### Risk Reasons")
    for reason in detail.get("risk_reasons", []):
        st.write(f"- {reason}")

    if detail.get("alerts"):
        st.markdown("### Anomaly Alerts")
        for alert in detail["alerts"]:
            if alert["severity"] == "high":
                st.error(alert["message"])
            else:
                st.warning(alert["message"])

st.markdown("---")
timeline_col, review_col = st.columns([1, 1])

with timeline_col:
    st.subheader("Claim Timeline")
    for event in detail.get("timeline", []):
        st.markdown(
            f"**{event['event_title']}**  \n"
            f"{event['event_description'] or ''}  \n"
            f"`{event['created_at']}`"
        )
        st.markdown("---")

with review_col:
    st.subheader("Admin Review")
    with st.form("review_form"):
        decision = st.radio("Decision", ["approved", "rejected"], horizontal=True)
        remarks = st.text_area("Remarks", value=detail.get("remarks") or "")
        submitted = st.form_submit_button("Save Review", use_container_width=True)

    if submitted:
        review_claim(
            claim_id=selected_claim_id,
            admin_id=st.session_state.user["id"],
            decision=decision,
            remarks=remarks,
        )
        st.success("Review saved successfully.")
        st.rerun()