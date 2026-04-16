# routers/business_routers/staff_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.api_models import ManagementRule_API
from services.management_rule_service import ManagementRuleService

staff_router = APIRouter()

def get_management_rule_service() -> ManagementRuleService:
    return ManagementRuleService()


@staff_router.get("/{org_id}/{provider_id}/{user_id}/{rule_id}/{offset}/{limit}")
def get_staff(
    org_id: int,
    provider_id: int,
    user_id: int,
    rule_id: int,
    offset: int,
    limit: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Fetch staff members with pagination.
    
    Args:
        org_id: Organisation ID filter
        provider_id: Provider ID filter
        user_id: User ID filter
        rule_id: Rule ID filter
        offset: Pagination offset
        limit: Pagination limit
    
    Returns:
        List of staff members (management rules)
    """
    return rule_service.get_all_rules(
        org_id=org_id,
        supplier_id=provider_id,
        user_id=user_id,
        rule_id=rule_id,
        offset=offset,
        limit=limit
    )


@staff_router.get("/user/{user_id}")
def get_user_staff(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PENDING, REJECTED)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all staff assignments for a specific user.
    """
    if status:
        return rule_service.get_user_rules(user_id, status)
    return rule_service.get_user_rules(user_id)


@staff_router.get("/provider/{provider_id}")
def get_provider_staff(
    provider_id: int,
    active_only: bool = Query(True, description="Return only active staff"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all staff members for a provider.
    """
    return rule_service.get_provider_staff(provider_id, active_only)


@staff_router.get("/pending/{user_id}")
def get_pending_invitations(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all pending invitations for a user.
    """
    return rule_service.get_pending_invitations(user_id)


@staff_router.post("/add")
def insert_staff_details(
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Insert a new staff member (create a management rule).
    """
    return rule_service.create_rule(rule)


@staff_router.put("/{staff_id}")
def update_staff_details(
    staff_id: int,
    staff: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Update staff details.
    """
    staff.id_management_rule = staff_id
    return rule_service.update_rule(staff)


@staff_router.put("/answer/{staff_id}")
def answer_staff_invitation(
    staff_id: int,
    accept: bool = Query(..., description="Accept (true) or reject (false) invitation"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Answer a staff invitation (accept or reject).
    
    Args:
        staff_id: The rule ID
        accept: True to accept, False to reject
    """
    return rule_service.answer_invitation(staff_id, accept)


@staff_router.delete("/delete/{staff_id}")
def delete_staff_by_id(
    staff_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Delete a staff member by ID.
    """
    return rule_service.delete_rule(staff_id)