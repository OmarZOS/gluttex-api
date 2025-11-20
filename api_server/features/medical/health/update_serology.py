


# here, we make schema translations

from datetime import datetime
from core.exception_handler import APIException
from core.api_models import Serology_API
from core.models import *
from features.insertion import update_record_in_api
from features.medical.health.fetch_serology import fetch_serology_by_id
from core.messages import *





def update_serology(serology_id: int,serology_api: Serology_API):
    
    serologies_old = fetch_serology_by_id(serology_id)
    if serologies_old == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=SEROLOGY_NOT_EXISTS)

    serology_old = serologies_old[0]

    serology_old.serology_date  = serology_api.serology_date,
    serology_old.indicator_value  = serology_api.serology_indicator_value
    # serology_old.serology_last_updated  = datetime.now(),

    serology = update_record_in_api(serology_old)
    
    return serology





