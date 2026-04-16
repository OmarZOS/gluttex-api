# services/auth_service.py (updated)
import json
import urllib
import secrets
import string
import httpx
from typing import Dict, Any, Optional
from fastapi import Request
from fastapi.responses import RedirectResponse
from core.api_models import AppUser_API, AuthData_API
from core.exception_handler import APIException
from core.messages import *
from constants import *
# from services.user_service import UserService
from features.auth_client import AuthClient

class AuthService:
    """Service for authentication and OAuth operations"""
    
    def __init__(self):
        # self.user_service = UserService()
        self.auth_client = AuthClient()
    
    @staticmethod
    def generate_random_password(length: int = 32) -> str:
        """Generate a strong random password for OAuth users."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def create_redirect_response(data: Dict[str, Any], error: Optional[str] = None) -> RedirectResponse:
        """Create a redirect response with encoded data or error."""
        if error:
            encoded_data = urllib.parse.quote(error)
            deep_link = f"gluttex://auth/callback?error={encoded_data}"
        else:
            json_data = json.dumps(data, default=str)
            encoded_data = urllib.parse.quote(json_data)
            deep_link = f"gluttex://auth/callback?data={encoded_data}"
        
        return RedirectResponse(url=deep_link)
    
    async def get_oauth_user_info(self, provider: str, token: dict) -> Optional[Dict[str, Any]]:
        """Fetch user information from OAuth provider."""
        
        if provider == "google":
            return await self._get_google_user_info(token)
        elif provider == "facebook":
            return await self._get_facebook_user_info(token)
        elif provider == "instagram":
            return await self._get_instagram_user_info(token)
        
        return None
    
    async def _get_google_user_info(self, token: dict) -> Optional[Dict[str, Any]]:
        """Fetch Google user info."""
        user_info = token.get("userinfo")
        if user_info:
            return {
                "id": user_info.get("sub"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "provider": "google"
            }
        
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
        return None
    
    async def _get_facebook_user_info(self, token: dict) -> Optional[Dict[str, Any]]:
        """Fetch Facebook user info."""
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
        return None
    
    async def _get_instagram_user_info(self, token: dict) -> Optional[Dict[str, Any]]:
        """Fetch Instagram user info."""
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
                    "email": None,
                    "name": data.get("username"),
                    "provider": "instagram"
                }
        return None
    
    async def handle_oauth_login(self, provider: str, request: Request, oauth_client) -> RedirectResponse:
        """Handle OAuth login redirect."""
        try:
            redirect_uri = f"{BASE_URL}/auth/{provider}"
            return await oauth_client.authorize_redirect(request, redirect_uri)
        except AttributeError:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=INTERFACE_ERROR,
                details=f"OAuth provider '{provider}' not properly configured"
            )
        except Exception as e:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=INTERFACE_ERROR,
                details=f"OAuth error: {str(e)}"
            )
    
    async def handle_oauth_callback(self, provider: str, request: Request, oauth_client) -> RedirectResponse:
        """Handle OAuth callback and process user authentication."""
        try:
            # Get access token from provider
            token = await oauth_client.authorize_access_token(request)
            
            # Get user info from provider
            user_info = await self.get_oauth_user_info(provider, token)
            if not user_info:
                return self.create_redirect_response({}, error="Failed to retrieve user information")
            
            # Store user in session
            request.session["user"] = user_info
            
            # Create or get user in your system
            user = await self.get_or_create_oauth_user(user_info, provider)
            
            # Prepare response data
            response_data = self.prepare_user_response(user, token)
            
            return self.create_redirect_response(response_data)
            
        except Exception as e:
            return self.create_redirect_response({}, error=str(e))
    
    async def get_or_create_oauth_user(self, user_info: Dict[str, Any], provider: str):
        """Get existing user or create a new one from OAuth data."""
        
        email = user_info.get("email")
        if not email and provider == "instagram":
            email = f"{user_info.get('id')}@instagram.user"
        
        # Check if user exists
        existing_user = self.user_service.get_user_by_email(email)
        
        if existing_user:
            return existing_user
        
        # Create new user
        app_user = AppUser_API(
            id_app_user=0,
            app_user_name=email,
            app_user_password=self.generate_random_password(),
            app_user_person_id=None,
            app_user_preferences=None,
            app_user_image_url=user_info.get("picture"),
            app_user_email=email,
            app_user_type_id=2  # Default user type for OAuth users
        )
        
        return await self.user_service.create_user(app_user, provider=provider)
    
    def prepare_user_response(self, user, token: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user response data."""
        
        # Convert user object to dictionary
        if hasattr(user, '__dict__'):
            user_dict = user.__dict__
            user_dict.pop('_sa_instance_state', None)
        elif hasattr(user, 'dict'):
            user_dict = user.dict()
        else:
            user_dict = dict(user)
        
        # Remove sensitive data
        user_dict.pop('app_user_password', None)
        
        return {
            "success": True,
            "user": user_dict,
            "token": token
        }
    
    async def login_user(self, auth_data: AuthData_API) -> Dict[str, Any]:
        """Authenticate user and return access token."""
        return await self.auth_client.login(
            username=auth_data.app_user_name,
            user_id=auth_data.id_app_user,
            password=auth_data.app_user_password
        )
    
    async def change_user_password(
        self,
        user_id: int,
        username: str,
        new_password: str,
        token: str
    ) -> Dict[str, Any]:
        """Change user password through auth server."""
        response = await self.auth_client.change_password(
            user_id=user_id,
            username=username,
            new_password=new_password,
            token=token
        )
        
        new_password_hash = response.get("hashed_password")
        
        # Update password in local database
        from core.api_models import AppUserUpdate_API
        user_update = AppUserUpdate_API(
            id_app_user=user_id,
            username=username,
            new_password=new_password
        )
        
        return self.user_service.update_user_password(user_update, new_password_hash)
    
    async def delete_user(self, user_id: int, username: str, password: str) -> None:
        """Delete user from auth server."""
        await self.auth_client.delete_user(user_id, username, password)
    
    def logout_user(self, request: Request) -> Dict[str, Any]:
        """Log out user by clearing session."""
        request.session.clear()
        return {"success": True, "message": "Logged out successfully"}