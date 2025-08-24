from features.location.location_insert import insert_location
from features.location.location_fetch import fetch_location_object
from features.location.location_update import update_location
from features.person.person_fetch import fetch_person, fetch_person_blood_type_object, fetch_person_details_object
from features.person.person_insert import refresh_or_insert_person 
from core.api_models import AppUser_API, Location_API, Person_API
from core.exception_handler import APIException
from core.messages import *
from features.user.user_fetch import fetch_user_by_id, fetch_user_type_object_by_id
from core.models import *
from features.insertion import update_record_in_api
from datetime import datetime;

def get_user(user_id: int):
    """
    Fetch a user by ID from the database.
    """
    user = fetch_user_by_id(user_id)
    if not user:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=APPUSER_NOT_EXISTS,
            message=f"{USER_FETCH_NOT_FOUND}: {user_id}"
        )
    return user


def update_api_user(user_record: AppUser_API,person_record: Person_API,location_record:Location_API):
    """
    Update user fields except password and image.
    """

    _user = get_user(user_record.id_app_user)  # Ensure the user exists before updating
    # people = fetch_person(person_record.id_person)
    
    people = refresh_or_insert_person(person_record,location_record)
    # if people == []:
    # else:
    #     _person_details_record = fetch_person_details_object
    #     (person_record.person_details_id)
    #     _blood_type_record = fetch_person_blood_type_object(str(person_record.id_blood_type))
    # _person = people
    # _location = fetch_location_object(str(location_record.id_location))

    # if not (_location):
    #     _location = insert_location(location_record)
    # else:
    #     _location = update_location(location_record.id_location,location_record)
    
    # _person.person_location.id_location = _location.id_location

    # if (_person_details_record!=None):
    #     _person.person_details = _person_details_record
    # if (_blood_type_record):
    #     _person.person_blood_type.id_blood_type = _blood_type_record.id_blood_type
    # if (_person):
    #     _user.app_user_person_id = _person.id_person


    # Define fields to update (exclude password & image_url)
    updatable_fields = [
        "app_user_preferences",
        "app_user_last_active",
        "app_user_image_url",
        # "app_user_last_updated",
        "app_user_type_id",
        # Add any other fields you want to allow updating
    ]

    # --- Validate user type ---
    user_type = fetch_user_type_object_by_id(user_record.app_user_type_id)
    if not user_type:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=APPUSERTYPE_NOT_EXISTS,
            details=f"{APPUSERTYPE_NOT_EXISTS}: {user_record.app_user_type_id}"
        )


    # Dynamically update allowed fields
    for field in updatable_fields:
        if hasattr(user_record, field):
            setattr(_user, field, getattr(user_record, field))

    try:
        _user.app_user_person_id = people.id_person
        _user.app_user_last_updated = datetime.now()
        return update_record_in_api(_user)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=USER_UPDATE_FAILED,
            message=f"{USER_UPDATE_FAILED}: {_user.id_app_user}",
            details=f"{str(e)}"
        )


def update_api_user_password(user_record, hashed_password):
    """
    Update only the user's password.
    """
    user = get_user(user_record.id_app_user)
    user.app_user_password = hashed_password

    try:
        return update_record_in_api(user)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=USER_UPDATE_FAILED,
            message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",
            details=f"{str(e)}"
        )


def update_api_user_image_url(user_record, image_url):
    """
    Update only the user's image URL.
    """
    user = get_user(user_record.id_app_user)
    user.app_user_image_url = image_url

    try:
        return update_record_in_api(user)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=USER_UPDATE_FAILED,
            message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",
            details=f"{str(e)}"
        )
