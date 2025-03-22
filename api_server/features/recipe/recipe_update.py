


# here, we make schema translations

from datetime import datetime
from core.api_models import Recipe_API, RecipeImage_API
from core.messages import RECIPE_CATEGORY_NOT_EXISTS, RECIPE_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.recipe.recipe_fetch import fetch_recipe_by_id
from features.recipe.recipe_insert import fetch_recipe_category_object_by_id





def update_recipe(recipe_id: int,recipe_api: Recipe_API, image: RecipeImage_API):
    

    recipe_category = fetch_recipe_category_object_by_id(recipe_api.recipe_category_id)
    if recipe_category == [] : 
        raise Exception(RECIPE_CATEGORY_NOT_EXISTS)
    
    recipes_old = fetch_recipe_by_id(recipe_id)
    if recipes_old == [] : 
        raise Exception(RECIPE_NOT_EXISTS)
    recipe_old = recipes_old[0]

    recipe_old.recipe_preparation_time  = recipe_api.recipe_preparation_time,
    recipe_old.recipe_instructions  = recipe_api.recipe_instructions,
    recipe_old.recipe_name  = recipe_api.recipe_name,
    recipe_old.recipe_description  = recipe_api.recipe_description,
    recipe_old.recipe_last_updated  = datetime.now(),

    # recipe_old.recipe_provider_id = recipe_suppliers[0].id_recipe_provider
    recipe_old.recipe_category_id = recipe_category.id_recipe_category
    
    recipe = update_record_in_api(recipe_old)
    if (image.id_recipe_image==0):
        if (image.recipe_image_url):
            recipe_image = RecipeImage(recipe_image_url = image.recipe_image_url)
            recipe_image.recipe_ref_id = recipe_old.id_recipe
            code,new_image,msg = insert_or_complete_or_raise(recipe_image)
    
    return recipe





