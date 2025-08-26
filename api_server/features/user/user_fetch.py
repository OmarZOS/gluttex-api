
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func


def fetch_all_users():
    return storage_broker.get(AppUser)

def fetch_full_user_by_id(user_id: str):
    """
    Fetch a user by ID along with related AppUserType and Person details.
    """
    # Fetch user with AppUserType joined
    users = storage_broker.get(
        table=AppUser,
        conditions={AppUser.id_app_user: int(user_id)},
        join_tables=[AppUser.app_user_person,AppUser.app_user_type],
        eager_load_depth=[AppUser.app_user_type,{AppUser.app_user_person:[Person.person_details,Person.person_blood_type,{Person.person_location:[Location.location_address,Location.location_name,Location.position_wkt]}]}],
        offset=0,
        limit=1
    )

    if users == []:
        return None

    user = users[0]

    return user

def fetch_user_by_id(user_id: str):
    user_list = storage_broker.get(AppUser
                              ,{AppUser.id_app_user :int(user_id)}
                              ,[AppUserType]
                              ,[AppUser.app_user_type,{AppUser.app_user_person:[Person.person_details]}]
                              ,None
                              )
                            
    if user_list == []:
        return None 
    return user_list[0]

# def fetch_user_object_by_id(user_id: str):
#     records = storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[AppUser.app_user_type,AppUser.app_user_person,Person.person_details])

#     return True

def fetch_user_by_name(user_name: str):
    return storage_broker.get(AppUser,{AppUser.app_user_name:user_name},None,[])

def fetch_user_type_object_by_id(type_id: str):
    record = storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])
    if record == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=APPUSERTYPE_NOT_EXISTS)
    
    user_type = AppUserType(id_app_user_type=record[0].id_app_user_type)
    return user_type

def fetch_user_object_by_id(user_id: int):
    record = storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[])
    if record == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=APPUSER_NOT_EXISTS)
    
    user_obj = AppUser(id_app_user=record[0].id_app_user
                                        ,app_user_person_id = record[0].app_user_person_id)
    return user_obj

# def fetch_user_by_id(user_id: int):
#     return storage_broker.get(AppUser,{AppUser.id_app_user:user_id},None,[],[AppUser.app_user_person,AppUser.app_user_type])

def fetch_user_type_by_id(type_id: str):
    return storage_broker.get(AppUserType,{AppUserType.id_app_user_type:type_id},None,[])
