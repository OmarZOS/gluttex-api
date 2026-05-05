# core/exceptions/specific/business_exceptions.py
"""
Business operation specific exceptions.
"""

from core.exceptions.handler import APIException
from core.messages.error_codes import ErrorCode
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from typing import Optional, Dict, Any


class BusinessOperationException(APIException):
    """Base exception for business operation errors"""
    
    def __init__(
        self,
        message: str = "Business operation error",
        error_code: ErrorCode = ErrorCode.FAILED,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class BusinessOperationNotFoundException(BusinessOperationException):
    """Exception when business operations are not found"""
    
    def __init__(
        self,
        supplier_id: int = None,
        order_id: int = None,
        cart_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if supplier_id:
            error_details["supplier_id"] = supplier_id
        if order_id:
            error_details["order_id"] = order_id
        if cart_id:
            error_details["cart_id"] = cart_id
        
        message = "Business operations not found"
        if supplier_id:
            message = f"No business operations found for supplier ID '{supplier_id}'"
        elif order_id:
            message = f"No business operations found for order ID '{order_id}'"
        elif cart_id:
            message = f"No business operations found for cart ID '{cart_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.FAILED,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class BusinessOperationServiceException(BusinessOperationException):
    """Exception for business operation service errors"""
    
    def __init__(
        self,
        message: str = "Business operation service error",
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["service_error"] = error
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )