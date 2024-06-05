

from core.messages import APPUSER_NOT_EXISTS, APPUSERTYPE_NOT_EXISTS
from core.models import AppUser, AppUserType, BloodType, Location, Person, PersonDetails
import storage.storage_broker as storage_broker
from features.person.person_fetch import fetch_person_blood_type_object, fetch_person_details_object

def fetch_all_users():
    return storage_broker.get(AppUser)

def fetch_user_by_id(user_id: str):
    return storage_broker.get(AppUser,{AppUser.id_app_user:user_id},[AppUserType,Person,PersonDetails],["*"])

# def fetch_user_object_by_id(user_id: str):
#     records = storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[AppUser.app_user_type,AppUser.app_user_person,Person.person_details])

#     return True

def fetch_user_by_name(user_name: str):
    return storage_broker.get(AppUser,{AppUser.app_user_name:user_name},None,[])

def fetch_user_type_object_by_id(type_id: str):
    record = storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])
    if record == []:
        raise Exception(APPUSERTYPE_NOT_EXISTS)
    
    user_type = AppUserType(id_app_user_type=record[0].id_app_user_type)
    return user_type

def fetch_user_object_by_id(user_id: int):
    record = storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[])
    if record == []:
        raise Exception(APPUSER_NOT_EXISTS)
    
    user_obj = AppUser(id_app_user=record[0].id_app_user
                                        ,app_user_person_id = record[0].app_user_person_id)
    return user_obj

# def fetch_user_by_id(user_id: int):
#     return storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[],[AppUser.app_user_person,AppUser.app_user_type])

def fetch_user_type_by_id(type_id: str):
    return storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])


