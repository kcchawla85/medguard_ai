from dataclasses import dataclass


@dataclass
class ClaimPayload:
    full_name: str
    age: int
    gender: str
    hospital_name: str
    provider_name: str
    location: str
    diagnosis_code: str
    procedure_code: str
    procedure_count: int
    admission_type: str
    date_of_service: str
    claim_amount: float
    insurance_coverage: float
    out_of_pocket: float
    billing_date: str
    description: str = ""