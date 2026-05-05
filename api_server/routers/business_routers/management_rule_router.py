# routers/management_rule_router.py
"""
Management Rule router for handling staff assignments, invitations, and rules.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.api_models import ManagementRule_API
from core.models import ManagementRule
from core.response_models import (
    SuccessResponseModel,
    PaginatedResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)
from core.exceptions.specific.staff_exceptions import (
    RuleNotFoundException,
    RuleAlreadyExistsException,
    RuleInsertFailedException,
    RuleUpdateFailedException,
    RuleDeleteFailedException,
    RuleInvalidStatusException,
    InvitationAlreadyProcessedException
)
from services.management_rule_service import ManagementRuleService

logger = logging.getLogger(__name__)

management_rule_router = APIRouter(
    # tags=["management-rules"],
    # prefix="/api/management-rules"
)


def get_management_rule_service() -> ManagementRuleService:
    """Dependency to get ManagementRuleService instance"""
    return ManagementRuleService()


# ==================== Management Rule Listing Endpoints ====================

@management_rule_router.get(
    "/",
    response_model=SuccessResponseModel,
    summary="Get all rules",
    description="Get all management rules with pagination and filters",
    responses={
        200: {
            "description": "Rules retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_all_rules(
    org_id: int = Query(0, description="Filter by organisation ID"),
    supplier_id: int = Query(0, description="Filter by supplier ID"),
    user_id: int = Query(0, description="Filter by user ID"),
    rule_id: int = Query(0, description="Filter by rule ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all management rules with pagination and filters.
    
    - **org_id**: Filter by organisation ID
    - **supplier_id**: Filter by supplier ID
    - **user_id**: Filter by user ID
    - **rule_id**: Filter by rule ID
    - **offset**: Pagination offset
    - **limit**: Number of records to return (max 1000)
    """
    logger.info(f"Fetching rules - org:{org_id}, supplier:{supplier_id}, user:{user_id}, rule:{rule_id}, offset:{offset}, limit:{limit}")
    
    result = rule_service.get_all_rules(org_id, supplier_id, user_id, rule_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} rules",
        details={
            "filters": {
                "organisation_id": org_id if org_id > 0 else None,
                "supplier_id": supplier_id if supplier_id > 0 else None,
                "user_id": user_id if user_id > 0 else None,
                "rule_id": rule_id if rule_id > 0 else None
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result) if isinstance(result, list) else 0
            }
        }
    )


