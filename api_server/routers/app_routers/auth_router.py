# routers/app_routers/auth_router.py
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from core.exception_handler import APIException
from core.messages import *
from core.api_models import AuthData_API
from services.auth_service import AuthService
from services.oauth_config_service import OAuthConfigService

auth_router = APIRouter()

# Dependency injection
def get_auth_service() -> AuthService:
    return AuthService()

def get_oauth_config() -> OAuthConfigService:
    return OAuthConfigService()


@auth_router.get("/login/{provider}")
async def login(
    provider: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    oauth_config: OAuthConfigService = Depends(get_oauth_config)
):
    """
    Redirects user to the OAuth provider's login page.
    """
    if not oauth_config.is_supported_provider(provider):
        raise APIException(
            status=status.HTTP_400_BAD_REQUEST,
            code=INTERFACE_ERROR,
            details=f"Unsupported provider: {provider}"
        )
    
    oauth_client = oauth_config.get_client(provider)
    if not oauth_client:
        raise APIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=INTERFACE_ERROR,
            details=f"OAuth provider '{provider}' not properly configured"
        )
    
    return await auth_service.handle_oauth_login(provider, request, oauth_client)


@auth_router.get("/auth/{provider}")
async def auth_callback(
    provider: str,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    oauth_config: OAuthConfigService = Depends(get_oauth_config)
):
    """
    Handles the OAuth provider's callback and retrieves user info.
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


@auth_router.post("/authentication/token")
async def login_user(
    user: AuthData_API,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticates the user and returns an access token.
    """
    return await auth_service.login_user(user)


@auth_router.get("/logout")
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logs out the user by clearing the session.
    """
    return auth_service.logout_user(request)