from typing import Dict, Any, Optional
from core.api_models import Notification_API
from core.models import Notification
from services.notification_service import NotificationService

from datetime import datetime


class NotificationBuilderService:
    """Builder pattern for creating different types of notifications"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def build_invitation_notification(
        self, 
        user_ref: int, 
        role_name: str, 
        invited_by: str
    ) -> Notification_API:
        """Build an invitation notification"""
        return Notification_API(
            notification_code="ROLE_INVITATION",
            notification_params={
                "role_name": role_name,
                "invited_by": invited_by,
                "invitation_date": str(datetime.datetime.now())
            },
            notification_user_ref=user_ref
        )
    
    def build_system_alert_notification(
        self, 
        user_ref: int, 
        alert_type: str, 
        message: str
    ) -> Notification_API:
        """Build a system alert notification"""
        return Notification_API(
            notification_code="SYSTEM_ALERT",
            notification_params={
                "alert_type": alert_type,
                "message": message,
                "timestamp": str(datetime.datetime.now())
            },
            notification_user_ref=user_ref
        )
    
    def build_reminder_notification(
        self, 
        user_ref: int, 
        reminder_type: str, 
        due_date: str
    ) -> Notification_API:
        """Build a reminder notification"""
        return Notification_API(
            notification_code="REMINDER",
            notification_params={
                "reminder_type": reminder_type,
                "due_date": due_date,
                "created_at": str(datetime.datetime.now())
            },
            notification_user_ref=user_ref
        )
    
    def create_and_send_invitation(
        self, 
        user_ref: int, 
        role_name: str, 
        invited_by: str
    ) -> Notification:
        """Create and send an invitation notification"""
        notification_data = self.build_invitation_notification(
            user_ref, role_name, invited_by
        )
        return self.notification_service.create_notification(notification_data)