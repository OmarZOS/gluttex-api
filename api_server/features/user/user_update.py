from features.user.user_fetch import fetch_user_by_id
from core.models import *
from features.insertion import  update_record_in_api

def get_user(user_id: int):
    """
    Fetch a user by ID from the database.
    """
    user = fetch_user_by_id(user_id)
    if not user:
        raise Exception(f"User with ID {user_id} does not exist.")
    return user


def update_api_user_password(user_record , hashed_password):
    

    user = get_user(user_record.id_app_user)  # Ensure the user exists before updating

    user.app_user_password = hashed_password

    return update_record_in_api(user)

def update_api_user_image_url(user_record , image_url):

    user = get_user(user_record.id_app_user)  # Ensure the user exists before updating

    user.app_user_image_url = image_url

    return update_record_in_api(user)