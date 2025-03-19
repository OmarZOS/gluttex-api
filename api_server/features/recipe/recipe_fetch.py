
from core.models import  Ingredient, Recipe, RecipeCategory, RecipeContainsIngredient, RecipeImage
import storage.storage_broker as storage_broker




def get_recipe_image_by_id(image_id: int):
    return storage_broker.get(RecipeImage,{RecipeImage.id_recipe_image:image_id},[],None,[])


def fetch_recipe_by_id(prod_id: int):
    return storage_broker.get(Recipe,{Recipe.id_recipe:prod_id}
                              ,[RecipeContainsIngredient],
                              [
                                  {
                                      Recipe.recipe_contains_ingredient:
                                        [RecipeContainsIngredient.contained_quantity
                                            ,RecipeContainsIngredient.contained_ingredient_id
                                        ]
                                  }
                              ]
                              )


def fetch_recipe_by_name(recipe_name: str):
    records = storage_broker.get(Recipe,{Recipe.recipe_name:recipe_name},[])
    if records == []:
        return None
    return records[0]



def fetch_recipe_category_object_by_id(category_id: str):
    record = storage_broker.get(RecipeCategory,{RecipeCategory.id_recipe_category:category_id},None,[])
    if record == []:
        return None
    category = RecipeCategory(id_recipe_category = record[0].id_recipe_category)
    return category 


# def fetch_recipes_by_category(Category_id: int):
#     return storage_broker.get(Category,{Category.categoryId:Category_id},[])

def get_recipes_by_category_id(category_id: int):
    return storage_broker.get(Recipe,{Recipe.recipe_category_id:category_id},[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_owner])

def get_recipe_categories():
    return storage_broker.get(RecipeCategory)

def get_ingredients():
    return storage_broker.get(Ingredient)


def fetch_all_recipe(offset: int,limit: int):
    return storage_broker.get(Recipe,None,[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_contains_ingredient,{Recipe.recipe_image: [RecipeImage.id_recipe_image]}],None,offset,limit)
