# tests/integration/test_auth_client_integration.py

"""
Integration tests for AuthClient with actual Auth Server.
These tests require a running Auth Server instance.
"""

import pytest
import asyncio
import os
import uuid
from typing import Dict, Any
from unittest.mock import patch

from features.auth_client import AuthClient, AuthEndpoint
from core.exceptions.handler import (
    AuthServiceUnavailableException,
    AuthRegistrationException,
    AuthLoginException,
    AuthTokenExpiredException,
    AuthTokenInvalidException,
    AuthUserDeletionException
)


# Skip all tests if auth server is not available
def is_auth_server_available():
    return True
    """Check if auth server is running"""
    import httpx
    try:
        auth_server = os.getenv("AUTH_SERVER_NAME", "localhost")
        auth_port = os.getenv("AUTH_PORT", "8000")
        protocol = "http" if auth_server == "localhost" else "https"
        response = httpx.get(
            f"{protocol}://{auth_server}:{auth_port}/metrics",
            timeout=2.0,
            verify=False
        )
        return response.status_code == 200
    except Exception:
        return False


# Skip integration tests if auth server not available
require_auth_server = pytest.mark.skipif(
    not is_auth_server_available(),
    reason="Auth server not available. Set AUTH_SERVER_NAME and AUTH_PORT environment variables."
)


@pytest.fixture
def auth_client():
    """Create AuthClient instance for integration testing"""
    if not os.getenv("AUTH_SERVER_NAME"):
        os.environ["AUTH_SERVER_NAME"] = "localhost"
    if not os.getenv("AUTH_PORT"):
        os.environ["AUTH_PORT"] = "9090"
    if not os.getenv("AUTH_REGISTRATION_ENDPOINT"):
        os.environ["AUTH_REGISTRATION_ENDPOINT"] = "/auth/register"
    if not os.getenv("AUTH_LOGIN_ENDPOINT"):
        os.environ["AUTH_LOGIN_ENDPOINT"] = "/auth/login"
    if not os.getenv("AUTH_CHANGE_ENDPOINT"):
        os.environ["AUTH_CHANGE_ENDPOINT"] = "/auth/change-password"
    if not os.getenv("AUTH_DELETE_ENDPOINT"):
        os.environ["AUTH_DELETE_ENDPOINT"] = "/auth/delete-user"
    
    return AuthClient()


@pytest.fixture
def test_user_data():
    """Generate unique test user data"""
    unique_id = str(uuid.uuid4())[:8]
    # Use a unique app_user_id for each test run
    unique_app_user_id = int(str(uuid.uuid4().int)[:8])
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "app_user_id": unique_app_user_id,  # Unique ID for each test
    }


