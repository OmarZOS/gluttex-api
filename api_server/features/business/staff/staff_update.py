


from features.business.staff.staff_add import build_rule
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from core.api_models import ManagementRule_API
from features.business.staff.staff_fetch import touch_rule_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func

def update_staff(rule: ManagementRule_API):
    # Build conditions dynamically
    old_rule = touch_rule_by_id(rule.id_management_rule)
    if int(rule.id_management_rule) != 0:
        if not old_rule :
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=RULE_NOT_EXISTS,
            details=f"Rule number '{rule.id_management_rule}' not exists."
        )

    new_rule = build_rule(rule)

    old_rule.management_rule_code = new_rule.management_rule_code
    old_rule.management_rule_status = new_rule.management_rule_status
    old_rule.management_rule_expiry = new_rule.management_rule_expiry

    

    try:
        final_rule = update_record_in_api(old_rule)
        return final_rule
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=RULE_INSERT_FAILED,
            details=f"{str(e)}"
        )












