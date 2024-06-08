from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import Recipe_API, RecipeImage_API
from features.recipe.recipe_fetch import fetch_all_recipe, fetch_recipe_by_id, get_recipe_categories, get_recipe_image_by_id, get_recipes_by_category_id
from features.recipe.recipe_insert import insert_recipe
from features.recipe.recipe_update import update_recipe
from features.recipe.recipe_delete import delete_recipe



recipe_router = APIRouter()


# # Recipe related endpoints

@recipe_router.get("/Recipe/all")
def get_all_Recipes():
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(fetch_all_recipe()))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch recipes."}),
    )
    return res
    

@recipe_router.post("/recipe/{recipe_id}")
def update_Recipe(recipe_id: int,recipe: Recipe_API, image: RecipeImage_API):
    
    try:
        res = update_recipe(recipe_id,recipe, image)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't update recipe."}),
    )
    return res

@recipe_router.put("/recipe/add")
def insert_Recipe(recipe: Recipe_API, image: RecipeImage_API):
    
    try:
        res = insert_recipe(recipe, image)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert recipe."}),
    )
    return res

@recipe_router.get("/image/recipe/{image_id}")
def getRecipeImage(image_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_recipe_image_by_id(image_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch image."}),
    )
    return res

@recipe_router.get("/recipe/{Recipe_id}")
def get_Recipe_by_id(Recipe_id: int):

    try:
        res = fetch_recipe_by_id(Recipe_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch recipe."}),
    )
    return res


@recipe_router.delete("/Recipe/delete/{Recipe_id}")
def delete_Recipe_by_id(Recipe_id: int):

    try:
        res = delete_recipe(Recipe_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete recipe."}),
    )
    return res

@recipe_router.get("/recipe/category/{category_id}")
def get_recipes_by_category(category_id: int):
    try:
        res = get_recipes_by_category_id(category_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get recipes."}),
    )
    return res

@recipe_router.get("/recipe/Category/all")
def get_categories():
    try:
        res = get_recipe_categories()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch recipe."}),
    )
    return res

