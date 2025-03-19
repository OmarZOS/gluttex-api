
# here, we make schema translations

from core.api_models import Serology_API
from core.messages import PATIENT_NOT_EXISTS, SEROLOGY_ALREADY_EXISTS, SEROLOGY_INDICATOR_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.health.fetch_serology import fetch_serology_by_indicator_and_date, fetch_serology_indicator_by_id, get_patient_by_id



def build_serology(serology_api: Serology_API):
    return Serology(
            indicator_id=serology_api.serology_indicator_id,
            serology_date=serology_api.serology_date,
            patient_id=serology_api.id_patient,
            indicator_value=serology_api.serology_indicator_value
        )

def insert_serology(serology_api: Serology_API):
    
    serology_old = fetch_serology_by_indicator_and_date(serology_api.id_patient,serology_api.serology_indicator_id,serology_api.serology_date)
    if serology_old != [] : 
        raise Exception(SEROLOGY_ALREADY_EXISTS)

    serology_indicator = fetch_serology_indicator_by_id(serology_api.serology_indicator_id)
    if serology_indicator == [] : 
        raise Exception(SEROLOGY_INDICATOR_NOT_EXISTS)

    serology_owner = get_patient_by_id(serology_api.id_patient)
    if serology_owner == [] : 
        raise Exception(PATIENT_NOT_EXISTS)

    serology = build_serology(serology_api)

    code,serology,msg = insert_or_complete_or_raise(serology)
    if (code == 1): return msg
    
    return serology










