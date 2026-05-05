
from typing import Optional, Dict, Any, List
from enum import Enum

from core.messages.error_codes import ErrorCode
from core.messages.error_messages import get_error_message
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
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

class PersonNotFoundException(APIException):
    def __init__(self, person_id: int = None):
        details = {"person_id": person_id} if person_id else None
        super().__init__(
            status_code=HTTP_404_NOT_FOUND,
            error_code=ErrorCode.PERSON_NOT_EXISTS,
            message=f"Person with ID '{person_id}' not found" if person_id else "Person not found",
            details=details
        )

class PersonServiceException(APIException):
    """Base exception for person service errors"""
    
    def __init__(
        self,
        message: str = "Person service error",
        error_code: ErrorCode = ErrorCode.PERSON_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class PersonDetailsCreationException(PersonServiceException):
    """Exception for person details creation failures"""
    
    def __init__(
        self,
        error: str = None,
        first_name: str = None,
        last_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["creation_error"] = error
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        
        message = "Failed to create person details"
        if first_name and last_name:
            message = f"Failed to create person details for {first_name} {last_name}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DETAIL_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonNotFoundException(PersonServiceException):
    """Exception when a person is not found"""
    
    def __init__(
        self,
        person_id: str = None,
        email: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if email:
            error_details["email"] = email
        
        message = "Person not found"
        if person_id:
            message = f"Person with ID '{person_id}' not found"
        elif email:
            message = f"Person with email '{email}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class PersonInsertFailedException(PersonServiceException):
    """Exception when person insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        first_name: str = None,
        last_name: str = None,
        person_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        if person_id:
            error_details["person_id"] = person_id
        
        message = "Failed to insert person record"
        if first_name and last_name:
            message = f"Failed to insert person record for {first_name} {last_name}"
        elif person_id:
            message = f"Failed to insert person record with ID '{person_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonUpdateFailedException(PersonServiceException):
    """Exception when person update fails"""
    
    def __init__(
        self,
        person_id: str = None,
        error: str = None,
        fields_attempted: list = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update person record"
        if person_id:
            message = f"Failed to update person record with ID '{person_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonDeleteFailedException(PersonServiceException):
    """Exception when person deletion fails"""
    
    def __init__(
        self,
        person_id: str = None,
        error: str = None,
        has_relations: bool = False,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if error:
            error_details["delete_error"] = error
        if has_relations:
            error_details["has_relations"] = has_relations
            error_details["reason"] = "Person has existing relationships"
        
        message = "Failed to delete person record"
        if person_id:
            message = f"Failed to delete person record with ID '{person_id}'"
        
        if has_relations:
            message += " - Person has existing relationships"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class PersonDetailsNotFoundException(PersonServiceException):
    """Exception when person details are not found"""
    
    def __init__(
        self,
        details_id: int = None,
        person_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if details_id:
            error_details["details_id"] = details_id
        if person_id:
            error_details["person_id"] = person_id
        
        message = "Person details not found"
        if details_id:
            message = f"Person details with ID '{details_id}' not found"
        elif person_id:
            message = f"Person details for person ID '{person_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DETAILS_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class BloodTypeNotFoundException(PersonServiceException):
    """Exception when blood type is not found"""
    
    def __init__(
        self,
        blood_type_id: str = None,
        blood_type_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if blood_type_id:
            error_details["blood_type_id"] = blood_type_id
        if blood_type_name:
            error_details["blood_type_name"] = blood_type_name
        
        message = "Blood type not found"
        if blood_type_id:
            message = f"Blood type with ID '{blood_type_id}' not found"
        elif blood_type_name:
            message = f"Blood type '{blood_type_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.BLOOD_TYPE_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class InvalidPersonDataException(PersonServiceException):
    """Exception when person data is invalid"""
    
    def __init__(
        self,
        message: str = "Invalid person data provided",
        field: str = None,
        value: any = None,
        validation_errors: dict = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["provided_value"] = value
        if validation_errors:
            error_details["validation_errors"] = validation_errors
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DuplicatePersonException(PersonServiceException):
    """Exception when trying to create a duplicate person"""
    
    def __init__(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        national_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        if email:
            error_details["email"] = email
        if national_id:
            error_details["national_id"] = national_id
        
        message = "Person record already exists"
        if first_name and last_name:
            message = f"Person '{first_name} {last_name}' already exists"
        elif email:
            message = f"Person with email '{email}' already exists"
        elif national_id:
            message = f"Person with national ID '{national_id}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_INSERT_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class PersonValidationException(PersonServiceException):
    """Exception for person validation errors"""
    
    def __init__(
        self,
        errors: dict,
        message: str = "Person validation failed",
        details: dict = None
    ):
        error_details = details or {}
        error_details["validation_errors"] = errors
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )



# core/exceptions/specific/person_exceptions.py
"""
Person specific exceptions for person management.
"""

from core.exceptions.handler import APIException
from core.messages.error_codes import ErrorCode
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR
)
from typing import Optional, Dict, Any, List


# ==================== Person Service Exceptions ====================

class PersonServiceException(APIException):
    """Base exception for person service errors"""
    
    def __init__(
        self,
        message: str = "Person service error",
        error_code: ErrorCode = ErrorCode.PERSON_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: dict = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


class PersonException(PersonServiceException):
    """Alias for PersonServiceException for backward compatibility"""
    pass


class PersonNotFoundException(PersonServiceException):
    """Exception when a person is not found"""
    
    def __init__(
        self,
        person_id: str = None,
        email: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if email:
            error_details["email"] = email
        
        message = "Person not found"
        if person_id:
            message = f"Person with ID '{person_id}' not found"
        elif email:
            message = f"Person with email '{email}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class PersonDetailsCreationException(PersonServiceException):
    """Exception when person details creation fails"""
    
    def __init__(
        self,
        error: str = None,
        first_name: str = None,
        last_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["creation_error"] = error
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        
        message = "Failed to create person details"
        if first_name and last_name:
            message = f"Failed to create person details for {first_name} {last_name}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DETAIL_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonInsertFailedException(PersonServiceException):
    """Exception when person insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        first_name: str = None,
        last_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        
        message = "Failed to insert person record"
        if first_name and last_name:
            message = f"Failed to insert person record for {first_name} {last_name}"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonUpdateFailedException(PersonServiceException):
    """Exception when person update fails"""
    
    def __init__(
        self,
        person_id: str = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update person record"
        if person_id:
            message = f"Failed to update person record with ID '{person_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class PersonDeleteFailedException(PersonServiceException):
    """Exception when person deletion fails"""
    
    def __init__(
        self,
        person_id: str = None,
        error: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if person_id:
            error_details["person_id"] = person_id
        if error:
            error_details["delete_error"] = error
        
        message = "Failed to delete person record"
        if person_id:
            message = f"Failed to delete person record with ID '{person_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class PersonDetailsNotFoundException(PersonServiceException):
    """Exception when person details are not found"""
    
    def __init__(
        self,
        details_id: int = None,
        person_id: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if details_id:
            error_details["details_id"] = details_id
        if person_id:
            error_details["person_id"] = person_id
        
        message = "Person details not found"
        if details_id:
            message = f"Person details with ID '{details_id}' not found"
        elif person_id:
            message = f"Person details for person ID '{person_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_DETAILS_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class BloodTypeNotFoundException(PersonServiceException):
    """Exception when blood type is not found"""
    
    def __init__(
        self,
        blood_type_id: str = None,
        blood_type_name: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if blood_type_id:
            error_details["blood_type_id"] = blood_type_id
        if blood_type_name:
            error_details["blood_type_name"] = blood_type_name
        
        message = "Blood type not found"
        if blood_type_id:
            message = f"Blood type with ID '{blood_type_id}' not found"
        elif blood_type_name:
            message = f"Blood type '{blood_type_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.BLOOD_TYPE_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class InvalidPersonDataException(PersonServiceException):
    """Exception when person data is invalid"""
    
    def __init__(
        self,
        message: str = "Invalid person data provided",
        field: str = None,
        value: any = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["provided_value"] = value
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_400_BAD_REQUEST,
            details=error_details
        )


class DuplicatePersonException(PersonServiceException):
    """Exception when trying to create a duplicate person"""
    
    def __init__(
        self,
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        details: dict = None
    ):
        error_details = details or {}
        
        if first_name:
            error_details["first_name"] = first_name
        if last_name:
            error_details["last_name"] = last_name
        if email:
            error_details["email"] = email
        
        message = "Person record already exists"
        if first_name and last_name:
            message = f"Person '{first_name} {last_name}' already exists"
        elif email:
            message = f"Person with email '{email}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.PERSON_INSERT_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class PersonValidationException(PersonServiceException):
    """Exception for person validation errors"""
    
    def __init__(
        self,
        errors: dict,
        message: str = "Person validation failed",
        details: dict = None
    ):
        error_details = details or {}
        error_details["validation_errors"] = errors
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )