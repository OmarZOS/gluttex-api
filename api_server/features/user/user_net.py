import json
from core.exception_handler import APIException
from communication.communication_broker import send_delete_request, send_post_request, send_put_request
from constants import     *
from core.messages import *
from core.api_models import AppUser_API, AppUserUpdate_API, AuthData_API
from features.user.user_update import update_api_user_password

async def create_user(user_data: dict):
    """
    Register a new user with the authentication server.
    """
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_REGISTRATION_ENDPOINT}"
    
    try:
        response = await send_post_request(url, json_data=user_data)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json()
    except Exception as e:
        raise APIException(status=HTTP_410_GONE,code=USER_AUTH_CREATION_FAILED,details=str(e))

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
        # response.raise_for_status()
        return response.json()
    except APIException as e:
        raise APIException(status= e.status,code=e.code,message=e.message)

async def update_user_password(existing_user: AppUserUpdate_API, token: str):
    """
    Update a user's password through the authentication server.
    """
    user_update = {
        "app_user_id": existing_user.id_app_user,
        "username": existing_user.username,
        "new_password": existing_user.new_password
    }

    flags = {"headers": {"Authorization": f"Bearer {token}"}}
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_CHANGE_ENDPOINT}"

    try:
        response = await send_put_request(url, input_data=user_update, flags=flags)
        response.raise_for_status()
    except Exception as e:
        raise APIException(status=HTTP_502_BAD_GATEWAY,code=USER_NET_FAILED,details=str(e))
    try:
        # Parse response and extract new password hash
        user_data = response.json()
        new_password_hash = user_data.get("hashed_password")
    except Exception as e:
            raise APIException(status=HTTP_401_UNAUTHORIZED,code=INCORRECT_CREDENTIALS,details=str(e))
        # Update password in local database
    try:
        return update_api_user_password(existing_user, new_password_hash)
    except Exception as e:
        raise APIException(status=HTTP_417_EXPECTATION_FAILED,code=USER_UPDATE_FAILED,details=str(e))

async def delete_user(existing_user: AppUserUpdate_API):
    """
    Delete a user through the authentication server.
    """
    user_update = {
        "app_user_id": existing_user.id_app_user,
        "username": existing_user.username,
        "new_password": existing_user.new_password
    }

    # flags = {"headers": {"Authorization": f"Bearer {token}"}}
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_DELETE_ENDPOINT}"

    try:
        response = await send_delete_request(url, input_data=user_update)
        response.raise_for_status()
    except Exception as e:
        raise APIException(status=HTTP_502_BAD_GATEWAY,code=USER_DELETE_FAILED,details=str(e))
        
    
