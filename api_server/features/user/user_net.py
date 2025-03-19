import json
from communication.communication_broker import send_post_request, send_put_request
from constants import (
    AUTH_SERVER_NAME, AUTH_PORT, AUTH_REGISTRATION_ENDPOINT, 
    AUTH_LOGIN_ENDPOINT, AUTH_CHANGE_ENDPOINT
)
from core.api_models import AppUser_API, AuthData_API
from features.user.user_update import update_api_user_password

async def create_user(user_data: dict):
    """
    Register a new user with the authentication server.
    """
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_REGISTRATION_ENDPOINT}"
    
    try:
        response = await send_post_request(url, payload_data=user_data)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json()
    except Exception as e:
        raise Exception(f"User registration failed: {e}")

async def login_for_access_token(app_user: AuthData_API):
    """
    Authenticate a user and retrieve an access token.
    """
    form_data = {
        "username": app_user.app_user_name,
        "app_user_id": app_user.id_app_user,
        "password": app_user.app_user_password,   
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_LOGIN_ENDPOINT}"

    try:
        response = await send_post_request(url, payload_data=form_data, flags=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Login failed: {e}")

async def update_user_password(existing_user: AppUser_API, token: str):
    """
    Update a user's password through the authentication server.
    """
    user_update = {
        "username": existing_user.app_user_name,
        "new_password": existing_user.app_user_password
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_CHANGE_ENDPOINT}"

    try:
        response = await send_put_request(url, payload_data=user_update, flags=headers)
        response.raise_for_status()

        # Parse response and extract new password hash
        user_data = response.json()
        new_password_hash = user_data.get("hashed_password")

        # Update password in local database
        return update_api_user_password(existing_user, new_password_hash)
    except Exception as e:
        raise Exception(f"Password update failed: {e}")
