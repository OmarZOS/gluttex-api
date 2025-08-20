


# here, we make schema translations

from datetime import datetime
from core.exception_handler import APIException
from features.recipe.recipe_delete import delete_containment
from core.api_models import Recipe_API, RecipeImage_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.recipe.recipe_fetch import fetch_recipe_by_name, fetch_recipe_containments, fetch_recipe_image_by_id, fetch_recipe_record_by_id
from features.recipe.recipe_insert import fetch_recipe_category_object_by_id





def update_recipe(recipe_id: int, recipe_api: Recipe_API, image: RecipeImage_API):
    recipe_category = fetch_recipe_category_object_by_id(recipe_api.recipe_category_id)
    if recipe_category == []: 
        raise APIException(status= HTTP_404_NOT_FOUND,code=RECIPE_ALREADY_EXISTS,message=RECIPE_CATEGORY_NOT_EXISTS,details=f"{str(e)}")
    
    
    recipes_old = fetch_recipe_record_by_id(recipe_id)
    if recipes_old == []: 
        raise APIException(status= HTTP_404_NOT_FOUND,code=RECIPE_ALREADY_EXISTS,message=RECIPE_NOT_EXISTS,details=f"{str(e)}")
    
    recipe_old = recipes_old[0]
    
    if(recipe_old.recipe_name != recipe_api.recipe_name):
        other_recipes = fetch_recipe_by_name(recipe_api.recipe_name)
        if other_recipes != None :
            raise APIException(status= HTTP_409_CONFLICT,code=RECIPE_ALREADY_EXISTS,message=RECIPE_ALREADY_EXISTS,details=f"{str(e)}")

    # update basic fields
    recipe_old.recipe_preparation_time = recipe_api.recipe_preparation_time
    recipe_old.recipe_instructions = recipe_api.recipe_instructions
    recipe_old.recipe_name = recipe_api.recipe_name
    recipe_old.recipe_description = recipe_api.recipe_description
    recipe_old.recipe_last_updated = datetime.now()
    recipe_old.recipe_category_id = recipe_category.id_recipe_category
    try:
        # persist recipe update
        recipe = update_record_in_api(recipe_old)
    except Exception as e:
        raise APIException(status= HTTP_409_CONFLICT,code=RECIPE_UPDATE_FAILED,details=f"{str(e)}")

    recipe_ingredients = fetch_recipe_containments(recipe_old.id_recipe)

    # --- Ingredient sync logic ---
        # Convert old containments into a dict for quick lookup
    old_containments = {
        containment.contained_ingredient_id: containment
        for containment in recipe_ingredients
    }

    for ingredient_id,ingredient_qty in recipe_api.recipe_ingredients.items():
        # ingredient_id = ingredient_obj.contained_ingredient_id  # adjust field name if different
        # ingredient_qty = ingredient_obj.contained_quantity  # adjust field name if different

        if ingredient_id in old_containments:
            # Update the existing containment
            containment = old_containments[ingredient_id]
            containment.contained_quantity = ingredient_qty
            
            try:
                update_record_in_api(containment)
            except Exception as e:
                raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=RECIPE_UPDATE_FAILED,message=RECIPE_UPDATE_FAILED,details=f"{str(e)}")
            
            old_containments.pop(ingredient_id) 
        else:
            # Create a new containment
            containment = RecipeContainsIngredient(
                contained_ingredient_id=ingredient_id,
                contained_quantity=ingredient_qty,
                containing_recipe_id=recipe_old.id_recipe
            )
            try:
                insert_or_complete_or_raise(containment)
            except Exception as e:
                raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=RECIPE_UPDATE_FAILED,message=RECIPE_UPDATE_FAILED,details=f"{str(e)}")

        # updated_containments.append(containment)

    # --- image handling ---
    if image.recipe_image_url:
        if image.id_recipe_image == 0:
            _image = RecipeImage(recipe_image_url=image.recipe_image_url)
            _image.recipe_ref = recipe_old
            code, _, msg = insert_or_complete_or_raise(_image)
        else:
            same_image = fetch_recipe_image_by_id(image.id_recipe_image)[0]
            same_image.recipe_image_url = image.recipe_image_url
            update_record_in_api(same_image)

    for k,v in  old_containments.items():
        delete_containment(v)

    final_recipes = fetch_recipe_record_by_id(recipe_id)[0]
    
    return final_recipes






