from fastapi import APIRouter, HTTPException, status
from core.api_models import AppUser_API, Location_API, Person_API
from features.user.user_delete import delete_user
from features.user.user_fetch import fetch_all_users, fetch_user_by_id
from features.user.user_insert import insert_user
from features.user.user_net import update_user_password
from features.user.user_update import update_api_user_image_url

app_user_router = APIRouter()
@app_user_router.get("/app_user")
def get_all_users():
    """
    Retrieve all users.
    """
    try:
        return fetch_all_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"Error fetching users: {str(e)}"
        )

@app_user_router.get("/app_user/{user_id}")
def get_user_by_id(user_id: int):
    """
    Retrieve a user by ID.
    """
    try:
        user = fetch_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching user: {str(e)}"
        )

@app_user_router.put("/app_user/add")
async def insert_user_endpoint(user: AppUser_API, person: Person_API = None, location: Location_API = None):
    """
    Insert a new user.
    """
    try:
        return await insert_user(user, person, location)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Couldn't insert user: {str(e)}"
        )

@app_user_router.delete("/app_user/delete")
def delete_user_endpoint(user: AppUser_API):
    """
    Delete a user.
    """
    try:
        return delete_user(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Couldn't delete user: {str(e)}"
        )

@app_user_router.post("/app_user/update_password")
def update_user_password_endpoint(user: AppUser_API, token: str):
    """
    Update the user password.
    """
    try:
        return update_user_password(user, token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Couldn't update user password: {str(e)}"
        )

@app_user_router.post("/app_user/update_image_url")
def update_user_image_url_endpoint(user: AppUser_API, image_url: str):
    """
        Update the user image url.
    """
    try:
        return update_api_user_image_url(user, image_url)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Couldn't update user image url: {str(e)}"
        )
