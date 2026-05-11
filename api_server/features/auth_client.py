# clients/auth_client.py
"""
Client for external authentication server API calls.
Handles all communication with the authentication microservice.
"""

import json
import logging
from typing import Dict, Any, Optional
from enum import Enum

from communication.communication_broker import send_delete_request, send_post_request, send_put_request
from constants import (
    AUTH_SERVER_NAME,
    AUTH_PORT,
    AUTH_REGISTRATION_ENDPOINT,
    AUTH_LOGIN_ENDPOINT,
    AUTH_CHANGE_ENDPOINT,
    AUTH_DELETE_ENDPOINT
)
from core.exceptions.handler import (
    AuthServiceUnavailableException,
    AuthRegistrationException,
    AuthLoginException,
    AuthPasswordChangeException,
    AuthUserDeletionException,
    AuthTokenExpiredException,
    AuthTokenInvalidException,
    AuthNetworkException
)

logger = logging.getLogger(__name__)


class AuthEndpoint(str, Enum):
    """Authentication service endpoints"""
    REGISTRATION = "registration"
    LOGIN = "login"
    CHANGE_PASSWORD = "change_password"
    DELETE_USER = "delete_user"


class AuthClient:
    """Client for external authentication server API calls"""
    
    def __init__(self, timeout: int = 30):
        """
        Initialize AuthClient.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.base_url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}"
        self.registration_endpoint = AUTH_REGISTRATION_ENDPOINT
        self.login_endpoint = AUTH_LOGIN_ENDPOINT
        self.change_password_endpoint = AUTH_CHANGE_ENDPOINT
        self.delete_user_endpoint = AUTH_DELETE_ENDPOINT
        self.timeout = timeout
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate that required configuration is present"""
        if not AUTH_SERVER_NAME:
            logger.error("AUTH_SERVER_NAME not configured")
            raise AuthServiceUnavailableException(
                service="authentication",
                error="Server name not configured"
            )
        
        if not AUTH_PORT:
            logger.error("AUTH_PORT not configured")
            raise AuthServiceUnavailableException(
                service="authentication",
                error="Server port not configured"
            )
        
        logger.info(f"AuthClient initialized with base URL: {self.base_url}")
    
    def _get_endpoint_url(self, endpoint: AuthEndpoint) -> str:
        """Get full URL for an auth endpoint"""
        endpoint_map = {
            AuthEndpoint.REGISTRATION: self.registration_endpoint,
            AuthEndpoint.LOGIN: self.login_endpoint,
            AuthEndpoint.CHANGE_PASSWORD: self.change_password_endpoint,
            AuthEndpoint.DELETE_USER: self.delete_user_endpoint
        }
        
        endpoint_path = endpoint_map.get(endpoint)
        if not endpoint_path:
            raise AuthServiceUnavailableException(
                service="authentication",
                error=f"Unknown endpoint: {endpoint}"
            )
        
        return f"{self.base_url}{endpoint_path}"
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user with the authentication server.
        
        Args:
            user_data: User registration data containing:
                - username: User's username
                - app_user_id: User's ID from main database
                - password: User's password
                
        Returns:
            Response from auth server with hashed password
            
        Raises:
            AuthRegistrationException: If registration fails
            AuthServiceUnavailableException: If auth service is unavailable
            AuthNetworkException: If network error occurs
        """
        url = self._get_endpoint_url(AuthEndpoint.REGISTRATION)
        username = user_data.get("username")
        
        logger.info(f"Registering user '{username}' with authentication service")
        
        try:
            response = await send_post_request(
                url, 
                json_data=user_data,
                # timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully registered user '{username}'")
            return result
            
        except TimeoutError as e:
            logger.error(f"Timeout registering user '{username}': {e}")
            raise AuthNetworkException(
                error=f"Request timeout: {str(e)}",
                endpoint="registration",
                details={"username": username, "timeout": self.timeout}
            )
        
        except ConnectionError as e:
            logger.error(f"Connection error registering user '{username}': {e}")
            raise AuthServiceUnavailableException(
                service="authentication",
                error=f"Connection failed: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Failed to register user '{username}': {e}")
            
            # Check for specific HTTP status codes in response
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                
                if status_code == 409:
                    # Conflict - user already exists
                    raise AuthRegistrationException(
                        error="User already exists",
                        username=username,
                        details={"status_code": status_code}
                    )
                elif status_code == 400:
                    # Bad request - invalid data
                    raise AuthRegistrationException(
                        error="Invalid registration data",
                        username=username,
                        details={"status_code": status_code}
                    )
            
            raise AuthRegistrationException(
                error=str(e),
                username=username,
                details={"endpoint": "registration"}
            )
    
    async def login(self, username: str, user_id: int, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and retrieve an access token.
        
        Args:
            username: User's username
            user_id: User's ID from main database
            password: User's password
            
        Returns:
            Authentication response with token and hashed password
            
        Raises:
            AuthLoginException: If login fails
            AuthServiceUnavailableException: If auth service is unavailable
        """
        url = self._get_endpoint_url(AuthEndpoint.LOGIN)
        
        form_data = {
            "username": username,
            "app_user_id": user_id,
            "password": password,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        logger.info(f"Authenticating user '{username}'")
        
        try:
            response = await send_post_request(
                url,
                payload_data=form_data,
                flags=headers,
                # timeout=self.timeout
            )
            
            result = response.json()
            
            # Check for error response
            if response.status_code != 200:
                error_msg = result.get("detail", "Authentication failed")
                raise AuthLoginException(
                    error=error_msg,
                    username=username,
                    details={"status_code": response.status_code}
                )
            
            logger.info(f"Successfully authenticated user '{username}'")
            return result
            
        except TimeoutError as e:
            logger.error(f"Timeout during login for '{username}': {e}")
            raise AuthNetworkException(
                error=f"Login timeout: {str(e)}",
                endpoint="login",
                details={"username": username}
            )
        
        except ConnectionError as e:
            logger.error(f"Connection error during login for '{username}': {e}")
            raise AuthServiceUnavailableException(
                service="authentication",
                error=f"Connection failed: {str(e)}"
            )
        
        except AuthLoginException:
            # Re-raise as-is
            raise
        
        except Exception as e:
            logger.error(f"Login failed for '{username}': {e}")
            raise AuthLoginException(
                error=str(e),
                username=username,
                details={"endpoint": "login"}
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
            user_id: User's ID from main database
            username: User's username
            new_password: New password to set
            token: Authentication token for authorization
            
        Returns:
            Response with new password hash
            
        Raises:
            AuthPasswordChangeException: If password change fails
            AuthTokenExpiredException: If token has expired
            AuthTokenInvalidException: If token is invalid
            AuthServiceUnavailableException: If auth service is unavailable
        """
        url = self._get_endpoint_url(AuthEndpoint.CHANGE_PASSWORD)
        
        user_update = {
            "app_user_id": user_id,
            "username": username,
            "new_username": username,
            "new_password": new_password
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        logger.info(f"Changing password for user '{username}'")
        
        try:
            response = await send_post_request(
                url,
                json_data=user_update,
                headers=headers,
                # timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully changed password for user '{username}'")
            return result
            
        except TimeoutError as e:
            logger.error(f"Timeout changing password for '{username}': {e}")
            raise AuthNetworkException(
                error=f"Password change timeout: {str(e)}",
                endpoint="change_password",
                details={"username": username}
            )
        
        except ConnectionError as e:
            logger.error(f"Connection error changing password for '{username}': {e}")
            raise AuthServiceUnavailableException(
                service="authentication",
                error=f"Connection failed: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Password change failed for user '{username}': {e}")
            
            # Check for token-related errors
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                
                if status_code == 401:
                    # Unauthorized - token issue
                    try:
                        error_data = e.response.json()
                        error_detail = error_data.get("detail", "")
                        
                        if "expired" in error_detail.lower():
                            raise AuthTokenExpiredException(token=token)
                        else:
                            raise AuthTokenInvalidException(error=error_detail)
                    except:
                        raise AuthTokenInvalidException(error="Invalid token")
                
                elif status_code == 403:
                    raise AuthPasswordChangeException(
                        error="Not authorized to change this user's password",
                        user_id=user_id,
                        username=username,
                        details={"status_code": status_code}
                    )
            
            raise AuthPasswordChangeException(
                error=str(e),
                user_id=user_id,
                username=username,
                details={"endpoint": "change_password"}
            )
    
    async def delete_user(self, user_id: int, username: str, password: str) -> None:
        """
        Delete a user through the authentication server.
        
        Args:
            user_id: User's ID from main database
            username: User's username
            password: User's password for verification
            
        Raises:
            AuthUserDeletionException: If deletion fails
            AuthServiceUnavailableException: If auth service is unavailable
        """
        url = self._get_endpoint_url(AuthEndpoint.DELETE_USER)
        
        user_data = {
            "app_user_id": user_id,
            "username": username,
            "new_password": password  # Used as verification
        }
        
        logger.info(f"Deleting user '{username}' from authentication service")
        
        try:
            response = await send_delete_request(
                url,
                input_data=user_data,
                # timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info(f"Successfully deleted user '{username}'")
            
        except TimeoutError as e:
            logger.error(f"Timeout deleting user '{username}': {e}")
            raise AuthNetworkException(
                error=f"User deletion timeout: {str(e)}",
                endpoint="delete_user",
                details={"username": username}
            )
        
        except ConnectionError as e:
            logger.error(f"Connection error deleting user '{username}': {e}")
            raise AuthServiceUnavailableException(
                service="authentication",
                error=f"Connection failed: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"Failed to delete user '{username}': {e}")
            
            # Check for specific HTTP status codes
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                
                if status_code == 404:
                    raise AuthUserDeletionException(
                        error="User not found in authentication service",
                        user_id=user_id,
                        username=username,
                        details={"status_code": status_code}
                    )
                elif status_code == 401:
                    raise AuthUserDeletionException(
                        error="Invalid credentials for user deletion",
                        user_id=user_id,
                        username=username,
                        details={"status_code": status_code}
                    )
            
            raise AuthUserDeletionException(
                error=str(e),
                user_id=user_id,
                username=username,
                details={"endpoint": "delete_user"}
            )
    
    async def health_check(self) -> bool:
        """
        Check if authentication service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try a simple connection test
            url = f"{self.base_url}/health"  # Assuming health endpoint exists
            response = await send_post_request(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Auth service health check failed: {e}")
            return False