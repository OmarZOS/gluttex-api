# routers/recipe_router.py (updated)
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from services.helpers.auth.auth_dependencies import get_current_user_id
from core.models.api_models import Recipe_API, RecipeImage_API, Ingredient_API
from services.recipe_service import RecipeService

recipe_router = APIRouter()

def get_recipe_service() -> RecipeService:
    return RecipeService()

# ==================== Recipe Endpoints ====================

@recipe_router.get("/recipes")
def get_all_recipes(
    user_id: int = Query(0, description="Filter by user ID"),
    category_id: int = Query(0, description="Filter by category ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get recipes with filters"""
    if user_id > 0:
        return recipe_service.get_recipes_by_user(user_id, offset, limit)
    elif category_id > 0:
        return recipe_service.get_recipes_by_category(category_id, offset, limit)
    else:
        return recipe_service.get_all_recipes(offset, limit)

@recipe_router.get("/recipes/categories")
def get_recipe_categories(
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get all recipe categories"""
    return recipe_service.get_recipe_categories()

@recipe_router.get("/recipes/{recipe_id}")
def get_recipe(
    recipe_id: int,
    full: bool = Query(True, description="Include all related data"),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get recipe by ID"""
    return recipe_service.get_recipe_by_id(recipe_id, full)

@recipe_router.post("/recipes")
async def create_recipe(
    recipe: Recipe_API,
    image: RecipeImage_API,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Create a new recipe"""
    recipe.recipe_owner_id = user_id
    return await recipe_service.create_recipe(recipe, image)

@recipe_router.put("/recipes/{recipe_id}")
def update_recipe(
    recipe_id: int,
    recipe: Recipe_API,
    image: RecipeImage_API,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Update an existing recipe"""
    
    return recipe_service.update_recipe(recipe_id, recipe, image,user_id)

@recipe_router.delete("/recipes/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Delete a recipe"""
    return recipe_service.delete_recipe(recipe_id, user_id)

# ==================== Ingredient Endpoints ====================

@recipe_router.get("/recipes/ingredients/all")
def get_all_ingredients(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get all ingredients"""
    return recipe_service.get_all_ingredients(offset, limit)

@recipe_router.get("/recipes/ingredients/{ingredient_id}")
def get_ingredient(
    ingredient_id: int,
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Get ingredient by ID"""
    return recipe_service.get_ingredient_by_id(ingredient_id)

@recipe_router.post("/recipes/ingredients")
async def create_ingredient(
    ingredient: Ingredient_API,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Create a new ingredient"""
    return await recipe_service.create_ingredient(ingredient,user_id)

@recipe_router.put("/recipes/ingredients/{ingredient_id}")
def update_ingredient(
    ingredient_id: int,
    ingredient: Ingredient_API,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Update an existing ingredient"""
    return recipe_service.update_ingredient(ingredient_id, ingredient,user_id)

@recipe_router.delete("/recipes/ingredients/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    user_id: int = Depends(get_current_user_id),
    recipe_service: RecipeService = Depends(get_recipe_service)
):
    """Delete an ingredient"""
    return recipe_service.delete_ingredient(ingredient_id, user_id)