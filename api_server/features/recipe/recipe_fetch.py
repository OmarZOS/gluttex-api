
from core.models import  AppUser, Ingredient, Recipe, RecipeCategory, RecipeContainsIngredient, RecipeImage, RecipeReaction
import storage.storage_broker as storage_broker




def get_recipe_image_by_id(image_id: int):
    return storage_broker.get(RecipeImage,{RecipeImage.id_recipe_image:image_id},[],None,[])

def get_ingredient_by_id(id: int):
    return storage_broker.get(Ingredient,{Ingredient.id_ingredient:id},[],None,[])

def get_ingredient_by_name(name: str):
    return storage_broker.get(Ingredient,{Ingredient.ingredient_name:name})

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

def fetch_recipe_image_by_id(image_id: str):
    records = storage_broker.get(
        RecipeImage
        ,{
            RecipeImage.id_recipe_image:image_id
        }
        ,None
        ,None)
    # if records == []: return None
    return records


def fetch_recipe_record_by_id(recipe: int):
    return storage_broker.get(Recipe,{Recipe.id_recipe:recipe},[],[
        Recipe.recipe_category
,Recipe.recipe_owner
,Recipe.recipe_contains_ingredient
,Recipe.recipe_image
,Recipe.recipe_reaction    ])

def fetch_recipe_containments(recipe_id: int):
    return storage_broker.get(RecipeContainsIngredient,{RecipeContainsIngredient.containing_recipe_id:recipe_id})


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

def get_recipes_by(user_id: int,category_id: int,offset: int,limit: int):
    conditions = {}
    if category_id and category_id !=0:
        conditions[Recipe.recipe_category_id]=category_id
    if user_id and user_id !=0:
        conditions[Recipe.recipe_owner_id]=user_id
    
    return storage_broker.get(Recipe,conditions,[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_owner,Recipe.recipe_image],offset=offset,limit=limit)

def get_recipe_categories():
    return storage_broker.get(RecipeCategory)

def get_ingredients(offset: int, limit: int):
    return storage_broker.get(Ingredient, None, [], [], offset=offset, limit=limit)

# def fetch_all_recipe(offset: int,limit: int):
#     return storage_broker.get(Recipe,None,[RecipeCategory],[Recipe.recipe_category,Recipe.recipe_contains_ingredient,{Recipe.recipe_image: [RecipeImage.id_recipe_image,RecipeImage.recipe_image_url]}],offset,limit)
