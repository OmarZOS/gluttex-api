

class Patient_API(BaseModel):
    id_patient: int
    patient_person_id: Optional[int]
    patient_disease_severity_id: Optional[int]

    #  Diagnosis
    id_diagnosis: int
    diagnosis_details: Optional[str]
    diagnosis_date: Optional[str]  # You might need to handle date formats
    patient_id: Optional[int]

    # DiseaseSeverity_API
    id_disease_severity: int
    disease_severity_desc: Optional[str]

