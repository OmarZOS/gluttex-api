
# here, we make schema translations

from core.api_models import AppUser_API, Location_API, Person_API
from core.messages import APPUSER_ALREADY_EXISTS, SUCCESS_MESSAGE
from core.models import Address, AppUser, BloodType, Location, Person, PersonDetails
from features.insertion import get_existent_object, insert_or_complete_or_raise
from features.person.person_fetch import fetch_person, fetch_person_object
from features.person.person_insert import generate_person_object
from features.search import find_object_by_id
from features.user.user_fetch import fetch_user_by_id, fetch_user_by_name, fetch_user_type_by_id, fetch_user_type_object_by_id



def insert_user(user: AppUser_API,mensch: Person_API=None,location: Location_API=None):
    
    if fetch_user_by_name(user.app_user_name) != []:
        raise Exception(APPUSER_ALREADY_EXISTS)

    user_type = fetch_user_type_object_by_id(user.app_user_type_id)

    app_user = AppUser(
                        # id_app_user= user.id_app_user,
                        app_user_name= user.app_user_name,
                        app_user_password= user.app_user_password,
                        app_user_preferences= user.app_user_preferences,
                        app_user_image = user.app_user_image,
                        # app_user_person_id= person.id_person,
                        app_user_type_id= user_type.id_app_user_type,
                        )
    if mensch:
        person_object = fetch_person_object(mensch.id_person)
        if person_object :
            app_user.app_user_person_id= person_object.id_person
        else:
            person = generate_person_object(mensch,location)
            app_user.app_user_person = person


    code,nutzer,msg = insert_or_complete_or_raise(app_user)
    if (code == 1): raise Exception(msg)
    
    return nutzer






