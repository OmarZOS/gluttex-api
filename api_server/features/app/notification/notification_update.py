


from features.business.staff.staff_fetch import touch_rule_by_id
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.app.notification.notification_fetch import touch_notification_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func
import datetime 

def read_notification(notification_id: int):
    # Build conditions dynamically
    old_notification = touch_notification_by_id(notification_id)
    if int(notification_id) != 0:
        if not old_notification :
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=NOTIFICATION_NOT_EXISTS,
            details=f"notification number '{notification_id}' already exists."
        )

    old_notification.notification_read_at = datetime.datetime.now()

    try:
        final_notification = update_record_in_api(old_notification)
        return final_notification
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=NOTIFICATION_INSERT_FAILED,
            details=f"{str(e)}"
        )





def answer_staff(rule_id: int,answer :int):
    # Build conditions dynamically
    old_rule = touch_rule_by_id(rule_id)
    if int(rule_id) != 0:
        if not old_rule :
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=RULE_NOT_EXISTS,
            details=f"Rule number '{rule_id}' doesn't exists."
        )
    if answer == 0:
        old_rule.management_rule_status = 'ACTIVE'
    else: 
        old_rule.management_rule_status = 'REJECTED'
    
    try:
        final_rule = update_record_in_api(old_rule)
        return final_rule
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=RULE_INSERT_FAILED,
            details=f"{str(e)}"
        )











