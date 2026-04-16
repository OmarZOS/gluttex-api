# services/notification_service.py
import logging
import datetime
from typing import List, Optional, Dict, Any
from core.api_models import Notification_API
from core.exception_handler import APIException
from core.messages import *
from core.models import Notification
from repositories.notification_repository import NotificationRepository
from communication.publisher import notify_invitation_to_role_received

logger = logging.getLogger("FastAPIApp")

class NotificationService:
    """Service for notification-related business logic"""
    
    def __init__(self):
        self.notification_repo = NotificationRepository()
    
    def _parse_expiry(self, value: str | None) -> datetime.datetime | None:
        """
        Parse management_notification_expiry without external libraries.
        Returns datetime or None.
        """
        if not value or str(value).lower() == "null":
            return None

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
                return datetime.datetime.strptime(value, fmt)
            except ValueError:
                continue

        return None
    
    def _build_notification_model(self, notification_data: Notification_API) -> Notification:
        """Convert API model to database model"""
        new_notification = Notification(
            notification_code=notification_data.notification_code,
            notification_params=notification_data.notification_params,
            notification_user_ref=notification_data.notification_user_ref,
        )
        
        # Set created at if not provided
        if not notification_data.notification_created_at:
            new_notification.notification_created_at = datetime.datetime.now()
        else:
            new_notification.notification_created_at = notification_data.notification_created_at
        
        # Set read at if provided
        if notification_data.notification_read_at:
            new_notification.notification_read_at = notification_data.notification_read_at
        
        return new_notification
    
    def create_notification(
        self, 
        notification_data: Notification_API
    ) -> Notification:
        """Create a new notification"""
        
        # Check if notification already exists
        if notification_data.id_notification:
            existing = self.notification_repo.get_by_id(
                notification_data.id_notification
            )
            if existing:
                raise APIException(
                    status=HTTP_409_CONFLICT,
                    code=NOTIFICATION_ALREADY_EXISTS,
                    details=f"Notification '{notification_data.id_notification}' already exists."
                )
        
        # Build notification model
        new_notification = self._build_notification_model(notification_data)
        
        try:
            return self.notification_repo.create(new_notification)
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=NOTIFICATION_INSERT_FAILED,
                details=str(e)
            )
    
    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        notification = self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=NOTIFICATION_NOT_EXISTS,
                details=f"Notification '{notification_id}' does not exist."
            )
        return notification
    
    def get_user_notifications(
        self, 
        user_ref: int, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """Get all notifications for a user"""
        return self.notification_repo.get_by_user_ref(user_ref, offset, limit)
    
    def mark_notification_as_read(self, notification_id: int) -> Notification:
        """Mark a single notification as read"""
        notification = self.get_notification_by_id(notification_id)
        
        if notification.notification_read_at:
            # Already read, return as is
            return notification
        
        try:
            updated = self.notification_repo.mark_as_read(notification_id)
            if not updated:
                raise APIException(
                    status=HTTP_404_NOT_FOUND,
                    code=NOTIFICATION_NOT_EXISTS,
                    details=f"Notification '{notification_id}' not found."
                )
            return updated
        except Exception as e:
            logger.error(f"Failed to mark notification as read: {e}")
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=NOTIFICATION_UPDATE_FAILED,
                details=str(e)
            )
    
    def mark_all_notifications_as_read(self, user_ref: int) -> int:
        """Mark all notifications for a user as read"""
        notifications = self.get_user_notifications(user_ref)
        unread_count = 0
        
        for notification in notifications:
            if not notification.notification_read_at:
                try:
                    self.mark_notification_as_read(notification.id_notification)
                    unread_count += 1
                except Exception as e:
                    logger.warning(f"Failed to mark notification {notification.id_notification}: {e}")
        
        return unread_count
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification"""
        notification = self.get_notification_by_id(notification_id)
        return self.notification_repo.delete(notification_id)
    
    def delete_all_user_notifications(self, user_ref: int) -> int:
        """Delete all notifications for a user"""
        notifications = self.get_user_notifications(user_ref)
        deleted_count = 0
        
        for notification in notifications:
            try:
                if self.notification_repo.delete(notification.id_notification):
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete notification {notification.id_notification}: {e}")
        
        return deleted_count
    
    def get_unread_notification_count(self, user_ref: int) -> Dict[str, Any]:
        """Get count of unread notifications for a user"""
        count = self.notification_repo.get_unread_count(user_ref)
        return {
            "user_ref": user_ref,
            "unread_count": count
        }
    
    def send_invitation_notification(
        self, 
        user_ref: int, 
        invitation_data: Dict[str, Any]
    ) -> Notification:
        """Send an invitation notification to a user"""
        
        # Create notification
        notification_data = Notification_API(
            notification_code="INVITATION_RECEIVED",
            notification_params=invitation_data,
            notification_user_ref=user_ref,
        )
        
        notification = self.create_notification(notification_data)
        
        # Publish to message queue if needed
        try:
            notify_invitation_to_role_received(notification)
        except Exception as e:
            logger.warning(f"Failed to publish invitation notification: {e}")
        
        return notification
    
    def bulk_create_notifications(
        self, 
        notifications_data: List[Notification_API]
    ) -> List[Notification]:
        """Create multiple notifications at once"""
        created = []
        errors = []
        
        for notification_data in notifications_data:
            try:
                notification = self.create_notification(notification_data)
                created.append(notification)
            except Exception as e:
                errors.append({
                    "data": notification_data.dict(),
                    "error": str(e)
                })
        
        if errors and not created:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=NOTIFICATION_BULK_INSERT_FAILED,
                details=f"Failed to create {len(errors)} notifications",
                data={"errors": errors}
            )
        
        return created