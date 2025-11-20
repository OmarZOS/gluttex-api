# here, we make schema translations

from core.exception_handler import APIException
from core.messages import *
from features.insertion import delete_record_from_api
from features.medical.health.fetch_serology import fetch_serology_by_id



def delete_serology(serology_id: int):
    serologys = fetch_serology_by_id(serology_id)
    if serologys == []:
        exception = APIException()
        exception.code = HEALTH_DELETE_FAILED
        exception.status =HTTP
        raise APIException(SEROLOGY_NOT_EXISTS)
    # for now, just delete the serology, since we don't want to delete person records
    return delete_record_from_api(serologys[0])