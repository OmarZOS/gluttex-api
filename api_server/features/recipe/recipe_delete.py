# here, we make schema translations

from core.messages import RECIPE_NOT_EXISTS
from features.insertion import delete_record_from_api
from features.recipe.recipe_fetch import fetch_recipe_record_by_id

def delete_recipe(recipe_id: int):
    recipes = fetch_recipe_record_by_id(recipe_id)
    if recipes == []:
        raise Exception(RECIPE_NOT_EXISTS)
    # for now, just delete the recipe, since we don't want to delete person records
    return delete_record_from_api(recipes[0])
