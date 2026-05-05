# core/error_schemas.py
"""
OpenAPI error schemas for API documentation.
These match the response schemas in your OpenAPI spec.
"""

from typing import Dict, Any

# OpenAPI schema for error responses
ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["code", "message", "status_code"],
    "properties": {
        "success": {
            "type": "boolean",
            "example": False,
            "description": "Always false for error responses"
        },
        "status_code": {
            "type": "integer",
            "description": "HTTP status code",
            "example": 400
        },
        "code": {
            "type": "string",
            "description": "Machine-readable error code",
            "example": "VALIDATION_ERROR"
        },
        "message": {
            "type": "string",
            "description": "Human-readable error message",
            "example": "Invalid email format"
        },
        "details": {
            "type": "object",
            "description": "Additional error context",
            "additionalProperties": True,
            "example": {
                "field": "email",
                "reason": "must be a valid email address",
                "provided_value": "invalid-email"
            }
        },
        "request_id": {
            "type": "string",
            "description": "Request trace ID for debugging",
            "format": "uuid",
            "example": "123e4567-e89b-12d3-a456-426614174000"
        },
        "timestamp": {
            "type": "string",
            "description": "Error timestamp",
            "format": "date-time",
            "example": "2024-01-01T12:00:00Z"
        },
        "path": {
            "type": "string",
            "description": "Request path that caused error",
            "example": "/api/users/123"
        }
    }
}

# Validation error schema (matches FastAPI's validation errors)
VALIDATION_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean", "example": False},
        "status_code": {"type": "integer", "example": 422},
        "code": {"type": "string", "example": "VALIDATION_ERROR"},
        "message": {"type": "string", "example": "Request validation failed"},
        "details": {
            "type": "object",
            "properties": {
                "errors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "loc": {
                                "type": "array",
                                "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                                "example": ["body", "email"]
                            },
                            "msg": {"type": "string", "example": "field required"},
                            "type": {"type": "string", "example": "value_error.missing"}
                        }
                    }
                }
            }
        },
        "request_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "path": {"type": "string"}
    }
}


def get_error_responses(status_codes: list) -> Dict[str, Any]:
    """
    Helper to generate OpenAPI error responses for a list of status codes.
    
    Usage:
        @app.get("/users")
        async def get_users():
            ...
            responses=get_error_responses([400, 401, 403, 404])
    """
    error_responses = {}
    
    error_descriptions = {
        400: "Bad Request - Invalid input parameters",
        401: "Unauthorized - Authentication required",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Resource does not exist",
        409: "Conflict - Resource already exists",
        422: "Validation Error - Request validation failed",
        429: "Too Many Requests - Rate limit exceeded",
        500: "Internal Server Error - Something went wrong"
    }
    
    for code in status_codes:
        schema = VALIDATION_ERROR_SCHEMA if code == 422 else ERROR_RESPONSE_SCHEMA
        error_responses[code] = {
            "description": error_descriptions.get(code, "Error occurred"),
            "content": {
                "application/json": {
                    "schema": schema,
                    "examples": {
                        f"error_{code}": {
                            "value": {
                                "success": False,
                                "status_code": code,
                                "code": "ERROR_CODE",
                                "message": error_descriptions.get(code, "An error occurred"),
                                "request_id": "00000000-0000-0000-0000-000000000000",
                                "timestamp": "2024-01-01T12:00:00Z",
                                "path": "/api/example"
                            }
                        }
                    }
                }
            }
        }
    
    return error_responses