
# here, we make schema translations

import json
from core.api_models import User_API
from core.messages import SUCCESS_MESSAGE
from core.models import UserMed, UserMedPreferences, UserMedRole
from features.insertion import insert_or_complete_or_raise

def insert_preferences(user: User_API):
    med_pref = UserMedPreferences(
        user_preferencesId=user.preferences_id,
        preferences=json.dumps(user.user_preferences))
    
    code,med_pref,msg = insert_or_complete_or_raise(med_pref)
    if (code == 1): return msg
    return med_pref


def insert_role(user: User_API):
    med_role = UserMedRole(
        user_RoleId=user.user_RoleId,
        user_role=user.user_role)
    
    code,med_role,msg = insert_or_complete_or_raise(med_role)
    if (code == 1): return msg
    return med_role

def insert_user(user: User_API):

    preferences = insert_preferences(user)
    role = insert_role(user)

    med_user = UserMed(
                        user_MedId= user.user_MedId,
                        user_Medname= user.user_Medname,
                        email= user.email,
                        password= user.password,
                        fullName= user.fullName,
                        address= user.address,
                        User_MedRole = role,
                        User_MedPreferences = preferences
                        )
    code,med_user,msg = insert_or_complete_or_raise(med_user)
    if (code == 1): return msg
    
    return SUCCESS_MESSAGE






