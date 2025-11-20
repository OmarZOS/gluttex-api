


from features.app.notification.notification_fetch import touch_notification_by_id
from features.insertion import insert_or_complete_or_raise
from core.api_models import  Notification_API
# from features.business.staff.staff_fetch import touch_notification_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func

from datetime import datetime




def parse_expiry(value: str | None):
    """
    Parse management_notification_expiry without external libraries.
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
def build_notification(notification: Notification_API):
    new_notification = Notification(
        # id_notification = notification.id_notification,
        notification_code  = notification.notification_code,
        notification_params  = notification.notification_params,
        notification_user_ref  = notification.notification_user_ref,
        
    )
    if notification.notification_created_at == None:
        new_notification.notification_created_at  = datetime.now(), 
    if notification.notification_read_at  :
        new_notification.notification_read_at  = notification.notification_read_at
    return new_notification




def insert_notification(notification: Notification_API):
    # Build conditions dynamically
    if notification.id_notification :
        if touch_notification_by_id(notification.id_notification):
                    raise APIException(
            status=HTTP_409_CONFLICT,
            code=NOTIFICATION_ALREADY_EXISTS,
            details=f"notification number '{notification.id_notification}' already exists."
        )
    new_notification = build_notification(notification)

    try:
        final_notification = insert_or_complete_or_raise(new_notification)
        return final_notification
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=NOTIFICATION_INSERT_FAILED,
            details=f"{str(e)}"
        )












