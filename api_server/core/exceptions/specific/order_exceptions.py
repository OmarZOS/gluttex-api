
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


# core/exceptions/specific/product_exceptions.py
"""
Product specific exceptions for product management, barcode search, and AI recognition.
"""

from core.exceptions.handler import APIException
from core.messages.error_codes import ErrorCode
from typing import Optional, Dict, Any, List


# core/exceptions/specific/order_exceptions.py
"""
Order specific exceptions for order management, items, and status transitions.
"""

from core.messages.error_codes import ErrorCode
from typing import Optional, Dict, Any, List


# ==================== Base Order Exception ====================

class OrderException(APIException):
    """Base exception for all order-related errors"""
    
    def __init__(
        self,
        message: str = "Order service error",
        error_code: ErrorCode = ErrorCode.ORDER_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


# ==================== Order Exceptions ====================

class OrderNotFoundException(OrderException):
    """Exception when an order is not found"""
    
    def __init__(
        self,
        order_id: int = None,
        user_id: int = None,
        reference: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if user_id:
            error_details["user_id"] = user_id
        if reference:
            error_details["reference"] = reference
        
        message = "Order not found"
        if order_id:
            message = f"Order with ID '{order_id}' not found"
        elif user_id:
            message = f"No orders found for user ID '{user_id}'"
        elif reference:
            message = f"Order with reference '{reference}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class OrderAlreadyExistsException(OrderException):
    """Exception when trying to create a duplicate order"""
    
    def __init__(
        self,
        order_id: int = None,
        reference: str = None,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if reference:
            error_details["reference"] = reference
        if user_id:
            error_details["user_id"] = user_id
        
        message = "Order already exists"
        if order_id:
            message = f"Order with ID '{order_id}' already exists"
        elif reference:
            message = f"Order with reference '{reference}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_INSERT_CONFLICT,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class OrderCreationFailedException(OrderException):
    """Exception when order creation fails"""
    
    def __init__(
        self,
        error: str = None,
        order_id: int = None,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["creation_error"] = error
        if order_id:
            error_details["order_id"] = order_id
        if user_id:
            error_details["user_id"] = user_id
        
        message = "Failed to create order"
        if user_id:
            message = f"Failed to create order for user ID '{user_id}'"
        elif order_id:
            message = f"Failed to create order with ID '{order_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrderUpdateFailedException(OrderException):
    """Exception when order update fails"""
    
    def __init__(
        self,
        order_id: int = None,
        error: str = None,
        fields_attempted: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update order"
        if order_id:
            message = f"Failed to update order with ID '{order_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrderDeleteFailedException(OrderException):
    """Exception when order deletion fails"""
    
    def __init__(
        self,
        order_id: int = None,
        error: str = None,
        has_items: bool = False,
        has_payments: bool = False,
        is_shipped: bool = False,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if error:
            error_details["delete_error"] = error
        if has_items:
            error_details["has_items"] = has_items
        if has_payments:
            error_details["has_payments"] = has_payments
        if is_shipped:
            error_details["is_shipped"] = is_shipped
        
        message = "Failed to delete order"
        if order_id:
            message = f"Failed to delete order with ID '{order_id}'"
        
        reasons = []
        if has_items:
            reasons.append("has existing items")
        if has_payments:
            reasons.append("has payments processed")
        if is_shipped:
            reasons.append("order has already been shipped")
        
        if reasons:
            message += f" - {', '.join(reasons)}. Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class OrderFetchNotFoundException(OrderException):
    """Exception when order fetch returns no results"""
    
    def __init__(
        self,
        user_id: int = None,
        status: str = None,
        date_range: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if user_id:
            error_details["user_id"] = user_id
        if status:
            error_details["status"] = status
        if date_range:
            error_details["date_range"] = date_range
        
        message = "Unable to retrieve order information"
        if user_id:
            message = f"No orders found for user '{user_id}'"
        elif status:
            message = f"No orders found with status '{status}'"
        elif date_range:
            message = f"No orders found in date range '{date_range}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_FETCH_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


# ==================== Order Status Exceptions ====================

class InvalidOrderStatusException(OrderException):
    """Exception for invalid order status transitions"""
    
    def __init__(
        self,
        order_id: int = None,
        current_status: str = None,
        requested_status: str = None,
        allowed_statuses: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if current_status:
            error_details["current_status"] = current_status
        if requested_status:
            error_details["requested_status"] = requested_status
        if allowed_statuses:
            error_details["allowed_statuses"] = allowed_statuses
        
        message = "Invalid order status transition"
        if current_status and requested_status:
            message = f"Cannot change order status from '{current_status}' to '{requested_status}'"
        elif requested_status and allowed_statuses:
            message = f"Status '{requested_status}' is not allowed. Allowed statuses: {', '.join(allowed_statuses)}"
        elif requested_status:
            message = f"Invalid status value '{requested_status}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_ORDER_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class OrderStatusTransitionNotAllowedException(OrderException):
    """Exception when a specific status transition is not allowed"""
    
    def __init__(
        self,
        order_id: int = None,
        from_status: str = None,
        to_status: str = None,
        reason: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if from_status:
            error_details["from_status"] = from_status
        if to_status:
            error_details["to_status"] = to_status
        if reason:
            error_details["reason"] = reason
        
        message = f"Cannot transition order from '{from_status}' to '{to_status}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_ORDER_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class OrderAlreadyCancelledException(OrderException):
    """Exception when trying to cancel an already cancelled order"""
    
    def __init__(
        self,
        order_id: int = None,
        current_status: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if current_status:
            error_details["current_status"] = current_status
        
        message = "Order is already cancelled"
        if order_id:
            message = f"Order '{order_id}' has already been cancelled"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_ORDER_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class OrderAlreadyCompletedException(OrderException):
    """Exception when trying to modify a completed order"""
    
    def __init__(
        self,
        order_id: int = None,
        action: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if action:
            error_details["action"] = action
        
        message = "Cannot modify completed order"
        if order_id:
            message = f"Order '{order_id}' is already completed and cannot be modified"
        if action:
            message += f" (action: {action})"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_ORDER_STATUS,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


# ==================== Order Item Exceptions ====================

class OrderItemException(OrderException):
    """Base exception for order item errors"""
    
    def __init__(
        self,
        message: str = "Order item error",
        error_code: ErrorCode = ErrorCode.ORDER_ITEMS_DELETE_FAILED,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class OrderItemsNotFoundException(OrderItemException):
    """Exception when order items are not found"""
    
    def __init__(
        self,
        order_id: int = None,
        item_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if item_id:
            error_details["item_id"] = item_id
        
        message = "Order items not found"
        if order_id:
            message = f"Order items for order ID '{order_id}' not found"
        elif item_id:
            message = f"Order item with ID '{item_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_ITEMS_DELETE_FAILED,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class OrderItemNotFoundException(OrderItemException):
    """Exception when a specific order item is not found"""
    
    def __init__(
        self,
        item_id: int = None,
        order_id: int = None,
        product_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if item_id:
            error_details["item_id"] = item_id
        if order_id:
            error_details["order_id"] = order_id
        if product_id:
            error_details["product_id"] = product_id
        
        message = "Order item not found"
        if item_id:
            message = f"Order item with ID '{item_id}' not found"
        elif order_id and product_id:
            message = f"Product '{product_id}' not found in order '{order_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_ITEMS_DELETE_FAILED,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class OrderItemInsertFailedException(OrderItemException):
    """Exception when adding items to order fails"""
    
    def __init__(
        self,
        order_id: int = None,
        product_id: int = None,
        quantity: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if product_id:
            error_details["product_id"] = product_id
        if quantity:
            error_details["quantity"] = quantity
        if error:
            error_details["insert_error"] = error
        
        message = "Failed to add items to order"
        if order_id:
            message = f"Failed to add items to order ID '{order_id}'"
        if product_id:
            message += f" (product: {product_id})"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_ITEM_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrderItemUpdateFailedException(OrderItemException):
    """Exception when updating order items fails"""
    
    def __init__(
        self,
        item_id: int = None,
        order_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if item_id:
            error_details["item_id"] = item_id
        if order_id:
            error_details["order_id"] = order_id
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update order item"
        if item_id:
            message = f"Failed to update order item with ID '{item_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class OrderItemDeleteFailedException(OrderItemException):
    """Exception when deleting order items fails"""
    
    def __init__(
        self,
        item_id: int = None,
        order_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if item_id:
            error_details["item_id"] = item_id
        if order_id:
            error_details["order_id"] = order_id
        if error:
            error_details["delete_error"] = error
        
        message = "Failed to delete order item"
        if item_id:
            message = f"Failed to delete order item with ID '{item_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_ITEMS_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# ==================== Order Conflict Exceptions ====================

class OrderConflictException(OrderException):
    """Exception for order conflicts (duplicate, concurrent modification)"""
    
    def __init__(
        self,
        order_id: int = None,
        reason: str = None,
        conflicting_order_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if reason:
            error_details["reason"] = reason
        if conflicting_order_id:
            error_details["conflicting_order_id"] = conflicting_order_id
        
        message = "Order conflict detected"
        if reason:
            message = f"Order conflict: {reason}"
        elif order_id:
            message = f"Conflict with order ID '{order_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_INSERT_CONFLICT,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class OrderLibraryException(OrderException):
    """Exception for order processing library errors"""
    
    def __init__(
        self,
        error: str = None,
        library_name: str = None,
        operation: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["library_error"] = error
        if library_name:
            error_details["library_name"] = library_name
        if operation:
            error_details["operation"] = operation
        
        message = "Order processing library error"
        if library_name:
            message = f"Error in {library_name} while processing order"
        if operation:
            message += f" during {operation}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.ORDER_LIB_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# ==================== Order Validation Exceptions ====================

class OrderValidationException(OrderException):
    """Exception for order data validation errors"""
    
    def __init__(
        self,
        message: str = "Order validation failed",
        errors: Dict[str, List[str]] = None,
        details: Dict[str, Any] = None
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


class OrderEmptyException(OrderValidationException):
    """Exception when order has no items"""
    
    def __init__(
        self,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if user_id:
            error_details["user_id"] = user_id
        
        message = "Order must contain at least one item"
        if user_id:
            message = f"Order for user '{user_id}' must contain at least one item"
        
        super().__init__(
            message=message,
            errors={"items": ["At least one item is required"]},
            details=error_details
        )


class OrderTotalMismatchException(OrderValidationException):
    """Exception when order total doesn't match calculated total"""
    
    def __init__(
        self,
        order_id: int = None,
        expected_total: float = None,
        actual_total: float = None,
        difference: float = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if order_id:
            error_details["order_id"] = order_id
        if expected_total is not None:
            error_details["expected_total"] = expected_total
        if actual_total is not None:
            error_details["actual_total"] = actual_total
        if difference is not None:
            error_details["difference"] = difference
        
        message = "Order total mismatch"
        if expected_total is not None and actual_total is not None:
            message = f"Order total {actual_total} does not match calculated total {expected_total} (difference: {difference})"
        
        super().__init__(
            message=message,
            errors={"total_amount": [message]},
            details=error_details
        )


class OrderInsertFailedException(APIException):
    """Exception raised when order creation fails."""
    
    def __init__(self, error: str, user_id: int = None):
        details = {"error": error}
        if user_id:
            details["user_id"] = user_id
        
        super().__init__(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ErrorCode.ORDER_INSERT_FAILED,
            message="Failed to create order",
            details=details
        )

class OrderStatusTransitionException(APIException):
    """Exception raised when an invalid status transition is attempted."""
    
    def __init__(self, current_status: str, new_status: str, allowed_transitions: list):
        super().__init__(
            status=HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.INVALID_ORDER_STATUS,
            message=f"Cannot transition order from {current_status} to {new_status}",
            details={
                "current_status": current_status,
                "new_status": new_status,
                "allowed_transitions": allowed_transitions
            }
        )
