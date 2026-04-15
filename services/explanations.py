from services.codebook import get_diagnosis_name, get_procedure_name
from services.medical_rules import evaluate_diagnosis_procedure_consistency


def generate_risk_reasons(claim: dict, fraud_probability: float) -> list[str]:
    reasons = []

    claim_amount = float(claim.get("claim_amount", 0))
    procedure_count = int(claim.get("procedure_count", 1))
    admission_type = str(claim.get("admission_type", "planned")).lower()
    out_of_pocket = float(claim.get("out_of_pocket", 0))
    age = int(claim.get("age", 0))
    diagnosis_code = claim.get("diagnosis_code", "")
    procedure_code = claim.get("procedure_code", "")

    diagnosis_name = get_diagnosis_name(diagnosis_code)
    procedure_name = get_procedure_name(procedure_code)

    if claim_amount >= 75000:
        reasons.append("Claim amount is significantly higher than the normal expected range.")
    elif claim_amount >= 30000:
        reasons.append("Claim amount is moderately elevated and should be reviewed carefully.")

    if procedure_count >= 4:
        reasons.append("Procedure count is unusually high for a single submission.")
    elif procedure_count >= 3:
        reasons.append("Multiple procedures were reported in the same claim.")

    if admission_type == "emergency":
        reasons.append("Emergency admission increases fraud review priority due to higher billing variability.")

    if out_of_pocket >= 10000:
        reasons.append("Out-of-pocket amount is unusually high compared to typical claims.")

    if age >= 75:
        reasons.append("Patient age increases claim complexity and may require closer verification.")

    consistency = evaluate_diagnosis_procedure_consistency(diagnosis_code, procedure_code)
    if not consistency["is_consistent"]:
        reasons.append(consistency["message"])

    if fraud_probability >= 0.70:
        reasons.append("Overall model confidence indicates a high-risk fraud pattern.")
    elif fraud_probability >= 0.40:
        reasons.append("The AI model detected several features associated with medium-risk behavior.")

    if not reasons:
        reasons.append(
            f"The diagnosis '{diagnosis_name}' and procedure '{procedure_name}' appear consistent, "
            "and no strong fraud indicators were detected."
        )

    return reasons


def generate_user_summary(claim: dict, fraud_probability: float, risk_level: str, risk_reasons: list[str]) -> str:
    diagnosis_name = get_diagnosis_name(claim.get("diagnosis_code", ""))
    procedure_name = get_procedure_name(claim.get("procedure_code", ""))

    if risk_level == "High Risk":
        return (
            f"Your claim for '{diagnosis_name}' with procedure '{procedure_name}' has been submitted successfully. "
            "Our AI screening system identified several patterns that require detailed manual review before a final decision is made."
        )

    if risk_level == "Medium Risk":
        return (
            f"Your claim for '{diagnosis_name}' with procedure '{procedure_name}' has been submitted and screened by our AI system. "
            "It requires an additional review step before final processing."
        )

    return (
        f"Your claim for '{diagnosis_name}' with procedure '{procedure_name}' has been submitted successfully. "
        "At the moment, the claim appears to be low risk and is awaiting routine review."
    )


def generate_admin_summary(claim: dict, fraud_probability: float, risk_level: str, risk_reasons: list[str]) -> str:
    diagnosis_name = get_diagnosis_name(claim.get("diagnosis_code", ""))
    procedure_name = get_procedure_name(claim.get("procedure_code", ""))
    reasons_text = " ".join(risk_reasons[:3])

    if risk_level == "High Risk":
        return (
            f"The AI model classified this claim as high risk with a fraud probability of {fraud_probability:.2%}. "
            f"Diagnosis: {diagnosis_name}. Procedure: {procedure_name}. Key drivers include: {reasons_text} "
            "Manual review is strongly recommended before approval."
        )

    if risk_level == "Medium Risk":
        return (
            f"The AI model classified this claim as medium risk with a fraud probability of {fraud_probability:.2%}. "
            f"Diagnosis: {diagnosis_name}. Procedure: {procedure_name}. Key indicators include: {reasons_text}"
        )

    return (
        f"The AI model classified this claim as low risk with a fraud probability of {fraud_probability:.2%}. "
        f"Diagnosis: {diagnosis_name}. Procedure: {procedure_name}. The current pattern appears relatively normal."
    )