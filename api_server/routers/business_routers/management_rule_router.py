# routers/management_rule_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.api_models import ManagementRule_API
from core.models import ManagementRule
from services.management_rule_service import ManagementRuleService

management_rule_router = APIRouter()

def get_management_rule_service() -> ManagementRuleService:
    return ManagementRuleService()

# ==================== Management Rule Endpoints ====================

@management_rule_router.get("/")
def get_all_rules(
    org_id: int = Query(0, description="Filter by organisation ID"),
    supplier_id: int = Query(0, description="Filter by supplier ID"),
    user_id: int = Query(0, description="Filter by user ID"),
    rule_id: int = Query(0, description="Filter by rule ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get all management rules with pagination and filters"""
    return rule_service.get_all_rules(org_id, supplier_id, user_id, rule_id, offset, limit)

@management_rule_router.get("/user/{user_id}")
def get_user_rules(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get all rules for a specific user"""
    return rule_service.get_user_rules(user_id, status)

@management_rule_router.get("/user/{user_id}/pending")
def get_pending_invitations(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get pending invitations for a user"""
    return rule_service.get_pending_invitations(user_id)

@management_rule_router.get("/user/{user_id}/active")
def get_user_active_rules(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get active rules for a user"""
    return rule_service.get_user_active_rules(user_id)

@management_rule_router.get("/provider/{provider_id}/staff")
def get_provider_staff(
    provider_id: int,
    active_only: bool = Query(True, description="Return only active staff"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get all staff members for a provider"""
    return rule_service.get_provider_staff(provider_id, active_only)

@management_rule_router.get("/expiring")
def get_expiring_rules(
    days_threshold: int = Query(7, description="Days threshold for expiry"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get rules that will expire soon"""
    return rule_service.get_expiring_rules(days_threshold)

@management_rule_router.get("/{rule_id}")
def get_rule(
    rule_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Get management rule by ID"""
    return rule_service.get_rule_by_id(rule_id)

@management_rule_router.post("/")
def create_rule(
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Create a new management rule"""
    return rule_service.create_rule(rule)

@management_rule_router.put("/{rule_id}")
def update_rule(
    rule_id: int,
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Update an existing management rule"""
    rule.id_management_rule = rule_id
    return rule_service.update_rule(rule)

@management_rule_router.patch("/{rule_id}/answer")
def answer_invitation(
    rule_id: int,
    accept: bool = Query(..., description="Accept (true) or reject (false) invitation"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Respond to an invitation"""
    return rule_service.answer_invitation(rule_id, accept)

@management_rule_router.delete("/{rule_id}")
def delete_rule(
    rule_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """Delete a management rule"""
    return rule_service.delete_rule(rule_id)