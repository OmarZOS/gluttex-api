# routers/app_routers/auth_router.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.messages import *


# ==================== Request Models ====================

class AuthData_API(BaseModel):
    """Authentication data model."""
    app_user_name: str = Field(..., description="Username")
    app_user_password: str = Field(..., description="Password")
    id_app_user: Optional[int] = Field(None, description="User ID (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "app_user_name": "john_doe",
                "app_user_password": "secure_password",
                "id_app_user": 123
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


class UserProfileUpdate_API(BaseModel):
    """User profile update request model."""
    username: Optional[str] = Field(None, description="New username")
    email: Optional[str] = Field(None, description="New email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_username",
                "email": "new_email@example.com",
                "first_name": "John",
                "last_name": "Smith"
            }
        }


class ChangePassword_API(BaseModel):
    """Change password request model."""
    # current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                # "current_password": "old_password",
                "new_password": "new_password123"
            }
        }


class AccountDeletionConfirmation(BaseModel):
    """Account deletion confirmation request model."""
    password: str = Field(..., description="Password confirmation")
    confirm: bool = Field(..., description="Confirmation checkbox")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "my_password",
                "confirm": True
            }
        }


# ==================== Response Models ====================

class TokenResponse(BaseModel):
    """JWT token response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    app_user_id: Optional[int] = Field(None, description="User ID")
    username: Optional[str] = Field(None, description="Username")
    email: Optional[str] = Field(None, description="User email")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 3600,
                "app_user_id": 123,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            }
        }


class UserProfileResponse(BaseModel):
    """User profile response model."""
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    app_user_preferences: Optional[str] = Field(None, description="Preferences")
    app_user_creation: Optional[datetime] = Field(None, description="Account creation date")
    last_name: Optional[str] = Field(None, description="Last name")
    user_type: Optional[str] = Field(None, description="User type description")
    image_url: Optional[str] = Field(None, description="Profile image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "user_type": "user",
                "created_at": "2024-01-01T12:00:00Z",
                "image_url": "https://example.com/avatar.jpg"
            }
        }


class LogoutResponse(BaseModel):
    """Response model for logout."""
    success: bool = Field(..., description="Logout success status")
    message: str = Field(..., description="Logout message")
    timestamp: datetime = Field(..., description="Logout timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully logged out",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }


class ChangePasswordResponse(BaseModel):
    """Response model for password change."""
    success: bool = Field(..., description="Password change success")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="User ID")
    changed_at: datetime = Field(..., description="Change timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Password changed successfully",
                "user_id": 123,
                "changed_at": "2024-01-01T12:00:00Z"
            }
        }


class AvatarUploadResponse(BaseModel):
    """Response model for avatar upload."""
    success: bool = Field(..., description="Upload success")
    message: str = Field(..., description="Response message")
    avatar_url: Optional[str] = Field(None, description="Uploaded avatar URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Avatar uploaded successfully",
                "avatar_url": "https://example.com/avatars/user_123.jpg"
            }
        }


class DeleteAccountResponse(BaseModel):
    """Response model for account deletion."""
    success: bool = Field(..., description="Deletion success")
    message: str = Field(..., description="Response message")
    user_id: int = Field(..., description="Deleted user ID")
    deleted_at: datetime = Field(..., description="Deletion timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Account deleted successfully",
                "user_id": 123,
                "deleted_at": "2024-01-01T12:00:00Z"
            }
        }


class ErrorResponseModel(BaseModel):
    """Error response model for OpenAPI documentation."""
    success: bool = Field(default=False, description="Success flag (always false for errors)")
    status_code: int = Field(..., description="HTTP status code")
    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for debugging")
    timestamp: str = Field(..., description="Error timestamp")
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "status_code": 401,
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid username or password",
                "details": {"attempts": 3},
                "request_id": "req_abc123",
                "timestamp": "2024-01-01T12:00:00Z",
                "path": "/api/auth/login"
            }
        }


class OAuthRedirectResponse(BaseModel):
    """OAuth redirect response model."""
    redirect_url: str = Field(..., description="OAuth provider authorization URL")
    state: Optional[str] = Field(None, description="OAuth state parameter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "redirect_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
                "state": "random_state_string"
            }
        }


class OAuthCallbackResponse(BaseModel):
    """OAuth callback response model."""
    success: bool = Field(..., description="OAuth callback success")
    message: str = Field(..., description="Response message")
    user_id: Optional[int] = Field(None, description="User ID if authenticated")
    token: Optional[str] = Field(None, description="Access token if authenticated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "OAuth authentication successful",
                "user_id": 123,
                "token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


# ==================== Combined Response for Admin ====================

class AdminUsersListResponse(BaseModel):
    """Admin users list response model."""
    users: List[UserProfileResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(default=1, description="Current page")
    limit: int = Field(default=50, description="Items per page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "users": [
                    {
                        "user_id": 123,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "user_type": "user",
                        "created_at": "2024-01-01T12:00:00Z",
                        "image_url": "https://example.com/avatar.jpg"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 50
            }
        }