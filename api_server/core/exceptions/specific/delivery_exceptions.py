
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
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
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

# ==================== Base Delivery Exception ====================

class DeliveryException(APIException):
    """Base exception for all delivery-related errors"""
    
    def __init__(
        self,
        message: str = "Delivery service error",
        error_code: ErrorCode = ErrorCode.DELIVERY_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


# ==================== Delivery Exceptions ====================

class DeliveryNotFoundException(DeliveryException):
    """Exception when a delivery is not found"""
    
    def __init__(
        self,
        delivery_id: int = None,
        order_id: int = None,
        tracking_number: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if order_id:
            error_details["order_id"] = order_id
        if tracking_number:
            error_details["tracking_number"] = tracking_number
        
        message = "Delivery not found"
        if delivery_id:
            message = f"Delivery with ID '{delivery_id}' not found"
        elif order_id:
            message = f"Delivery for order ID '{order_id}' not found"
        elif tracking_number:
            message = f"Delivery with tracking number '{tracking_number}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class DeliveryCreationFailedException(DeliveryException):
    """Exception when delivery creation fails"""
    
    def __init__(
        self,
        error: str = None,
        delivery_id: int = None,
        order_id: int = None,
        provider_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["creation_error"] = error
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if order_id:
            error_details["order_id"] = order_id
        if provider_id:
            error_details["provider_id"] = provider_id
        
        message = "Failed to create delivery"
        if order_id:
            message = f"Failed to create delivery for order '{order_id}'"
        elif provider_id:
            message = f"Failed to create delivery for provider '{provider_id}'"
        elif delivery_id:
            message = f"Failed to create delivery with ID '{delivery_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class DeliveryUpdateFailedException(DeliveryException):
    """Exception when delivery update fails"""
    
    def __init__(
        self,
        delivery_id: int = None,
        error: str = None,
        fields_attempted: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update delivery"
        if delivery_id:
            message = f"Failed to update delivery with ID '{delivery_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class DeliveryDeleteFailedException(DeliveryException):
    """Exception when delivery deletion fails"""
    
    def __init__(
        self,
        delivery_id: int = None,
        error: str = None,
        is_in_transit: bool = False,
        has_packages: bool = False,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if error:
            error_details["delete_error"] = error
        if is_in_transit:
            error_details["is_in_transit"] = is_in_transit
        if has_packages:
            error_details["has_packages"] = has_packages
        
        message = "Failed to delete delivery"
        if delivery_id:
            message = f"Failed to delete delivery with ID '{delivery_id}'"
        
        reasons = []
        if is_in_transit:
            reasons.append("delivery is in transit")
        if has_packages:
            reasons.append("delivery has packages assigned")
        
        if reasons:
            message += f" - {', '.join(reasons)}. Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class DeliveryValidationFailedException(DeliveryException):
    """Exception when delivery data validation fails"""
    
    def __init__(
        self,
        field: str = None,
        value: Any = None,
        reason: str = None,
        validation_errors: Dict[str, List[str]] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["provided_value"] = value
        if reason:
            error_details["reason"] = reason
        if validation_errors:
            error_details["validation_errors"] = validation_errors
        
        message = "Delivery validation failed"
        if field and reason:
            message = f"Validation failed for field '{field}': {reason}"
        elif reason:
            message = reason
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_VALIDATION_FAILED,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )


class DeliveryCannotBeUpdatedException(DeliveryException):
    """Exception when a delivery cannot be updated in its current state"""
    
    def __init__(
        self,
        delivery_id: int = None,
        current_status: str = None,
        attempted_action: str = None,
        allowed_actions: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if current_status:
            error_details["current_status"] = current_status
        if attempted_action:
            error_details["attempted_action"] = attempted_action
        if allowed_actions:
            error_details["allowed_actions"] = allowed_actions
        
        message = "Delivery cannot be updated in its current state"
        if delivery_id and current_status:
            message = f"Delivery '{delivery_id}' cannot be updated because it is '{current_status}'"
        elif attempted_action and current_status:
            message = f"Cannot {attempted_action} delivery because it is '{current_status}'"
        
        # Add allowed actions if provided
        if allowed_actions and len(allowed_actions) > 0:
            message += f". Allowed actions: {', '.join(allowed_actions)}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_CANNOT_BE_UPDATED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DeliveryAlreadyExistsException(DeliveryException):
    """Exception when a delivery already exists for an order"""
    
    def __init__(
        self,
        order_id: int = None,
        delivery_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if delivery_id:
            error_details["existing_delivery_id"] = delivery_id
        
        message = "Delivery already exists"
        if order_id:
            message = f"A delivery already exists for order '{order_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_INSERT_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


# ==================== Bulk Delivery Exceptions ====================

class DeliveryBulkOperationException(DeliveryException):
    """Base exception for bulk delivery operations"""
    
    def __init__(
        self,
        message: str = "Bulk delivery operation failed",
        error_code: ErrorCode = ErrorCode.DELIVERY_BULK_UPDATE_FAILED,
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class DeliveryBulkUpdateFailedException(DeliveryBulkOperationException):
    """Exception when bulk update of deliveries fails"""
    
    def __init__(
        self,
        delivery_ids: List[int] = None,
        target_status: str = None,
        success_count: int = None,
        failed_count: int = None,
        failed_ids: List[int] = None,
        errors: List[Dict[str, Any]] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_ids:
            error_details["delivery_ids"] = delivery_ids
        if target_status:
            error_details["target_status"] = target_status
        if success_count is not None:
            error_details["success_count"] = success_count
        if failed_count is not None:
            error_details["failed_count"] = failed_count
        if failed_ids:
            error_details["failed_ids"] = failed_ids
        if errors:
            error_details["errors"] = errors
        
        message = "Bulk update of deliveries failed"
        if success_count is not None and failed_count is not None:
            message = f"Bulk update completed with {success_count} successes and {failed_count} failures"
        elif target_status:
            message = f"Failed to update deliveries to status '{target_status}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_BULK_UPDATE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class DeliveryBulkDeleteFailedException(DeliveryBulkOperationException):
    """Exception when bulk deletion of deliveries fails"""
    
    def __init__(
        self,
        provider_id: int = None,
        order_id: int = None,
        status: str = None,
        success_count: int = None,
        failed_count: int = None,
        errors: List[Dict[str, Any]] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if provider_id:
            error_details["provider_id"] = provider_id
        if order_id:
            error_details["order_id"] = order_id
        if status:
            error_details["status"] = status
        if success_count is not None:
            error_details["success_count"] = success_count
        if failed_count is not None:
            error_details["failed_count"] = failed_count
        if errors:
            error_details["errors"] = errors
        
        message = "Bulk deletion of deliveries failed"
        if provider_id:
            message = f"Failed to delete deliveries for provider '{provider_id}'"
        elif order_id:
            message = f"Failed to delete deliveries for order '{order_id}'"
        elif status:
            message = f"Failed to delete deliveries with status '{status}'"
        
        if success_count is not None and failed_count is not None:
            message = f"Bulk deletion completed with {success_count} successes and {failed_count} failures"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_BULK_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# ==================== Delivery Status Exceptions ====================

class DeliveryStatusInvalidException(DeliveryException):
    """Exception when delivery status is invalid"""
    
    def __init__(
        self,
        delivery_id: int = None,
        current_status: str = None,
        requested_status: str = None,
        allowed_statuses: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if current_status:
            error_details["current_status"] = current_status
        if requested_status:
            error_details["requested_status"] = requested_status
        if allowed_statuses:
            error_details["allowed_statuses"] = allowed_statuses
        
        message = "Invalid delivery status transition"
        if current_status and requested_status:
            message = f"Cannot change delivery status from '{current_status}' to '{requested_status}'"
        elif requested_status and allowed_statuses:
            message = f"Status '{requested_status}' is not allowed. Allowed: {', '.join(allowed_statuses)}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_VALIDATION_FAILED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DeliveryAlreadyDeliveredException(DeliveryException):
    """Exception when trying to modify a delivered delivery"""
    
    def __init__(
        self,
        delivery_id: int = None,
        action: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if action:
            error_details["attempted_action"] = action
        
        message = "Cannot modify delivered delivery"
        if delivery_id:
            message = f"Delivery '{delivery_id}' has already been delivered and cannot be modified"
        elif action:
            message = f"Cannot {action} a delivery that has already been delivered"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_CANNOT_BE_UPDATED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DeliveryCancelledException(DeliveryException):
    """Exception when trying to modify a cancelled delivery"""
    
    def __init__(
        self,
        delivery_id: int = None,
        action: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if action:
            error_details["attempted_action"] = action
        
        message = "Cannot modify cancelled delivery"
        if delivery_id:
            message = f"Delivery '{delivery_id}' has been cancelled and cannot be modified"
        elif action:
            message = f"Cannot {action} a delivery that has been cancelled"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_CANNOT_BE_UPDATED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


# ==================== Delivery Tracking Exceptions ====================

class DeliveryTrackingException(DeliveryException):
    """Base exception for delivery tracking errors"""
    
    def __init__(
        self,
        message: str = "Delivery tracking error",
        error_code: ErrorCode = ErrorCode.DELIVERY_UPDATE_FAILED,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class DeliveryTrackingUpdateFailedException(DeliveryTrackingException):
    """Exception when updating delivery tracking fails"""
    
    def __init__(
        self,
        delivery_id: int = None,
        current_address_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if current_address_id:
            error_details["current_address_id"] = current_address_id
        if error:
            error_details["tracking_error"] = error
        
        message = "Failed to update delivery tracking"
        if delivery_id:
            message = f"Failed to update tracking for delivery '{delivery_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_UPDATE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class InvalidTrackingAddressException(DeliveryTrackingException):
    """Exception when the tracking address is invalid"""
    
    def __init__(
        self,
        address_id: int = None,
        delivery_id: int = None,
        reason: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if address_id:
            error_details["address_id"] = address_id
        if delivery_id:
            error_details["delivery_id"] = delivery_id
        if reason:
            error_details["reason"] = reason
        
        message = "Invalid tracking address"
        if address_id:
            message = f"Address '{address_id}' is not a valid tracking location"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DELIVERY_VALIDATION_FAILED,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )