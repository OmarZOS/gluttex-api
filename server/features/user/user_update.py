


# here, we make schema translations

from datetime import datetime
from core.api_models import Recipe_API, RecipeImage_API
from core.messages import RECIPE_CATEGORY_NOT_EXISTS, RECIPE_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.recipe.recipe_fetch import fetch_recipe_by_id
from features.recipe.recipe_insert import fetch_recipe_category_object_by_id





def update_user_password(user_record , hashed_password):
    
    user_record.app_user_password = hashed_password

    return update_record_in_api(user_record)
    