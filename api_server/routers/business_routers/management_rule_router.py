# routers/management_rule_router.py
"""
Management Rule router for handling staff assignments, invitations, and rules.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.models.api_models import ManagementRule_API
from core.models.models import ManagementRule
from core.response_models import ErrorResponseModel, get_crud_error_responses
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

management_rule_router = APIRouter()


def get_management_rule_service() -> ManagementRuleService:
    """Dependency to get ManagementRuleService instance"""
    return ManagementRuleService()


# ==================== Management Rule Listing Endpoints ====================

@management_rule_router.get(
    "/",
    # response_model=List[ManagementRule_API],
    summary="Get all rules",
    description="Get all management rules with pagination and filters",
    responses={
        200: {"description": "Rules retrieved successfully"},
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
    """
    logger.info(f"Fetching rules - org:{org_id}, supplier:{supplier_id}, user:{user_id}, rule:{rule_id}, offset:{offset}, limit:{limit}")
    return rule_service.get_all_rules(org_id, supplier_id, user_id, rule_id, offset, limit)


@management_rule_router.get(
    "/user/{user_id}",
    # response_model=List[ManagementRule_API],
    summary="Get user rules",
    description="Get all rules for a specific user",
    responses={
        200: {"description": "User rules retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_rules(
    user_id: int,
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PENDING, REJECTED, EXPIRED)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get all rules for a specific user.
    """
    logger.info(f"Fetching rules for user {user_id} (status={status})")
    return rule_service.get_user_rules(user_id, status)


@management_rule_router.get(
    "/user/{user_id}/pending",
    # response_model=List[ManagementRule_API],
    summary="Get pending invitations",
    description="Get pending invitations for a user",
    responses={
        200: {"description": "Pending invitations retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_pending_invitations(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get pending invitations for a user.
    """
    logger.info(f"Fetching pending invitations for user {user_id}")
    return rule_service.get_pending_invitations(user_id)


@management_rule_router.get(
    "/user/{user_id}/active",
    # response_model=List[ManagementRule_API],
    summary="Get user active rules",
    description="Get active rules for a user",
    responses={
        200: {"description": "Active rules retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_active_rules(
    user_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get active rules for a user.
    """
    logger.info(f"Fetching active rules for user {user_id}")
    return rule_service.get_user_active_rules(user_id)


@management_rule_router.get(
    "/provider/{provider_id}/staff",
    # response_model=List[ManagementRule_API],
    summary="Get provider staff",
    description="Get all staff members for a provider",
    responses={
        200: {"description": "Provider staff retrieved successfully"},
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
    """
    logger.info(f"Fetching staff for provider {provider_id} (active_only={active_only})")
    return rule_service.get_provider_staff(provider_id, active_only)


@management_rule_router.get(
    "/expiring",
    # response_model=List[ManagementRule_API],
    summary="Get expiring rules",
    description="Get rules that will expire soon",
    responses={
        200: {"description": "Expiring rules retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_expiring_rules(
    days_threshold: int = Query(7, ge=1, le=365, description="Days threshold for expiry (1-365)"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get rules that will expire soon.
    """
    logger.info(f"Fetching rules expiring within {days_threshold} days")
    return rule_service.get_expiring_rules(days_threshold)


@management_rule_router.get(
    "/{rule_id}",
    # response_model=ManagementRule_API,
    summary="Get rule by ID",
    description="Get management rule by ID",
    responses={
        200: {"description": "Rule retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_rule(
    rule_id: int,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Get management rule by ID.
    """
    logger.info(f"Fetching rule with ID: {rule_id}")
    return rule_service.get_rule_by_id(rule_id)


# ==================== Management Rule CRUD Endpoints ====================

@management_rule_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # response_model=ManagementRule_API,
    summary="Create rule",
    description="Create a new management rule",
    responses={
        201: {"description": "Rule created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_rule(
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Create a new management rule.
    """
    logger.info(f"Creating new rule for user: {rule.rule_ref_user}")
    return rule_service.create_rule(rule)


@management_rule_router.put(
    "/{rule_id}",
    # response_model=ManagementRule_API,
    summary="Update rule",
    description="Update an existing management rule",
    responses={
        200: {"description": "Rule updated successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_rule(
    rule_id: int,
    rule: ManagementRule_API,
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Update an existing management rule.
    """
    logger.info(f"Updating rule with ID: {rule_id}")
    rule.id_management_rule = rule_id
    return rule_service.update_rule(rule)


@management_rule_router.patch(
    "/{rule_id}/answer",
    # response_model=ManagementRule_API,
    summary="Answer invitation",
    description="Respond to an invitation (accept or reject)",
    responses={
        200: {"description": "Invitation answered successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def answer_invitation(
    rule_id: int,
    accept: bool = Query(..., description="Accept (true) or reject (false) invitation"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Respond to an invitation (accept or reject).
    """
    action = "accept" if accept else "reject"
    logger.info(f"Processing invitation {action} for rule {rule_id}")
    return rule_service.answer_invitation(rule_id, accept)


@management_rule_router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete rule",
    description="Delete a management rule",
    responses={
        204: {"description": "Rule deleted successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def delete_rule(
    rule_id: int,
    force_delete: bool = Query(False, description="Force delete even if rule is active"),
    rule_service: ManagementRuleService = Depends(get_management_rule_service)
):
    """
    Delete a management rule.
    """
    logger.info(f"Deleting rule with ID: {rule_id} (force={force_delete})")
    rule_service.delete_rule(rule_id, force_delete)
    return None  # 204 No Content