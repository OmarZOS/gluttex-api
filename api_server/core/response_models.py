# core/response_models.py
"""
Shared response models for OpenAPI documentation.
Provides standardized, reusable response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, Generic, TypeVar
from datetime import datetime

# Generic type variable for reusable response models
T = TypeVar('T')


# ==================== Base Response Models ====================

class ErrorResponseModel(BaseModel):
    """Standard error response model for all error responses"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "status_code": 404,
                "code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found",
                "details": {"resource_id": 123, "resource_type": "product"},
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-01T12:00:00Z",
                "path": "/api/resources/123"
            }
        }
    )
    
    success: bool = Field(False, description="Indicates if request was successful")
    status_code: int = Field(..., description="HTTP status code", ge=100, le=599)
    code: str = Field(..., description="Machine-readable error code", min_length=1)
    message: str = Field(..., description="Human-readable error message", min_length=1)
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request trace ID for debugging")
    timestamp: str = Field(..., description="Error timestamp in ISO format")
    path: Optional[str] = Field(None, description="Request path that caused the error")


class SuccessResponseModel(BaseModel, Generic[T]):
    """Standard success response model for all successful responses"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1, "name": "Example"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(True, description="Indicates if request was successful")
    message: Optional[str] = Field(None, description="Success message")
    data: Optional[T] = Field(None, description="Response data payload")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class PaginatedResponseModel(BaseModel, Generic[T]):
    """Standard paginated response model for list endpoints"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
                "pagination": {
                    "offset": 0,
                    "limit": 10,
                    "total": 25,
                    "next_offset": 10,
                    "previous_offset": None,
                    "has_next": True,
                    "has_previous": False
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(True, description="Indicates if request was successful")
    data: List[T] = Field(..., description="List of items")
    pagination: Dict[str, Any] = Field(
        ...,
        description="Pagination information",
        example={"offset": 0, "limit": 10, "total": 25, "next_offset": 10, "previous_offset": None}
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class EmptyResponseModel(BaseModel):
    """Response model for operations that return no data (DELETE, etc.)"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Resource deleted successfully",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(True, description="Indicates if request was successful")
    message: Optional[str] = Field(None, description="Success message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class IdResponseModel(BaseModel):
    """Response model for operations that return only an ID"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "id": 12345,
                "message": "Resource created successfully",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(True, description="Indicates if request was successful")
    id: int = Field(..., description="Resource ID", ge=1)
    message: Optional[str] = Field(None, description="Success message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class BulkOperationResponseModel(BaseModel):
    """Response model for bulk operations"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "total_processed": 10,
                "successful": 9,
                "failed": 1,
                "errors": [
                    {"id": 5, "error": "Resource not found"}
                ],
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(True, description="Indicates if request was successful")
    total_processed: int = Field(..., description="Total number of items processed", ge=0)
    successful: int = Field(..., description="Number of successfully processed items", ge=0)
    failed: int = Field(..., description="Number of failed items", ge=0)
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors for failed items")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ValidationErrorResponseModel(BaseModel):
    """Response model for validation errors (422)"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "status_code": 422,
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "errors": [
                    {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"},
                    {"loc": ["body", "age"], "msg": "must be greater than 0", "type": "value_error.number.not_gt"}
                ],
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    )
    
    success: bool = Field(False, description="Indicates if request was successful")
    status_code: int = Field(422, description="HTTP status code")
    code: str = Field("VALIDATION_ERROR", description="Error code")
    message: str = Field("Request validation failed", description="Error message")
    errors: List[Dict[str, Any]] = Field(..., description="List of validation errors")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


# ==================== Helper Functions ====================

def get_standard_responses(
    success_model: Optional[BaseModel] = None,
    include_404: bool = True,
    include_403: bool = True,
    custom_responses: Optional[Dict[int, Dict[str, Any]]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Get standard HTTP response schemas for CRUD endpoints.
    
    Args:
        success_model: Pydantic model for 200 success response
        include_404: Whether to include 404 Not Found response
        include_403: Whether to include 403 Forbidden response
        custom_responses: Additional custom responses to merge
    
    Returns:
        Dictionary of HTTP status code to response schema
    """
    responses = {
        400: {
            "description": "Bad Request - Invalid input parameters",
            "model": ErrorResponseModel
        },
        401: {
            "description": "Unauthorized - Authentication required",
            "model": ErrorResponseModel
        },
        422: {
            "description": "Validation Error - Request validation failed",
            "model": ValidationErrorResponseModel
        },
        429: {
            "description": "Too Many Requests - Rate limit exceeded",
            "model": ErrorResponseModel
        },
        500: {
            "description": "Internal Server Error - Something went wrong",
            "model": ErrorResponseModel
        },
        503: {
            "description": "Service Unavailable - Server temporarily unavailable",
            "model": ErrorResponseModel
        }
    }
    
    if include_403:
        responses[403] = {
            "description": "Forbidden - Insufficient permissions",
            "model": ErrorResponseModel
        }
    
    if include_404:
        responses[404] = {
            "description": "Not Found - Resource does not exist",
            "model": ErrorResponseModel
        }
    
    if success_model:
        responses[200] = {
            "description": "Successful Response",
            "model": success_model
        }
    
    if custom_responses:
        responses.update(custom_responses)
    
    return responses


def get_paginated_responses(
    item_model: BaseModel,
    include_404: bool = True
) -> Dict[int, Dict[str, Any]]:
    """
    Get standard responses for paginated list endpoints.
    
    Args:
        item_model: Pydantic model for individual items in the list
        include_404: Whether to include 404 Not Found response
    
    Returns:
        Dictionary of HTTP status code to response schema
    """
    # Create a concrete PaginatedResponseModel with the item model
    class ConcretePaginatedResponse(PaginatedResponseModel[item_model]):  # type: ignore
        pass
    
    return get_standard_responses(
        success_model=ConcretePaginatedResponse,
        include_404=include_404
    )


def get_crud_responses(
    create_model: Optional[BaseModel] = None,
    update_model: Optional[BaseModel] = None,
    delete_model: Optional[BaseModel] = None,
    get_model: Optional[BaseModel] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Get standard responses for CRUD operations.
    
    Args:
        create_model: Response model for POST (create) operations
        update_model: Response model for PUT/PATCH (update) operations
        delete_model: Response model for DELETE operations
        get_model: Response model for GET (retrieve) operations
    
    Returns:
        Dictionary of HTTP status code to response schema for each operation
    """
    responses = {}
    
    if create_model:
        responses[201] = {
            "description": "Created - Resource created successfully",
            "model": create_model
        }
        responses[409] = {
            "description": "Conflict - Resource already exists",
            "model": ErrorResponseModel
        }
    
    if update_model:
        responses[200] = {
            "description": "OK - Resource updated successfully",
            "model": update_model
        }
    
    if delete_model:
        responses[200] = {
            "description": "OK - Resource deleted successfully",
            "model": delete_model
        }
        responses[409] = {
            "description": "Conflict - Cannot delete due to dependencies",
            "model": ErrorResponseModel
        }
    
    if get_model:
        responses[200] = {
            "description": "OK - Resource retrieved successfully",
            "model": get_model
        }
    
    # Add common error responses
    responses.update(get_standard_responses(include_404=True))
    
    return responses


# ==================== Common Response Examples ====================

class ResponseExamples:
    """Common response examples for documentation"""
    
    # Success examples
    SUCCESS_CREATE = {
        "summary": "Create Success",
        "value": {
            "success": True,
            "message": "Resource created successfully",
            "data": {"id": 123},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    SUCCESS_UPDATE = {
        "summary": "Update Success",
        "value": {
            "success": True,
            "message": "Resource updated successfully",
            "data": {"id": 123, "updated_field": "new_value"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    SUCCESS_DELETE = {
        "summary": "Delete Success",
        "value": {
            "success": True,
            "message": "Resource deleted successfully",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    SUCCESS_RETRIEVE = {
        "summary": "Retrieve Success",
        "value": {
            "success": True,
            "data": {"id": 123, "name": "Example Resource"},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    # Error examples
    ERROR_NOT_FOUND = {
        "summary": "Resource Not Found",
        "value": {
            "success": False,
            "status_code": 404,
            "code": "RESOURCE_NOT_FOUND",
            "message": "Resource with ID 123 not found",
            "details": {"resource_id": 123, "resource_type": "product"},
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-01T12:00:00Z",
            "path": "/api/resources/123"
        }
    }
    
    ERROR_VALIDATION = {
        "summary": "Validation Error",
        "value": {
            "success": False,
            "status_code": 422,
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "errors": [
                {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}
            ],
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    ERROR_UNAUTHORIZED = {
        "summary": "Unauthorized",
        "value": {
            "success": False,
            "status_code": 401,
            "code": "UNAUTHORIZED",
            "message": "Authentication required",
            "timestamp": "2024-01-01T12:00:00Z",
            "path": "/api/protected-resource"
        }
    }
    
    ERROR_FORBIDDEN = {
        "summary": "Forbidden",
        "value": {
            "success": False,
            "status_code": 403,
            "code": "FORBIDDEN",
            "message": "Insufficient permissions to access this resource",
            "details": {"required_role": "admin"},
            "timestamp": "2024-01-01T12:00:00Z",
            "path": "/api/admin/users"
        }
    }
    
    ERROR_CONFLICT = {
        "summary": "Conflict",
        "value": {
            "success": False,
            "status_code": 409,
            "code": "CONFLICT",
            "message": "Resource with name 'example' already exists",
            "details": {"existing_id": 456},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }
    
    ERROR_INTERNAL = {
        "summary": "Internal Server Error",
        "value": {
            "success": False,
            "status_code": 500,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "request_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-01T12:00:00Z"
        }
    }

def get_crud_error_responses(
    include_404: bool = True,
    include_403: bool = True,
    include_409: bool = False,
    custom_responses: Optional[Dict[int, Dict[str, Any]]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Get standard error responses for CRUD operations.
    
    Args:
        include_404: Whether to include 404 Not Found response
        include_403: Whether to include 403 Forbidden response
        include_409: Whether to include 409 Conflict response
        custom_responses: Additional custom responses to merge
    
    Returns:
        Dictionary of HTTP status code to error response schema
    """
    responses = {
        400: {
            "description": "Bad Request - Invalid input parameters",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_input": {
                            "summary": "Invalid Input",
                            "value": {
                                "success": False,
                                "status_code": 400,
                                "code": "BAD_REQUEST",
                                "message": "Invalid input parameters",
                                "details": {"field": "email", "reason": "must be a valid email"},
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - Authentication required",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "unauthorized": {
                            "summary": "Missing Authentication",
                            "value": {
                                "success": False,
                                "status_code": 401,
                                "code": "UNAUTHORIZED",
                                "message": "Authentication required to access this resource",
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation Error - Request validation failed",
            "model": ValidationErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "validation_error": {
                            "summary": "Validation Failed",
                            "value": {
                                "success": False,
                                "status_code": 422,
                                "code": "VALIDATION_ERROR",
                                "message": "Request validation failed",
                                "errors": [
                                    {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}
                                ],
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        },
        429: {
            "description": "Too Many Requests - Rate limit exceeded",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "rate_limited": {
                            "summary": "Rate Limit Exceeded",
                            "value": {
                                "success": False,
                                "status_code": 429,
                                "code": "RATE_LIMIT_EXCEEDED",
                                "message": "Too many requests. Please try again later.",
                                "details": {"retry_after": 60},
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - Something went wrong",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "internal_error": {
                            "summary": "Server Error",
                            "value": {
                                "success": False,
                                "status_code": 500,
                                "code": "INTERNAL_SERVER_ERROR",
                                "message": "An unexpected error occurred",
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        },
        503: {
            "description": "Service Unavailable - Server temporarily unavailable",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "service_unavailable": {
                            "summary": "Service Down",
                            "value": {
                                "success": False,
                                "status_code": 503,
                                "code": "SERVICE_UNAVAILABLE",
                                "message": "Service is temporarily unavailable",
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Add 403 Forbidden if requested
    if include_403:
        responses[403] = {
            "description": "Forbidden - Insufficient permissions",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "forbidden": {
                            "summary": "Access Denied",
                            "value": {
                                "success": False,
                                "status_code": 403,
                                "code": "FORBIDDEN",
                                "message": "Insufficient permissions to access this resource",
                                "details": {"required_role": "admin"},
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        }
    
    # Add 404 Not Found if requested
    if include_404:
        responses[404] = {
            "description": "Not Found - Resource does not exist",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "not_found": {
                            "summary": "Resource Not Found",
                            "value": {
                                "success": False,
                                "status_code": 404,
                                "code": "NOT_FOUND",
                                "message": "The requested resource was not found",
                                "details": {"resource_id": 123, "resource_type": "product"},
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        }
    
    # Add 409 Conflict if requested
    if include_409:
        responses[409] = {
            "description": "Conflict - Resource conflict",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "examples": {
                        "conflict": {
                            "summary": "Resource Conflict",
                            "value": {
                                "success": False,
                                "status_code": 409,
                                "code": "CONFLICT",
                                "message": "Resource already exists or conflicts with existing data",
                                "details": {"existing_id": 456, "conflict_field": "email"},
                                "timestamp": "2024-01-01T12:00:00Z"
                            }
                        }
                    }
                }
            }
        }
    
    # Add custom responses if provided
    if custom_responses:
        responses.update(custom_responses)
    
    return responses


def get_success_response_examples() -> Dict[str, Any]:
    """
    Get examples of successful responses for documentation.
    """
    return {
        "200_create": {
            "summary": "Resource Created",
            "value": {
                "success": True,
                "message": "Resource created successfully",
                "data": {"id": 123},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        },
        "200_update": {
            "summary": "Resource Updated",
            "value": {
                "success": True,
                "message": "Resource updated successfully",
                "data": {"id": 123, "updated_field": "new_value"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        },
        "200_delete": {
            "summary": "Resource Deleted",
            "value": {
                "success": True,
                "message": "Resource deleted successfully",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        },
        "200_retrieve": {
            "summary": "Resource Retrieved",
            "value": {
                "success": True,
                "data": {"id": 123, "name": "Example Resource"},
                "timestamp": "2024-01-01T12:00:00Z"
            }
        },
        "200_list": {
            "summary": "List Retrieved",
            "value": {
                "success": True,
                "data": [{"id": 1}, {"id": 2}],
                "pagination": {
                    "offset": 0,
                    "limit": 10,
                    "total": 25
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }
    }


