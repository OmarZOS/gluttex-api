
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


class DocumentException(APIException):
    """Base exception for document-related errors"""
    
    def __init__(
        self,
        message: str = "Document generation error",
        error_code: ErrorCode = ErrorCode.PAYMENT_FAILED,
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class DocumentGenerationFailedException(DocumentException):
    """Exception when document generation fails"""
    
    def __init__(
        self,
        document_type: str = None,
        format: str = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if document_type:
            error_details["document_type"] = document_type
        if format:
            error_details["format"] = format
        if error:
            error_details["generation_error"] = error
        
        message = f"Failed to generate {document_type} document" if document_type else "Failed to generate document"
        if format:
            message += f" in {format} format"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PAYMENT_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )