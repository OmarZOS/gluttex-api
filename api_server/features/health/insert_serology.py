
# here, we make schema translations

from core.exception_handler import APIException
from core.api_models import Serology_API
from core.messages import *
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
        raise APIException(status= HTTP_409_CONFLICT,code=SEROLOGY_ALREADY_EXISTS,message=SEROLOGY_ALREADY_EXISTS,meassage=f"{SEROLOGY_ALREADY_EXISTS}: {serology_api.serology_date}")

    serology_indicator = fetch_serology_indicator_by_id(serology_api.serology_indicator_id)
    if serology_indicator == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=SEROLOGY_INDICATOR_NOT_EXISTS,message=SEROLOGY_INDICATOR_NOT_EXISTS,meassage=f"{SEROLOGY_INDICATOR_NOT_EXISTS}: {serology_api.serology_indicator_id}")

    serology_owner = get_patient_by_id(serology_api.id_patient)
    if serology_owner == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=PATIENT_NOT_EXISTS,message=PATIENT_NOT_EXISTS,meassage=f"{PATIENT_NOT_EXISTS}: {serology_api.id_patient}")

    serology = build_serology(serology_api)

    
    try:
        serology = insert_or_complete_or_raise(serology)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=SEROLOGY_INSERT_FAILED,details=f"{str(e)}")


    return serology










