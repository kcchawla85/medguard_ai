from services.database import create_anomaly_alert


def create_rule_based_alerts(claim_id: int, claim: dict, prediction_result: dict) -> list[dict]:
    created_alerts = []

    claim_amount = float(claim.get("claim_amount", 0))
    procedure_count = int(claim.get("procedure_count", 1))
    admission_type = str(claim.get("admission_type", "planned")).lower()
    risk_level = prediction_result.get("risk_level", "Low Risk")
    fraud_probability = float(prediction_result.get("fraud_probability", 0))

    def add(alert_type: str, severity: str, message: str):
        create_anomaly_alert(
            claim_id=claim_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )
        created_alerts.append({
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
        })

    if claim_amount >= 90000:
        add("claim_amount_spike", "high", "Claim amount is unusually high and exceeds the critical review threshold.")
    elif claim_amount >= 50000:
        add("claim_amount_spike", "medium", "Claim amount is higher than normal and should be reviewed.")

    if procedure_count >= 5:
        add("procedure_volume", "high", "Procedure count is unusually high for a single claim.")
    elif procedure_count >= 3:
        add("procedure_volume", "medium", "Multiple procedures were included in the claim.")

    if admission_type == "emergency" and claim_amount >= 40000:
        add("emergency_billing_pattern", "medium", "Emergency admission is combined with elevated billing values.")

    if risk_level == "High Risk" or fraud_probability >= 0.80:
        add("ai_high_risk_flag", "high", "The AI model flagged this claim as highly suspicious.")

    return created_alerts