def map_dashboard_input_to_model_features(claim: dict) -> dict:
    claim_amount = claim.get("claim_amount", 0)
    procedure_count = claim.get("procedure_count", 1)
    age = claim.get("age", 0)
    admission_type = claim.get("admission_type", "planned").lower()
    out_of_pocket = claim.get("out_of_pocket", 0)

    claim_period_days = 2 if admission_type == "planned" else 6
    admission_period_days = 1 if admission_type == "planned" else 5
    phy_count = min(max(procedure_count, 1), 3)
    phy_same = 0 if procedure_count <= 2 else 3

    return {
        "phy_same": phy_same,
        "phy_count": phy_count,
        "claim_period_days": claim_period_days,
        "admission_period_days": admission_period_days,
        "age": age,
        "alife": 1,
        "provider_InscClaimAmtReimbursed_mean": claim_amount * 1.00,
        "provider_InscClaimAmtReimbursed_std": claim_amount * 0.20,
        "provider_DeductibleAmtPaid_mean": out_of_pocket,
        "provider_DeductibleAmtPaid_std": max(out_of_pocket * 0.10, 1),
        "bene_InscClaimAmtReimbursed_mean": claim_amount * 0.95,
        "bene_InscClaimAmtReimbursed_std": claim_amount * 0.18,
        "bene_DeductibleAmtPaid_mean": out_of_pocket * 0.95,
        "bene_DeductibleAmtPaid_std": max(out_of_pocket * 0.08, 1),
        "diag1_InscClaimAmtReimbursed_mean": claim_amount * 0.98,
        "diag1_InscClaimAmtReimbursed_std": claim_amount * 0.19,
        "diag1_DeductibleAmtPaid_mean": out_of_pocket * 0.98,
        "diag1_DeductibleAmtPaid_std": max(out_of_pocket * 0.09, 1),
        "provider_NoOfMonths_PartACov_mean": 12,
        "provider_NoOfMonths_PartBCov_mean": 12,
        "bene_NoOfMonths_PartACov_mean": 12,
        "bene_NoOfMonths_PartBCov_mean": 12,
        "diag1_NoOfMonths_PartACov_mean": 12,
        "diag1_NoOfMonths_PartBCov_mean": 12,
        "provider_IPAnnualReimbursementAmt_mean": claim_amount * 0.45,
        "provider_OPAnnualReimbursementAmt_mean": claim_amount * 0.55,
        "bene_IPAnnualReimbursementAmt_mean": claim_amount * 0.42,
        "bene_OPAnnualReimbursementAmt_mean": claim_amount * 0.52,
        "diag1_IPAnnualReimbursementAmt_mean": claim_amount * 0.44,
        "diag1_OPAnnualReimbursementAmt_mean": claim_amount * 0.54,
    }