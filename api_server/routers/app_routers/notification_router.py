# routers/notification_router.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from core.api_models import Notification_API
from core.exception_handler import APIException
from core.messages import *
from services.notification_service import NotificationService
from services.helpers.notification_builder_service import NotificationBuilderService

notification_router = APIRouter()

# Dependency injection
def get_notification_service() -> NotificationService:
    return NotificationService()

def get_notification_builder() -> NotificationBuilderService:
    return NotificationBuilderService()

@notification_router.post("/create")
def create_notification(
    notification: Notification_API,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Create a new notification.
    """
    return notification_service.create_notification(notification)

@notification_router.get("/{notification_id}")
def get_notification(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get notification by ID.
    """
    return notification_service.get_notification_by_id(notification_id)

@notification_router.get("/user/{user_ref}")
def get_user_notifications(
    user_ref: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get all notifications for a user with pagination.
    """
    return notification_service.get_user_notifications(user_ref, offset, limit)

@notification_router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark a specific notification as read.
    """
    return notification_service.mark_notification_as_read(notification_id)

@notification_router.put("/user/{user_ref}/read-all")
def mark_all_notifications_as_read(
    user_ref: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Mark all notifications for a user as read.
    """
    count = notification_service.mark_all_notifications_as_read(user_ref)
    return {
        "message": f"Marked {count} notifications as read",
        "user_ref": user_ref,
        "marked_count": count
    }

@notification_router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Delete a specific notification.
    """
    success = notification_service.delete_notification(notification_id)
    if success:
        return {"message": f"Notification {notification_id} deleted successfully"}
    raise APIException(
        status=HTTP_404_NOT_FOUND,
        code=NOTIFICATION_NOT_EXISTS,
        details=f"Notification {notification_id} not found"
    )

@notification_router.delete("/user/{user_ref}/all")
def delete_all_user_notifications(
    user_ref: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Delete all notifications for a user.
    """
    count = notification_service.delete_all_user_notifications(user_ref)
    return {
        "message": f"Deleted {count} notifications for user {user_ref}",
        "user_ref": user_ref,
        "deleted_count": count
    }

@notification_router.get("/user/{user_ref}/unread-count")
def get_unread_count(
    user_ref: int,
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Get count of unread notifications for a user.
    """
    return notification_service.get_unread_notification_count(user_ref)

@notification_router.post("/invitation/send")
def send_invitation_notification(
    user_ref: int,
    role_name: str,
    invited_by: str,
    notification_builder: NotificationBuilderService = Depends(get_notification_builder)
):
    """
    Send an invitation notification to a user.
    """
    notification = notification_builder.create_and_send_invitation(
        user_ref, role_name, invited_by
    )
    return {
        "message": f"Invitation sent to user {user_ref}",
        "notification": notification
    }

@notification_router.post("/bulk/create")
def bulk_create_notifications(
    notifications: List[Notification_API],
    notification_service: NotificationService = Depends(get_notification_service)
):
    """
    Create multiple notifications at once.
    """
    created = notification_service.bulk_create_notifications(notifications)
    return {
        "message": f"Successfully created {len(created)} notifications",
        "notifications": created
    }