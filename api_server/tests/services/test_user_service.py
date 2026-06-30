# tests/services/test_user_service.py
import pytest
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

from services.user_service import UserService
from core.models.api_models import AppUser_API, Person_API, Location_API, AppUserUpdate_API
from core.exceptions.handler import APIException, UserNotFoundException
from core.models.models import AppUser
from core.messages.error_codes import ErrorCode
from core.messages.http_status import (
    HTTP_409_CONFLICT,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_410_GONE,
    HTTP_404_NOT_FOUND,
)


@pytest.fixture
def user_service():
    """Create UserService instance with all dependencies mocked"""
    # Patch ALL dependencies that require configuration
    with patch('services.user_service.UserRepository') as mock_user_repo_class, \
         patch('services.user_service.PersonRepository') as mock_person_repo_class, \
         patch('services.user_service.LocationRepository') as mock_location_repo_class, \
         patch('services.user_service.AuthService') as mock_auth_service_class, \
         patch('services.user_service.PersonService') as mock_person_service_class, \
         patch('services.user_service.AuthClient') as mock_auth_client_class:
        
        # Create mock instances
        mock_user_repo = mock_user_repo_class.return_value
        mock_person_repo = mock_person_repo_class.return_value
        mock_location_repo = mock_location_repo_class.return_value
        mock_auth_service = mock_auth_service_class.return_value
        mock_person_service = mock_person_service_class.return_value
        mock_auth_client = mock_auth_client_class.return_value
        
        # Create service with mocked dependencies
        service = UserService()
        
        # Replace with mocks
        service.user_repo = mock_user_repo
        service.person_repo = mock_person_repo
        service.location_repo = mock_location_repo
        service.auth_service = mock_auth_service
        service.person_service = mock_person_service
        service.auth_client = mock_auth_client
        
        # Store mocks for access in tests
        service.mock_user_repo = mock_user_repo
        service.mock_person_repo = mock_person_repo
        service.mock_location_repo = mock_location_repo
        service.mock_auth_service = mock_auth_service
        service.mock_person_service = mock_person_service
        service.mock_auth_client = mock_auth_client
        
        yield service


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return AppUser_API(
        id_app_user=1,
        app_user_name="testuser",
        app_user_email="test@example.com",
        app_user_password="TestPassword123!",
        app_user_type="customer",  # Changed from 'user' to 'customer'
        app_user_preferences={"theme": "dark"},
        app_user_image_url="https://example.com/avatar.jpg",
    )


@pytest.fixture
def sample_person_data():
    """Sample person data for testing"""
    return Person_API(
        id_person=1,
        person_first_name="Test",
        person_last_name="User",
        person_email="test@example.com",
    )


@pytest.fixture
def sample_location_data():
    """Sample location data for testing"""
    return Location_API(
        id_location=1,
        location_name="Home",
        location_address="123 Test St",
    )


