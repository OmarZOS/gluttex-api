
# here, we make schema translations

import uuid
from core.exception_handler import APIException
from features.media_net import upload_image
from core.api_models import Ingredient_API, Recipe_API, RecipeImage_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.medical.recipe.recipe_fetch import  fetch_recipe_by_name, fetch_recipe_category_object_by_id, get_ingredient_by_id, get_ingredient_by_name
from features.app.user.user_fetch import fetch_user_by_id
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
        raise APIException(status= HTTP_409_CONFLICT,code=RECIPE_ALREADY_EXISTS)

    recipe_category = fetch_recipe_category_object_by_id(recipe_api.recipe_category_id)
    if recipe_category == None : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=RECIPE_CATEGORY_NOT_EXISTS)

    recipe_owners = fetch_user_by_id(recipe_api.recipe_owner_id)
    if recipe_owners == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=APPUSER_NOT_EXISTS)

    recipe = build_recipe(recipe_api)

    recipe.recipe_category_id = recipe_category.id_recipe_category    

    if (image.recipe_image_url):
        # inserted_image_url = await upload_image("recipe",recipe_api.recipe_owner_id,uuid.uuid4(),image.recipe_image_url)
        recipe_image = RecipeImage(recipe_image_url  = image.recipe_image_url)
        recipe.recipe_image = [recipe_image]

    if (recipe_api.recipe_ingredients):
        # id_recipe = recipe.id_recipe
        ingredient_list = []
        for id,value in recipe_api.recipe_ingredients.items():
            containment = RecipeContainsIngredient(contained_ingredient_id =id,contained_quantity=value)
            ingredient_list.append(containment)
        recipe.recipe_contains_ingredient = ingredient_list

    try:
        recipe = insert_or_complete_or_raise(recipe)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,details=f"{str(e)}",code=RECIPE_INSERT_FAILED)


    return recipe


async def insert_ingredient(ingredient: Ingredient_API):
    
    ingredients = get_ingredient_by_name(ingredient.ingredient_name)
    if ingredients != [] : 
        raise APIException(status= HTTP_409_CONFLICT,code=INGREDIENT_ALREADY_EXISTS)
    ingredient_model = Ingredient(ingredient_name=ingredient.ingredient_name,ingredient_icon_url=ingredient.ingredient_icon_url,ingredient_quantifier= ingredient.ingredient_quantifier)
    try:
        new_ingredient = insert_or_complete_or_raise(ingredient_model)
    except APIException as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=INGREDIENT_INSERT_FAILED,details=f"{str(e)}")
    return new_ingredient
