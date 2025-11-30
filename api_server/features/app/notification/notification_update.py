


from communication.publisher import notify_invitation_to_role_received
from core.api_models import Notification_API
from features.app.notification.builders.notification_builder import NotificationFactory
from features.app.notification.notification_add import build_notification, insert_notification
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













