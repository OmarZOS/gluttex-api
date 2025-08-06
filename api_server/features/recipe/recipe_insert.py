
# here, we make schema translations

import uuid
from features.media_net import upload_image
from core.api_models import Recipe_API, RecipeImage_API
from core.messages import APPUSER_NOT_EXISTS, RECIPE_ALREADY_EXISTS, RECIPE_CATEGORY_NOT_EXISTS, RECIPE_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.recipe.recipe_fetch import  fetch_recipe_by_name, fetch_recipe_category_object_by_id
from features.user.user_fetch import fetch_user_by_id
from datetime import datetime;



def build_recipe(recipe: Recipe_API):
    return Recipe(
        recipe_preparation_time  = recipe.recipe_preparation_time,
        recipe_instructions  = recipe.recipe_instructions,
        recipe_name  = recipe.recipe_name,
        recipe_owner_id = recipe.recipe_owner_id,
        recipe_description  = recipe.recipe_description,
        recipe_creation  = datetime.now(),
        recipe_last_updated  = datetime.now())

async def insert_recipe(recipe_api: Recipe_API, image: RecipeImage_API):
    
    recipe_old = fetch_recipe_by_name(recipe_api.recipe_name)
    if recipe_old != None : 
        raise Exception(RECIPE_ALREADY_EXISTS)

    recipe_category = fetch_recipe_category_object_by_id(recipe_api.recipe_category_id)
    if recipe_category == None : 
        raise Exception(RECIPE_CATEGORY_NOT_EXISTS)

    recipe_owners = fetch_user_by_id(recipe_api.recipe_owner_id)
    if recipe_owners == [] : 
        raise Exception(APPUSER_NOT_EXISTS)

    recipe = build_recipe(recipe_api)

    recipe.recipe_category_id = recipe_category.id_recipe_category    

    if (image.recipe_image_data):
        # inserted_image_url = await upload_image("recipe",recipe_api.recipe_owner_id,uuid.uuid4(),image.recipe_image_data)
        recipe_image = RecipeImage(recipe_image_url  = image.recipe_image_data)
        recipe.recipe_image = [recipe_image]


    
    if (recipe_api.recipe_ingredients):
        # id_recipe = recipe.id_recipe
        ingredient_list = []
        for id,value in recipe_api.recipe_ingredients.items():
            containment = RecipeContainsIngredient(contained_ingredient_id =id,contained_quantity=value)
            ingredient_list.append(containment)
            # code,containment,msg = insert_or_complete_or_raise(containment)
        recipe.recipe_contains_ingredient = ingredient_list

    
    code,recipe,msg = insert_or_complete_or_raise(recipe)
    if (code == 1): return msg
    return recipe

