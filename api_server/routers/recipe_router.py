from fastapi import APIRouter, HTTPException, status
from core.api_models import Recipe_API, RecipeImage_API
from features.recipe.recipe_fetch import (
    fetch_all_recipe, fetch_recipe_record_by_id, get_ingredients, 
    get_recipe_categories, get_recipe_image_by_id, get_recipes_by_category_id
)
from features.recipe.recipe_insert import insert_recipe
from features.recipe.recipe_update import update_recipe
from features.recipe.recipe_delete import delete_recipe

recipe_router = APIRouter()

# ----------------- Recipe Endpoints -----------------

@recipe_router.get("/recipe/all/{offset}/{limit}")
def get_all_recipes(offset: int, limit: int):
    """
    Fetch all recipes with pagination.
    """
    try:
        return fetch_all_recipe(offset, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch recipes: {str(e)}"
        )

@recipe_router.get("/recipe/{recipe_id}")
def get_recipe_by_id(recipe_id: int):
    """
    Retrieve a recipe by its ID.
    """
    try:
        return fetch_recipe_record_by_id(recipe_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch recipe: {str(e)}"
        )

@recipe_router.get("/recipe/category/{category_id}/{offset}/{limit}")
def get_recipes_by_category(category_id: int,offset: int,limit: int):
    """
    Retrieve recipes by category.
    """
    try:
        return get_recipes_by_category_id(category_id,offset,limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch recipes by category: {str(e)}"
        )

@recipe_router.get("/recipe/category/all")
def get_recipe_categories():
    """
    Fetch all recipe categories.
    """
    try:
        return get_recipe_categories()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch recipe categories: {str(e)}"
        )



@recipe_router.get("/recipe/ingredients/all/{offset}/{limit}")
def get_ingredients_list(offset: int, limit: int):
    """
    Retrieve all available ingredients.
    """
    try:
        return get_ingredients(offset, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch ingredients: {str(e)}"
        )

# ----------------- Recipe Image Endpoint -----------------

@recipe_router.get("/image/recipe/{image_id}")
def get_recipe_image(image_id: int):
    """
    Fetch a recipe image by ID.
    """
    try:
        return get_recipe_image_by_id(image_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch recipe image: {str(e)}"
        )

# ----------------- Recipe Modification Endpoints -----------------

@recipe_router.post("/recipe/{recipe_id}")
def update_recipe_details(recipe_id: int, recipe: Recipe_API, image: RecipeImage_API):
    """
    Update recipe details.
    """
    try:
        return update_recipe(recipe_id, recipe, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update recipe: {str(e)}"
        )

@recipe_router.put("/recipe/add")
async def insert_new_recipe(recipe: Recipe_API, image: RecipeImage_API):
    """
    Insert a new recipe.
    """
    try:
        return await insert_recipe(recipe, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert recipe: {str(e)}"
        )

@recipe_router.delete("/recipe/delete/{recipe_id}")
def delete_recipe_by_id(recipe_id: int):
    """
    Delete a recipe by ID.
    """
    try:
        return delete_recipe(recipe_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete recipe: {str(e)}"
        )
