import pytest
from fastapi.testclient import TestClient
from database import schemas, crud
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Fixtures from conftest.py
@pytest.mark.order(1)
def test_create_user(client: TestClient, db_session: Session):
    """Test user registration."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "1234567890",
        "date_of_birth": "2000-01-01T00:00:00",
        "gender": "male",
        "roles": "user",
        "app_user_id": 1,
        "password": "secret123",
        "login_count": "0",
        "failed_login_attempts": "0"
    }

    response = client.post("/auth/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "hashed_password" in data

@pytest.mark.order(2)
def test_login_for_access_token(client: TestClient):
    """Test login endpoint."""
    data = {
        "username": "testuser",
        "password": "secret123"
    }
    response = client.post("/auth/token", data=data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.order(3)
def test_read_users_me(client: TestClient):
    """Test fetching current user info."""
    # Login first
    login_data = {"username": "testuser", "password": "secret123"}
    login_res = client.post("/auth/token", data=login_data)
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users/me/", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"

@pytest.mark.order(4)
def test_update_user_password(client: TestClient):
    """Test updating user password."""
    # Login first
    login_data = {"username": "testuser", "password": "secret123"}
    login_res = client.post("/auth/token", data=login_data)
    token = login_res.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "username": "testuser",
        "app_user_id": 1,
        "new_password": "newsecret123"
    }

    response = client.post("/auth/users/update-password/", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

    # Verify that login works with new password
    login_data_new = {"username": "testuser", "password": "newsecret123"}
    login_res_new = client.post("/auth/token", data=login_data_new)
    assert login_res_new.status_code == 200
    assert "access_token" in login_res_new.json()

@pytest.mark.order(5)
def test_delete_user(client: TestClient):
    """Test deleting a user."""
    # Login first
    login_data = {"username": "testuser", "password": "newsecret123"}
    login_res = client.post("/auth/token", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_data = {
        "username": "testuser",
        "app_user_id": 1,
        "new_password": "newsecret123"
    }

    response = client.delete("/auth/users/delete", json=delete_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

    # Verify login fails after deletion
    login_res_after = client.post("/auth/token", data=login_data)
    assert login_res_after.status_code == 401
