# here, we make schema translations

from core.exception_handler import APIException
from core.api_models import Serology_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.health.fetch_serology import get_patient_by_id
from datetime import datetime
from features.health.symptoms_fetch import get_symptom_by_id;


def insert_symptoms(symptoms_api: Serology_API):
    
    symptoms_owner = get_patient_by_id(symptoms_api.id_patient)
    if symptoms_owner == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=PATIENT_NOT_EXISTS,message=PATIENT_NOT_EXISTS,meassage=f"{PATIENT_NOT_EXISTS}: {symptoms_api.id_patient}")

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
        
        try:
            symptoms_occurence = insert_or_complete_or_raise(symptoms_occurence)
        except Exception as e:
            raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=SYMPTOM_INSERT_FAILED,details=f"{str(e)}")
        
        
        
        
        
        return symptoms_occurence

    return "Haven't inserted symptoms, none specified"

