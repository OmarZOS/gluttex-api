
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


# core/exceptions/location.py
from typing import Optional, Any
from core.exceptions.handler import APIException
from core.messages import *


class LocationNotFoundError(APIException):
    """Exception raised when a location is not found"""
    
    def __init__(self, location_id: str, details: Optional[Any] = None):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            error_code=ErrorCode.LOCATION_NOT_FOUND,
            message=f"Location {location_id} not found",
            details=details or {"location_id": location_id}
        )


class AddressNotFoundError(APIException):
    """Exception raised when an address is not found"""
    
    def __init__(self, address_id: str, details: Optional[Any] = None):
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            error_code=ErrorCode.ADDRESS_NOT_FOUND,
            message=f"Address {address_id} not found",
            details=details or {"address_id": address_id}
        )


class LocationValidationError(APIException):
    """Exception raised when location data validation fails"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            error_code=ErrorCode.LOCATION_VALIDATION_FAILED,
            message=message,
            details=details
        )


class LocationCreationError(APIException):
    """Exception raised when location creation fails"""
    
    def __init__(self, message: str = "Failed to create location", details: Optional[Any] = None):
        super().__init__(
            status_code=HTTP_417_EXPECTATION_FAILED,
            error_code=ErrorCode.LOCATION_INSERT_FAILED,
            message=message,
            details=details
        )


class LocationUpdateError(APIException):
    """Exception raised when location update fails"""
    
    def __init__(self, location_id: str, message: str = "Failed to update location", details: Optional[Any] = None):
        super().__init__(
            status_code=HTTP_417_EXPECTATION_FAILED,
            # error_code=LOCATION_UPDATE_FAILED,
            message=message,
            details=details or {"location_id": location_id}
        )