# here, we make schema translations

from server.core.api_models import AppUser_API
from server.core.messages import APPUSER_ALREADY_EXISTS, APPUSER_NOT_EXISTS
from server.core.models import AppUser
from server.features.insertion import delete_record_from_api
from server.features.user.user_fetch import  fetch_user_by_id, fetch_user_object_by_id

def delete_user(user: AppUser_API):
    
    nutzers = fetch_user_by_id(user.id_app_user)
    if nutzers == []:
        raise Exception(APPUSER_NOT_EXISTS)
    # for now, just delete the user, since we don't want to delete person records
    return delete_record_from_api(nutzers[0])