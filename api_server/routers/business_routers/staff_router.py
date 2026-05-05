# routers/business_routers/staff_router.py
"""
Staff router for managing staff assignments (management rules).
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.api_models import ManagementRule_API
from core.response_models import (
    SuccessResponseModel,
    PaginatedResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)

from core.exceptions.specific.staff_exceptions import (
    StaffException,
    RuleNotFoundException,
    RuleAlreadyExistsException,
    RuleInsertFailedException,
    RuleUpdateFailedException,
    RuleDeleteFailedException,
    RuleInvalidStatusException,
    InvitationAlreadyProcessedException,
    
    OrganisationNotFoundExceptionForStaff
)
from services.management_rule_service import ManagementRuleService

logger = logging.getLogger(__name__)

# Create router with tags and prefix
staff_router = APIRouter(
    # tags=["staff"],
    # prefix="/api"
)


def get_management_rule_service() -> ManagementRuleService:
    """Dependency to get ManagementRuleService instance"""
    return ManagementRuleService()


# ==================== Staff Listing Endpoints ====================

@staff_router.get(
    "/staff/{org_id}/{provider_id}/{user_id}/{rule_id}/{offset}/{limit}",
    response_model=SuccessResponseModel,
    summary="Get staff members",
    description="Fetch staff members with pagination and filters",
    responses={
        200: {
            "description": "Staff members retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
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
    
    - **org_id**: Organisation ID filter (use 0 to ignore)
    - **provider_id**: Provider ID filter (use 0 to ignore)
    - **user_id**: User ID filter (use 0 to ignore)
    - **rule_id**: Rule ID filter (use 0 to ignore)
    - **offset**: Pagination offset
    - **limit**: Pagination limit (max 100)
    """
    # Validate limit
    if limit > 100:
        limit = 100
    
    logger.info(f"Fetching staff - org_id:{org_id}, provider_id:{provider_id}, user_id:{user_id}, rule_id:{rule_id}, offset:{offset}, limit:{limit}")
    
    result = rule_service.get_all_rules(
        org_id=org_id if org_id > 0 else None,
        supplier_id=provider_id if provider_id > 0 else None,
        user_id=user_id if user_id > 0 else None,
        rule_id=rule_id if rule_id > 0 else None,
        offset=offset,
        limit=limit
    )
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'staff'} members",
        details={
            "filters": {
                "organisation_id": org_id if org_id > 0 else None,
                "provider_id": provider_id if provider_id > 0 else None,
                "user_id": user_id if user_id > 0 else None,
                "rule_id": rule_id if rule_id > 0 else None
            },
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@staff_router.get(
    "/staff/user/{user_id}",
    response_model=SuccessResponseModel,
    summary="Get user staff assignments",
    description="Get all staff assignments for a specific user",
    responses={
        200: {
            "description": "User staff assignments retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "User not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_staff(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PENDING, REJECTED, EXPIRED)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all staff assignments for a specific user.
    
    - **user_id**: User ID to fetch assignments for
    - **status**: Optional status filter
    """
    logger.info(f"Fetching staff assignments for user {user_id} (status={status})")
    
    if status:
        result = rule_service.get_user_rules(user_id, status.upper())
    else:
        result = rule_service.get_user_rules(user_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'assignments'} for user {user_id}",
        details={
            "user_id": user_id,
            "status_filter": status.upper() if status else None,
            "total_count": len(result) if isinstance(result, list) else 0
        }
    )


@staff_router.get(
    "/staff/provider/{provider_id}",
    response_model=SuccessResponseModel,
    summary="Get provider staff",
    description="Get all staff members for a provider",
    responses={
        200: {
            "description": "Provider staff retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Provider not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_provider_staff(
    provider_id: int,
    active_only: bool = Query(True, description="Return only active staff"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all staff members for a provider.
    
    - **provider_id**: Provider ID to fetch staff for
    - **active_only**: Return only active staff members
    """
    logger.info(f"Fetching staff for provider {provider_id} (active_only={active_only})")
    
    result = rule_service.get_provider_staff(provider_id, active_only)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'staff'} members for provider {provider_id}",
        details={
            "provider_id": provider_id,
            "active_only": active_only
        }
    )


@staff_router.get(
    "/staff/pending/{user_id}",
    response_model=SuccessResponseModel,
    summary="Get pending invitations",
    description="Get all pending invitations for a user",
    responses={
        200: {
            "description": "Pending invitations retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "User not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_pending_invitations(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all pending invitations for a user.
    
    - **user_id**: User ID to fetch pending invitations for
    """
    logger.info(f"Fetching pending invitations for user {user_id}")
    
    result = rule_service.get_pending_invitations(user_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'pending'} invitations for user {user_id}",
        details={
            "user_id": user_id,
            "pending_count": len(result) if isinstance(result, list) else 0
        }
    )


# ==================== Staff CRUD Operations ====================

@staff_router.post(
    "/staff",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create staff assignment",
    description="Insert a new staff member (create a management rule)",
    responses={
        201: {
            "description": "Staff assignment created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "User, Provider, or Organisation not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Staff assignment already exists",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False, include_409=True)
    }
)
def insert_staff_details(
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Insert a new staff member (create a management rule).
    
    - **rule**: Management rule/staff assignment details
    """
    logger.info(f"Creating new staff assignment for user: {rule.rule_ref_user}")
    
    result = rule_service.create_rule(rule)
    
    return SuccessResponseModel(
        success=True,
        message="Staff assignment created successfully",
        data=result,
        details={
            "rule_id": getattr(result, 'id_management_rule', None),
            "user_id": rule.rule_ref_user,
            "provider_id": rule.rule_ref_provider,
            "status": rule.management_rule_status
        }
    )


@staff_router.put(
    "/staff/{staff_id}",
    response_model=SuccessResponseModel,
    summary="Update staff assignment",
    description="Update staff details",
    responses={
        200: {
            "description": "Staff assignment updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Staff assignment not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Invalid status transition",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_staff_details(
    staff_id: int,
    staff: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Update staff details.
    
    - **staff_id**: Staff assignment ID to update
    - **staff**: Updated staff assignment details
    """
    logger.info(f"Updating staff assignment with ID: {staff_id}")
    
    staff.id_management_rule = staff_id
    result = rule_service.update_rule(staff)
    
    return SuccessResponseModel(
        success=True,
        message=f"Staff assignment {staff_id} updated successfully",
        data=result,
        details={
            "rule_id": staff_id,
            "updated_fields": {
                "status_updated": True,
                "expiry_updated": staff.management_rule_expiry is not None
            }
        }
    )


@staff_router.put(
    "/staff/answer/{staff_id}",
    response_model=SuccessResponseModel,
    summary="Answer staff invitation",
    description="Answer a staff invitation (accept or reject)",
    responses={
        200: {
            "description": "Invitation answered successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invitation already processed or invalid status",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Staff assignment not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def answer_staff_invitation(
    staff_id: int,
    accept: bool = Query(..., description="Accept (true) or reject (false) invitation"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Answer a staff invitation (accept or reject).
    
    - **staff_id**: The rule/staff assignment ID
    - **accept**: True to accept, False to reject
    """
    action = "accept" if accept else "reject"
    logger.info(f"Processing invitation {action} for staff assignment {staff_id}")
    
    result = rule_service.answer_invitation(staff_id, accept)
    
    new_status = "ACTIVE" if accept else "REJECTED"
    
    return SuccessResponseModel(
        success=True,
        message=f"Invitation {action}ed successfully",
        data=result,
        details={
            "rule_id": staff_id,
            "action": action,
            "new_status": new_status
        }
    )


@staff_router.delete(
    "/staff/delete/{staff_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete staff assignment",
    description="Delete a staff member by ID",
    responses={
        200: {
            "description": "Staff assignment deleted successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Staff assignment not found",
            "model": ErrorResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete active assignment",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_staff_by_id(
    staff_id: int,
    force_delete: bool = Query(False, description="Force delete even if assignment is active"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Delete a staff member by ID.
    
    - **staff_id**: Staff assignment ID to delete
    - **force_delete**: Force delete even if assignment is active
    """
    logger.info(f"Deleting staff assignment with ID: {staff_id} (force={force_delete})")
    
    result = rule_service.delete_rule(staff_id)
    
    return SuccessResponseModel(
        success=True,
        message=f"Staff assignment {staff_id} deleted successfully",
        data=result,
        details={
            "rule_id": staff_id,
            "force_deleted": force_delete
        }
    )