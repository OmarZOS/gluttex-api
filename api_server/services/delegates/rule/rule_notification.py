"""
Notification handling for management rules.
"""

import logging
from datetime import datetime
from typing import Optional

from core.models.api_models import Notification_API
from services.notification_service import NotificationService
from services.helpers.notification_builder_service import NotificationBuilderService
from repositories.supplier_repository import SupplierRepository
from communication.publisher import notify_invitation_to_role_received, notify_rule_to_role_received

logger = logging.getLogger(__name__)


class RuleNotification:
    """Notification handler for management rule operations"""
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.notification_builder = NotificationBuilderService()
        self.supplier_repo = SupplierRepository()
    
    def create_invitation_notification(self, rule) -> None:
        """
        Create invitation notification for a rule.
        
        Args:
            rule: Created rule
        """
        try:
            notification = self.notification_builder.create_and_send_invitation(
                rule_id=rule.id_management_rule,
                role=rule.management_rule_code,
                provider_id=rule.rule_ref_provider,
                organization_id=rule.rule_ref_org,
                destination_user=rule.rule_ref_user,
                invited_by=rule.rule_ref_provider
            )
            
            logger.info(f"Created invitation notification for rule {rule.id_management_rule}")
            
            # Try to send real-time notification via publisher
            try:
                notify_invitation_to_role_received({
                    "rule_id": rule.id_management_rule,
                    "role": rule.management_rule_code,
                    "provider_id": rule.rule_ref_provider,
                    "organization_id": rule.rule_ref_org,
                    "destination_user": rule.rule_ref_user,
                    "invited_by": rule.rule_ref_provider
                }, rule.rule_ref_user)
            except Exception as e:
                logger.error(f"Failed to send real-time notification: {e}")
                
        except Exception as e:
            logger.error(f"Failed to create invitation notification: {e}")
    
    def create_rule_update_notification(self, rule) -> None:
        """
        Create notification for rule update.
        
        Args:
            rule: Updated rule
        """
        try:
            notification_data = {
                "rule_id": rule.id_management_rule,
                "role": rule.management_rule_code,
                "rule_type": rule.management_rule_status,
                "user_id": rule.rule_ref_user,
                "provider_id": rule.rule_ref_provider,
                "organization_id": rule.rule_ref_org,
                "invited_by": rule.rule_ref_user,
                "notification_date": str(datetime.now())
            }
            
            notification_api = Notification_API(
                notification_code="NEW_RULE_ADDED",
                notification_params=notification_data,
                notification_user_ref=rule.rule_ref_user,
            )
            
            self.notification_service.create_notification(notification_api)
            logger.info(f"Created rule update notification for rule {rule.id_management_rule}")
            
            # Notify provider owner
            try:
                supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
                if supplier and supplier.product_provider_owner:
                    owner_notification = Notification_API(
                        notification_code="NEW_RULE_ADDED",
                        notification_params=notification_data,
                        notification_user_ref=supplier.product_provider_owner,
                    )
                    self.notification_service.create_notification(owner_notification)
            except Exception as e:
                logger.error(f"Failed to send rule notifications: {e}")
                
        except Exception as e:
            logger.error(f"Failed to create rule update notification: {e}")
    
    def create_invitation_response_notification(self, rule, accepted: bool) -> None:
        """
        Create notification for invitation response.
        
        Args:
            rule: Rule being responded to
            accepted: Whether invitation was accepted
        """
        try:
            notification_code = "INVITATION_ACCEPTED" if accepted else "INVITATION_REJECTED"
            message = "accepted" if accepted else "rejected"
            
            notification_data = {
                "rule_id": rule.id_management_rule,
                "user_id": rule.rule_ref_user,
                "organization_id": rule.rule_ref_org,
                "provider_id": rule.rule_ref_provider,
                "role": rule.management_rule_code,
                "status": rule.management_rule_status,
                "response_date": str(datetime.now())
            }
            
            notification_api = Notification_API(
                notification_code=notification_code,
                notification_params=notification_data,
                notification_user_ref=rule.rule_ref_user,
            )
            
            self.notification_service.create_notification(notification_api)
            logger.info(f"Created invitation {message} notification for rule {rule.id_management_rule}")
            
            # Notify provider owner
            try:
                supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
                if supplier and supplier.product_provider_owner:
                    owner_notification = Notification_API(
                        notification_code=notification_code,
                        notification_params=notification_data,
                        notification_user_ref=supplier.product_provider_owner,
                    )
                    self.notification_service.create_notification(owner_notification)
                    
                    # Try to publish real-time notification
                    try:
                        notify_rule_to_role_received(notification_api, supplier.product_provider_owner)
                    except Exception as e:
                        logger.error(f"Failed to send acceptance notification: {e}")
            except Exception as e:
                logger.error(f"Failed to notify provider owner: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to create invitation response notification: {e}")