# tests/features/auth/test_auth_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import json
import os

from features.auth_client import AuthClient, AuthEndpoint
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


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for AuthClient"""
    monkeypatch.setattr('features.auth_client.AUTH_SERVER_NAME', 'localhost')
    monkeypatch.setattr('features.auth_client.AUTH_PORT', '9090')
    monkeypatch.setattr('features.auth_client.AUTH_REGISTRATION_ENDPOINT', '/auth/register')
    monkeypatch.setattr('features.auth_client.AUTH_LOGIN_ENDPOINT', '/auth/login')
    monkeypatch.setattr('features.auth_client.AUTH_CHANGE_ENDPOINT', '/auth/change-password')
    monkeypatch.setattr('features.auth_client.AUTH_DELETE_ENDPOINT', '/auth/delete-user')
    return monkeypatch


@pytest.fixture
def auth_client(mock_env_vars):
    """Create AuthClient instance with mocked dependencies"""
    with patch('features.auth_client.send_post_request') as mock_post, \
         patch('features.auth_client.send_put_request') as mock_put, \
         patch('features.auth_client.send_delete_request') as mock_delete:
        
        client = AuthClient()
        client.mock_post = mock_post
        client.mock_put = mock_put
        client.mock_delete = mock_delete
        
        yield client


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "username": "testuser",
        "app_user_id": 123,
        "password": "TestPassword123!"
    }


@pytest.fixture
def sample_login_response():
    """Sample login response from auth server"""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "expires_in": 3600,
        "expires_at": "2024-01-01T13:00:00Z",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "iat": "2024-01-01T12:00:00Z",
        "iss": "localhost"
    }


class MockResponse:
    """Mock HTTP response"""
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class TestAuthClient:
    """Test suite for AuthClient"""

    def test_init_success(self, mock_env_vars):
        """Test successful AuthClient initialization"""
        with patch('features.auth_client.send_post_request'):
            client = AuthClient()
            assert client.base_url == "http://localhost:9090"
            assert client.registration_endpoint == "/auth/register"
            assert client.timeout == 30

    def test_init_missing_server_name(self, monkeypatch):
        """Test initialization with missing server name"""
        monkeypatch.setattr('features.auth_client.AUTH_SERVER_NAME', '')
        monkeypatch.setattr('features.auth_client.AUTH_PORT', '9090')
        
        with patch('features.auth_client.send_post_request'):
            with pytest.raises(AuthServiceUnavailableException) as exc_info:
                AuthClient()
            
            assert exc_info.value.service == "authentication"
            assert "Authentication service is unavailable" in str(exc_info.value)

    def test_init_missing_port(self, monkeypatch):
        """Test initialization with missing port"""
        monkeypatch.setattr('features.auth_client.AUTH_SERVER_NAME', 'localhost')
        monkeypatch.setattr('features.auth_client.AUTH_PORT', '')
        
        with patch('features.auth_client.send_post_request'):
            with pytest.raises(AuthServiceUnavailableException) as exc_info:
                AuthClient()
            
            assert exc_info.value.service == "authentication"
            assert "Authentication service is unavailable" in str(exc_info.value)

    def test_get_endpoint_url(self, auth_client):
        """Test endpoint URL generation"""
        url = auth_client._get_endpoint_url(AuthEndpoint.REGISTRATION)
        assert url == "http://localhost:9090/auth/register"
        
        url = auth_client._get_endpoint_url(AuthEndpoint.LOGIN)
        assert url == "http://localhost:9090/auth/login"
        
        url = auth_client._get_endpoint_url(AuthEndpoint.CHANGE_PASSWORD)
        assert url == "http://localhost:9090/auth/change-password"
        
        url = auth_client._get_endpoint_url(AuthEndpoint.DELETE_USER)
        assert url == "http://localhost:9090/auth/delete-user"

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_client, sample_user_data):
        """Test successful user registration"""
        mock_response = MockResponse(200, {
            "hashed_password": "hashed_password_123",
            "user_id": 123
        })
        auth_client.mock_post.return_value = mock_response
        
        result = await auth_client.register_user(sample_user_data)
        
        assert result["hashed_password"] == "hashed_password_123"
        auth_client.mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_conflict(self, auth_client, sample_user_data):
        """Test registration with existing user (409 Conflict)"""
        mock_response = MockResponse(409, {"message": "User already exists"})
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthRegistrationException) as exc_info:
            await auth_client.register_user(sample_user_data)
        
        assert "Failed to register user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_user_bad_request(self, auth_client, sample_user_data):
        """Test registration with invalid data (400 Bad Request)"""
        mock_response = MockResponse(400, {"message": "Invalid data"})
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthRegistrationException) as exc_info:
            await auth_client.register_user(sample_user_data)
        
        assert "Failed to register user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_user_timeout(self, auth_client, sample_user_data):
        """Test registration timeout"""
        auth_client.mock_post.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(AuthNetworkException) as exc_info:
            await auth_client.register_user(sample_user_data)
        
        assert "network error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_register_user_connection_error(self, auth_client, sample_user_data):
        """Test registration connection error"""
        auth_client.mock_post.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(AuthServiceUnavailableException) as exc_info:
            await auth_client.register_user(sample_user_data)
        
        assert "unavailable" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_login_success(self, auth_client, sample_login_response):
        """Test successful login"""
        mock_response = MockResponse(200, sample_login_response)
        auth_client.mock_post.return_value = mock_response
        
        result = await auth_client.login("testuser", 123, "TestPassword123!")
        
        assert result["access_token"] == "eyJhbGciOiJIUzI1NiIs..."
        assert result["app_user_id"] == 123
        assert result["username"] == "testuser"
        auth_client.mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_unauthorized(self, auth_client):
        """Test login with invalid credentials (401 Unauthorized)"""
        mock_response = MockResponse(401, {
            "message": "Invalid credentials",
            "error_code": "INVALID_CREDENTIALS"
        })
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthLoginException) as exc_info:
            await auth_client.login("testuser", 123, "wrongpassword")
        
        assert "Failed to authenticate" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_login_server_error(self, auth_client):
        """Test login with server error (500 Internal Server Error)"""
        mock_response = MockResponse(500)
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthLoginException) as exc_info:
            await auth_client.login("testuser", 123, "password")
        
        assert "Failed to authenticate" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_change_password_success(self, auth_client):
        """Test successful password change"""
        mock_response = MockResponse(200, {
            "hashed_password": "new_hashed_password_456"
        })
        auth_client.mock_post.return_value = mock_response
        
        result = await auth_client.change_password(
            user_id=123,
            username="testuser",
            new_password="NewPassword456!",
            token="valid_token"
        )
        
        assert result["hashed_password"] == "new_hashed_password_456"
        auth_client.mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_token_expired(self, auth_client):
        """Test password change with expired token (401 Unauthorized)"""
        mock_response = MockResponse(401, {"detail": "Token has expired"})
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthTokenExpiredException) as exc_info:
            await auth_client.change_password(
                user_id=123,
                username="testuser",
                new_password="NewPassword456!",
                token="expired_token"
            )
        
        assert "expired" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_change_password_invalid_token(self, auth_client):
        """Test password change with invalid token (401 Unauthorized)"""
        mock_response = MockResponse(401, {"detail": "Invalid token"})
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthTokenInvalidException) as exc_info:
            await auth_client.change_password(
                user_id=123,
                username="testuser",
                new_password="NewPassword456!",
                token="invalid_token"
            )
        
        assert "Invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_change_password_forbidden(self, auth_client):
        """Test password change without permission (403 Forbidden)"""
        mock_response = MockResponse(403)
        auth_client.mock_post.return_value = mock_response
        
        with pytest.raises(AuthPasswordChangeException) as exc_info:
            await auth_client.change_password(
                user_id=123,
                username="testuser",
                new_password="NewPassword456!",
                token="valid_token"
            )
        
        assert "Failed to change password" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, auth_client):
        """Test successful user deletion"""
        mock_response = MockResponse(204)
        auth_client.mock_delete.return_value = mock_response
        
        await auth_client.delete_user(123, "testuser", "TestPassword123!")
        
        auth_client.mock_delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, auth_client):
        """Test deletion of non-existent user (404 Not Found)"""
        mock_response = MockResponse(404, {"message": "User not found"})
        auth_client.mock_delete.return_value = mock_response
        
        with pytest.raises(AuthUserDeletionException) as exc_info:
            await auth_client.delete_user(999, "nonexistent", "password")
        
        assert "Failed to delete user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_invalid_credentials(self, auth_client):
        """Test deletion with invalid credentials (401 Unauthorized)"""
        mock_response = MockResponse(401)
        auth_client.mock_delete.return_value = mock_response
        
        with pytest.raises(AuthUserDeletionException) as exc_info:
            await auth_client.delete_user(123, "testuser", "wrongpassword")
        
        assert "Failed to delete user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_timeout(self, auth_client):
        """Test deletion timeout"""
        auth_client.mock_delete.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(AuthNetworkException) as exc_info:
            await auth_client.delete_user(123, "testuser", "password")
        
        assert "network error" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_health_check_success(self, auth_client):
        """Test successful health check"""
        mock_response = MockResponse(200)
        auth_client.mock_post.return_value = mock_response
        
        result = await auth_client.health_check()
        
        assert result is True
        auth_client.mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure(self, auth_client):
        """Test health check failure"""
        auth_client.mock_post.side_effect = Exception("Connection refused")
        
        result = await auth_client.health_check()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_register_user_network_error(self, auth_client, sample_user_data):
        """Test registration network error"""
        auth_client.mock_post.side_effect = Exception("Network error")
        
        with pytest.raises(AuthRegistrationException) as exc_info:
            await auth_client.register_user(sample_user_data)
        
        assert "Failed to register user" in str(exc_info.value)


class TestAuthEndpoint:
    """Test AuthEndpoint enum"""

    def test_auth_endpoint_values(self):
        """Test AuthEndpoint enum values"""
        assert AuthEndpoint.REGISTRATION.value == "/auth/register"
        assert AuthEndpoint.LOGIN.value == "/auth/login"
        assert AuthEndpoint.CHANGE_PASSWORD.value == "/auth/change-password"
        assert AuthEndpoint.DELETE_USER.value == "/auth/delete-user"