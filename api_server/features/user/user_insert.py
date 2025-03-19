
# here, we make schema translations

from asyncio.log import logger
import logging
from core.api_models import AppUser_API, Location_API, Person_API
from core.messages import APPUSER_ALREADY_EXISTS
from core.models import  AppUser
from features.insertion import delete_record_from_api, insert_or_complete_or_raise
from features.person.person_fetch import  fetch_person_object
from features.person.person_insert import generate_person_object
from features.user.user_fetch import  fetch_user_by_name, fetch_user_type_object_by_id
from features.user.user_net import create_user
from features.user.user_update import update_api_user_password
import datetime


# logger = logging.getLogger("FastAPIApp")

async def insert_user  (user: AppUser_API,mensch: Person_API=None,location: Location_API=None):
    
    if fetch_user_by_name(user.app_user_name) != []:
        raise Exception(APPUSER_ALREADY_EXISTS)


    user_type = fetch_user_type_object_by_id(user.app_user_type_id)
    if isinstance(user.app_user_image, str):
        user.app_user_image = user.app_user_image.encode('utf-8')
    app_user = AppUser(
                        # id_app_user= user.id_app_user,
                        app_user_name= user.app_user_name,
                        app_user_password= "", # intentionally empty
                        app_user_preferences= user.app_user_preferences,
                        app_user_image = user.app_user_image,
                        # app_user_person_id= person.id_person,
                        app_user_type_id= user_type.id_app_user_type,
                        app_user_last_active= str(datetime.datetime.now()),
                        app_user_last_updated= str(datetime.datetime.now()),
                        app_user_creation= str(datetime.datetime.now()),
                        )
    if mensch:
        person_object = fetch_person_object(mensch.id_person)
        if person_object :
            app_user.app_user_person_id= person_object.id_person
        else:
            person = generate_person_object(mensch,location)
            app_user.app_user_person = person
    logger.info("Creating auth record for user in database")
    code,nutzer,msg = insert_or_complete_or_raise(app_user)
    if (code == 1): raise Exception(msg)
        
    # try:
    # create auth record for user
    user_auth_data = {
        "username":nutzer.app_user_name,
        "app_user_id":nutzer.id_app_user,
        "password":user.app_user_password,   
    }

    # create auth record for user
    logger.info("Creating auth record for user")
    user_auth_record = await create_user(user_auth_data)
    logger.info(user_auth_record)
    logger.info("Updating auth record for user")
    update_api_user_password(nutzer,user_auth_record["hashed_password"])

    return nutzer
    # except Exception as e:
    #     delete_record_from_api(nutzer)
    #     raise Exception("Error on creating auth record")



