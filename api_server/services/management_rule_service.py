# services/management_rule_service.py (enhanced)
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import BackgroundTasks
from core.api_models import ManagementRule_API, Notification_API
from core.exception_handler import APIException
from core.messages import *
from core.models import ManagementRule
from repositories.management_rule_repository import ManagementRuleRepository
from repositories.supplier_repository import SupplierRepository
from services.notification_service import NotificationService
from communication.publisher import notify_invitation_to_role_received, notify_rule_to_role_received

class ManagementRuleService:
    """Service for management rule/staff operations"""
    
    def __init__(self):
        self.rule_repo = ManagementRuleRepository()
        self.supplier_repo = SupplierRepository()
        self.notification_service = NotificationService()
    
    def _parse_expiry(self, value: str | None) -> datetime | None:
        """Parse expiry date from string to datetime"""
        if not value or str(value).lower() == "null":
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        return None
    
    def _build_rule_model(self, rule_data: ManagementRule_API) -> ManagementRule:
        """Build ManagementRule model from API data"""
        new_rule = ManagementRule(
            rule_ref_org=rule_data.rule_ref_org,
            rule_ref_provider=rule_data.rule_ref_provider,
            rule_ref_user=rule_data.rule_ref_user,
            management_rule_code=rule_data.management_rule_code,
            management_rule_status=rule_data.management_rule_status,
            management_rule_expiry=self._parse_expiry(rule_data.management_rule_expiry),
        )
        
        if rule_data.id_management_rule != 0:
            new_rule.id_management_rule = rule_data.id_management_rule
        
        return new_rule
    
    def _create_invitation_notification(self, rule: ManagementRule) -> None:
        """Create invitation notification for a rule"""
        from features.app.notification.builders.notification_builder import NotificationFactory
        
        notification = NotificationFactory.personnel.work_invitation(
            rule_id=rule.id_management_rule,
            role=rule.management_rule_code,
            provider_id=rule.rule_ref_provider,
            organization_id=rule.rule_ref_org,
            invited_by=rule.rule_ref_user
        )
        
        notification_api = Notification_API(
            notification_code="role_invitation",
            notification_params=NotificationFactory.dump_dict(notification),
            notification_user_ref=rule.rule_ref_user,
        )
        
        self.notification_service.create_notification(notification_api)
        
        # Try to send real-time notification
        try:
            notify_invitation_to_role_received(notification, rule.rule_ref_user)
        except Exception as e:
            print(f"Failed to send real-time notification: {e}")
    
    def _create_rule_update_notification(self, rule: ManagementRule) -> None:
        """Create notification for rule update"""
        from features.app.notification.builders.notification_builder import NotificationFactory
        
        supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
        if not supplier:
            return
        
        notification = NotificationFactory.rule.new_rule_added(
            rule_id=rule.id_management_rule,
            role=rule.management_rule_code,
            rule_type=rule.management_rule_status,
            user_id=rule.rule_ref_user,
            provider_id=rule.rule_ref_provider,
            organization_id=rule.rule_ref_org,
            invited_by=rule.rule_ref_user
        )
        
        notification_api = Notification_API(
            notification_code="new_rule_added",
            notification_params=NotificationFactory.dump_dict(notification),
            notification_user_ref=rule.rule_ref_user,
        )
        
        self.notification_service.create_notification(notification_api)
        
        # Notify relevant parties
        try:
            owner_id = supplier.product_provider_owner
            notify_invitation_to_role_received(notification, owner_id)
            notify_invitation_to_role_received(notification, rule.rule_ref_user)
        except Exception as e:
            print(f"Failed to send rule notifications: {e}")
    
    def _create_invitation_response_notification(self, rule: ManagementRule, accepted: bool) -> None:
        """Create notification for invitation response"""
        from features.app.notification.builders.notification_builder import NotificationFactory
        
        if accepted:
            notification = NotificationFactory.personnel.invitation_accepted(
                rule_id=rule.id_management_rule,
                user_id=rule.rule_ref_user,
                organization_id=rule.rule_ref_org,
                provider_id=rule.rule_ref_provider,
                role=rule.management_rule_code
            )
            
            notification_api = Notification_API(
                notification_code="invitation_accepted",
                notification_params=NotificationFactory.dump_dict(notification),
                notification_user_ref=rule.rule_ref_user,
            )
            
            self.notification_service.create_notification(notification_api)
            
            # Notify provider owner
            supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
            if supplier:
                try:
                    notify_rule_to_role_received(notification, supplier.product_provider_owner)
                except Exception as e:
                    print(f"Failed to send acceptance notification: {e}")
    
    def get_rule_by_id(self, rule_id: int) -> ManagementRule:
        """Get management rule by ID"""
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=RULE_NOT_EXISTS,
                message=f"{RULE_NOT_EXISTS}: {rule_id}"
            )
        return rule
    
    def get_all_rules(
        self,
        org_id: int = 0,
        supplier_id: int = 0,
        user_id: int = 0,
        rule_id: int = 0,
        offset: int = 0,
        limit: int = 100
    ) -> List[ManagementRule]:
        """Get all management rules with filters"""
        return self.rule_repo.get_all(org_id, supplier_id, user_id, rule_id, offset, limit)
    
    def create_rule(self, rule_data: ManagementRule_API) -> ManagementRule:
        """Create a new management rule"""
        
        # Check if rule already exists
        if rule_data.id_management_rule != 0:
            existing = self.rule_repo.get_by_id(rule_data.id_management_rule)
            if existing:
                raise APIException(
                    status=HTTP_409_CONFLICT,
                    code=RULE_ALREADY_EXISTS,
                    details=f"Rule '{rule_data.id_management_rule}' already exists."
                )
        
        # Build and create rule
        new_rule = self._build_rule_model(rule_data)
        
        try:
            final_rule = self.rule_repo.create(new_rule)
            
            # Create notification for the invitation
            self._create_invitation_notification(final_rule)
            
            return final_rule
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=RULE_INSERT_FAILED,
                details=str(e)
            )
    
    def update_rule(self, rule_data: ManagementRule_API) -> ManagementRule:
        """Update an existing management rule"""
        
        # Get existing rule
        existing_rule = self.get_rule_by_id(rule_data.id_management_rule)
        
        # Update fields
        existing_rule.management_rule_code = rule_data.management_rule_code
        existing_rule.management_rule_status = rule_data.management_rule_status
        existing_rule.management_rule_expiry = self._parse_expiry(rule_data.management_rule_expiry)
        
        try:
            final_rule = self.rule_repo.update(existing_rule)
            
            # Create notification for the update
            self._create_rule_update_notification(final_rule)
            
            return final_rule
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=RULE_UPDATE_FAILED,
                details=str(e)
            )
    
    def delete_rule(self, rule_id: int) -> Dict[str, Any]:
        """Delete a management rule"""
        
        rule = self.get_rule_by_id(rule_id)
        success = self.rule_repo.delete(rule)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=RULE_DELETE_FAILED,
                details=f"Failed to delete rule {rule_id}"
            )
        
        return {
            "message": "Rule deleted successfully",
            "rule_id": rule_id
        }
    
    def answer_invitation(self, rule_id: int, accept: bool) -> ManagementRule:
        """Respond to an invitation (accept or reject)"""
        
        # Get existing rule
        existing_rule = self.get_rule_by_id(rule_id)
        
        # Check if already answered
        if existing_rule.management_rule_status in ['ACTIVE', 'REJECTED']:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=INVITATION_ALREADY_PROCESSED,
                details=f"Invitation has already been {existing_rule.management_rule_status.lower()}"
            )
        
        # Update status based on answer
        if accept:
            existing_rule.management_rule_status = 'ACTIVE'
        else:
            existing_rule.management_rule_status = 'REJECTED'
        
        try:
            final_rule = self.rule_repo.update(existing_rule)
            
            # Create notification for the response
            self._create_invitation_response_notification(final_rule, accept)
            
            return final_rule
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=RULE_UPDATE_FAILED,
                details=str(e)
            )
    
    def get_user_rules(self, user_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get all rules for a specific user"""
        if status:
            return self.rule_repo.get_by_user(user_id, status)
        return self.rule_repo.get_by_user(user_id)
    
    def get_provider_staff(self, provider_id: int, active_only: bool = True) -> List[ManagementRule]:
        """Get all staff members for a provider"""
        if active_only:
            return self.rule_repo.get_by_provider(provider_id, status='ACTIVE')
        return self.rule_repo.get_by_provider(provider_id)
    
    def get_pending_invitations(self, user_id: int) -> List[ManagementRule]:
        """Get pending invitations for a user"""
        return self.rule_repo.get_by_user(user_id, status='PENDING')
    
    def get_user_active_rules(self, user_id: int) -> List[ManagementRule]:
        """Get active rules for a user"""
        return self.rule_repo.get_by_user(user_id, status='ACTIVE')
    
    def get_expiring_rules(self, days_threshold: int = 7) -> List[ManagementRule]:
        """Get rules that will expire soon"""
        return self.rule_repo.get_expiring_rules(days_threshold)