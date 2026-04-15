DIAGNOSIS_CODES = {
    "D100": {
        "name": "Routine General Consultation",
        "category": "general",
        "expected_procedures": ["P100", "P200", "P300"],
        "risk_weight": 0.10,
    },
    "D110": {
        "name": "Seasonal Viral Fever",
        "category": "general",
        "expected_procedures": ["P100", "P200", "P310"],
        "risk_weight": 0.12,
    },
    "D120": {
        "name": "Mild Respiratory Infection",
        "category": "respiratory",
        "expected_procedures": ["P100", "P200", "P320"],
        "risk_weight": 0.15,
    },
    "D130": {
        "name": "Hypertension Review",
        "category": "cardiac",
        "expected_procedures": ["P100", "P200", "P330"],
        "risk_weight": 0.18,
    },
    "D140": {
        "name": "Diabetes Management",
        "category": "endocrine",
        "expected_procedures": ["P100", "P200", "P340"],
        "risk_weight": 0.20,
    },
    "D150": {
        "name": "Minor Injury Assessment",
        "category": "trauma",
        "expected_procedures": ["P100", "P210", "P350"],
        "risk_weight": 0.18,
    },
    "D160": {
        "name": "Routine Cardiac Check",
        "category": "cardiac",
        "expected_procedures": ["P200", "P330", "P360"],
        "risk_weight": 0.22,
    },
    "D170": {
        "name": "Digestive Disorder Review",
        "category": "gastro",
        "expected_procedures": ["P100", "P200", "P370"],
        "risk_weight": 0.18,
    },
    "D180": {
        "name": "Orthopedic Follow-Up",
        "category": "orthopedic",
        "expected_procedures": ["P200", "P380", "P390"],
        "risk_weight": 0.20,
    },
    "D190": {
        "name": "Kidney Function Evaluation",
        "category": "renal",
        "expected_procedures": ["P200", "P340", "P400"],
        "risk_weight": 0.24,
    },
    "D200": {
        "name": "Emergency Cardiac Complaint",
        "category": "cardiac_emergency",
        "expected_procedures": ["P360", "P410", "P420"],
        "risk_weight": 0.55,
    },
    "D210": {
        "name": "Acute Respiratory Distress",
        "category": "respiratory_emergency",
        "expected_procedures": ["P320", "P430", "P440"],
        "risk_weight": 0.52,
    },
    "D220": {
        "name": "Surgical Abdomen Suspicion",
        "category": "surgical",
        "expected_procedures": ["P370", "P450", "P460"],
        "risk_weight": 0.58,
    },
    "D230": {
        "name": "Neurological Emergency Review",
        "category": "neuro",
        "expected_procedures": ["P470", "P480", "P490"],
        "risk_weight": 0.60,
    },
    "D240": {
        "name": "Complex Multi-System Evaluation",
        "category": "complex",
        "expected_procedures": ["P420", "P460", "P490"],
        "risk_weight": 0.65,
    },
}

PROCEDURE_CODES = {
    "P100": {
        "name": "Routine Consultation",
        "category": "general",
        "complexity": "low",
        "risk_weight": 0.08,
    },
    "P200": {
        "name": "Routine Blood Test",
        "category": "lab",
        "complexity": "low",
        "risk_weight": 0.10,
    },
    "P210": {
        "name": "Basic Wound Care",
        "category": "trauma",
        "complexity": "low",
        "risk_weight": 0.12,
    },
    "P300": {
        "name": "Basic Vital Screening",
        "category": "general",
        "complexity": "low",
        "risk_weight": 0.08,
    },
    "P310": {
        "name": "Fever Panel Test",
        "category": "lab",
        "complexity": "medium",
        "risk_weight": 0.14,
    },
    "P320": {
        "name": "Chest Imaging",
        "category": "respiratory",
        "complexity": "medium",
        "risk_weight": 0.18,
    },
    "P330": {
        "name": "Cardiac Monitoring",
        "category": "cardiac",
        "complexity": "medium",
        "risk_weight": 0.22,
    },
    "P340": {
        "name": "Kidney and Metabolic Panel",
        "category": "renal",
        "complexity": "medium",
        "risk_weight": 0.20,
    },
    "P350": {
        "name": "Minor Imaging Procedure",
        "category": "trauma",
        "complexity": "medium",
        "risk_weight": 0.18,
    },
    "P360": {
        "name": "Advanced Cardiac Evaluation",
        "category": "cardiac",
        "complexity": "high",
        "risk_weight": 0.40,
    },
    "P370": {
        "name": "Abdominal Diagnostic Scan",
        "category": "gastro",
        "complexity": "high",
        "risk_weight": 0.36,
    },
    "P380": {
        "name": "Orthopedic Imaging",
        "category": "orthopedic",
        "complexity": "medium",
        "risk_weight": 0.22,
    },
    "P390": {
        "name": "Joint Procedure",
        "category": "orthopedic",
        "complexity": "high",
        "risk_weight": 0.34,
    },
    "P400": {
        "name": "Renal Monitoring Procedure",
        "category": "renal",
        "complexity": "high",
        "risk_weight": 0.32,
    },
    "P410": {
        "name": "Emergency Cardiac Intervention",
        "category": "cardiac_emergency",
        "complexity": "critical",
        "risk_weight": 0.60,
    },
    "P420": {
        "name": "Critical Care Monitoring",
        "category": "complex",
        "complexity": "critical",
        "risk_weight": 0.58,
    },
    "P430": {
        "name": "Respiratory Support Procedure",
        "category": "respiratory_emergency",
        "complexity": "high",
        "risk_weight": 0.42,
    },
    "P440": {
        "name": "Emergency Airway Procedure",
        "category": "respiratory_emergency",
        "complexity": "critical",
        "risk_weight": 0.62,
    },
    "P450": {
        "name": "Minor Surgical Procedure",
        "category": "surgical",
        "complexity": "high",
        "risk_weight": 0.38,
    },
    "P460": {
        "name": "Major Surgical Procedure",
        "category": "surgical",
        "complexity": "critical",
        "risk_weight": 0.65,
    },
    "P470": {
        "name": "Neurological Scan",
        "category": "neuro",
        "complexity": "high",
        "risk_weight": 0.40,
    },
    "P480": {
        "name": "Brain Imaging Procedure",
        "category": "neuro",
        "complexity": "critical",
        "risk_weight": 0.58,
    },
    "P490": {
        "name": "Advanced Neurological Intervention",
        "category": "neuro",
        "complexity": "critical",
        "risk_weight": 0.70,
    },
}


def diagnosis_options():
    return [f"{code} - {meta['name']}" for code, meta in DIAGNOSIS_CODES.items()]


def procedure_options():
    return [f"{code} - {meta['name']}" for code, meta in PROCEDURE_CODES.items()]


def extract_code(selection: str) -> str:
    return selection.split(" - ")[0].strip()


def get_diagnosis_name(code: str) -> str:
    return DIAGNOSIS_CODES.get(code, {}).get("name", "Unknown Diagnosis")


def get_procedure_name(code: str) -> str:
    return PROCEDURE_CODES.get(code, {}).get("name", "Unknown Procedure")