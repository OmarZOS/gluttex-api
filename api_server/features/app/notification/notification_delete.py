from features.insertion import delete_record_from_api
from features.business.staff.staff_fetch import touch_rule_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func

def delete_rule(rule_id):

    old_rule = touch_rule_by_id(rule_id)
    if not old_rule :
        raise APIException(status= HTTP_404_NOT_FOUND,code=RULE_NOT_EXISTS,message=f"{RULE_DELETE_FAILED}: {rule_id}")
        
    return delete_record_from_api(old_rule)