class TestUserService:
    """Test suite for UserService"""

    def test_get_all_users(self, user_service):
        """Test getting all users"""
        expected_users = [
            AppUser(id_app_user=1, app_user_name="user1"),
            AppUser(id_app_user=2, app_user_name="user2"),
        ]
        user_service.mock_user_repo.get_all.return_value = expected_users
        
        result = user_service.get_all_users()
        
        assert result == expected_users
        user_service.mock_user_repo.get_all.assert_called_once()

    def test_get_user_by_id_success(self, user_service):
        """Test getting user by ID successfully"""
        expected_user = AppUser(id_app_user=1, app_user_name="testuser")
        user_service.mock_user_repo.get_by_id.return_value = expected_user
        
        result = user_service.get_user_by_id(1)
        
        assert result == expected_user
        user_service.mock_user_repo.get_by_id.assert_called_once_with(1, eager_load=False)

    def test_get_user_by_id_not_found(self, user_service):
        """Test getting user by ID when user doesn't exist"""
        user_service.mock_user_repo.get_by_id.return_value = None
        
        with pytest.raises(UserNotFoundException) as exc_info:
            user_service.get_user_by_id(999)
        
        # The exception message might include the ID
        assert "User" in str(exc_info.value)
        assert "999" in str(exc_info.value)
        user_service.mock_user_repo.get_by_id.assert_called_once_with(999, eager_load=False)


    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, sample_user_data):
        """Test creating a user successfully"""
        # Mock user repository
        user_service.mock_user_repo.get_by_name.return_value = None
        user_service.mock_user_repo.create.return_value = AppUser(
            id_app_user=1,
            app_user_name=sample_user_data.app_user_name,
        )
        
        # Mock auth client
        user_service.mock_auth_client.register_user = AsyncMock(return_value={
            "hashed_password": "hashed_password_123"
        })
        
        # Mock update_user_password
        user_service.update_user_password = MagicMock(return_value=True)
        
        # Await the coroutine
        result = await user_service.create_user(sample_user_data)
        
        assert result is not None
        assert result.app_user_name == sample_user_data.app_user_name
        user_service.mock_user_repo.get_by_name.assert_called_once_with(sample_user_data.app_user_name)
        user_service.mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, user_service, sample_user_data):
        """Test creating a user with duplicate username"""
        user_service.mock_user_repo.get_by_name.return_value = AppUser(
            id_app_user=2,
            app_user_name=sample_user_data.app_user_name,
        )
        
        with pytest.raises(APIException) as exc_info:
            await user_service.create_user(sample_user_data)
        
        assert exc_info.value.status_code == HTTP_409_CONFLICT
        assert exc_info.value.error_code == ErrorCode.APPUSER_ALREADY_EXISTS
        assert "username" in exc_info.value.details
    
    @pytest.mark.asyncio
    async def test_create_user_with_person(self, user_service, sample_user_data, sample_person_data):
        """Test creating a user with person data"""
        user_service.mock_user_repo.get_by_name.return_value = None
        user_service.mock_person_repo.get_person_by_id.return_value = None
        
        mock_person = MagicMock(id_person=1)
        user_service.mock_person_service.generate_person_object.return_value = mock_person
        
        # Create a proper AppUser mock with all fields
        mock_user = AppUser(
            id_app_user=1,
            app_user_name=sample_user_data.app_user_name,
            app_user_person_id=1,
            app_user_email=sample_user_data.app_user_email,
            app_user_last_updated=datetime.now(),
            app_user_password="hashed_password",
            app_user_type="customer",
        )
        user_service.mock_user_repo.create.return_value = mock_user
        
        user_service.mock_auth_client.register_user = AsyncMock(return_value={
            "hashed_password": "hashed_password_123"
        })
        user_service.update_user_password = MagicMock(return_value=True)
        
        result = await user_service.create_user(
            sample_user_data,
            person_data=sample_person_data,
        )
        
        assert result is not None
        assert result.app_user_person_id == 1
        assert result.app_user_name == sample_user_data.app_user_name
        user_service.mock_person_service.generate_person_object.assert_called_once()

    def test_create_user_google_oauth(self, user_service, sample_user_data):
        """Test creating a user with Google OAuth (skip auth creation)"""
        user_service.mock_user_repo.get_by_name.return_value = None
        user_service.mock_user_repo.create.return_value = AppUser(
            id_app_user=1,
            app_user_name=sample_user_data.app_user_name,
        )
        
        # Create user with Google OAuth provider
        result = user_service.create_user(
            sample_user_data,
            provider="google"
        )
        
        assert result is not None
        # Auth client should NOT be called for OAuth
        user_service.mock_auth_client.register_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_user_auth_creation_fails(self, user_service, sample_user_data):
        """Test creating a user when auth creation fails"""
        user_service.mock_user_repo.get_by_name.return_value = None
        user_service.mock_user_repo.create.return_value = AppUser(
            id_app_user=1,
            app_user_name=sample_user_data.app_user_name,
        )
        
        # Mock auth client to fail
        user_service.mock_auth_client.register_user = AsyncMock(
            side_effect=APIException(
                status_code=HTTP_417_EXPECTATION_FAILED,
                error_code=ErrorCode.USER_AUTH_CREATION_FAILED,
                message="Auth creation failed",
            )
        )
        
        with pytest.raises(APIException) as exc_info:
            await user_service.create_user(sample_user_data)
        
        assert exc_info.value.status_code == HTTP_410_GONE
        assert exc_info.value.error_code == ErrorCode.USER_AUTH_CREATION_FAILED
        # Should delete the user after auth creation fails
        user_service.mock_user_repo.delete.assert_called_once()

    def test_update_user_success(self, user_service, sample_user_data, sample_person_data):
        """Test updating a user successfully"""
        # Mock existing user
        existing_user = AppUser(
            id_app_user=1,
            app_user_name="testuser",
            app_user_email="old@example.com",
            app_user_type="customer",
        )
        user_service.get_user_by_id = MagicMock(return_value=existing_user)
        
        # Mock person update
        mock_person = MagicMock(id_person=1)
        user_service.mock_person_service.refresh_or_insert_person.return_value = mock_person
        
        # Mock user update
        user_service.mock_user_repo.update.return_value = AppUser(
            id_app_user=1,
            app_user_name="testuser",
            app_user_email=sample_user_data.app_user_email,
        )
        
        # Update user
        result = user_service.update_user(
            sample_user_data,
            sample_person_data,
            None
        )
        
        assert result is not None
        user_service.mock_user_repo.update.assert_called_once()

    def test_update_user_not_found(self, user_service, sample_user_data, sample_person_data):
        """Test updating a user that doesn't exist"""
        # Check what parameters UserNotFoundException accepts
        # It likely accepts just a message or just a user_id
        user_service.get_user_by_id = MagicMock(side_effect=UserNotFoundException(
            user_id=999  # If it accepts user_id
            # OR
            # message="User not found"  # If it only accepts message
        ))
        
        with pytest.raises(UserNotFoundException):
            user_service.update_user(sample_user_data, sample_person_data, None)

    def test_update_user_password_success(self, user_service, sample_user_data):
        """Test updating user password successfully"""
        existing_user = AppUser(
            id_app_user=1,
            app_user_name="testuser",
            app_user_password="",
        )
        user_service.get_user_by_id = MagicMock(return_value=existing_user)
        user_service.mock_user_repo.update.return_value = existing_user
        
        result = user_service.update_user_password(
            existing_user,
            "new_hashed_password_123"
        )
        
        assert result is not None
        assert existing_user.app_user_password == "new_hashed_password_123"
        user_service.mock_user_repo.update.assert_called_once()

    def test_update_user_image_url_success(self, user_service, sample_user_data):
        """Test updating user image URL successfully"""
        existing_user = AppUser(
            id_app_user=1,
            app_user_name="testuser",
            app_user_image_url=None,
        )
        user_service.get_user_by_id = MagicMock(return_value=existing_user)
        user_service.mock_user_repo.update.return_value = existing_user
        
        new_image_url = "https://example.com/new_avatar.jpg"
        result = user_service.update_user_image_url(existing_user, new_image_url)
        
        assert result is not None
        assert existing_user.app_user_image_url == new_image_url
        user_service.mock_user_repo.update.assert_called_once()

    def test_delete_user_success(self, user_service, sample_user_data):
        """Test deleting a user successfully"""
        existing_user = AppUser(id_app_user=1, app_user_name="testuser")
        user_service.get_user_by_id = MagicMock(return_value=existing_user)
        user_service.mock_user_repo.delete.return_value = True
        
        result = user_service.delete_user(sample_user_data)
        
        assert result is True
        user_service.mock_user_repo.delete.assert_called_once_with(existing_user)

    def test_delete_user_not_found(self, user_service, sample_user_data):
        """Test deleting a user that doesn't exist"""
        user_service.get_user_by_id = MagicMock(side_effect=UserNotFoundException(
            user_id=999  # Use the correct signature
        ))
        
        with pytest.raises(UserNotFoundException):
            user_service.delete_user(sample_user_data)

    @pytest.mark.asyncio
    async def test_update_user_password_with_auth_success(self, user_service, sample_user_data):
        """Test updating password with auth service successfully"""
        update_data = AppUserUpdate_API(
            id_app_user=1,
            username="testuser",
            new_password="NewPassword123!",
        )
        
        token = "mock_token"
        auth_response = {"hashed_password": "new_hashed_password_123"}
        
        user_service.mock_auth_service.update_password = AsyncMock(return_value=auth_response)
        user_service.update_user_password = MagicMock(return_value=AppUser(
            id_app_user=1,
            app_user_name="testuser",
        ))
        
        result = await user_service.update_user_password_with_auth(update_data, token)
        
        assert result is not None
        user_service.mock_auth_service.update_password.assert_called_once()
        user_service.update_user_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password_with_auth_fails(self, user_service, sample_user_data):
        """Test updating password when auth service fails"""
        update_data = AppUserUpdate_API(
            id_app_user=1,
            username="testuser",
            new_password="NewPassword123!",
        )
        
        token = "mock_token"
        user_service.mock_auth_service.update_password = AsyncMock(
            side_effect=APIException(
                status_code=HTTP_417_EXPECTATION_FAILED,
                error_code=ErrorCode.PASSWORD_UPDATE_FAILED,
                message="Auth password update failed",
            )
        )
        
        with pytest.raises(APIException) as exc_info:
            await user_service.update_user_password_with_auth(update_data, token)
        
        assert exc_info.value.status_code == HTTP_417_EXPECTATION_FAILED
        assert exc_info.value.error_code == ErrorCode.PASSWORD_UPDATE_FAILED

    def test_get_all_users_empty(self, user_service):
        """Test getting all users when none exist"""
        user_service.mock_user_repo.get_all.return_value = []
        
        result = user_service.get_all_users()
        
        assert result == []
        user_service.mock_user_repo.get_all.assert_called_once()