
from core.api_models import Recipe_API
from core.models import  Recipe, RecipeCategory
import storage.storage_broker as storage_broker




def fetch_recipe_by_id(prod_id: int):
    return storage_broker.get(Recipe,{Recipe.id_recipe:prod_id},[])


def fetch_recipe_by_name(recipe_name: str):
    records = storage_broker.get(Recipe,{Recipe.recipe_name:recipe_name},[])
    if records == []:
        return None
    return records[0]




# def fetch_recipes_by_category(Category_id: int):
#     return storage_broker.get(Category,{Category.categoryId:Category_id},[])

def get_recipes_by_category_id(category_id: int):
    return storage_broker.get(Recipe,{Recipe.recipe_category_id:category_id},[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_owner])

def get_recipe_categories():
    return storage_broker.get(RecipeCategory)

def fetch_all_recipe():
    return storage_broker.get(Recipe,None,[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_image])
