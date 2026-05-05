
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



class ServiceException(APIException):
    """Base exception for all service-related errors"""
    
    def __init__(
        self,
        message: str = "Service error occurred",
        error_code: ErrorCode = ErrorCode.SERVICE_NOT_FOUND,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class ServiceNotFoundException(ServiceException):
    """Exception when a service is not found"""
    
    def __init__(
        self,
        service_id: int = None,
        service_name: str = None,
        provider_id: int = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if service_name:
            error_details["service_name"] = service_name
        if provider_id:
            error_details["provider_id"] = provider_id
        
        message = "Service not found"
        if service_id:
            message = f"Service with ID '{service_id}' not found"
        elif service_name:
            message = f"Service '{service_name}' not found"
        elif provider_id:
            message = f"No services found for provider ID '{provider_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class ServiceCreationFailedException(ServiceException):
    """Exception when service creation fails"""
    
    def __init__(
        self,
        error: str = None,
        service_name: str = None,
        provider_id: int = None,
        category_id: int = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["creation_error"] = error
        if service_name:
            error_details["service_name"] = service_name
        if provider_id:
            error_details["provider_id"] = provider_id
        if category_id:
            error_details["category_id"] = category_id
        
        message = "Failed to create service"
        if service_name:
            message = f"Failed to create service '{service_name}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class ServiceUpdateFailedException(ServiceException):
    """Exception when service update fails"""
    
    def __init__(
        self,
        service_id: int = None,
        error: str = None,
        fields_attempted: list = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update service"
        if service_id:
            message = f"Failed to update service with ID '{service_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class ServiceDeleteFailedException(ServiceException):
    """Exception when service deletion fails"""
    
    def __init__(
        self,
        service_id: int = None,
        error: str = None,
        has_requirements: bool = False,
        has_staff_requirements: bool = False,
        has_active_bookings: bool = False,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if error:
            error_details["delete_error"] = error
        if has_requirements:
            error_details["has_requirements"] = has_requirements
        if has_staff_requirements:
            error_details["has_staff_requirements"] = has_staff_requirements
        if has_active_bookings:
            error_details["has_active_bookings"] = has_active_bookings
        
        message = "Failed to delete service"
        if service_id:
            message = f"Failed to delete service with ID '{service_id}'"
        
        reasons = []
        if has_requirements:
            reasons.append("has resource requirements")
        if has_staff_requirements:
            reasons.append("has staff requirements")
        if has_active_bookings:
            reasons.append("has active bookings")
        
        if reasons:
            message += f" - Service {', '.join(reasons)}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class ServiceCategoryNotFoundException(ServiceException):
    """Exception when a service category is not found"""
    
    def __init__(
        self,
        category_id: int = None,
        category_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if category_id:
            error_details["category_id"] = category_id
        if category_name:
            error_details["category_name"] = category_name
        
        message = "Service category not found"
        if category_id:
            message = f"Service category with ID '{category_id}' not found"
        elif category_name:
            message = f"Service category '{category_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_CATEGORY_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class ServiceProviderNotFoundException(ServiceException):
    """Exception when a service provider is not found"""
    
    def __init__(
        self,
        provider_id: int = None,
        provider_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if provider_id:
            error_details["provider_id"] = provider_id
        if provider_name:
            error_details["provider_name"] = provider_name
        
        message = "Service provider not found"
        if provider_id:
            message = f"Service provider with ID '{provider_id}' not found"
        elif provider_name:
            message = f"Service provider '{provider_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SUPPLIER_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class ServiceToggleStatusException(ServiceException):
    """Exception when toggling service status fails"""
    
    def __init__(
        self,
        service_id: int = None,
        current_status: bool = None,
        requested_status: bool = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if current_status is not None:
            error_details["current_status"] = current_status
        if requested_status is not None:
            error_details["requested_status"] = requested_status
        if error:
            error_details["toggle_error"] = error
        
        message = "Failed to toggle service status"
        if service_id:
            message = f"Failed to toggle status for service ID '{service_id}'"
        
        if current_status is not None and requested_status is not None:
            if current_status == requested_status:
                message = f"Service is already {'active' if requested_status else 'inactive'}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UPDATE_FAILED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class ServiceRequirementNotFoundException(ServiceException):
    """Exception when service requirements are not found"""
    
    def __init__(
        self,
        service_id: int = None,
        requirement_id: int = None,
        requirement_type: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if requirement_id:
            error_details["requirement_id"] = requirement_id
        if requirement_type:
            error_details["requirement_type"] = requirement_type
        
        message = "Service requirement not found"
        if service_id and requirement_type:
            message = f"{requirement_type.capitalize()} requirements for service ID '{service_id}' not found"
        elif requirement_id:
            message = f"Service requirement with ID '{requirement_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class ServiceRequirementCreationException(ServiceException):
    """Exception when creating service requirements fails"""
    
    def __init__(
        self,
        service_id: int = None,
        requirement_type: str = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if requirement_type:
            error_details["requirement_type"] = requirement_type
        if error:
            error_details["creation_error"] = error
        
        message = "Failed to create service requirements"
        if requirement_type:
            message = f"Failed to create {requirement_type} for service"
        if service_id:
            message += f" ID '{service_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class ServiceRequirementUpdateFailedException(ServiceException):
    """Exception when updating service requirements fails"""
    
    def __init__(
        self,
        service_id: int = None,
        requirement_id: int = None,
        requirement_type: str = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if requirement_id:
            error_details["requirement_id"] = requirement_id
        if requirement_type:
            error_details["requirement_type"] = requirement_type
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update service requirement"
        if requirement_id:
            message = f"Failed to update requirement with ID '{requirement_id}'"
        elif service_id and requirement_type:
            message = f"Failed to update {requirement_type} for service ID '{service_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class ServiceRequirementDeleteFailedException(ServiceException):
    """Exception when deleting service requirements fails"""
    
    def __init__(
        self,
        service_id: int = None,
        requirement_id: int = None,
        requirement_type: str = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if requirement_id:
            error_details["requirement_id"] = requirement_id
        if requirement_type:
            error_details["requirement_type"] = requirement_type
        if error:
            error_details["delete_error"] = error
        
        message = "Failed to delete service requirement"
        if requirement_id:
            message = f"Failed to delete requirement with ID '{requirement_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class ServiceDuplicateException(ServiceException):
    """Exception when a duplicate service is being created"""
    
    def __init__(
        self,
        service_name: str = None,
        provider_id: int = None,
        existing_service_id: int = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_name:
            error_details["service_name"] = service_name
        if provider_id:
            error_details["provider_id"] = provider_id
        if existing_service_id:
            error_details["existing_service_id"] = existing_service_id
        
        message = "Service already exists"
        if service_name and provider_id:
            message = f"Service '{service_name}' already exists for this provider"
        elif service_name:
            message = f"Service '{service_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_INSERT_CONFLICT,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class ServiceValidationException(ServiceException):
    """Exception when service data validation fails"""
    
    def __init__(
        self,
        message: str = "Service data validation failed",
        errors: dict = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if errors:
            error_details["validation_errors"] = errors
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )


class ServicePriceException(ServiceException):
    """Exception when service pricing is invalid"""
    
    def __init__(
        self,
        service_id: int = None,
        base_price: float = None,
        final_price: float = None,
        reason: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if base_price:
            error_details["base_price"] = base_price
        if final_price:
            error_details["final_price"] = final_price
        if reason:
            error_details["reason"] = reason
        
        message = "Invalid service pricing"
        if base_price is not None and base_price < 0:
            message = "Service base price cannot be negative"
        elif final_price is not None and final_price < 0:
            message = "Service final price cannot be negative"
        elif reason:
            message = reason
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class ServiceInactiveException(ServiceException):
    """Exception when trying to use an inactive service"""
    
    def __init__(
        self,
        service_id: int = None,
        service_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if service_name:
            error_details["service_name"] = service_name
        
        message = "Service is currently inactive"
        if service_name:
            message = f"Service '{service_name}' is currently inactive"
        elif service_id:
            message = f"Service with ID '{service_id}' is currently inactive"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_NOT_FOUND,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class ServiceStaffRequirementNotFoundException(ServiceException):
    """Exception when service staff requirements are not found"""
    
    def __init__(
        self,
        service_id: int = None,
        staff_requirement_id: int = None,
        role: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if service_id:
            error_details["service_id"] = service_id
        if staff_requirement_id:
            error_details["staff_requirement_id"] = staff_requirement_id
        if role:
            error_details["role"] = role
        
        message = "Service staff requirement not found"
        if service_id and role:
            message = f"Staff requirement for role '{role}' on service ID '{service_id}' not found"
        elif staff_requirement_id:
            message = f"Staff requirement with ID '{staff_requirement_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )