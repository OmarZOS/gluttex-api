# routers/app_user_router.py
from fastapi import APIRouter, HTTPException, status, Depends
from core.exception_handler import APIException
from core.messages import *
from core.api_models import AppUser_API, AppUserUpdate_API, Location_API, Person_API, ReactionBase
from services.user_service import UserService
from services.social_service import SocialService

app_user_router = APIRouter()

# Dependency injection
def get_user_service() -> UserService:
    return UserService()

def get_social_service() -> SocialService:
    return SocialService()

@app_user_router.get("/app_user")
def get_all_users(user_service: UserService = Depends(get_user_service)):
    """
    Retrieve all users.
    """
    return user_service.get_all_users()

@app_user_router.get("/app_user/{user_id}")
def get_user_by_id(
    user_id: int,
    full: bool = False,
    user_service: UserService = Depends(get_user_service)
):
    """
    Retrieve a user by ID.
    """
    return user_service.get_user_by_id(user_id, full)

@app_user_router.get("/person/{person_id}")
def get_person_by_id(
    person_id: int,
    social_service: SocialService = Depends(get_social_service)
):
    """
    Retrieve a person by ID.
    """
    return social_service.get_person_by_id(person_id)

@app_user_router.post("/app_user/add")
async def insert_user_endpoint(
    user: AppUser_API,
    person: Person_API = None,
    location: Location_API = None,
    provider: str = None,
    user_service: UserService = Depends(get_user_service)
):
    """
    Insert a new user.
    """
    return await user_service.create_user(user, person, location, provider)

@app_user_router.delete("/app_user/delete")
def delete_user_endpoint(
    user: AppUser_API,
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a user.
    """
    return user_service.delete_user(user)

@app_user_router.put("/app_user/update_password")
async def update_user_password_endpoint(
    user: AppUserUpdate_API,
    token: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update the user password.
    """
    return await user_service.update_user_password_with_auth(user, token)

@app_user_router.put("/app_user/update_image_url")
def update_user_image_url_endpoint(
    user: AppUser_API,
    image_url: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update the user image url.
    """
    return user_service.update_user_image_url(user, image_url)

@app_user_router.put("/app_user/update")
def update_user_record_endpoint(
    user: AppUser_API,
    person_record: Person_API,
    location_record: Location_API,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update the user record.
    """
    return user_service.update_user(user, person_record, location_record)

@app_user_router.post("/reaction")
def reaction_endpoint(
    reaction: ReactionBase,
    social_service: SocialService = Depends(get_social_service)
):
    """
    Insert reactions or update them.
    """
    return social_service.handle_reaction(reaction)