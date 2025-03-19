# here, we make schema translations

from core.api_models import Serology_API
from core.messages import PATIENT_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.health.fetch_serology import get_patient_by_id
from datetime import datetime
from features.health.symptoms_fetch import get_symptom_by_id;


def insert_symptoms(symptoms_api: Serology_API):
    
    symptoms_owner = get_patient_by_id(symptoms_api.id_patient)
    if symptoms_owner == [] : 
        raise Exception(PATIENT_NOT_EXISTS)

    symptoms_occurence = SymptomsOccurence(
        symptoms_occurence_reason = symptoms_api.symptoms_occurence_reason ,
        reason_date = symptoms_api.reason_date ,
        symptoms_occurence_ref_patient = symptoms_api.id_patient ,
        symptoms_occurence_submission_time = datetime.now() ,
    )

    presented_symptoms = []
    for symptom_ref in symptoms_api.symptom_ids:
        if get_symptom_by_id(symptom_ref)!=[]:
            presented_symptoms.append(PresentedSymptom(presented_symptom_ref_symptom=symptom_ref)) 

    if presented_symptoms != [] :

        symptoms_occurence.presented_symptom = presented_symptoms
        code,symptoms_occurence,msg = insert_or_complete_or_raise(symptoms_occurence)
        if (code == 1): return msg
        return symptoms_occurence

    return "Haven't inserted symptoms, none specified"

