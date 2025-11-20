# here, we make schema translations

from core.exception_handler import APIException
from core.messages import *
from features.insertion import delete_record_from_api
from features.medical.recipe.recipe_fetch import fetch_only_recipe_by_id, fetch_recipe_containments, fetch_recipe_record_by_id, get_recipe_image_by_id

def delete_recipe(recipe_id: int):
    recipes = fetch_only_recipe_by_id(recipe_id)
    if recipes == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=RECIPE_NOT_EXISTS,message=f"{RECIPE_DELETE_FAILED}: {recipe_id}")
    
    containments = fetch_recipe_containments(recipe_id)

    images = get_recipe_image_by_id(recipe_id)

    for v in containments:
        delete_containment(v)
    
    for img in images:
        delete_record_from_api(img)
            


    # for now, just delete the recipe, since we don't want to delete person records
    return delete_record_from_api(recipes[0])

def delete_containment(containment):
    # for now, just delete the recipe, since we don't want to delete person records
    return delete_record_from_api(containment)