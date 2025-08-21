
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
        # join_tables=[Person],
        eager_load_depth=[AppUser.app_user_type,AppUser.app_user_person],
        offset=0,
        limit=1
    )

    if users == []:
        return None

    user = users[0]
    if (user.app_user_person):
        # Fetch related Person with details and blood type
        person = storage_broker.get(
            table=Person,
            conditions={Person.id_person: user.app_user_person.id_person},
            join_tables=[],
            eager_load_depth=[Person.person_blood_type,Person.person_details,Person.patient,{Person.person_location:[Location.location_name,Location.position_wkt,Location.location_address_id]}],
            offset=0,
            limit=1
        )[0]
        if person.person_location:
            addresses = storage_broker.get(
                table=Address,
                conditions={Address.id_address: person.person_location.location_address_id},
                # join_tables=[],
                # eager_load_depth=[Person.person_blood_type,Person.person_details,Person.patient,{Person.person_location:[Location.location_name,Location.position_wkt]}],
                offset=0,
                limit=1
            )
            if( addresses != []):
                person.person_location.location_address = addresses[0]


        user.app_user_person = person

    return user

def fetch_user_by_id(user_id: str):
    user_list = storage_broker.get(AppUser
                              ,{AppUser.id_app_user :int(user_id)}
                              ,[AppUserType]
                              ,[AppUser.app_user_type]
                              ,None
                              )
    user = None
    if len(user_list)>0:
        user  = user_list[0]
        person_list =  storage_broker.get(Person
                                ,{Person.id_person :user.app_user_person_id}
                                ,[PersonDetails,BloodType]
                                ,[Person.person_blood_type,Person.person_details]
                                ,None
                                )
        if len(person_list)>0:
            person  = person_list[0]
            user.app_user_person = person
    
    return user

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
