


from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func


def touch_notification_by_id(id : int):
    data = storage_broker.get(
        Notification,
        {Notification.id_notification:id},
        None,
        [
        ]
    )
    
    if data == []:
        return None

    return data[0]


def fetch_notifications(notification_user_ref, offset, limit):
    # Build conditions dynamically
    conditions = {}

    if int(notification_user_ref) !=0:
        conditions[Notification.notification_user_ref] = int(notification_user_ref)

    # Fetch data
    rule_list = storage_broker.get(
        Notification,
        conditions,
        None,
        [],
        offset,
        limit,
    )

    return rule_list