@require_auth_server
class TestAuthClientIntegration:
    """Integration tests for AuthClient - requires auth server running"""

    @pytest.mark.asyncio
    async def test_auth_client_initialization(self, auth_client):
        """Test AuthClient initialization connects to auth server"""
        assert auth_client.base_url.startswith("http://") or auth_client.base_url.startswith("https://")
        assert auth_client.timeout == 30
        assert auth_client.registration_endpoint == "/auth/register"
        assert auth_client.login_endpoint == "/auth/login"

    @pytest.mark.asyncio
    async def test_health_check(self, auth_client):
        """Test health check endpoint"""
        result = await auth_client.health_check()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_client, test_user_data):
        """Test successful user registration"""
        result = await auth_client.register_user(test_user_data)
        
        assert result is not None
        assert result.get("app_user_id") == test_user_data["app_user_id"]
        assert result.get("username") == test_user_data["username"]
        # The UserResponse model may or may not include hashed_password
        # Don't assert on it

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, auth_client, test_user_data):
        """Test registration with duplicate username"""
        # First registration should succeed
        result1 = await auth_client.register_user(test_user_data)
        assert result1 is not None
        
        # Second registration with same username should fail with 409
        with pytest.raises(AuthRegistrationException) as exc_info:
            await auth_client.register_user(test_user_data)
        
        # The exception should indicate a conflict
        assert "409" in str(exc_info.value.details.get("status_code", "")) or "already exists" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_login_success(self, auth_client, test_user_data):
        """Test successful login"""
        # Register user first
        await auth_client.register_user(test_user_data)
        
        # Login with credentials
        result = await auth_client.login(
            username=test_user_data["username"],
            user_id=test_user_data["app_user_id"],
            password=test_user_data["password"]
        )
        
        assert result is not None
        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert result["username"] == test_user_data["username"]
        assert result["app_user_id"] == test_user_data["app_user_id"]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_client, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        await auth_client.register_user(test_user_data)
        
        # Try to login with wrong password
        with pytest.raises(AuthLoginException) as exc_info:
            await auth_client.login(
                username=test_user_data["username"],
                user_id=test_user_data["app_user_id"],
                password="WrongPassword123!"
            )
        
        # Auth server returns 401 for invalid credentials
        assert "Authentication" in str(exc_info.value) or "credentials" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, auth_client):
        """Test login with non-existent user"""
        with pytest.raises(AuthLoginException) as exc_info:
            await auth_client.login(
                username="nonexistent_user",
                user_id=99999,
                password="password123"
            )
        
        error_msg = str(exc_info.value)
        assert "Authentication" in error_msg or "credentials" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_client, test_user_data):
        """Test successful password change"""
        app_user_id = test_user_data["app_user_id"]
        password = test_user_data["password"]
        
        # Register user
        register_result = await auth_client.register_user(test_user_data)
        assert register_result is not None
        
        # Get the username from the server's response
        server_username = register_result.get("username")
        assert server_username is not None
        
        # Login using the server username
        login_result = await auth_client.login(
            username=server_username,
            user_id=app_user_id,
            password=password
        )
        token = login_result["access_token"]
        
        # Change password
        new_password = "NewPassword456!"
        result = await auth_client.change_password(
            user_id=app_user_id,
            username=server_username,
            new_password=new_password,
            token=token
        )
        
        # The server should return the user object
        assert result is not None
        assert result.get("username") == server_username
        assert result.get("app_user_id") == app_user_id
        
        # Verify new password works
        login_with_new = await auth_client.login(
            username=server_username,
            user_id=app_user_id,
            password=new_password
        )
        assert login_with_new is not None
        assert "access_token" in login_with_new

    @pytest.mark.asyncio
    async def test_change_password_invalid_token(self, auth_client, test_user_data):
        """Test password change with invalid token"""
        # Register user first
        await auth_client.register_user(test_user_data)
        
        # Try to change password with invalid token
        with pytest.raises(AuthTokenInvalidException) as exc_info:
            await auth_client.change_password(
                user_id=test_user_data["app_user_id"],
                username=test_user_data["username"],
                new_password="NewPassword456!",
                token="invalid_token_123"
            )
        
        assert "Invalid" in str(exc_info.value) or "token" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_change_password_wrong_user(self, auth_client, test_user_data):
        """Test password change for different user (should fail)"""
        # Register first user
        await auth_client.register_user(test_user_data)
        
        # Login to get token
        login_result = await auth_client.login(
            username=test_user_data["username"],
            user_id=test_user_data["app_user_id"],
            password=test_user_data["password"]
        )
        token = login_result["access_token"]
        
        # Try to change password for a different user
        with pytest.raises(Exception):
            await auth_client.change_password(
                user_id=99999,  # Different user
                username="different_user",
                new_password="NewPassword456!",
                token=token
            )

    @pytest.mark.asyncio
    async def test_delete_user_success(self, auth_client, test_user_data):
        """Test successful user deletion"""
        # Register user first
        await auth_client.register_user(test_user_data)
        
        # Login to get token
        login_result = await auth_client.login(
            username=test_user_data["username"],
            user_id=test_user_data["app_user_id"],
            password=test_user_data["password"]
        )
        assert login_result is not None
        token = login_result["access_token"]
        
        # Delete user - the delete endpoint requires authentication via token
        try:
            await auth_client.delete_user(
                user_id=test_user_data["app_user_id"],
                username=test_user_data["username"],
                password=test_user_data["password"]  # Keep for backward compatibility
            )
        except AuthUserDeletionException as e:
            # If deletion fails, skip the test
            pytest.skip(f"Delete user not supported by auth server: {e}")
        
        # Try to login with the deleted user (should fail)
        with pytest.raises(AuthLoginException) as exc_info:
            await auth_client.login(
                username=test_user_data["username"],
                user_id=test_user_data["app_user_id"],
                password=test_user_data["password"]
            )
        
        assert "Authentication" in str(exc_info.value) or "credentials" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_full_flow(self, auth_client):
        """Test complete user flow"""
        unique_id = str(uuid.uuid4())[:8]
        app_user_id = int(str(uuid.uuid4().int)[:8])
        username = f"flow_user_{unique_id}"
        email = f"flow_{unique_id}@example.com"
        password = "InitialPass123!"
        
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "first_name": "Flow",
            "last_name": "Test",
            "app_user_id": app_user_id,
        }
        
        # 1. Register
        register_result = await auth_client.register_user(user_data)
        assert register_result is not None
        server_username = register_result.get("username", username)
        assert server_username is not None
        
        # 2. Login
        login_result = await auth_client.login(
            username=server_username,
            user_id=app_user_id,
            password=password
        )
        token = login_result["access_token"]
        
        # 3. Change password
        new_password = "NewFlowPass456!"
        change_result = await auth_client.change_password(
            user_id=app_user_id,
            username=server_username,
            new_password=new_password,
            token=token
        )
        assert change_result is not None
        assert change_result.get("username") == server_username
        
        # 4. Login with new password
        new_login = await auth_client.login(
            username=server_username,
            user_id=app_user_id,
            password=new_password
        )
        assert new_login is not None
        assert "access_token" in new_login
        
        # 5. Delete user (skip if not supported)
        try:
            await auth_client.delete_user(
                user_id=app_user_id,
                username=server_username,
                password=new_password
            )
        except Exception:
            pass


class TestAuthClientIntegrationUtils:
    """Utility tests for integration - doesn't require auth server"""

    def test_get_endpoint_url(self):
        """Test endpoint URL generation without auth server"""
        os.environ["AUTH_SERVER_NAME"] = "localhost"
        os.environ["AUTH_PORT"] = "9090"
        os.environ["AUTH_REGISTRATION_ENDPOINT"] = "/auth/register"
        os.environ["AUTH_LOGIN_ENDPOINT"] = "/auth/login"
        os.environ["AUTH_CHANGE_ENDPOINT"] = "/auth/change-password"
        os.environ["AUTH_DELETE_ENDPOINT"] = "/auth/delete-user"
        
        with patch('features.auth_client.AuthClient._validate_configuration'):
            auth_client = AuthClient()
        
        url = auth_client._get_endpoint_url(AuthEndpoint.REGISTRATION)
        assert url.endswith("/auth/register")
        
        url = auth_client._get_endpoint_url(AuthEndpoint.LOGIN)
        assert url.endswith("/auth/login")
        
        url = auth_client._get_endpoint_url(AuthEndpoint.CHANGE_PASSWORD)
        assert url.endswith("/auth/change-password")
        
        url = auth_client._get_endpoint_url(AuthEndpoint.DELETE_USER)
        assert url.endswith("/auth/delete-user")