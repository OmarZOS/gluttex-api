# services/recipe_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.api_models import Recipe_API, RecipeImage_API, Ingredient_API
from core.exception_handler import APIException
from core.messages import *
from core.models import Recipe, RecipeContainsIngredient, RecipeImage, Ingredient
from repositories.recipe_repository import RecipeRepository
from services.user_service import UserService

class RecipeService:
    """Service for recipe-related operations"""
    
    def __init__(self):
        self.recipe_repo = RecipeRepository()
        self.user_service = UserService()
    
    # ==================== Recipe Operations ====================
    
    def _build_recipe_model(self, recipe_data: Recipe_API) -> Recipe:
        """Build Recipe model from API data"""
        return Recipe(
            recipe_preparation_time=recipe_data.recipe_preparation_time,
            recipe_instructions=recipe_data.recipe_instructions,
            recipe_name=recipe_data.recipe_name,
            recipe_owner_id=recipe_data.recipe_owner_id,
            recipe_description=recipe_data.recipe_description,
            recipe_creation=datetime.now(),
            recipe_last_updated=datetime.now()
        )
    
    def get_recipe_by_id(self, recipe_id: int, full: bool = False) -> Recipe:
        """Get recipe by ID"""
        if full:
            recipe = self.recipe_repo.get_recipe_record_by_id(recipe_id)
        else:
            recipe = self.recipe_repo.get_recipe_by_id(recipe_id)
        
        if not recipe:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=RECIPE_NOT_EXISTS,
                message=f"{RECIPE_NOT_EXISTS}: {recipe_id}"
            )
        return recipe
    
    def get_recipes_by_user(self, user_id: int, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by user"""
        return self.recipe_repo.get_recipes_by_user(user_id, offset, limit)
    
    def get_recipes_by_category(self, category_id: int, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get recipes by category"""
        return self.recipe_repo.get_recipes_by_category(category_id, offset, limit)
    
    def get_all_recipes(self, offset: int = 0, limit: int = 100) -> List[Recipe]:
        """Get all recipes"""
        return self.recipe_repo.get_all_recipes(offset, limit)
    
    def get_recipe_categories(self) -> List:
        """Get all recipe categories"""
        return self.recipe_repo.get_all_recipe_categories()
    
    async def create_recipe(
        self,
        recipe_data: Recipe_API,
        image_data: RecipeImage_API
    ) -> Recipe:
        """Create a new recipe"""
        
        # Check if recipe name exists
        existing = self.recipe_repo.get_recipe_by_name(recipe_data.recipe_name)
        if existing:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=RECIPE_ALREADY_EXISTS,
                message=RECIPE_ALREADY_EXISTS
            )
        
        # Validate category
        category = self.recipe_repo.get_recipe_category_by_id(recipe_data.recipe_category_id)
        if not category:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=RECIPE_CATEGORY_NOT_EXISTS,
                message=RECIPE_CATEGORY_NOT_EXISTS
            )
        
        # Validate user
        user = self.user_service.get_user_by_id(recipe_data.recipe_owner_id)
        
        # Build recipe
        recipe = self._build_recipe_model(recipe_data)
        recipe.recipe_category_id = category.id_recipe_category
        
        # Handle image
        if image_data and image_data.recipe_image_url:
            recipe_image = RecipeImage(recipe_image_url=image_data.recipe_image_url)
            recipe.recipe_image = [recipe_image]
        
        # Handle ingredients
        if recipe_data.recipe_ingredients:
            ingredient_list = []
            for ingredient_id, quantity in recipe_data.recipe_ingredients.items():
                containment = RecipeContainsIngredient(
                    contained_ingredient_id=ingredient_id,
                    contained_quantity=quantity
                )
                ingredient_list.append(containment)
            recipe.recipe_contains_ingredient = ingredient_list
        
        # Save recipe
        try:
            return self.recipe_repo.create_recipe(recipe)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=RECIPE_INSERT_FAILED,
                details=str(e)
            )
    
    def update_recipe(
        self,
        recipe_id: int,
        recipe_data: Recipe_API,
        image_data: RecipeImage_API
    ) -> Recipe:
        """Update an existing recipe"""
        
        # Validate category
        category = self.recipe_repo.get_recipe_category_by_id(recipe_data.recipe_category_id)
        if not category:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=RECIPE_CATEGORY_NOT_EXISTS,
                message=RECIPE_CATEGORY_NOT_EXISTS
            )
        
        # Get existing recipe
        recipe = self.get_recipe_by_id(recipe_id, full=True)
        
        # Check name uniqueness
        if recipe.recipe_name != recipe_data.recipe_name:
            other = self.recipe_repo.get_recipe_by_name(recipe_data.recipe_name)
            if other:
                raise APIException(
                    status=HTTP_409_CONFLICT,
                    code=RECIPE_ALREADY_EXISTS,
                    message=RECIPE_ALREADY_EXISTS
                )
        
        # Update basic fields
        recipe.recipe_preparation_time = recipe_data.recipe_preparation_time
        recipe.recipe_instructions = recipe_data.recipe_instructions
        recipe.recipe_name = recipe_data.recipe_name
        recipe.recipe_description = recipe_data.recipe_description
        recipe.recipe_last_updated = datetime.now()
        recipe.recipe_category_id = category.id_recipe_category
        
        # Update recipe
        try:
            recipe = self.recipe_repo.update_recipe(recipe)
        except Exception as e:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=RECIPE_UPDATE_FAILED,
                details=str(e)
            )
        
        # Update ingredients
        self._sync_recipe_ingredients(recipe.id_recipe, recipe_data.recipe_ingredients)
        
        # Update image
        if image_data and image_data.recipe_image_url:
            self._handle_recipe_image(recipe.id_recipe, image_data)
        
        return self.get_recipe_by_id(recipe_id, full=True)
    
    def _sync_recipe_ingredients(self, recipe_id: int, new_ingredients: Dict[int, float]):
        """Sync recipe ingredients (add, update, delete)"""
        
        # Get existing containments
        old_containments = self.recipe_repo.get_recipe_containments(recipe_id)
        old_map = {c.contained_ingredient_id: c for c in old_containments}
        
        for ingredient_id, quantity in new_ingredients.items():
            if ingredient_id in old_map:
                # Update existing
                containment = old_map[ingredient_id]
                containment.contained_quantity = quantity
                self.recipe_repo.update_containment(containment)
                del old_map[ingredient_id]
            else:
                # Create new
                containment = RecipeContainsIngredient(
                    contained_ingredient_id=ingredient_id,
                    contained_quantity=quantity,
                    containing_recipe_id=recipe_id
                )
                self.recipe_repo.create_containment(containment)
        
        # Delete removed containments
        for containment in old_map.values():
            self.recipe_repo.delete_containment(containment)
    
    def _handle_recipe_image(self, recipe_id: int, image_data: RecipeImage_API):
        """Handle recipe image creation or update"""
        if image_data.id_recipe_image == 0:
            new_image = RecipeImage(recipe_image_url=image_data.recipe_image_url)
            new_image.recipe_ref_id = recipe_id
            self.recipe_repo.create_recipe_image(new_image)
        else:
            existing_images = self.recipe_repo.get_recipe_image_by_id(image_data.id_recipe_image)
            if existing_images:
                existing = existing_images[0]
                existing.recipe_image_url = image_data.recipe_image_url
                self.recipe_repo.update_recipe_image(existing)
    
    def delete_recipe(self, recipe_id: int) -> Dict[str, Any]:
        """Delete a recipe and all associated data"""
        
        recipe = self.get_recipe_by_id(recipe_id)
        
        # Delete containments
        containments = self.recipe_repo.get_recipe_containments(recipe_id)
        for containment in containments:
            self.recipe_repo.delete_containment(containment)
        
        # Delete images
        images = self.recipe_repo.get_recipe_images(recipe_id)
        for image in images:
            self.recipe_repo.delete_recipe_image(image)
        
        # Delete recipe
        success = self.recipe_repo.delete_recipe(recipe)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=RECIPE_DELETE_FAILED,
                message=f"{RECIPE_DELETE_FAILED}: {recipe_id}"
            )
        
        return {
            "message": f"Recipe {recipe_id} deleted successfully",
            "recipe_id": recipe_id
        }
    
    # ==================== Ingredient Operations ====================
    
    async def create_ingredient(self, ingredient_data: Ingredient_API) -> Ingredient:
        """Create a new ingredient"""
        
        # Check if ingredient exists
        existing = self.recipe_repo.get_ingredient_by_name(ingredient_data.ingredient_name)
        if existing:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=INGREDIENT_ALREADY_EXISTS,
                message=INGREDIENT_ALREADY_EXISTS
            )
        
        ingredient = Ingredient(
            ingredient_name=ingredient_data.ingredient_name,
            ingredient_icon_url=ingredient_data.ingredient_icon_url,
            ingredient_quantifier=ingredient_data.ingredient_quantifier
        )
        
        try:
            return self.recipe_repo.create_ingredient(ingredient)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=INGREDIENT_INSERT_FAILED,
                details=str(e)
            )
    
    def get_ingredient_by_id(self, ingredient_id: int) -> Ingredient:
        """Get ingredient by ID"""
        ingredient = self.recipe_repo.get_ingredient_by_id(ingredient_id)
        if not ingredient:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=INGREDIENT_NOT_EXISTS,
                details=f"Ingredient {ingredient_id} not found"
            )
        return ingredient
    
    def get_all_ingredients(self, offset: int = 0, limit: int = 100) -> List[Ingredient]:
        """Get all ingredients"""
        return self.recipe_repo.get_all_ingredients(offset, limit)
    
    def delete_ingredient(self, ingredient_id: int) -> Dict[str, Any]:
        """Delete an ingredient"""
        ingredient = self.get_ingredient_by_id(ingredient_id)
        success = self.recipe_repo.delete_ingredient(ingredient)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=INGREDIENT_DELETE_FAILED,
                details=f"Failed to delete ingredient {ingredient_id}"
            )
        
        return {
            "message": f"Ingredient {ingredient_id} deleted successfully",
            "ingredient_id": ingredient_id
        }