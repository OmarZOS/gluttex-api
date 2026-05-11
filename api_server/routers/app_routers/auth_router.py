# routers/app_routers/auth_router.py
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from core.responses.auth_responses import *
from core.exceptions.handler import OAuthException
from core.exceptions.handler import APIException
from core.messages import *
from core.api_models import AuthData_API
from core.exceptions.error_responses import ErrorResponse, create_error_response
from services.auth_service import AuthService
from services.oauth_config_service import OAuthConfigService


# ==================== Router ====================

auth_router = APIRouter()

# Dependency injection
def get_auth_service() -> AuthService:
    return AuthService()

def get_oauth_config() -> OAuthConfigService:
    return OAuthConfigService()


@auth_router.get(
    "/login/{provider}",
    summary="Login with OAuth provider",
    description="Redirects user to the OAuth provider's login page.",
    responses={
        302: {
            "description": "Redirect to OAuth provider",
            "headers": {
                "Location": {
                    "description": "OAuth provider authorization URL",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {
            "description": "Bad Request - Unsupported provider",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "status_code": 400,
                        "code": "INTERFACE_ERROR",
                        "message": "Unsupported provider: google",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error - OAuth configuration error",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "status_code": 500,
                        "code": "INTERFACE_ERROR",
                        "message": "OAuth provider 'google' not properly configured",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                }
            }
        }
    }
)
async def login(
    provider: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    oauth_config: OAuthConfigService = Depends(get_oauth_config)
):
    """
    Redirects user to the OAuth provider's login page.
    
    - **provider**: OAuth provider name (google, facebook, github)
    """
    if not oauth_config.is_supported_provider(provider):
        raise OAuthException()
    
    oauth_client = oauth_config.get_client(provider)
    if not oauth_client:
        raise OAuthException()
    
    return await auth_service.handle_oauth_login(provider, request, oauth_client)


@auth_router.get(
    "/auth/{provider}",
    summary="OAuth Callback",
    description="Handles the OAuth provider's callback and retrieves user info.",
    responses={
        302: {
            "description": "Redirect to frontend with user data or error",
            "headers": {
                "Location": {
                    "description": "Frontend callback URL with token or error",
                    "schema": {"type": "string"}
                }
            }
        },
        400: {
            "description": "Bad Request - OAuth callback error",
            "model": ErrorResponseModel
        },
        401: {
            "description": "Unauthorized - Invalid OAuth state",
            "model": ErrorResponseModel
        },
        500: {
            "description": "Internal Server Error",
            "model": ErrorResponseModel
        }
    }
)
async def auth_callback(
    provider: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    oauth_config: OAuthConfigService = Depends(get_oauth_config)
):
    """
    Handles the OAuth provider's callback and retrieves user info.
    
    - **provider**: OAuth provider name (google, facebook, github)
    """
    if not oauth_config.is_supported_provider(provider):
        return auth_service.create_redirect_response(
            {}, 
            error=f"Unsupported provider: {provider}"
        )
    
    oauth_client = oauth_config.get_client(provider)
    if not oauth_client:
        return auth_service.create_redirect_response(
            {},
            error=f"OAuth provider '{provider}' not properly configured"
        )
    
    return await auth_service.handle_oauth_callback(provider, request, oauth_client)


@auth_router.post(
    "/authentication/token",
    response_model=TokenResponse,
    summary="Login User",
    description="Authenticates the user and returns an access token.",
    responses={
        200: {
            "description": "Successfully authenticated",
            "model": TokenResponse,
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIs...",
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "user_id": 123,
                        "username": "john_doe"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Invalid credentials format",
            "model": ErrorResponseModel
        },
        401: {
            "description": "Unauthorized - Invalid credentials",
            "model": ErrorResponseModel,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "status_code": 401,
                        "code": "INCORRECT_CREDENTIALS",
                        "message": "Invalid username or password",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        422: {
            "description": "Validation Error",
            "model": ErrorResponseModel
        },
        429: {
            "description": "Too Many Requests",
            "model": ErrorResponseModel
        },
        500: {
            "description": "Internal Server Error",
            "model": ErrorResponseModel
        }
    }
)
async def login_user(
    user: AuthData_API,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticates the user and returns an access token.
    
    - **username**: User's username
    - **password**: User's password
    """
    result = await auth_service.login_user(user)
    print(result)
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type="bearer",
        expires_in=result.get("expires_in", 3600),
        app_user_id=result["app_user_id"],
        username=user.app_user_name
    )


@auth_router.get(
    "/logout",
    response_model=LogoutResponse,
    summary="Logout User",
    description="Logs out the user by clearing the session.",
    responses={
        200: {
            "description": "Successfully logged out",
            "model": LogoutResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Successfully logged out",
                        "timestamp": "2024-01-01T12:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized - No active session",
            "model": ErrorResponseModel
        },
        500: {
            "description": "Internal Server Error",
            "model": ErrorResponseModel
        }
    }
)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logs out the user by clearing the session.
    """
    result = auth_service.logout_user(request)
    return LogoutResponse(
        success=result["success"],
        message=result["message"],
        timestamp=datetime.now()
    )