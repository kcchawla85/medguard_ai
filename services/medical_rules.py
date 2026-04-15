from services.codebook import DIAGNOSIS_CODES, PROCEDURE_CODES, get_diagnosis_name, get_procedure_name


def evaluate_diagnosis_procedure_consistency(diagnosis_code: str, procedure_code: str) -> dict:
    diagnosis = DIAGNOSIS_CODES.get(diagnosis_code)
    procedure = PROCEDURE_CODES.get(procedure_code)

    if not diagnosis or not procedure:
        return {
            "is_consistent": True,
            "severity": "low",
            "message": "Diagnosis or procedure code could not be fully validated.",
            "score_adjustment": 0.0,
        }

    expected = diagnosis.get("expected_procedures", [])
    diagnosis_name = get_diagnosis_name(diagnosis_code)
    procedure_name = get_procedure_name(procedure_code)

    if procedure_code in expected:
        return {
            "is_consistent": True,
            "severity": "low",
            "message": f"The procedure '{procedure_name}' is consistent with diagnosis '{diagnosis_name}'.",
            "score_adjustment": 0.0,
        }

    procedure_complexity = procedure.get("complexity", "low")

    if procedure_complexity in {"critical", "high"}:
        return {
            "is_consistent": False,
            "severity": "high",
            "message": (
                f"The procedure '{procedure_name}' appears inconsistent with diagnosis "
                f"'{diagnosis_name}' and may require manual review."
            ),
            "score_adjustment": 0.20,
        }

    return {
        "is_consistent": False,
        "severity": "medium",
        "message": (
            f"The procedure '{procedure_name}' is not commonly expected for diagnosis "
            f"'{diagnosis_name}'."
        ),
        "score_adjustment": 0.10,
    }