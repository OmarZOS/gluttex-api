# services/management_rule_service.py
"""
Management rule service for handling staff assignments, invitations, and notifications.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import BackgroundTasks

from core.api_models import ManagementRule_API, Notification_API
from core.exceptions.specific.staff_exceptions import (
    StaffException,
    RuleNotFoundException,
    RuleAlreadyExistsException,
    RuleInsertFailedException,
    RuleUpdateFailedException,
    RuleDeleteFailedException,
    RuleInvalidStatusException,
    InvitationAlreadyProcessedException,
    InvitationExpiredException,
    UserNotFoundExceptionForStaff,
    ProviderNotFoundExceptionForStaff,
    OrganisationNotFoundExceptionForStaff,
    InvalidRuleCodeException,
    StaffPermissionDeniedException
)
from core.messages.error_codes import ErrorCode
from core.models import ManagementRule
from repositories.management_rule_repository import ManagementRuleRepository
from repositories.supplier_repository import SupplierRepository
from services.notification_service import NotificationService
from communication.publisher import notify_invitation_to_role_received, notify_rule_to_role_received

logger = logging.getLogger(__name__)


class ManagementRuleService:
    """Service for management rule/staff operations"""
    
    # Valid rule statuses
    VALID_STATUSES = ["PENDING", "ACTIVE", "REJECTED", "EXPIRED", "INACTIVE"]
    
    # Valid rule codes (roles)
    VALID_RULE_CODES = [1, 2, 3, 4, 5]  # Adjust based on your business logic
    
    def __init__(self):
        self.rule_repo = ManagementRuleRepository()
        self.supplier_repo = SupplierRepository()
        self.notification_service = NotificationService()
    
    # ==================== Private Helper Methods ====================
    
    def _parse_expiry(self, value: str | None) -> datetime | None:
        """
        Parse expiry date from string to datetime.
        
        Args:
            value: Expiry date string in various formats
            
        Returns:
            datetime object or None if invalid
        """
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
        
        logger.warning(f"Could not parse expiry date: {value}")
        return None
    
    def _validate_rule_data(self, rule_data: ManagementRule_API) -> None:
        """
        Validate rule data before creation/update.
        
        Args:
            rule_data: Rule data to validate
            
        Raises:
            InvalidRuleCodeException: If rule code is invalid
            RuleInvalidStatusException: If status is invalid
        """
        # Validate rule code
        if rule_data.management_rule_code not in self.VALID_RULE_CODES:
            logger.warning(f"Invalid rule code: {rule_data.management_rule_code}")
            raise InvalidRuleCodeException(
                rule_code=rule_data.management_rule_code,
                allowed_codes=self.VALID_RULE_CODES
            )
        
        # Validate status
        if rule_data.management_rule_status not in self.VALID_STATUSES:
            logger.warning(f"Invalid rule status: {rule_data.management_rule_status}")
            raise RuleInvalidStatusException(
                requested_status=rule_data.management_rule_status,
                allowed_statuses=self.VALID_STATUSES
            )
    
    def _validate_entities_exist(self, rule_data: ManagementRule_API) -> None:
        """
        Validate that all referenced entities exist.
        
        Args:
            rule_data: Rule data containing entity references
            
        Raises:
            UserNotFoundExceptionForStaff: If user not found
            ProviderNotFoundExceptionForStaff: If provider not found
            OrganisationNotFoundExceptionForStaff: If organisation not found
        """
        # Validate user (if provided)
        if rule_data.rule_ref_user:
            user = self.rule_repo.get_user_by_id(rule_data.rule_ref_user)
            if not user:
                logger.warning(f"User not found: {rule_data.rule_ref_user}")
                raise UserNotFoundExceptionForStaff(user_id=rule_data.rule_ref_user)
        
        # Validate provider (if provided)
        if rule_data.rule_ref_provider:
            provider = self.supplier_repo.get_supplier_basic(rule_data.rule_ref_provider)
            if not provider:
                logger.warning(f"Provider not found: {rule_data.rule_ref_provider}")
                raise ProviderNotFoundExceptionForStaff(provider_id=rule_data.rule_ref_provider)
        
        # Validate organisation (if provided)
        if rule_data.rule_ref_org:
            org = self.rule_repo.get_organisation_by_id(rule_data.rule_ref_org)
            if not org:
                logger.warning(f"Organisation not found: {rule_data.rule_ref_org}")
                raise OrganisationNotFoundExceptionForStaff(org_id=rule_data.rule_ref_org)
    
    def _check_duplicate_rule(self, rule_data: ManagementRule_API) -> None:
        """
        Check if a rule already exists for the same user and provider.
        
        Args:
            rule_data: Rule data to check
            
        Raises:
            RuleAlreadyExistsException: If duplicate rule found
        """
        existing = self.rule_repo.get_by_user_and_provider(
            rule_data.rule_ref_user,
            rule_data.rule_ref_provider
        )
        if existing:
            logger.warning(f"Duplicate rule found for user {rule_data.rule_ref_user} and provider {rule_data.rule_ref_provider}")
            raise RuleAlreadyExistsException(
                user_id=rule_data.rule_ref_user,
                provider_id=rule_data.rule_ref_provider,
                rule_id=existing.id_management_rule
            )
    
    def _check_invitation_expired(self, rule: ManagementRule) -> None:
        """
        Check if an invitation has expired.
        
        Args:
            rule: Rule to check
            
        Raises:
            InvitationExpiredException: If invitation has expired
        """
        if rule.management_rule_expiry and rule.management_rule_expiry < datetime.now():
            logger.warning(f"Invitation {rule.id_management_rule} has expired")
            raise InvitationExpiredException(
                rule_id=rule.id_management_rule,
                expiry_date=rule.management_rule_expiry.isoformat()
            )
    
    def _build_rule_model(self, rule_data: ManagementRule_API) -> ManagementRule:
        """
        Build ManagementRule model from API data.
        
        Args:
            rule_data: API rule data
            
        Returns:
            ManagementRule model instance
        """
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
        """
        Create invitation notification for a rule.
        
        Args:
            rule: Created rule
        """
        try:
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
            logger.info(f"Created invitation notification for rule {rule.id_management_rule}")
            
            # Try to send real-time notification
            try:
                notify_invitation_to_role_received(notification, rule.rule_ref_user)
            except Exception as e:
                logger.error(f"Failed to send real-time notification: {e}")
                
        except Exception as e:
            logger.error(f"Failed to create invitation notification: {e}")
    
    def _create_rule_update_notification(self, rule: ManagementRule) -> None:
        """
        Create notification for rule update.
        
        Args:
            rule: Updated rule
        """
        try:
            from features.app.notification.builders.notification_builder import NotificationFactory
            
            supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
            if not supplier:
                logger.warning(f"Supplier not found for rule update notification: {rule.rule_ref_provider}")
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
            logger.info(f"Created rule update notification for rule {rule.id_management_rule}")
            
            # Notify relevant parties
            try:
                owner_id = supplier.product_provider_owner
                notify_invitation_to_role_received(notification, owner_id)
                notify_invitation_to_role_received(notification, rule.rule_ref_user)
            except Exception as e:
                logger.error(f"Failed to send rule notifications: {e}")
                
        except Exception as e:
            logger.error(f"Failed to create rule update notification: {e}")
    
    def _create_invitation_response_notification(self, rule: ManagementRule, accepted: bool) -> None:
        """
        Create notification for invitation response.
        
        Args:
            rule: Rule being responded to
            accepted: Whether invitation was accepted
        """
        try:
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
                logger.info(f"Created invitation acceptance notification for rule {rule.id_management_rule}")
                
                # Notify provider owner
                supplier = self.supplier_repo.get_supplier_basic(rule.rule_ref_provider)
                if supplier:
                    try:
                        notify_rule_to_role_received(notification, supplier.product_provider_owner)
                    except Exception as e:
                        logger.error(f"Failed to send acceptance notification: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to create invitation response notification: {e}")
    
    # ==================== Rule CRUD Operations ====================
    
    def get_rule_by_id(self, rule_id: int) -> ManagementRule:
        """
        Get management rule by ID.
        
        Args:
            rule_id: Rule ID to retrieve
            
        Returns:
            ManagementRule object
            
        Raises:
            RuleNotFoundException: If rule not found
        """
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            logger.warning(f"Rule not found with ID: {rule_id}")
            raise RuleNotFoundException(rule_id=rule_id)
        
        logger.debug(f"Retrieved rule with ID: {rule_id}")
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
        """
        Get all management rules with filters.
        
        Args:
            org_id: Filter by organisation ID
            supplier_id: Filter by supplier/provider ID
            user_id: Filter by user ID
            rule_id: Filter by rule ID
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of ManagementRule objects
        """
        logger.debug(f"Fetching rules - org:{org_id}, supplier:{supplier_id}, user:{user_id}, offset:{offset}, limit:{limit}")
        return self.rule_repo.get_all(org_id, supplier_id, user_id, rule_id, offset, limit)
    
    def create_rule(self, rule_data: ManagementRule_API) -> ManagementRule:
        """
        Create a new management rule.
        
        Args:
            rule_data: Rule data to create
            
        Returns:
            Created ManagementRule object
            
        Raises:
            RuleAlreadyExistsException: If rule already exists
            RuleInsertFailedException: If creation fails
            InvalidRuleCodeException: If rule code is invalid
            Various entity not found exceptions
        """
        logger.info(f"Creating new rule for user: {rule_data.rule_ref_user}, provider: {rule_data.rule_ref_provider}")
        
        # Validate rule data
        self._validate_rule_data(rule_data)
        
        # Validate entities exist
        self._validate_entities_exist(rule_data)
        
        # Check for duplicate
        self._check_duplicate_rule(rule_data)
        
        # Build and create rule
        new_rule = self._build_rule_model(rule_data)
        
        try:
            final_rule = self.rule_repo.create(new_rule)
            logger.info(f"Rule created successfully with ID: {final_rule.id_management_rule}")
            
            # Create notification for the invitation
            self._create_invitation_notification(final_rule)
            
            return final_rule
            
        except Exception as e:
            logger.error(f"Failed to create rule: {e}")
            raise RuleInsertFailedException(
                error=str(e),
                user_id=rule_data.rule_ref_user,
                provider_id=rule_data.rule_ref_provider,
                org_id=rule_data.rule_ref_org
            )
    
    def update_rule(self, rule_data: ManagementRule_API) -> ManagementRule:
        """
        Update an existing management rule.
        
        Args:
            rule_data: Updated rule data
            
        Returns:
            Updated ManagementRule object
            
        Raises:
            RuleNotFoundException: If rule not found
            RuleUpdateFailedException: If update fails
            InvalidRuleCodeException: If rule code is invalid
        """
        logger.info(f"Updating rule with ID: {rule_data.id_management_rule}")
        
        # Validate rule data
        self._validate_rule_data(rule_data)
        
        # Get existing rule
        existing_rule = self.get_rule_by_id(rule_data.id_management_rule)
        
        # Track changes for logging
        changes = []
        if existing_rule.management_rule_code != rule_data.management_rule_code:
            changes.append(f"code: {existing_rule.management_rule_code} -> {rule_data.management_rule_code}")
        if existing_rule.management_rule_status != rule_data.management_rule_status:
            changes.append(f"status: {existing_rule.management_rule_status} -> {rule_data.management_rule_status}")
        
        # Update fields
        existing_rule.management_rule_code = rule_data.management_rule_code
        existing_rule.management_rule_status = rule_data.management_rule_status
        existing_rule.management_rule_expiry = self._parse_expiry(rule_data.management_rule_expiry)
        
        try:
            final_rule = self.rule_repo.update(existing_rule)
            logger.info(f"Rule {rule_data.id_management_rule} updated successfully. Changes: {changes if changes else 'none'}")
            
            # Create notification for the update
            self._create_rule_update_notification(final_rule)
            
            return final_rule
            
        except Exception as e:
            logger.error(f"Failed to update rule {rule_data.id_management_rule}: {e}")
            raise RuleUpdateFailedException(
                rule_id=rule_data.id_management_rule,
                error=str(e),
                fields_attempted=["management_rule_code", "management_rule_status", "management_rule_expiry"]
            )
    
    def delete_rule(self, rule_id: int, force_delete: bool = False) -> Dict[str, Any]:
        """
        Delete a management rule.
        
        Args:
            rule_id: Rule ID to delete
            force_delete: Force delete even if rule is active
            
        Returns:
            Dictionary with success message
            
        Raises:
            RuleNotFoundException: If rule not found
            RuleDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting rule with ID: {rule_id} (force={force_delete})")
        
        rule = self.get_rule_by_id(rule_id)
        
        # Check if rule is active and force_delete is not used
        if rule.management_rule_status == "ACTIVE" and not force_delete:
            logger.warning(f"Cannot delete active rule {rule_id}. Use force_delete=true.")
            raise RuleDeleteFailedException(
                rule_id=rule_id,
                is_active=True,
                error="Cannot delete active staff assignment"
            )
        
        success = self.rule_repo.delete(rule)
        
        if not success:
            logger.error(f"Failed to delete rule {rule_id}")
            raise RuleDeleteFailedException(
                rule_id=rule_id,
                error="Repository returned False"
            )
        
        logger.info(f"Rule {rule_id} deleted successfully")
        return {
            "success": True,
            "message": "Rule deleted successfully",
            "rule_id": rule_id
        }
    
    def answer_invitation(self, rule_id: int, accept: bool) -> ManagementRule:
        """
        Respond to an invitation (accept or reject).
        
        Args:
            rule_id: Rule ID to respond to
            accept: True to accept, False to reject
            
        Returns:
            Updated ManagementRule object
            
        Raises:
            RuleNotFoundException: If rule not found
            InvitationAlreadyProcessedException: If already processed
            InvitationExpiredException: If invitation expired
            RuleUpdateFailedException: If update fails
        """
        action = "accept" if accept else "reject"
        logger.info(f"Processing invitation {action} for rule {rule_id}")
        
        # Get existing rule
        existing_rule = self.get_rule_by_id(rule_id)
        
        # Check if invitation has expired
        self._check_invitation_expired(existing_rule)
        
        # Check if already answered
        if existing_rule.management_rule_status in ['ACTIVE', 'REJECTED']:
            logger.warning(f"Invitation {rule_id} already {existing_rule.management_rule_status.lower()}")
            raise InvitationAlreadyProcessedException(
                rule_id=rule_id,
                current_status=existing_rule.management_rule_status
            )
        
        # Update status based on answer
        new_status = 'ACTIVE' if accept else 'REJECTED'
        existing_rule.management_rule_status = new_status
        
        try:
            final_rule = self.rule_repo.update(existing_rule)
            logger.info(f"Invitation {rule_id} {action}ed successfully")
            
            # Create notification for the response
            self._create_invitation_response_notification(final_rule, accept)
            
            return final_rule
            
        except Exception as e:
            logger.error(f"Failed to update rule {rule_id} for invitation response: {e}")
            raise RuleUpdateFailedException(
                rule_id=rule_id,
                error=str(e),
                fields_attempted=["management_rule_status"]
            )
    
    # ==================== Query Methods ====================
    
    def get_user_rules(self, user_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """
        Get all rules for a specific user.
        
        Args:
            user_id: User ID to fetch rules for
            status: Optional status filter
            
        Returns:
            List of ManagementRule objects
        """
        logger.debug(f"Fetching rules for user {user_id} (status={status})")
        
        # Validate user exists
        user = self.rule_repo.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundExceptionForStaff(user_id=user_id)
        
        if status:
            return self.rule_repo.get_by_user(user_id, status.upper())
        return self.rule_repo.get_by_user(user_id)
    
    def get_provider_staff(self, provider_id: int, active_only: bool = True) -> List[ManagementRule]:
        """
        Get all staff members for a provider.
        
        Args:
            provider_id: Provider ID to fetch staff for
            active_only: Return only active staff
            
        Returns:
            List of ManagementRule objects
        """
        logger.debug(f"Fetching staff for provider {provider_id} (active_only={active_only})")
        
        # Validate provider exists
        provider = self.supplier_repo.get_supplier_basic(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            raise ProviderNotFoundExceptionForStaff(provider_id=provider_id)
        
        if active_only:
            return self.rule_repo.get_by_provider(provider_id, status='ACTIVE')
        return self.rule_repo.get_by_provider(provider_id)
    
    def get_pending_invitations(self, user_id: int) -> List[ManagementRule]:
        """
        Get pending invitations for a user.
        
        Args:
            user_id: User ID to fetch pending invitations for
            
        Returns:
            List of pending ManagementRule objects
        """
        logger.debug(f"Fetching pending invitations for user {user_id}")
        
        # Validate user exists
        user = self.rule_repo.get_user_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundExceptionForStaff(user_id=user_id)
        
        return self.rule_repo.get_by_user(user_id, status='PENDING')
    
    def get_user_active_rules(self, user_id: int) -> List[ManagementRule]:
        """
        Get active rules for a user.
        
        Args:
            user_id: User ID to fetch active rules for
            
        Returns:
            List of active ManagementRule objects
        """
        logger.debug(f"Fetching active rules for user {user_id}")
        return self.rule_repo.get_by_user(user_id, status='ACTIVE')
    
    def get_expiring_rules(self, days_threshold: int = 7) -> List[ManagementRule]:
        """
        Get rules that will expire soon.
        
        Args:
            days_threshold: Number of days before expiry to consider
            
        Returns:
            List of expiring ManagementRule objects
        """
        logger.debug(f"Fetching rules expiring within {days_threshold} days")
        return self.rule_repo.get_expiring_rules(days_threshold)
    
    def get_rule_by_user_and_provider(self, user_id: int, provider_id: int) -> Optional[ManagementRule]:
        """
        Get rule for a specific user and provider.
        
        Args:
            user_id: User ID
            provider_id: Provider ID
            
        Returns:
            ManagementRule object or None if not found
        """
        logger.debug(f"Fetching rule for user {user_id} and provider {provider_id}")
        return self.rule_repo.get_by_user_and_provider(user_id, provider_id)