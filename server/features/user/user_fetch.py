

from server.core.messages import APPUSERTYPE_NOT_EXISTS
from server.core.models import AppUser, AppUserType, BloodType, Location, Person, PersonDetails
import server.storage.storage_broker as storage_broker
from server.features.person.person_fetch import fetch_person_blood_type_object, fetch_person_details_object

def fetch_all_users():
    return storage_broker.get(AppUser)

def fetch_user_by_id(user_id: str):
    return storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[AppUser.app_user_type,AppUser.app_user_person])

def fetch_user_by_name(user_name: str):
    return storage_broker.get(AppUser,{AppUser.app_user_name:user_name},None,[])

def fetch_user_type_object_by_id(type_id: str):
    record = storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])
    if record == []:
        raise Exception(APPUSERTYPE_NOT_EXISTS)
    
    user_type = AppUserType(id_app_user_type=record[0].id_app_user_type,
                            app_user_type_desc=record[0].app_user_type_desc)
    return user_type

def fetch_user_type_by_id(type_id: str):
    return storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])


