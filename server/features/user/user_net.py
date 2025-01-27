


import json
from communication.communication_broker import *
from constants import AUTH_SERVER_NAME,AUTH_PORT,AUTH_REGISTRATION_ENDPOINT,AUTH_LOGIN_ENDPOINT,AUTH_CHANGE_ENDPOINT
from core.api_models import AppUser_API, AuthData_API
from features.user.user_update import update_api_user_password



async def create_user(user_data):
    url = f"https://{AUTH_SERVER_NAME}:8000{AUTH_REGISTRATION_ENDPOINT}"
    response = await send_post_request(url, json_data= user_data)

    if response.status_code != 200:
        raise Exception(response.content)
    return  json.loads(response.content)

async def login_for_access_token( app_user : AuthData_API):
    form_data = {
        "username":app_user.app_user_name,
        "app_user_id":app_user.id_app_user,
        "password":app_user.app_user_password,   
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    url = f"https://{AUTH_SERVER_NAME}:8000{AUTH_LOGIN_ENDPOINT}"
    response = await send_post_request(url, payload_data= form_data,flags = headers)
    if response.status_code != 200:
        raise Exception(response.content)
    return  json.loads(response.content)
    

# async def read_users_me( token: str):
#     endpoint = "/users/me/"
#     headers = {"Authorization": f"Bearer {token}"}
# url = f"https://{AUTH_SERVER_NAME}:8000{}"    
# return await send_get_request(url, flags=headers)

async def update_user_password( ex_user, token):
    user_update = {
        "username":ex_user.app_user_name,
        "new_password":ex_user.app_user_password}
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://{AUTH_SERVER_NAME}:{AUTH_PORT}{AUTH_CHANGE_ENDPOINT}"
    response = await send_put_request(url, payload_data=user_update, flags=headers)
    
    user = json.loads(response.data)
    new_password_hash = user["hashed_password"]
    # ex_user.app_user_password = new_password_hash
    final_response = update_api_user_password(user, new_password_hash)
    
    
    return final_response




