from fastapi import APIRouter,  status
from core.exception_handler import APIException
from core.messages import *
from core.api_models import AppUser_API, AppUserUpdate_API, Location_API, Person_API
from features.app.user.user_delete import delete_user
from features.app.user.user_fetch import fetch_all_users, fetch_full_user_by_id, fetch_user_by_id
from features.app.user.user_insert import insert_user
from features.app.user.user_net import update_user_password
from features.app.user.user_update import update_api_user, update_api_user_image_url

app_user_router = APIRouter()
@app_user_router.get("/app_user")
def get_all_users():
    """
    Retrieve all users.
    """
    return fetch_all_users()

@app_user_router.get("/app_user/{user_id}")
def get_user_by_id(user_id: int):
    """
    Retrieve a user by ID.
    """
    user = fetch_full_user_by_id(user_id)
    if not user:
        raise APIException(status=HTTP_404_NOT_FOUND,code=APPUSER_NOT_EXISTS, details=f"{APPUSER_NOT_EXISTS}: {user_id}")
    return user

@app_user_router.post("/app_user/add")
async def insert_user_endpoint(user: AppUser_API, person: Person_API = None, location: Location_API = None):
    """
    Insert a new user.
    """
    return await insert_user(user, person, location)

@app_user_router.delete("/app_user/delete")
def delete_user_endpoint(user: AppUser_API):
    """
    Delete a user.
    """
    return delete_user(user)

@app_user_router.put("/app_user/update_password")
async def update_user_password_endpoint(user: AppUserUpdate_API, token: str):
    """
    Update the user password.
    """
    return await update_user_password(user, token)

@app_user_router.put("/app_user/update_image_url")
def update_user_image_url_endpoint(user: AppUser_API, image_url: str):
    """
        Update the user image url.
    """
    return update_api_user_image_url(user, image_url)

@app_user_router.put("/app_user/update")
def update_user_record_endpoint(user: AppUser_API, person_record: Person_API,location_record:Location_API):
    """
        Update the user image url.
    """
    return update_api_user(user, person_record,location_record)
