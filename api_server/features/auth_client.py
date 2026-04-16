# clients/auth_client.py
import json
from typing import Dict, Any
from communication.communication_broker import send_delete_request, send_post_request, send_put_request
from constants import *
from core.exception_handler import APIException
from core.messages import *

class AuthClient:
    """Client for external authentication server API calls"""
    
    def __init__(self):
        self.base_url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}"
        self.registration_endpoint = AUTH_REGISTRATION_ENDPOINT
        self.login_endpoint = AUTH_LOGIN_ENDPOINT
        self.change_password_endpoint = AUTH_CHANGE_ENDPOINT
        self.delete_user_endpoint = AUTH_DELETE_ENDPOINT
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user with the authentication server.
        
        Args:
            user_data: User registration data
            
        Returns:
            Response from auth server
            
        Raises:
            APIException: If registration fails
        """
        url = f"{self.base_url}{self.registration_endpoint}"
        
        try:
            response = await send_post_request(url, json_data=user_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise APIException(
                status=HTTP_410_GONE,
                code=USER_AUTH_CREATION_FAILED,
                details=str(e)
            )
    
    async def login(self, username: str, user_id: int, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and retrieve an access token.
        
        Args:
            username: User's username
            user_id: User's ID
            password: User's password
            
        Returns:
            Authentication response with token
            
        Raises:
            APIException: If login fails
        """
        form_data = {
            "username": username,
            "app_user_id": user_id,
            "password": password,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = f"{self.base_url}{self.login_endpoint}"
        
        try:
            response = await send_post_request(url, payload_data=form_data, flags=headers)
            return response.json()
        except APIException as e:
            raise APIException(
                status=e.status,
                code=e.code,
                message=e.message
            )
    
    async def change_password(
        self,
        user_id: int,
        username: str,
        new_password: str,
        token: str
    ) -> Dict[str, Any]:
        """
        Update a user's password through the authentication server.
        
        Args:
            user_id: User's ID
            username: User's username
            new_password: New password
            token: Authentication token
            
        Returns:
            Response with new password hash
            
        Raises:
            APIException: If password change fails
        """
        user_update = {
            "app_user_id": user_id,
            "username": username,
            "new_username": username,
            "new_password": new_password
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{self.base_url}{self.change_password_endpoint}"
        
        try:
            response = await send_post_request(url, json_data=user_update, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise APIException(
                status=HTTP_502_BAD_GATEWAY,
                code=USER_NET_FAILED,
                details=str(e)
            )
    
    async def delete_user(self, user_id: int, username: str, password: str) -> None:
        """
        Delete a user through the authentication server.
        
        Args:
            user_id: User's ID
            username: User's username
            password: User's password
            
        Raises:
            APIException: If deletion fails
        """
        user_update = {
            "app_user_id": user_id,
            "username": username,
            "new_password": password
        }
        
        url = f"{self.base_url}{self.delete_user_endpoint}"
        
        try:
            response = await send_delete_request(url, input_data=user_update)
            response.raise_for_status()
        except Exception as e:
            raise APIException(
                status=HTTP_502_BAD_GATEWAY,
                code=USER_DELETE_FAILED,
                details=str(e)
            )