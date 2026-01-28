# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from database import crud, schemas
from database.crypt import verify_password
from datetime import datetime

# -----------------------
# Unit Tests (CRUD/Auth)
# -----------------------

def test_create_user_unit(db_session):
    """Test creating a user via CRUD directly."""
    user_data = schemas.UserCreate(
        username="unituser",
        password="secret123",
        app_user_id=10,
        email="unit@example.com",
        first_name="Unit",
        last_name="Test",
        phone_number="5555555",
        date_of_birth=datetime(1990, 1, 1),
        gender="F",
        roles="user",
        login_count=0,
        failed_login_attempts=0,
        profile_picture=None
    )
    user = crud.create_user(db_session, user_data)
    assert user.username == "unituser"
    assert verify_password("secret123", user.hashed_password, user.password_salt)
    assert user.email == "unit@example.com"

def test_change_password_unit(db_session, test_user):
    """Test changing a user's password via CRUD."""
    from database.crud import change_user_password
    new_password_data = schemas.UserUpdate(
        username=test_user.username,
        new_password="newpass123",
        app_user_id=test_user.app_user_id
    )
    updated_user = change_user_password(db_session, new_password_data)
    assert verify_password("newpass123", updated_user.hashed_password, updated_user.password_salt)

def test_delete_user_unit(db_session):
    """Test deleting a user via CRUD."""
    # Create user
    user_data = schemas.UserCreate(
        username="deleteuser",
        password="secret123",
        app_user_id=20,
        email="delete@example.com",
        first_name="Delete",
        last_name="Me",
        phone_number="555666",
        date_of_birth=datetime(1980,1,1),
        gender="M",
        roles="user",
        login_count=0,
        failed_login_attempts=0,
        profile_picture=None
    )
    user = crud.create_user(db_session, user_data)
    # Delete
    delete_data = schemas.UserUpdate(
        username=user.username,
        new_password="doesntmatter",
        app_user_id=user.app_user_id
    )
    deleted_user = crud.delete_user(db_session, delete_data)
    assert deleted_user.app_user_id == user.app_user_id
    # Verify deletion
    assert crud.get_user(db_session, user_id=user.app_user_id) is None


# -----------------------
# Service/Integration Tests
# -----------------------

def test_register_user(client):
    """Test POST /auth/users/"""
    response = client.post("/auth/users/", json={
        "username": "serviceuser",
        "password": "mypassword",
        "app_user_id": 100,
        "email": "service@example.com",
        "first_name": "Service",
        "last_name": "Tester",
        "phone_number": "123123123",
        "date_of_birth": "2000-01-01T00:00:00",
        "gender": "M",
        "roles": "user",
        "login_count": 0,
        "failed_login_attempts": 0,
        "profile_picture": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "serviceuser"
    assert data["email"] == "service@example.com"


def test_login_user(client, test_user):
    """Test POST /auth/token"""
    response = client.post("/auth/token", data={
        "username": test_user.username,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["app_user_id"] == str(test_user.app_user_id)


def test_get_current_user(client, auth_headers):
    """Test GET /auth/users/me/"""
    response = client.get("/auth/users/me/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_update_password(client, auth_headers):
    """Test POST /auth/users/update-password/"""
    response = client.post("/auth/users/update-password/", headers=auth_headers, json={
        "username": "testuser",
        "app_user_id": 1,
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "hashed_password" in data
    # Confirm password changed via CRUD
    from database.crud import get_user
    from database.crypt import verify_password
    user = get_user(client.app.dependency_overrides[0](), 1)
    assert verify_password("newpassword123", user.hashed_password, user.password_salt)


def test_delete_user_service(client):
    """Test DELETE /auth/users/delete"""
    # Create user to delete
    user_data = {
        "username": "tobedeleted",
        "password": "pass123",
        "app_user_id": 200,
        "email": "delete@example.com",
        "first_name": "Delete",
        "last_name": "Me",
        "phone_number": "777888",
        "date_of_birth": "1995-05-05T00:00:00",
        "gender": "F",
        "roles": "user",
        "login_count": 0,
        "failed_login_attempts": 0,
        "profile_picture": None
    }
    client.post("/auth/users/", json=user_data)
    # Delete user
    response = client.delete("/auth/users/delete", json={
        "username": "tobedeleted",
        "app_user_id": 200,
        "new_password": "doesntmatter"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tobedeleted"
