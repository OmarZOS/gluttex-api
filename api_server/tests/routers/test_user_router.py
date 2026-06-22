# tests/routers/test_app_user_router.py
"""
Unit tests for App User Router endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional
import json

from routers.app_routers import user_router
from core.api_models import AppUser_API, AppUserUpdate_API, Person_API, Location_API, ReactionBase
from core.exceptions.handler import UserNotFoundException, APIException
from core.response_models import SuccessResponseModel
from core.messages.http_status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT


# ==================== Fixtures ====================

@pytest.fixture
def app():
    """Create FastAPI app with router"""
    app = FastAPI()
    app.include_router(user_router, prefix="/api/v1")
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_user_service():
    """Mock UserService"""
    with patch('routers.app_user_router.get_user_service') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_social_service():
    """Mock SocialService"""
    with patch('routers.app_user_router.get_social_service') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "id_app_user": 1,
        "app_user_name": "testuser",
        "app_user_password": "TestPassword123!",
        "app_user_email": "test@example.com",
        "app_user_type": "customer",
        "app_user_preferences": {"theme": "dark"},
        "app_user_image_url": "https://example.com/avatar.jpg"
    }


@pytest.fixture
def sample_person_data():
    """Sample person data for tests"""
    return {
        "id_person": 1,
        "person_first_name": "Test",
        "person_last_name": "User",
        "person_email": "test@example.com",
        "person_phone": "+1234567890",
        "person_gender": "male"
    }


@pytest.fixture
def sample_location_data():
    """Sample location data for tests"""
    return {
        "id_location": 1,
        "location_name": "Test Location",
        "location_latitude": 36.7538,
        "location_longitude": 3.0588,
        "address_street": "123 Test St",
        "address_city": "Test City",
        "address_postal_code": "12345",
        "address_country": "DZ"
    }


@pytest.fixture
def sample_reaction_data():
    """Sample reaction data for tests"""
    return {
        "user_id": 1,
        "reaction_value": "like",
        "rating_value": 4,
        "reaction_type": "product",
        "target_id": 1
    }


@pytest.fixture
def sample_user_update_data():
    """Sample user update data for tests"""
    return {
        "id_app_user": 1,
        "username": "testuser",
        "new_password": "NewPassword456!"
    }


# ==================== Test Class ====================

class TestAppUserRouter:
    """Test suite for App User Router"""

    # ==================== GET /app_user ====================

    def test_get_all_users_success(self, client, mock_user_service):
        """Test successful retrieval of all users"""
        expected_users = [
            {"id_app_user": 1, "app_user_name": "user1"},
            {"id_app_user": 2, "app_user_name": "user2"}
        ]
        mock_user_service.get_all_users.return_value = expected_users

        response = client.get("/api/v1/app_user?offset=0&limit=10")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_users
        mock_user_service.get_all_users.assert_called_once()

    def test_get_all_users_with_pagination(self, client, mock_user_service):
        """Test get all users with pagination parameters"""
        expected_users = [{"id_app_user": 1, "app_user_name": "user1"}]
        mock_user_service.get_all_users.return_value = expected_users

        response = client.get("/api/v1/app_user?offset=5&limit=20")

        assert response.status_code == status.HTTP_200_OK
        mock_user_service.get_all_users.assert_called_once()

    def test_get_all_users_empty(self, client, mock_user_service):
        """Test get all users when no users exist"""
        mock_user_service.get_all_users.return_value = []

        response = client.get("/api/v1/app_user")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    # ==================== GET /app_user/{user_id} ====================

    def test_get_user_by_id_success(self, client, mock_user_service):
        """Test successful retrieval of user by ID"""
        expected_user = {
            "id_app_user": 1,
            "app_user_name": "testuser",
            "app_user_email": "test@example.com"
        }
        mock_user_service.get_user_by_id.return_value = expected_user

        response = client.get("/api/v1/app_user/1")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_user
        mock_user_service.get_user_by_id.assert_called_once_with(1, False)

    def test_get_user_by_id_with_full_details(self, client, mock_user_service):
        """Test get user by ID with full details"""
        expected_user = {
            "id_app_user": 1,
            "app_user_name": "testuser",
            "app_user_person": {"id_person": 1, "person_first_name": "Test"}
        }
        mock_user_service.get_user_by_id.return_value = expected_user

        response = client.get("/api/v1/app_user/1?full=true")

        assert response.status_code == status.HTTP_200_OK
        mock_user_service.get_user_by_id.assert_called_once_with(1, True)

    def test_get_user_by_id_not_found(self, client, mock_user_service):
        """Test get user by ID when user not found"""
        mock_user_service.get_user_by_id.side_effect = UserNotFoundException(user_id=1)

        response = client.get("/api/v1/app_user/999")

        assert response.status_code == HTTP_404_NOT_FOUND

    # ==================== GET /person/{person_id} ====================

    def test_get_person_by_id_success(self, client, mock_social_service):
        """Test successful retrieval of person by ID"""
        expected_person = {
            "id_person": 1,
            "person_first_name": "Test",
            "person_last_name": "User"
        }
        mock_social_service.get_person_by_id.return_value = expected_person

        response = client.get("/api/v1/person/1")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_person
        mock_social_service.get_person_by_id.assert_called_once_with(1)

    def test_get_person_by_id_not_found(self, client, mock_social_service):
        """Test get person by ID when person not found"""
        mock_social_service.get_person_by_id.side_effect = UserNotFoundException(user_id=1)

        response = client.get("/api/v1/person/999")

        assert response.status_code == HTTP_404_NOT_FOUND

    # ==================== POST /app_user ====================

    @pytest.mark.asyncio
    async def test_create_user_success(self, client, mock_user_service, sample_user_data):
        """Test successful user creation"""
        expected_user = {**sample_user_data, "id_app_user": 1}
        mock_user_service.create_user = AsyncMock(return_value=expected_user)

        response = client.post(
            "/api/v1/app_user",
            json={"user": sample_user_data}
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_user
        mock_user_service.create_user.assert_called_once_with(
            sample_user_data, None, None, None
        )

    @pytest.mark.asyncio
    async def test_create_user_with_person_and_location(
        self, client, mock_user_service, sample_user_data, sample_person_data, sample_location_data
    ):
        """Test user creation with person and location data"""
        expected_user = {**sample_user_data, "id_app_user": 1}
        mock_user_service.create_user = AsyncMock(return_value=expected_user)

        response = client.post(
            "/api/v1/app_user",
            json={
                "user": sample_user_data,
                "person": sample_person_data,
                "location": sample_location_data
            }
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_user_service.create_user.assert_called_once_with(
            sample_user_data, sample_person_data, sample_location_data, None
        )

    @pytest.mark.asyncio
    async def test_create_user_with_oauth_provider(self, client, mock_user_service, sample_user_data):
        """Test user creation with OAuth provider"""
        expected_user = {**sample_user_data, "id_app_user": 1}
        mock_user_service.create_user = AsyncMock(return_value=expected_user)

        response = client.post(
            "/api/v1/app_user?provider=google",
            json={"user": sample_user_data}
        )

        assert response.status_code == status.HTTP_201_CREATED
        mock_user_service.create_user.assert_called_once_with(
            sample_user_data, None, None, "google"
        )

    @pytest.mark.asyncio
    async def test_create_user_conflict(self, client, mock_user_service, sample_user_data):
        """Test user creation with duplicate username"""
        mock_user_service.create_user = AsyncMock(
            side_effect=APIException(
                status_code=HTTP_409_CONFLICT,
                error_code="USER_ALREADY_EXISTS",
                message="User already exists"
            )
        )

        response = client.post(
            "/api/v1/app_user",
            json={"user": sample_user_data}
        )

        assert response.status_code == HTTP_409_CONFLICT

    # ==================== DELETE /app_user ====================

    def test_delete_user_success(self, client, mock_user_service, sample_user_data):
        """Test successful user deletion"""
        mock_user_service.delete_user.return_value = {"success": True}

        response = client.delete(
            "/api/v1/app_user",
            json=sample_user_data
        )

        assert response.status_code == status.HTTP_200_OK
        mock_user_service.delete_user.assert_called_once_with(sample_user_data)

    def test_delete_user_with_force_delete(self, client, mock_user_service, sample_user_data):
        """Test user deletion with force_delete flag"""
        mock_user_service.delete_user.return_value = {"success": True}

        response = client.delete(
            "/api/v1/app_user?force_delete=true",
            json=sample_user_data
        )

        assert response.status_code == status.HTTP_200_OK
        mock_user_service.delete_user.assert_called_once_with(sample_user_data)

    def test_delete_user_not_found(self, client, mock_user_service, sample_user_data):
        """Test user deletion when user not found"""
        mock_user_service.delete_user.side_effect = UserNotFoundException(user_id=1)

        response = client.delete(
            "/api/v1/app_user",
            json=sample_user_data
        )

        assert response.status_code == HTTP_404_NOT_FOUND

    # ==================== PUT /app_user/update_password ====================

    @pytest.mark.asyncio
    async def test_update_password_success(self, client, mock_user_service, sample_user_update_data):
        """Test successful password update"""
        expected_result = {"success": True, "message": "Password updated"}
        mock_user_service.update_user_password_with_auth = AsyncMock(return_value=expected_result)

        response = client.put(
            "/api/v1/app_user/update_password?token=valid_token",
            json=sample_user_update_data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        mock_user_service.update_user_password_with_auth.assert_called_once_with(
            sample_user_update_data, "valid_token"
        )

    @pytest.mark.asyncio
    async def test_update_password_missing_token(self, client, mock_user_service, sample_user_update_data):
        """Test password update without token"""
        response = client.put(
            "/api/v1/app_user/update_password",
            json=sample_user_update_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_update_password_unauthorized(self, client, mock_user_service, sample_user_update_data):
        """Test password update with invalid token"""
        mock_user_service.update_user_password_with_auth = AsyncMock(
            side_effect=APIException(
                status_code=401,
                error_code="UNAUTHORIZED",
                message="Invalid token"
            )
        )

        response = client.put(
            "/api/v1/app_user/update_password?token=invalid_token",
            json=sample_user_update_data
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # ==================== PUT /app_user/update_image_url ====================

    def test_update_image_url_success(self, client, mock_user_service, sample_user_data):
        """Test successful image URL update"""
        expected_result = {"success": True, "message": "Image updated"}
        mock_user_service.update_user_image_url.return_value = expected_result

        response = client.put(
            "/api/v1/app_user/update_image_url?image_url=https://new-image.jpg",
            json=sample_user_data
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        mock_user_service.update_user_image_url.assert_called_once()

    def test_update_image_url_missing_image_url(self, client, mock_user_service, sample_user_data):
        """Test image URL update without image_url parameter"""
        response = client.put(
            "/api/v1/app_user/update_image_url",
            json=sample_user_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # ==================== PUT /app_user ====================

    def test_update_user_success(
        self, client, mock_user_service, sample_user_data, sample_person_data, sample_location_data
    ):
        """Test successful user update"""
        expected_result = {"success": True, "message": "User updated"}
        mock_user_service.update_user.return_value = expected_result

        response = client.put(
            "/api/v1/app_user",
            json={
                "user": sample_user_data,
                "person_record": sample_person_data,
                "location_record": sample_location_data
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        mock_user_service.update_user.assert_called_once_with(
            sample_user_data, sample_person_data, sample_location_data
        )

    def test_update_user_not_found(self, client, mock_user_service, sample_user_data):
        """Test user update when user not found"""
        mock_user_service.update_user.side_effect = UserNotFoundException(user_id=1)

        response = client.put(
            "/api/v1/app_user",
            json={
                "user": sample_user_data,
                "person_record": {},
                "location_record": {}
            }
        )

        assert response.status_code == HTTP_404_NOT_FOUND

    # ==================== POST /reaction ====================

    def test_reaction_success(self, client, mock_social_service, sample_reaction_data):
        """Test successful reaction creation"""
        expected_result = {
            "success": True,
            "message": "Reaction processed",
            "data": {"reaction_id": 1}
        }
        mock_social_service.handle_reaction.return_value = expected_result

        response = client.post(
            "/api/v1/reaction",
            json=sample_reaction_data
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_result
        mock_social_service.handle_reaction.assert_called_once()

    def test_reaction_invalid_data(self, client, mock_social_service):
        """Test reaction with invalid data"""
        invalid_data = {
            "user_id": 1
            # Missing required fields
        }

        response = client.post(
            "/api/v1/reaction",
            json=invalid_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_reaction_target_not_found(self, client, mock_social_service, sample_reaction_data):
        """Test reaction when target not found"""
        mock_social_service.handle_reaction.side_effect = UserNotFoundException(user_id=1)

        response = client.post(
            "/api/v1/reaction",
            json=sample_reaction_data
        )

        assert response.status_code == HTTP_404_NOT_FOUND

    # ==================== GET /app_user/search ====================

    def test_search_users_success(self, client, mock_user_service):
        """Test successful user search"""
        expected_results = [
            {"id_app_user": 1, "app_user_name": "testuser"},
            {"id_app_user": 2, "app_user_name": "testuser2"}
        ]
        mock_user_service.search_users.return_value = expected_results

        response = client.get("/api/v1/app_user/search?query=test")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"] == expected_results
        mock_user_service.search_users.assert_called_once_with("test", 20)

    def test_search_users_with_limit(self, client, mock_user_service):
        """Test user search with custom limit"""
        mock_user_service.search_users.return_value = []

        response = client.get("/api/v1/app_user/search?query=test&limit=5")

        assert response.status_code == status.HTTP_200_OK
        mock_user_service.search_users.assert_called_once_with("test", 5)

    def test_search_users_query_too_short(self, client, mock_user_service):
        """Test user search with query too short"""
        response = client.get("/api/v1/app_user/search?query=a")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_users_no_results(self, client, mock_user_service):
        """Test user search with no results"""
        mock_user_service.search_users.return_value = []

        response = client.get("/api/v1/app_user/search?query=nonexistent")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"] == []

    # ==================== GET /app_user/by-email/{email} ====================

    def test_get_user_by_email_success(self, client, mock_user_service):
        """Test successful retrieval of user by email"""
        expected_user = {
            "id_app_user": 1,
            "app_user_name": "testuser",
            "app_user_email": "test@example.com"
        }
        mock_user_service.get_user_by_email.return_value = expected_user

        response = client.get("/api/v1/app_user/by-email/test@example.com")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"] == expected_user
        mock_user_service.get_user_by_email.assert_called_once_with("test@example.com")

    def test_get_user_by_email_not_found(self, client, mock_user_service):
        """Test get user by email when user not found"""
        mock_user_service.get_user_by_email.return_value = None

        response = client.get("/api/v1/app_user/by-email/nonexistent@example.com")

        assert response.status_code == HTTP_404_NOT_FOUND

    def test_get_user_by_email_invalid_format(self, client, mock_user_service):
        """Test get user by email with invalid format"""
        response = client.get("/api/v1/app_user/by-email/invalid-email")

        assert response.status_code == HTTP_404_NOT_FOUND


# ==================== Integration Tests ====================

class TestAppUserRouterIntegration:
    """Integration tests with real service (requires database)"""

    @pytest.mark.skip(reason="Requires database setup")
    def test_full_user_flow(self):
        """Test complete user CRUD flow"""
        pass

    @pytest.mark.skip(reason="Requires database setup")
    def test_user_reaction_flow(self):
        """Test user reaction flow"""
        pass