@management_rule_router.get(
    "/user/{user_id}",
    response_model=SuccessResponseModel,
    summary="Get user rules",
    description="Get all rules for a specific user",
    responses={
        200: {
            "description": "User rules retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_rules(
    user_id: int,  # Path parameter - NO Query()
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PENDING, REJECTED, EXPIRED)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all rules for a specific user.
    
    - **user_id**: User ID to fetch rules for (path parameter)
    - **status**: Filter by status (query parameter)
    """
    logger.info(f"Fetching rules for user {user_id} (status={status})")
    
    result = rule_service.get_user_rules(user_id, status)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} rules for user {user_id}",
        details={
            "user_id": user_id,
            "status_filter": status,
            "total": len(result) if isinstance(result, list) else 0
        }
    )


@management_rule_router.get(
    "/user/{user_id}/pending",
    response_model=SuccessResponseModel,
    summary="Get pending invitations",
    description="Get pending invitations for a user",
    responses={
        200: {
            "description": "Pending invitations retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_pending_invitations(
    user_id: int,  # Path parameter - NO Query()
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get pending invitations for a user.
    
    - **user_id**: User ID to fetch pending invitations for (path parameter)
    """
    logger.info(f"Fetching pending invitations for user {user_id}")
    
    result = rule_service.get_pending_invitations(user_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} pending invitations for user {user_id}",
        details={
            "user_id": user_id,
            "pending_count": len(result) if isinstance(result, list) else 0
        }
    )


@management_rule_router.get(
    "/user/{user_id}/active",
    response_model=SuccessResponseModel,
    summary="Get user active rules",
    description="Get active rules for a user",
    responses={
        200: {
            "description": "Active rules retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_active_rules(
    user_id: int,  # Path parameter - NO Query()
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get active rules for a user.
    
    - **user_id**: User ID to fetch active rules for (path parameter)
    """
    logger.info(f"Fetching active rules for user {user_id}")
    
    result = rule_service.get_user_active_rules(user_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} active rules for user {user_id}",
        details={
            "user_id": user_id,
            "active_count": len(result) if isinstance(result, list) else 0
        }
    )


@management_rule_router.get(
    "/provider/{provider_id}/staff",
    response_model=SuccessResponseModel,
    summary="Get provider staff",
    description="Get all staff members for a provider",
    responses={
        200: {
            "description": "Provider staff retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_provider_staff(
    provider_id: int,  # Path parameter - NO Query()
    active_only: bool = Query(True, description="Return only active staff"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all staff members for a provider.
    
    - **provider_id**: Provider ID to fetch staff for (path parameter)
    - **active_only**: Return only active staff (query parameter)
    """
    logger.info(f"Fetching staff for provider {provider_id} (active_only={active_only})")
    
    result = rule_service.get_provider_staff(provider_id, active_only)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} staff members for provider {provider_id}",
        details={
            "provider_id": provider_id,
            "active_only": active_only,
            "total": len(result) if isinstance(result, list) else 0
        }
    )


@management_rule_router.get(
    "/expiring",
    response_model=SuccessResponseModel,
    summary="Get expiring rules",
    description="Get rules that will expire soon",
    responses={
        200: {
            "description": "Expiring rules retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_expiring_rules(
    days_threshold: int = Query(7, ge=1, le=365, description="Days threshold for expiry (1-365)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get rules that will expire soon.
    
    - **days_threshold**: Days threshold for expiry (query parameter, 1-365)
    """
    logger.info(f"Fetching rules expiring within {days_threshold} days")
    
    result = rule_service.get_expiring_rules(days_threshold)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} rules expiring within {days_threshold} days",
        details={
            "days_threshold": days_threshold,
            "expiring_count": len(result) if isinstance(result, list) else 0
        }
    )


@management_rule_router.get(
    "/{rule_id}",
    response_model=SuccessResponseModel,
    summary="Get rule by ID",
    description="Get management rule by ID",
    responses={
        200: {
            "description": "Rule retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_rule(
    rule_id: int,  # Path parameter - NO Query()
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get management rule by ID.
    
    - **rule_id**: Rule ID to fetch (path parameter)
    """
    logger.info(f"Fetching rule with ID: {rule_id}")
    
    result = rule_service.get_rule_by_id(rule_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Rule {rule_id} retrieved successfully"
    )


# ==================== Management Rule CRUD Endpoints ====================

@management_rule_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create rule",
    description="Create a new management rule",
    responses={
        201: {
            "description": "Rule created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - User or provider not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Rule already exists",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_rule(
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Create a new management rule.
    
    - **rule**: Rule data (request body)
    """
    logger.info(f"Creating new rule for user: {rule.rule_ref_user}")
    
    result = rule_service.create_rule(rule)
    
    rule_id = getattr(result, 'id_management_rule', None)
    
    return SuccessResponseModel(
        success=True,
        message="Rule created successfully",
        data=result,
        details={
            "rule_id": rule_id,
            "user_id": rule.rule_ref_user,
            "provider_id": rule.rule_ref_provider,
            "status": rule.management_rule_status
        }
    )


@management_rule_router.put(
    "/{rule_id}",
    response_model=SuccessResponseModel,
    summary="Update rule",
    description="Update an existing management rule",
    responses={
        200: {
            "description": "Rule updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Rule not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Invalid status transition",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_rule(
    rule_id: int,  # Path parameter - NO Query()
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Update an existing management rule.
    
    - **rule_id**: Rule ID to update (path parameter)
    - **rule**: Updated rule data (request body)
    """
    logger.info(f"Updating rule with ID: {rule_id}")
    
    rule.id_management_rule = rule_id
    result = rule_service.update_rule(rule)
    
    return SuccessResponseModel(
        success=True,
        message=f"Rule {rule_id} updated successfully",
        data=result,
        details={
            "rule_id": rule_id,
            "status": rule.management_rule_status,
            "expiry": rule.management_rule_expiry
        }
    )


@management_rule_router.patch(
    "/{rule_id}/answer",
    response_model=SuccessResponseModel,
    summary="Answer invitation",
    description="Respond to an invitation (accept or reject)",
    responses={
        200: {
            "description": "Invitation answered successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid action or already processed",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Rule not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def answer_invitation(
    rule_id: int,  # Path parameter - NO Query()
    accept: bool = Query(..., description="Accept (true) or reject (false) invitation"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Respond to an invitation (accept or reject).
    
    - **rule_id**: Rule ID to respond to (path parameter)
    - **accept**: True to accept, False to reject (query parameter)
    """
    action = "accept" if accept else "reject"
    logger.info(f"Processing invitation {action} for rule {rule_id}")
    
    result = rule_service.answer_invitation(rule_id, accept)
    
    new_status = "ACTIVE" if accept else "REJECTED"
    
    return SuccessResponseModel(
        success=True,
        message=f"Invitation {action}ed successfully",
        data=result,
        details={
            "rule_id": rule_id,
            "action": action,
            "new_status": new_status
        }
    )


@management_rule_router.delete(
    "/{rule_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete rule",
    description="Delete a management rule",
    responses={
        200: {
            "description": "Rule deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete active rule",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_rule(
    rule_id: int,  # Path parameter - NO Query()
    force_delete: bool = Query(False, description="Force delete even if rule is active"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Delete a management rule.
    
    - **rule_id**: Rule ID to delete (path parameter)
    - **force_delete**: Force delete even if rule is active (query parameter)
    """
    logger.info(f"Deleting rule with ID: {rule_id} (force={force_delete})")
    
    result = rule_service.delete_rule(rule_id, force_delete)
    
    return SuccessResponseModel(
        success=True,
        message=f"Rule {rule_id} deleted successfully",
        data=result,
        details={
            "rule_id": rule_id,
            "force_deleted": force_delete
        }
    )