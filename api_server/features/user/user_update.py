from core.exception_handler import APIException
from core.messages import *
from features.user.user_fetch import fetch_user_by_id
from core.models import *
from features.insertion import  update_record_in_api

def get_user(user_id: int):
    """
    Fetch a user by ID from the database.
    """
    user = fetch_user_by_id(user_id)
    if not user:
        raise APIException(status= HTTP_404_NOT_FOUND,code=USER_FETCH_NOT_FOUND,message=f"{USER_FETCH_NOT_FOUND}: {user_id}",details=f"{str(e)}")
    return user

def update_api_user_password(user_record , hashed_password):
    
    user = get_user(user_record.id_app_user)  # Ensure the user exists before updating

    user.app_user_password = hashed_password

    try:
        return update_record_in_api(user)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=USER_UPDATE_FAILED,message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",details=f"{str(e)}")



def update_api_user_image_url(user_record , image_url):

    user = get_user(user_record.id_app_user)  # Ensure the user exists before updating

    user.app_user_image_url = image_url

    try:
        return update_record_in_api(user)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=USER_UPDATE_FAILED,message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",details=f"{str(e)}")