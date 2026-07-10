# repositories/management_rule_repository.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.models.models import ManagementRule, AppUser, ProductProvider, Person, RoleInvitation
import storage.storage_broker as storage_broker
from datetime import datetime, timedelta



class ManagementRuleRepository:
    """Repository for ManagementRule-related database operations"""
    
    def get_by_id(self, rule_id: int) -> Optional[ManagementRule]:
        """Get management rule by ID"""
        data = storage_broker.get(
            ManagementRule,
            {ManagementRule.id_management_rule: rule_id},
            None,
            [
                ManagementRule.id_management_rule,
                ManagementRule.rule_ref_org,
                ManagementRule.rule_ref_provider,
                ManagementRule.rule_ref_user,
                ManagementRule.management_rule_code,
                ManagementRule.management_rule_status,
                ManagementRule.management_rule_expiry,
                ManagementRule.role_invitation]
        )
        return data[0] if data else None
    
    def get_all(
        self,
        org_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        user_id: Optional[int] = None,
        rule_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[ManagementRule]:
        """Get management rules with filters"""
        conditions = {}
        
        # Build conditions only for non-None and non-zero values
        if rule_id and rule_id != 0:
            conditions[ManagementRule.id_management_rule] = rule_id
        else:
            if user_id and user_id != 0:
                conditions[ManagementRule.rule_ref_user] = user_id
            if supplier_id and supplier_id != 0:
                conditions[ManagementRule.rule_ref_provider] = supplier_id
            if org_id and org_id != 0:
                conditions[ManagementRule.rule_ref_org] = org_id
        
        # Log the conditions for debugging
        # logger.debug(f"Fetching rules with conditions: {conditions}")
        
        # Define eager load depth based on whether we have conditions
        eager_load_depth = [
            ManagementRule.management_rule_code,
            ManagementRule.management_rule_status,
            ManagementRule.management_rule_expiry,
            ManagementRule.provider_organisation,
            {
                ManagementRule.product_provider: [ProductProvider.product_provider_details]
            },
            {
                ManagementRule.app_user: [{
                    AppUser.app_user_person: [Person.person_details]
                }]
            },
        ]
        
        try:
            results = storage_broker.get(
                ManagementRule,
                conditions,
                None,
                eager_load_depth,
                offset,
                limit,
            )
            
            # logger.debug(f"Found {len(results) if results else 0} rules")
            return results if results else []
            
        except Exception as e:
            # logger.error(f"Error fetching rules: {e}")
            # Try without eager loading as fallback
            # logger.info("Retrying without eager loading...")
            results = storage_broker.get(
                ManagementRule,
                conditions,
                None,
                [],  # No eager loading
                offset,
                limit,
            )
            return results if results else []

    
    def get_by_user(self, user_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get rules by user with optional status filter"""
        conditions = {ManagementRule.rule_ref_user: user_id}
        if status:
            conditions[ManagementRule.management_rule_status] = status
        
        return storage_broker.get(
            ManagementRule,
            conditions,
            None,
            [ManagementRule.role_invitation,
            ManagementRule.product_provider,
            ManagementRule.provider_organisation]
        )
    
    def get_by_provider(self, provider_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get rules by provider with optional status filter"""
        conditions = {ManagementRule.rule_ref_provider: provider_id}
        if status:
            conditions[ManagementRule.management_rule_status] = status
        
        return storage_broker.get(
            ManagementRule,
            conditions,
            None,
            [ManagementRule.app_user, ManagementRule.provider_organisation]
        )
    
    def get_by_organisation(self, org_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get rules by organisation with optional status filter"""
        conditions = {ManagementRule.rule_ref_org: org_id}
        if status:
            conditions[ManagementRule.management_rule_status] = status
        
        return storage_broker.get(
            ManagementRule,
            conditions,
            None,
            [ManagementRule.app_user, ManagementRule.product_provider]
        )
    
    def get_active_rules(self) -> List[ManagementRule]:
        """Get all active rules"""
        return storage_broker.get(
            ManagementRule,
            {ManagementRule.management_rule_status: 'ACTIVE'},
            None,
            []
        )
    
    def create(self, rule: ManagementRule) -> ManagementRule:
        """Create a new management rule"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(rule)
    
    def create_invitation(self, inv: RoleInvitation) -> RoleInvitation:
        """Create a new management rule"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(inv)
    
    def update(self, rule: ManagementRule) -> ManagementRule:
        """Update an existing management rule"""
        from features.insertion import update_record_in_api
        return update_record_in_api(rule)
    
    def update_invitation(self, inv: RoleInvitation) -> RoleInvitation:
        """Update an existing management inv"""
        from features.insertion import update_record_in_api
        return update_record_in_api(inv)
    
    def delete(self, rule: ManagementRule) -> bool:
        """Delete a management rule"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(rule)
    
    def get_rules_by_status(self, status: str) -> List[ManagementRule]:
        """Get rules by status"""
        return storage_broker.get(
            ManagementRule,
            {ManagementRule.management_rule_status: status},
            None,
            []
        )
    
    def get_expiring_rules(self, days_threshold: int = 7) -> List[ManagementRule]:
        """Get rules that expire within the given days"""
        from datetime import datetime, timedelta
        
        expiry_threshold = datetime.now() + timedelta(days=days_threshold)
        # This is a simplified version - you might need a more complex query
        all_rules = self.get_all()
        return [rule for rule in all_rules 
                if rule.management_rule_expiry and rule.management_rule_expiry <= expiry_threshold]

    
    def get_by_user_and_provider(self, user_id: int,provider_id:int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get rules by user with optional status filter"""
        conditions = {ManagementRule.rule_ref_user: user_id,ManagementRule.rule_ref_provider: provider_id}
        if status:
            conditions[ManagementRule.management_rule_status] = status
        
        return storage_broker.get(
            ManagementRule,
            conditions,
            None,
            [ManagementRule.product_provider, ManagementRule.provider_organisation]
        )
    
    def get_by_provider(self, provider_id: int, status: Optional[str] = None) -> List[ManagementRule]:
        """Get rules by provider with optional status filter"""
        conditions = {ManagementRule.rule_ref_provider: provider_id}
        if status:
            conditions[ManagementRule.management_rule_status] = status
        
        return storage_broker.get(
            ManagementRule,
            conditions,
            None,
            [ManagementRule.app_user, ManagementRule.provider_organisation]
        )
    
    def get_expiring_rules(self, days_threshold: int = 7) -> List[ManagementRule]:
        """Get rules that expire within the given days"""
        expiry_threshold = datetime.now() + timedelta(days=days_threshold)
        # This is a simplified version - you might need a more complex query
        all_rules = self.get_all()
        return [rule for rule in all_rules 
                if rule.management_rule_expiry and rule.management_rule_expiry <= expiry_threshold]
    

# repositories/staff_repository.py (if you want separate staff-specific operations)
from typing import Optional, List
from core.models.models import ManagementRule
import storage.storage_broker as storage_broker

class StaffRepository:
    """Repository for staff-specific operations (extends ManagementRule)"""
    
    def get_staff_by_user(self, user_id: int) -> List[ManagementRule]:
        """Get all staff assignments for a user"""
        return storage_broker.get(
            ManagementRule,
            {ManagementRule.rule_ref_user: user_id},
            None,
            [ManagementRule.product_provider, ManagementRule.provider_organisation]
        )
    
    def get_staff_by_provider(self, provider_id: int) -> List[ManagementRule]:
        """Get all staff members for a provider"""
        return storage_broker.get(
            ManagementRule,
            {ManagementRule.rule_ref_provider: provider_id},
            None,
            [ManagementRule.app_user]
        )
    
    def get_active_staff(self, provider_id: int) -> List[ManagementRule]:
        """Get active staff members for a provider"""
        return storage_broker.get(
            ManagementRule,
            {
                ManagementRule.rule_ref_provider: provider_id,
                ManagementRule.management_rule_status: 'ACTIVE'
            },
            None,
            [ManagementRule.app_user]
        )
    
    def get_pending_invitations(self, user_id: int) -> List[ManagementRule]:
        """Get pending invitations for a user"""
        return storage_broker.get(
            ManagementRule,
            {
                ManagementRule.rule_ref_user: user_id,
                ManagementRule.management_rule_status: 'PENDING'
            },
            None,
            [ManagementRule.product_provider, ManagementRule.provider_organisation,ManagementRule.role_invitation]
        )