import streamlit as st

from models.schemas import ClaimPayload
from services.auth import require_user, sidebar_login
from services.database import create_claim, create_prediction
from services.predictor import get_predictor
from services.alerts import create_rule_based_alerts
from services.codebook import (
    diagnosis_options,
    procedure_options,
    extract_code,
    get_diagnosis_name,
    get_procedure_name,
)

sidebar_login()
require_user()

st.title("Submit Claim")
st.caption("Submit a new health insurance claim for AI fraud screening")

diag_opts = diagnosis_options()
proc_opts = procedure_options()

with st.form("submit_claim_form"):
    st.subheader("Patient Information")
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", value=st.session_state.user["full_name"])
        age = st.number_input("Age", min_value=0, max_value=120, value=42)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    with col2:
        hospital_name = st.text_input("Hospital Name", value="General Health Center")
        provider_name = st.text_input("Provider Name", value="Dr. Singh")
        location = st.text_input("Location", value="Delhi")

    st.subheader("Medical Details")
    col3, col4 = st.columns(2)
    with col3:
        diagnosis_selection = st.selectbox("Diagnosis Code", diag_opts, index=0)
        procedure_selection = st.selectbox("Procedure Code", proc_opts, index=1)
        procedure_count = st.number_input("Procedure Count", min_value=1, max_value=10, value=1)
    with col4:
        admission_type = st.selectbox("Admission Type", ["planned", "emergency"])
        date_of_service = st.date_input("Date of Service")
        billing_date = st.date_input("Billing Date")

    st.subheader("Selected Medical Meanings")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.info(f"Diagnosis: {diagnosis_selection}")
    with dcol2:
        st.info(f"Procedure: {procedure_selection}")

    st.subheader("Billing Details")
    col5, col6 = st.columns(2)
    with col5:
        claim_amount = st.number_input("Claim Amount", min_value=0.0, value=12000.0, step=500.0)
        insurance_coverage = st.number_input("Insurance Coverage", min_value=0.0, value=10000.0, step=500.0)
    with col6:
        out_of_pocket = st.number_input("Out of Pocket", min_value=0.0, value=2000.0, step=100.0)
        description = st.text_area("Description", value="Standard medical treatment")

    submitted = st.form_submit_button("Submit Claim", use_container_width=True)

if submitted:
    diagnosis_code = extract_code(diagnosis_selection)
    procedure_code = extract_code(procedure_selection)

    payload = ClaimPayload(
        full_name=full_name,
        age=int(age),
        gender=gender,
        hospital_name=hospital_name,
        provider_name=provider_name,
        location=location,
        diagnosis_code=diagnosis_code,
        procedure_code=procedure_code,
        procedure_count=int(procedure_count),
        admission_type=admission_type,
        date_of_service=str(date_of_service),
        claim_amount=float(claim_amount),
        insurance_coverage=float(insurance_coverage),
        out_of_pocket=float(out_of_pocket),
        billing_date=str(billing_date),
        description=description,
    ).__dict__

    predictor = get_predictor()
    result = predictor.predict(payload)

    claim_id = create_claim(payload, st.session_state.user["id"])
    create_prediction(claim_id, result)
    created_alerts = create_rule_based_alerts(claim_id, payload, result)

    st.success(f"Claim submitted successfully. Claim ID: {claim_id}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Prediction", result["prediction_text"])
    c2.metric("Risk Level", result["risk_level"])
    c3.metric("Fraud Probability", f"{result['fraud_probability']:.2%}")

    if result["risk_level"] == "High Risk":
        st.error("This claim appears highly suspicious.")
    elif result["risk_level"] == "Medium Risk":
        st.warning("This claim needs closer review.")
    else:
        st.success("This claim appears low risk.")

    st.subheader("Readable Medical Information")
    st.write(f"**Diagnosis:** {diagnosis_code} — {get_diagnosis_name(diagnosis_code)}")
    st.write(f"**Procedure:** {procedure_code} — {get_procedure_name(procedure_code)}")

    st.subheader("AI Summary for User")
    st.info(result["user_summary"])

    st.subheader("Why the AI flagged this")
    for reason in result["risk_reasons"]:
        st.write(f"- {reason}")

    st.subheader("Diagnosis–Procedure Consistency Check")
    consistency = result["consistency_check"]
    if consistency["is_consistent"]:
        st.success(consistency["message"])
    else:
        if consistency["severity"] == "high":
            st.error(consistency["message"])
        else:
            st.warning(consistency["message"])

    if created_alerts:
        st.subheader("Anomaly Alerts")
        for alert in created_alerts:
            if alert["severity"] == "high":
                st.error(alert["message"])
            else:
                st.warning(alert["message"])