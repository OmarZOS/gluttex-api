# repositories/recipe_repository.py
from typing import Optional, List
from core.models.models import (
    Recipe, RecipeCategory, RecipeContainsIngredient, 
    RecipeImage, Ingredient, RecipeReaction
)
import storage.storage_broker as storage_broker

class RecipeRepository:
    """Repository for Recipe-related database operations"""
    
    # ==================== Recipe Operations ====================
    
    def get_recipe_by_id(self, recipe_id: int, eager_load: bool = True) -> Optional[Recipe]:
        """Get recipe by ID with optional eager loading"""
        if eager_load:
            records = storage_broker.get(
                Recipe,
                {Recipe.id_recipe: recipe_id},
                [RecipeContainsIngredient],
                [
                    {
                        Recipe.recipe_contains_ingredient: [
                            RecipeContainsIngredient.contained_quantity,
                            RecipeContainsIngredient.contained_ingredient_id
                        ]
                    },
                    Recipe.recipe_reaction
                ]
            )
        else:
            records = storage_broker.get(Recipe, {Recipe.id_recipe: recipe_id}, [], [])
        return records[0] if records else None
    
    def get_recipe_record_by_id(self, recipe_id: int) -> Optional[Recipe]:
        """Get recipe record with relationships"""
        records = storage_broker.get(
            Recipe,
            {Recipe.id_recipe: recipe_id},
            [],
            [
                Recipe.recipe_category,
                Recipe.recipe_owner,
                Recipe.recipe_contains_ingredient,
                Recipe.recipe_image,
                Recipe.recipe_reaction
            ]
        )
        return records[0] if records else None
    
    def get_recipe_by_name(self, recipe_name: str) -> Optional[Recipe]:
        """Get recipe by name"""
        records = storage_broker.get(Recipe, {Recipe.recipe_name: recipe_name}, [])
        return records[0] if records else None
    
    def get_recipes_by_user(self, user_id: int, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by user ID"""
        return storage_broker.get(
            Recipe,
            {Recipe.recipe_owner_id: user_id},
            [RecipeCategory],
            [Recipe.recipe_contains_ingredient, Recipe.recipe_category, Recipe.recipe_owner, Recipe.recipe_image],
            offset=offset,
            limit=limit
        )
    
    def get_recipes_by_category(self, category_id: int, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by category ID"""
        return storage_broker.get(
            Recipe,
            {Recipe.recipe_category_id: category_id},
            [RecipeCategory],
            [Recipe.recipe_contains_ingredient, Recipe.recipe_category, Recipe.recipe_owner, Recipe.recipe_image],
            offset=offset,
            limit=limit
        )
    
    def get_all_recipes(self, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get all recipes with pagination"""
        return storage_broker.get(
            Recipe,
            None,
            [RecipeCategory],
            [Recipe.recipe_category, Recipe.recipe_contains_ingredient, {Recipe.recipe_image: [RecipeImage.id_recipe_image, RecipeImage.recipe_image_url]}],
            offset=offset,
            limit=limit
        )
    
    def create_recipe(self, recipe: Recipe) -> Recipe:
        """Create a new recipe"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(recipe)
    
    def update_recipe(self, recipe: Recipe) -> Recipe:
        """Update an existing recipe"""
        from features.insertion import update_record_in_api
        return update_record_in_api(recipe)
    
    def delete_recipe(self, recipe: Recipe) -> bool:
        """Delete a recipe"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(recipe)
    
    # ==================== Recipe Category Operations ====================
    
    def get_recipe_category_by_id(self, category_id: str) -> Optional[RecipeCategory]:
        """Get recipe category by ID"""
        records = storage_broker.get(RecipeCategory, {RecipeCategory.id_recipe_category: category_id}, None, [])
        if records:
            return RecipeCategory(id_recipe_category=records[0].id_recipe_category)
        return None
    
    def get_all_recipe_categories(self) -> List[RecipeCategory]:
        """Get all recipe categories"""
        return storage_broker.get(RecipeCategory, {}, None, [])
    
    # ==================== Recipe Contains Ingredient Operations ====================
    
    def get_recipe_containments(self, recipe_id: int) -> List[RecipeContainsIngredient]:
        """Get all containments for a recipe"""
        return storage_broker.get(
            RecipeContainsIngredient,
            {RecipeContainsIngredient.containing_recipe_id: recipe_id},
            None,
            []
        )
    
    def create_containment(self, containment: RecipeContainsIngredient) -> RecipeContainsIngredient:
        """Create a containment"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(containment)
    
    def update_containment(self, containment: RecipeContainsIngredient) -> RecipeContainsIngredient:
        """Update a containment"""
        from features.insertion import update_record_in_api
        return update_record_in_api(containment)
    
    def delete_containment(self, containment: RecipeContainsIngredient) -> bool:
        """Delete a containment"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(containment)
    
    # ==================== Recipe Image Operations ====================
    
    def get_recipe_image_by_id(self, image_id: int) -> List[RecipeImage]:
        """Get recipe image by ID"""
        return storage_broker.get(RecipeImage, {RecipeImage.id_recipe_image: image_id}, None, None)
    
    def get_recipe_images(self, recipe_id: int) -> List[RecipeImage]:
        """Get all images for a recipe"""
        return storage_broker.get(RecipeImage, {RecipeImage.recipe_ref_id: recipe_id}, None, None)
    
    def create_recipe_image(self, image: RecipeImage) -> RecipeImage:
        """Create a recipe image"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(image)
    
    def update_recipe_image(self, image: RecipeImage) -> RecipeImage:
        """Update a recipe image"""
        from features.insertion import update_record_in_api
        return update_record_in_api(image)
    
    def delete_recipe_image(self, image: RecipeImage) -> bool:
        """Delete a recipe image"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(image)
    
    # ==================== Ingredient Operations ====================
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Get ingredient by ID"""
        records = storage_broker.get(Ingredient, {Ingredient.id_ingredient: ingredient_id}, [], None)
        return records[0] if records else None
    
    def get_ingredient_by_name(self, name: str) -> Optional[Ingredient]:
        """Get ingredient by name"""
        records = storage_broker.get(Ingredient, {Ingredient.ingredient_name: name})
        return records[0] if records else None
    
    def get_all_ingredients(self, offset: int = 0, limit: int = 100) -> List[Ingredient]:
        """Get all ingredients with pagination"""
        return storage_broker.get(Ingredient, None, [], [], offset=offset, limit=limit)
    
    def create_ingredient(self, ingredient: Ingredient) -> Ingredient:
        """Create an ingredient"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(ingredient)
    
    def update_ingredient(self, ingredient: Ingredient) -> Ingredient:
        """Update an ingredient"""
        from features.insertion import update_record_in_api
        return update_record_in_api(ingredient)
    
    def delete_ingredient(self, ingredient: Ingredient) -> bool:
        """Delete an ingredient"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(ingredient)