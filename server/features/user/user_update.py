from core.models import *
from features.insertion import  update_record_in_api

def update_api_user_password(user_record , hashed_password):
    
    user_record.app_user_password = hashed_password

    return update_record_in_api(user_record)
    