
from typing import Optional, Dict, Any, List
from enum import Enum

from core.messages.error_codes import ErrorCode
from core.messages.error_messages import get_error_message
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_402_PAYMENT_REQUIRED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
)
from core.exceptions.handler import APIException


# ==================== Staff/Management Rule Exceptions ====================

class StaffException(APIException):
    """Base exception for all staff/management rule errors"""
    
    def __init__(
        self,
        message: str = "Staff service error",
        error_code: ErrorCode = ErrorCode.RULE_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class RuleNotFoundException(StaffException):
    """Exception when a management rule is not found"""
    
    def __init__(
        self,
        rule_id: int = None,
        user_id: int = None,
        provider_id: int = None,
        org_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if user_id:
            error_details["user_id"] = user_id
        if provider_id:
            error_details["provider_id"] = provider_id
        if org_id:
            error_details["organisation_id"] = org_id
        
        message = "Staff assignment not found"
        if rule_id:
            message = f"Staff assignment with ID '{rule_id}' not found"
        elif user_id and provider_id:
            message = f"Staff assignment for user '{user_id}' at provider '{provider_id}' not found"
        elif user_id:
            message = f"No staff assignments found for user '{user_id}'"
        elif provider_id:
            message = f"No staff assignments found for provider '{provider_id}'"
        elif org_id:
            message = f"No staff assignments found for organisation '{org_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class RuleAlreadyExistsException(StaffException):
    """Exception when a management rule already exists"""
    
    def __init__(
        self,
        user_id: int = None,
        provider_id: int = None,
        org_id: int = None,
        rule_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if user_id:
            error_details["user_id"] = user_id
        if provider_id:
            error_details["provider_id"] = provider_id
        if org_id:
            error_details["organisation_id"] = org_id
        if rule_id:
            error_details["existing_rule_id"] = rule_id
        
        message = "Staff assignment already exists"
        if user_id and provider_id:
            message = f"Staff assignment already exists for user '{user_id}' at provider '{provider_id}'"
        elif user_id:
            message = f"Staff assignment already exists for user '{user_id}'"
        elif provider_id:
            message = f"Staff assignment already exists for provider '{provider_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_ALREADY_EXISTS,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class RuleInsertFailedException(StaffException):
    """Exception when rule insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        user_id: int = None,
        provider_id: int = None,
        org_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if user_id:
            error_details["user_id"] = user_id
        if provider_id:
            error_details["provider_id"] = provider_id
        if org_id:
            error_details["organisation_id"] = org_id
        
        message = "Failed to create staff assignment"
        if user_id and provider_id:
            message = f"Failed to create staff assignment for user '{user_id}' at provider '{provider_id}'"
        elif user_id:
            message = f"Failed to create staff assignment for user '{user_id}'"
        elif provider_id:
            message = f"Failed to create staff assignment for provider '{provider_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class RuleUpdateFailedException(StaffException):
    """Exception when rule update fails"""
    
    def __init__(
        self,
        rule_id: int = None,
        error: str = None,
        fields_attempted: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update staff assignment"
        if rule_id:
            message = f"Failed to update staff assignment with ID '{rule_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class RuleDeleteFailedException(StaffException):
    """Exception when rule deletion fails"""
    
    def __init__(
        self,
        rule_id: int = None,
        error: str = None,
        has_dependencies: bool = False,
        is_active: bool = False,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if error:
            error_details["delete_error"] = error
        if has_dependencies:
            error_details["has_dependencies"] = has_dependencies
        if is_active:
            error_details["is_active"] = is_active
        
        message = "Failed to delete staff assignment"
        if rule_id:
            message = f"Failed to delete staff assignment with ID '{rule_id}'"
        
        if is_active:
            message += " - Assignment is active. Use force_delete=true to delete."
        elif has_dependencies:
            message += " - Assignment has dependencies"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class RuleInvalidStatusException(StaffException):
    """Exception for invalid rule status transitions"""
    
    def __init__(
        self,
        rule_id: int = None,
        current_status: str = None,
        requested_status: str = None,
        allowed_statuses: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if current_status:
            error_details["current_status"] = current_status
        if requested_status:
            error_details["requested_status"] = requested_status
        if allowed_statuses:
            error_details["allowed_statuses"] = allowed_statuses
        
        message = "Invalid staff assignment status transition"
        if current_status and requested_status:
            message = f"Cannot change status from '{current_status}' to '{requested_status}'"
        elif requested_status:
            message = f"Invalid status value '{requested_status}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_INVALID_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class InvitationAlreadyProcessedException(StaffException):
    """Exception when an invitation has already been processed"""
    
    def __init__(
        self,
        rule_id: int = None,
        current_status: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if current_status:
            error_details["current_status"] = current_status
        
        message = "Invitation has already been processed"
        if current_status:
            if current_status.upper() == "ACTIVE":
                message = "Invitation has already been accepted"
            elif current_status.upper() == "REJECTED":
                message = "Invitation has already been rejected"
            elif current_status.upper() == "EXPIRED":
                message = "Invitation has expired"
            else:
                message = f"Invitation has already been {current_status.lower()}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVITATION_ALREADY_PROCESSED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class InvitationExpiredException(StaffException):
    """Exception when an invitation has expired"""
    
    def __init__(
        self,
        rule_id: int = None,
        expiry_date: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_id:
            error_details["rule_id"] = rule_id
        if expiry_date:
            error_details["expiry_date"] = expiry_date
        
        message = "Invitation has expired"
        if expiry_date:
            message = f"Invitation expired on {expiry_date}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVITATION_ALREADY_PROCESSED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class UserNotFoundExceptionForStaff(StaffException):
    """Exception when a user is not found for staff operations"""
    
    def __init__(
        self,
        user_id: int = None,
        username: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if user_id:
            error_details["user_id"] = user_id
        if username:
            error_details["username"] = username
        
        message = "User not found"
        if user_id:
            message = f"User with ID '{user_id}' not found"
        elif username:
            message = f"User '{username}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.APPUSER_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class ProviderNotFoundExceptionForStaff(StaffException):
    """Exception when a provider is not found for staff operations"""
    
    def __init__(
        self,
        provider_id: int = None,
        provider_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if provider_id:
            error_details["provider_id"] = provider_id
        if provider_name:
            error_details["provider_name"] = provider_name
        
        message = "Provider not found"
        if provider_id:
            message = f"Provider with ID '{provider_id}' not found"
        elif provider_name:
            message = f"Provider '{provider_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class OrganisationNotFoundExceptionForStaff(StaffException):
    """Exception when an organisation is not found for staff operations"""
    
    def __init__(
        self,
        org_id: int = None,
        org_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if org_id:
            error_details["organisation_id"] = org_id
        if org_name:
            error_details["organisation_name"] = org_name
        
        message = "Organisation not found"
        if org_id:
            message = f"Organisation with ID '{org_id}' not found"
        elif org_name:
            message = f"Organisation '{org_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORGANISATION_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class InvalidRuleCodeException(StaffException):
    """Exception when an invalid management rule code is provided"""
    
    def __init__(
        self,
        rule_code: int = None,
        allowed_codes: List[int] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if rule_code:
            error_details["rule_code"] = rule_code
        if allowed_codes:
            error_details["allowed_codes"] = allowed_codes
        
        message = "Invalid management rule code"
        if rule_code:
            message = f"Management rule code '{rule_code}' is invalid"
        if allowed_codes:
            message += f". Allowed codes: {allowed_codes}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RULE_INVALID_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class StaffPermissionDeniedException(StaffException):
    """Exception when a user doesn't have permission for staff operations"""
    
    def __init__(
        self,
        user_id: int = None,
        action: str = None,
        required_role: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if user_id:
            error_details["user_id"] = user_id
        if action:
            error_details["action"] = action
        if required_role:
            error_details["required_role"] = required_role
        
        message = "Permission denied for staff operation"
        if action:
            message = f"User does not have permission to {action} staff assignments"
        if required_role:
            message += f" (requires {required_role} role)"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTH_UNAUTHORIZED,
            status_code=HTTP_403_FORBIDDEN,
            details=error_details
        )