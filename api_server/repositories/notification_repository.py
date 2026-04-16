# repositories/notification_repository.py
from typing import List, Optional, Dict, Any
from core.models import Notification
import storage.storage_broker as storage_broker

class NotificationRepository:
    """Repository for Notification-related database operations"""
    
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        data = storage_broker.get(
            Notification,
            {Notification.id_notification: notification_id},
            None,
            []
        )
        return data[0] if data else None
    
    def get_by_user_ref(
        self, 
        user_ref: int, 
        offset: int = 0, 
        limit: int = 100
    ) -> List[Notification]:
        """Get notifications by user reference"""
        conditions = {}
        if user_ref != 0:
            conditions[Notification.notification_user_ref] = user_ref
        
        return storage_broker.get(
            Notification,
            conditions,
            None,
            [],
            offset,
            limit,
        )
    
    def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(notification)
    
    def update(self, notification: Notification) -> Notification:
        """Update an existing notification"""
        from features.insertion import update_record_in_api
        return update_record_in_api(notification)
    
    def delete(self, notification_id: int) -> bool:
        """Delete a notification"""
        from features.insertion import delete_record_from_api
        notification = self.get_by_id(notification_id)
        if notification:
            return delete_record_from_api(notification)
        return False
    
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """Mark a notification as read"""
        notification = self.get_by_id(notification_id)
        if notification:
            import datetime
            notification.notification_read_at = datetime.datetime.now()
            return self.update(notification)
        return None
    
    def get_unread_count(self, user_ref: int) -> int:
        """Get count of unread notifications for a user"""
        notifications = self.get_by_user_ref(user_ref)
        return sum(1 for n in notifications if n.notification_read_at is None)