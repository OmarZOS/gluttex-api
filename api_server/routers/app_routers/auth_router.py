import json

import urllib
from features.user.user_fetch import fetch_user_by_name
from features.user.user_insert import insert_user
from constants import *
from core.messages import *
from fastapi import APIRouter, Request, Depends, status
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from core.exception_handler import APIException
from core.api_models import AppUser_API, AuthData_API
from features.user.user_net import login_for_access_token
import os
import httpx
import secrets
import string


auth_router = APIRouter()

# OAuth configuration
oauth = OAuth()

# Get base URL from environment or use default
# BASE_URL = os.getenv("BASE_URL", "http://localhost:9000/api")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:9070")





# Register Google OAuth with correct configuration
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

# Register Facebook OAuth
oauth.register(
    name="facebook",
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    authorize_url="https://www.facebook.com/v18.0/dialog/oauth",
    access_token_url="https://graph.facebook.com/v18.0/oauth/access_token",
    api_base_url="https://graph.facebook.com/v18.0/",
    client_kwargs={"scope": "email public_profile"},
)

# Register Instagram OAuth (Note: Instagram Basic Display API)
oauth.register(
    name="instagram",
    client_id=os.getenv("INSTAGRAM_CLIENT_ID"),
    client_secret=os.getenv("INSTAGRAM_CLIENT_SECRET"),
    authorize_url="https://api.instagram.com/oauth/authorize",
    access_token_url="https://api.instagram.com/oauth/access_token",
    client_kwargs={"scope": "user_profile user_media"},
)

SUPPORTED_PROVIDERS = {"google", "facebook", "instagram"}


def generate_random_password(length: int = 32) -> str:
    """Generate a strong random password for OAuth users."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_oauth_client(provider: str):
    """Get OAuth client by provider name."""
    return getattr(oauth, provider)
@auth_router.get("/login/{provider}")
async def login(provider: str, request: Request):
    """Redirects user to the OAuth provider's login page."""
    if provider not in SUPPORTED_PROVIDERS:
        raise APIException(
            status=status.HTTP_400_BAD_REQUEST,
            code=INTERFACE_ERROR,
            details=f"Unsupported provider: {provider}"
        )

    try:
        # Get OAuth client for provider
        client = get_oauth_client(provider)
        
        # Dynamic redirect URI based on provider
        redirect_uri = f"{BASE_URL}/auth/{provider}"
        return await client.authorize_redirect(request, redirect_uri)
    except AttributeError:
        raise APIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=INTERFACE_ERROR,
            details=f"OAuth provider '{provider}' not properly configured"
        )
    except Exception as e:
        raise APIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=INTERFACE_ERROR,
            details=f"OAuth error: {str(e)}"
        )


@auth_router.get("/auth/{provider}")
async def auth(provider: str, request: Request):
    """Handles the OAuth provider's callback and retrieves user info."""
    if provider not in SUPPORTED_PROVIDERS:
        raise APIException(
            status=status.HTTP_400_BAD_REQUEST,
            code=INTERFACE_ERROR,
            details=f"Unsupported provider: {provider}"
        )
    
    try:
        # Get OAuth client for provider
        client = get_oauth_client(provider)
        
        # Get access token from provider
        token = await client.authorize_access_token(request)
        
        # Get user info based on provider
        user_info = await get_user_info(provider, token)
        if not user_info:
            raise APIException(
                status=status.HTTP_401_UNAUTHORIZED,
                code=AUTH_UNAUTHORIZED,
                details="Failed to retrieve user information"
            )
        
        # Store user in session
        request.session["user"] = user_info
        
        user_data = user_info

        app_user = AppUser_API(
            id_app_user=0,
            app_user_name=user_data["email"],
            app_user_password=generate_random_password(),
            app_user_person_id=None,
            app_user_preferences=None,
            app_user_image_url=user_data.get("picture"),
            app_user_type_id=2
        )

        nutzern = fetch_user_by_name(user_data["email"])
        
        if nutzern == []:
            nutzer = await insert_user(app_user, provider=provider)
        else:
            nutzer = nutzern[0]
        
        # Generate YOUR app's JWT token (not the OAuth token!)
        # You need to implement this function to create a JWT for your app
        # app_jwt_token = create_jwt_token(nutzer)  # TODO: Implement this
        
        # Convert nutzer object to dictionary if it's not already
        # Adjust based on your actual user model
        if hasattr(nutzer, '__dict__'):
            user_dict = nutzer.__dict__
            # Remove SQLAlchemy internal state if present
            user_dict.pop('_sa_instance_state', None)
        elif hasattr(nutzer, 'dict'):
            user_dict = nutzer.dict()
        else:
            user_dict = dict(nutzer)
        
        # Remove sensitive data
        user_dict.pop('app_user_password', None)
        
        # Prepare response data
        response_data = {
            "success": True,
            "user": user_dict,
            "token": token  # Use YOUR JWT token, not OAuth token
        }
        
        # Encode and redirect to deep link
        json_data = json.dumps(response_data, default=str)  # default=str handles datetime objects
        encoded_data = urllib.parse.quote(json_data)
        
        deep_link = f"gluttex://auth/callback?data={encoded_data}"
        
        return RedirectResponse(url=deep_link)
        
    except AttributeError as e:
        error_message = urllib.parse.quote(f"Configuration error: {str(e)}")
        deep_link = f"gluttex://auth/callback?error={error_message}"
        return RedirectResponse(url=deep_link)
        
    except Exception as e:
        error_message = urllib.parse.quote(str(e))
        deep_link = f"gluttex://auth/callback?error={error_message}"
        return RedirectResponse(url=deep_link)


async def get_user_info(provider: str, token: dict) -> dict:
    """Fetch user information from OAuth provider."""
    
    if provider == "google":
        # Google provides userinfo in the token
        user_info = token.get("userinfo")
        # print(user_info)
        if user_info:
            
            return user_info
            # {
            #     "id": user_info.get("sub"),
            #     "email": user_info.get("email"),
            #     "name": user_info.get("name"),
            #     "picture": user_info.get("picture"),
            #     "provider": "google"
            # }
        # Fallback: fetch from userinfo endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "picture": data.get("picture"),
                    "provider": "google"
                }
    
    elif provider == "facebook":
        # Fetch Facebook user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/v18.0/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": token["access_token"]
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "email": data.get("email"),
                    "name": data.get("name"),
                    "picture": data.get("picture", {}).get("data", {}).get("url"),
                    "provider": "facebook"
                }
    
    elif provider == "instagram":
        # Fetch Instagram user info
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.instagram.com/me",
                params={
                    "fields": "id,username,account_type",
                    "access_token": token["access_token"]
                }
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "username": data.get("username"),
                    "email": None,  # Instagram doesn't provide email
                    "name": data.get("username"),
                    "provider": "instagram"
                }
    
    return None


@auth_router.post("/authentication/token")
async def login_user(user: AuthData_API):
    """Authenticates the user and returns an access token."""
    return await login_for_access_token(user)


@auth_router.get("/logout")
async def logout(request: Request):
    """Logs out the user by clearing the session."""
    request.session.clear()
    return {"success": True, "message": "Logged out successfully"}