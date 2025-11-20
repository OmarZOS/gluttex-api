
import json
import logging
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from features.app.notification.notification_update import read_notification
from features.app.notification.notification_fetch import fetch_notifications
from features.app.notification.builders.notification_builder import NotificationFactory


notification_router = APIRouter()
logger = logging.getLogger("FastAPIApp")



@notification_router.get("/notifications/{user_id}/{offset}/{limit}")
def get_notifications(user_id: int,offset: int, limit: int):
    """
    Fetch notifications with pagination.
    """
    return fetch_notifications(user_id, offset, limit)


@notification_router.put("/notification/{notification_id}")
def read_notif(notification_id: int):
    """
    read notification.
    """
    return read_notification(notification_id)




