


from features.app.notification.notification_add import build_notification, insert_notification
from communication.publisher import notify_invitation_to_role_received
from features.app.notification.builders.notification_builder import *
from features.insertion import insert_or_complete_or_raise
from core.api_models import ManagementRule_API, Notification_API
from features.business.staff.staff_fetch import touch_rule_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func
from datetime import datetime 
from datetime import datetime




def parse_expiry(value: str | None):
    """
    Parse management_rule_expiry without external libraries.
    Returns datetime or None.
    """
    if not value or str(value).lower() == "null":
        return None

    # List of allowed formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",      # ISO no timezone
        "%Y-%m-%d %H:%M:%S",      # "YYYY-MM-DD HH:MM:SS"
        "%Y-%m-%d",               # Date only
        "%Y/%m/%d %H:%M:%S",      # Slash format
        "%d/%m/%Y %H:%M:%S",      # 01/02/2025 10:20:30
        "%d/%m/%Y",               # 01/02/2025
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None
def build_rule(rule: ManagementRule_API):
    new_rule = ManagementRule(
        rule_ref_org  = rule.rule_ref_org,
        rule_ref_provider  = rule.rule_ref_provider,
        rule_ref_user  = rule.rule_ref_user,
        management_rule_code  = rule.management_rule_code,
        management_rule_status = rule.management_rule_status,
        management_rule_expiry = parse_expiry(rule.management_rule_expiry),
    )

    if int(rule.id_management_rule) !=0 :
        new_rule.id_management_rule  = rule.id_management_rule
    return new_rule


def insert_rule(rule: ManagementRule_API):
    # Build conditions dynamically
    if int(rule.id_management_rule) != 0:
        if touch_rule_by_id(rule.id_management_rule):
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=RULE_ALREADY_EXISTS,
            details=f"Rule number '{rule.id_management_rule}' already exists."
        )
    new_rule = build_rule(rule)

    try:
        final_rule = insert_or_complete_or_raise(new_rule)
        notification = NotificationFactory.personnel.work_invitation(rule_id=final_rule.id_management_rule
                                                               ,role=final_rule.management_rule_code
                                                               ,provider_id=final_rule.rule_ref_provider
                                                               ,organization_id=final_rule.rule_ref_org
                                                               ,invited_by=final_rule.rule_ref_user)

        insert_notification(build_notification(Notification_API(
            #  id_notification = 0,
             notification_code="role_invitation",
             notification_params= NotificationFactory.dump_dict(notification),
             notification_user_ref= rule.rule_ref_user,
            #  notification_created_at= str(datetime.now())
        )))

        try:
            notify_invitation_to_role_received(notification,final_rule.rule_ref_user)
        except :
            pass

        return final_rule
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=RULE_INSERT_FAILED,
            details=f"{str(e)}"
        )












