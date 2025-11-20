from fastapi import APIRouter, status
from core.api_models import Ingredient_API, Recipe_API, RecipeImage_API
from features.medical.recipe.recipe_fetch import (
    fetch_recipe_record_by_id, get_ingredients, 
    get_recipe_categories, get_recipe_image_by_id, get_recipes_by
)
from features.medical.recipe.recipe_insert import insert_ingredient, insert_recipe
from features.medical.recipe.recipe_update import update_recipe
from features.medical.recipe.recipe_delete import delete_recipe

recipe_router = APIRouter()

# ----------------- Recipe Endpoints -----------------


@recipe_router.get("/recipe/{recipe_id}")
def get_recipe_by_id(recipe_id: int):
    """
    Retrieve a recipe by its ID.
    """
    return fetch_recipe_record_by_id(recipe_id)

@recipe_router.get("/recipe/{user_id}/{category_id}/{offset}/{limit}")
def get_recipes(user_id:int,category_id: int,offset: int,limit: int):
    """
    Retrieve recipes by category.
    """
    return get_recipes_by(user_id,category_id,offset,limit)

@recipe_router.get("/recipe/category/all")
def get_recipe_category_list():
    """
    Fetch all recipe categories.
    """
    return get_recipe_categories()



@recipe_router.get("/ingredient/{offset}/{limit}")
def get_ingredients_list(offset: int, limit: int):
    """
    Retrieve all available ingredients.
    """
    return get_ingredients(offset, limit)

# ----------------- Recipe Image Endpoint -----------------

@recipe_router.get("/image/recipe/{image_id}")
def get_recipe_image(image_id: int):
    """
    Fetch a recipe image by ID.
    """
    return get_recipe_image_by_id(image_id)

# ----------------- Recipe Modification Endpoints -----------------

@recipe_router.put("/recipe/{recipe_id}")
def update_recipe_details(recipe_id: int, recipe: Recipe_API, image: RecipeImage_API):
    """
    Update recipe details.
    """
    return update_recipe(recipe_id, recipe, image)

@recipe_router.post("/recipe/add")
async def insert_new_recipe(recipe: Recipe_API, image: RecipeImage_API):
    """
    Insert a new recipe.
    """
    return await insert_recipe(recipe, image)
    
@recipe_router.post("/ingredient/add")
async def insert_new_ingredient(ingredient: Ingredient_API):
    """
    Insert a new ingredient.
    """
    return await insert_ingredient(ingredient)

@recipe_router.delete("/recipe/delete/{recipe_id}")
def delete_recipe_by_id(recipe_id: int):
    """
    Delete a recipe by ID.
    """
    return delete_recipe(recipe_id)
