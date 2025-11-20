import logging
import datetime
from core.exception_handler import APIException
from core.api_models import AppUser_API, Location_API, Person_API
from core.messages import *
from core.models import AppUser
from features.insertion import delete_record_from_api, insert_or_complete_or_raise
from features.medical.person.person_fetch import fetch_person_object
from features.medical.person.person_insert import generate_person_object
from features.app.user.user_fetch import fetch_user_by_name, fetch_user_type_object_by_id
from features.app.user.user_net import create_user, delete_user
from features.app.user.user_update import update_api_user_password

logger = logging.getLogger("FastAPIApp")


async def insert_user(
    user: AppUser_API,
    mensch: Person_API = None,
    location: Location_API = None,
    provider: str | None = None
):
    """
    Insert a new user into the system.
    - If `provider` is None: creates both the AppUser and an authentication record.
    - If `provider` is 'google' (or another OAuth provider): creates only the AppUser.
    """

    # --- Step 1: Check if user already exists ---
    if fetch_user_by_name(user.app_user_name):
        raise APIException(
            status=HTTP_409_CONFLICT,
            code=APPUSER_ALREADY_EXISTS,
            details=f"User '{user.app_user_name}' already exists."
        )

    # --- Step 2: Validate user type ---
    user_type = fetch_user_type_object_by_id(user.app_user_type_id)
    if not user_type:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code=APPUSERTYPE_NOT_EXISTS,
            details=f"Invalid user type ID: {user.app_user_type_id}"
        )

    # --- Step 3: Build AppUser object ---
    now = datetime.datetime.now()
    app_user = AppUser(
        app_user_name=user.app_user_name,
        app_user_password="",  # empty for OAuth users
        app_user_preferences=user.app_user_preferences,
        app_user_image_url=user.app_user_image_url,
        app_user_type_id=user_type.id_app_user_type,
        app_user_last_active=str(now),
        app_user_last_updated=str(now),
        app_user_creation=str(now),
    )

    # --- Step 4: Attach Person if provided ---
    if mensch:
        existing_person = fetch_person_object(mensch.id_person)
        if existing_person:
            app_user.app_user_person_id = existing_person.id_person
        else:
            app_user.app_user_person = generate_person_object(mensch, location)

    # --- Step 5: Save AppUser record ---
    try:
        nutzer = insert_or_complete_or_raise(app_user)
    except Exception as e:
        logger.error(f"Failed to insert AppUser: {e}")
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=USER_INSERT_FAILED,
            details=f"Failed to insert AppUser: {e}"
        )

    # --- Step 6: Handle authentication record ---
    if provider and provider.lower() == "google":
        # OAuth users don't need local auth data
        logger.info(f"Skipping auth creation for OAuth provider '{provider}'")
        return nutzer

    # Only for regular username/password users:
    user_auth_data = {
        "username": nutzer.app_user_name,
        "app_user_id": nutzer.id_app_user,
        "password": user.app_user_password,
    }

    try:
        logger.info(f"Creating auth record for user '{nutzer.app_user_name}'")
        user_auth_record = await create_user(user_auth_data)

        logger.info("Updating AppUser with hashed password")
        update_api_user_password(nutzer, user_auth_record["hashed_password"])

    except APIException as e:
        logger.error(f"Failed to create/update auth record: {e}")
        if e.status == HTTP_417_EXPECTATION_FAILED:
            delete_record_from_api(nutzer)
            delete_user(nutzer)
        raise APIException(
            status=HTTP_410_GONE,
            code=USER_AUTH_CREATION_FAILED,
            details=str(e)
        )

    return nutzer

