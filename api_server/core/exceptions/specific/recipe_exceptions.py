# core/exceptions/specific/recipe_exceptions.py
"""
Recipe specific exceptions for recipe management, ingredients, and recipe operations.
"""

from typing import Optional, Dict, Any, List
from enum import Enum

from core.messages.error_codes import ErrorCode
from core.messages.error_messages import get_error_message
from core.messages.http_status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_402_PAYMENT_REQUIRED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_410_GONE,
    HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
    HTTP_417_EXPECTATION_FAILED,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
    HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
)
from core.exceptions.handler import APIException


# ==================== Base Recipe Exception ====================

class RecipeException(APIException):
    """Base exception for all recipe-related errors"""
    
    def __init__(
        self,
        message: str = "Recipe service error",
        error_code: ErrorCode = ErrorCode.RECIPE_NOT_EXISTS,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            status_code=status_code,
            error_code=error_code,
            message=message,
            details=details or {}
        )


# ==================== Recipe Exceptions ====================

class RecipeNotFoundException(RecipeException):
    """Exception when a recipe is not found"""
    
    def __init__(
        self,
        recipe_id: int = None,
        recipe_name: str = None,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if recipe_name:
            error_details["recipe_name"] = recipe_name
        if user_id:
            error_details["user_id"] = user_id
        
        message = "Recipe not found"
        if recipe_id:
            message = f"Recipe with ID '{recipe_id}' not found"
        elif recipe_name:
            message = f"Recipe '{recipe_name}' not found"
        elif user_id:
            message = f"No recipes found for user with ID '{user_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class RecipeAlreadyExistsException(RecipeException):
    """Exception when trying to create a duplicate recipe"""
    
    def __init__(
        self,
        recipe_id: int = None,
        recipe_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if recipe_name:
            error_details["recipe_name"] = recipe_name
        
        message = "Recipe already exists"
        if recipe_id:
            message = f"Recipe with ID '{recipe_id}' already exists"
        elif recipe_name:
            message = f"Recipe '{recipe_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_ALREADY_EXISTS,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class RecipeInsertFailedException(RecipeException):
    """Exception when recipe insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        recipe_id: int = None,
        recipe_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if recipe_name:
            error_details["recipe_name"] = recipe_name
        
        message = "Failed to create recipe"
        if recipe_name:
            message = f"Failed to create recipe '{recipe_name}'"
        elif recipe_id:
            message = f"Failed to create recipe with ID '{recipe_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class RecipeUpdateFailedException(RecipeException):
    """Exception when recipe update fails"""
    
    def __init__(
        self,
        recipe_id: int = None,
        error: str = None,
        fields_attempted: List[str] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if error:
            error_details["update_error"] = error
        if fields_attempted:
            error_details["fields_attempted"] = fields_attempted
        
        message = "Failed to update recipe"
        if recipe_id:
            message = f"Failed to update recipe with ID '{recipe_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class RecipeDeleteFailedException(RecipeException):
    """Exception when recipe deletion fails"""
    
    def __init__(
        self,
        recipe_id: int = None,
        error: str = None,
        has_dependencies: bool = False,
        has_orders: bool = False,
        has_cart_items: bool = False,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if error:
            error_details["delete_error"] = error
        if has_dependencies:
            error_details["has_dependencies"] = has_dependencies
        if has_orders:
            error_details["has_orders"] = has_orders
        if has_cart_items:
            error_details["has_cart_items"] = has_cart_items
        
        message = "Failed to delete recipe"
        if recipe_id:
            message = f"Failed to delete recipe with ID '{recipe_id}'"
        
        reasons = []
        if has_orders:
            reasons.append("has existing orders")
        if has_cart_items:
            reasons.append("is in active carts")
        if reasons:
            message += f" - Recipe {', '.join(reasons)}. Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class RecipeFetchNotFoundException(RecipeException):
    """Exception when recipe fetch returns no results"""
    
    def __init__(
        self,
        identifier: str = None,
        search_type: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if identifier:
            error_details["identifier"] = identifier
        if search_type:
            error_details["search_type"] = search_type
        
        message = "Unable to retrieve recipe information"
        if search_type == "name":
            message = f"Recipe with name '{identifier}' not found"
        elif search_type == "user":
            message = f"No recipes found for user '{identifier}'"
        elif search_type == "category":
            message = f"No recipes found in category '{identifier}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_FETCH_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


# ==================== Recipe Category Exceptions ====================

class RecipeCategoryException(RecipeException):
    """Base exception for recipe category errors"""
    
    def __init__(
        self,
        message: str = "Recipe category error",
        error_code: ErrorCode = ErrorCode.RECIPE_CATEGORY_NOT_EXISTS,
        status_code: int = HTTP_404_NOT_FOUND,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class RecipeCategoryNotFoundException(RecipeCategoryException):
    """Exception when a recipe category is not found"""
    
    def __init__(
        self,
        category_id: int = None,
        category_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if category_id:
            error_details["category_id"] = category_id
        if category_name:
            error_details["category_name"] = category_name
        
        message = "Recipe category not found"
        if category_id:
            message = f"Recipe category with ID '{category_id}' not found"
        elif category_name:
            message = f"Recipe category '{category_name}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_CATEGORY_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class RecipeCategoryAlreadyExistsException(RecipeCategoryException):
    """Exception when trying to create a duplicate category"""
    
    def __init__(
        self,
        category_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if category_name:
            error_details["category_name"] = category_name
        
        message = "Recipe category already exists"
        if category_name:
            message = f"Recipe category '{category_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_ALREADY_EXISTS,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class RecipeCategoryInsertFailedException(RecipeCategoryException):
    """Exception when category insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        category_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if category_name:
            error_details["category_name"] = category_name
        
        message = "Failed to create recipe category"
        if category_name:
            message = f"Failed to create recipe category '{category_name}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


# ==================== Recipe Ingredient Exceptions ====================

class RecipeIngredientException(RecipeException):
    """Base exception for recipe ingredient errors"""
    
    def __init__(
        self,
        message: str = "Recipe ingredient error",
        error_code: ErrorCode = ErrorCode.INGREDIENT_NOT_EXISTS,
        status_code: int = HTTP_404_NOT_FOUND,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class IngredientNotFoundException(RecipeIngredientException):
    """Exception when an ingredient is not found"""
    
    def __init__(
        self,
        ingredient_id: int = None,
        ingredient_name: str = None,
        recipe_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if ingredient_id:
            error_details["ingredient_id"] = ingredient_id
        if ingredient_name:
            error_details["ingredient_name"] = ingredient_name
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        
        message = "Ingredient not found"
        if ingredient_id:
            message = f"Ingredient with ID '{ingredient_id}' not found"
        elif ingredient_name:
            message = f"Ingredient '{ingredient_name}' not found"
        elif recipe_id:
            message = f"No ingredients found for recipe with ID '{recipe_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_NOT_EXISTS,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class IngredientAlreadyExistsException(RecipeIngredientException):
    """Exception when trying to create a duplicate ingredient"""
    
    def __init__(
        self,
        ingredient_id: int = None,
        ingredient_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if ingredient_id:
            error_details["ingredient_id"] = ingredient_id
        if ingredient_name:
            error_details["ingredient_name"] = ingredient_name
        
        message = "Ingredient already exists"
        if ingredient_id:
            message = f"Ingredient with ID '{ingredient_id}' already exists"
        elif ingredient_name:
            message = f"Ingredient '{ingredient_name}' already exists"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_ALREADY_EXISTS,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class IngredientInsertFailedException(RecipeIngredientException):
    """Exception when ingredient insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        ingredient_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if ingredient_name:
            error_details["ingredient_name"] = ingredient_name
        
        message = "Failed to create ingredient"
        if ingredient_name:
            message = f"Failed to create ingredient '{ingredient_name}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class IngredientDeleteFailedException(RecipeIngredientException):
    """Exception when ingredient deletion fails"""
    
    def __init__(
        self,
        ingredient_id: int = None,
        error: str = None,
        has_dependencies: bool = False,
        used_in_recipes: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if ingredient_id:
            error_details["ingredient_id"] = ingredient_id
        if error:
            error_details["delete_error"] = error
        if has_dependencies:
            error_details["has_dependencies"] = has_dependencies
        if used_in_recipes:
            error_details["used_in_recipes"] = used_in_recipes
        
        message = "Failed to delete ingredient"
        if ingredient_id:
            message = f"Failed to delete ingredient with ID '{ingredient_id}'"
        
        if has_dependencies and used_in_recipes:
            message += f" - Ingredient is used in {used_in_recipes} recipe(s). Use force_delete=true to delete anyway."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_DELETE_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class IngredientUpdateFailedException(RecipeIngredientException):
    """Exception when ingredient update fails"""
    
    def __init__(
        self,
        ingredient_id: int = None,
        ingredient_name: str = None,
        error: str = None,
        name_conflict: bool = False,
        conflicting_ingredient_id: int = None,
        conflicting_ingredient_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if ingredient_id:
            error_details["ingredient_id"] = ingredient_id
        if ingredient_name:
            error_details["ingredient_name"] = ingredient_name
        if error:
            error_details["update_error"] = error
        if name_conflict:
            error_details["name_conflict"] = name_conflict
        if conflicting_ingredient_id:
            error_details["conflicting_ingredient_id"] = conflicting_ingredient_id
        if conflicting_ingredient_name:
            error_details["conflicting_ingredient_name"] = conflicting_ingredient_name
        
        message = "Failed to update ingredient"
        if ingredient_id:
            message = f"Failed to update ingredient with ID '{ingredient_id}'"
        elif ingredient_name:
            message = f"Failed to update ingredient '{ingredient_name}'"
        
        if name_conflict:
            if conflicting_ingredient_name:
                message += f" - Ingredient name '{ingredient_name or conflicting_ingredient_name}' already exists."
            else:
                message += " - Ingredient name already exists."
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_UPDATE_FAILED,
            status_code=HTTP_409_CONFLICT if name_conflict else HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


class IngredientUpdateFailedException(RecipeIngredientException):
    """Exception when ingredient update fails"""
    
    def __init__(
        self,
        ingredient_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if ingredient_id:
            error_details["ingredient_id"] = ingredient_id
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update ingredient"
        if ingredient_id:
            message = f"Failed to update ingredient with ID '{ingredient_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.INGREDIENT_UPDATE_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


# ==================== Recipe Image Exceptions ====================

class RecipeImageException(RecipeException):
    """Base exception for recipe image errors"""
    
    def __init__(
        self,
        message: str = "Recipe image error",
        error_code: ErrorCode = ErrorCode.RECIPE_IMAGE_NOT_FOUND,
        status_code: int = HTTP_404_NOT_FOUND,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class RecipeImageNotFoundException(RecipeImageException):
    """Exception when a recipe image is not found"""
    
    def __init__(
        self,
        image_id: int = None,
        recipe_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        
        message = "Recipe image not found"
        if image_id:
            message = f"Recipe image with ID '{image_id}' not found"
        elif recipe_id:
            message = f"Image for recipe '{recipe_id}' not found"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_IMAGE_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


class RecipeImageInsertFailedException(RecipeImageException):
    """Exception when recipe image insertion fails"""
    
    def __init__(
        self,
        error: str = None,
        recipe_id: int = None,
        image_url: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if error:
            error_details["insert_error"] = error
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if image_url:
            error_details["image_url"] = image_url[:100]  # Truncate long URLs
        
        message = "Failed to upload recipe image"
        if recipe_id:
            message = f"Failed to upload image for recipe '{recipe_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=error_details
        )


class RecipeImageUpdateFailedException(RecipeImageException):
    """Exception when recipe image update fails"""
    
    def __init__(
        self,
        image_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if error:
            error_details["update_error"] = error
        
        message = "Failed to update recipe image"
        if image_id:
            message = f"Failed to update recipe image with ID '{image_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_UPDATE_FAILED,
            status_code=HTTP_409_CONFLICT,
            details=error_details
        )


class RecipeImageDeleteFailedException(RecipeImageException):
    """Exception when recipe image deletion fails"""
    
    def __init__(
        self,
        image_id: int = None,
        error: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if image_id:
            error_details["image_id"] = image_id
        if error:
            error_details["delete_error"] = error
        
        message = "Failed to delete recipe image"
        if image_id:
            message = f"Failed to delete recipe image with ID '{image_id}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.IMAGE_INSERT_FAILED,
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details
        )


# ==================== Recipe Search Exceptions ====================

class RecipeSearchException(RecipeException):
    """Exception for recipe search errors"""
    
    def __init__(
        self,
        message: str = "Recipe search failed",
        search_term: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if search_term:
            error_details["search_term"] = search_term
        
        message = "Recipe search failed"
        if search_term:
            message = f"Recipe search failed for term '{search_term}'"
        
        super().__init__(
            message=message,
            error_code=ErrorCode.RECIPE_SEARCH_NOT_FOUND,
            status_code=HTTP_404_NOT_FOUND,
            details=error_details
        )


# ==================== Recipe Validation Exceptions ====================

class RecipeValidationException(RecipeException):
    """Exception for recipe data validation errors"""
    
    def __init__(
        self,
        message: str = "Recipe validation failed",
        errors: Dict[str, List[str]] = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if errors:
            error_details["validation_errors"] = errors
        
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details
        )


class RecipePreparationTimeInvalidException(RecipeValidationException):
    """Exception when preparation time is invalid"""
    
    def __init__(
        self,
        recipe_id: int = None,
        preparation_time: str = None,
        reason: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if preparation_time:
            error_details["preparation_time"] = preparation_time
        if reason:
            error_details["reason"] = reason
        
        message = "Invalid preparation time"
        if reason:
            message = reason
        else:
            message = "Preparation time must be a valid duration (e.g., '1h30m' or '90 minutes')"
        
        super().__init__(
            message=message,
            errors={"preparation_time": [message]},
            details=error_details
        )


class RecipeInstructionsInvalidException(RecipeValidationException):
    """Exception when recipe instructions are invalid"""
    
    def __init__(
        self,
        recipe_id: int = None,
        reason: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if reason:
            error_details["reason"] = reason
        
        message = "Recipe instructions are required"
        if reason:
            message = reason
        
        super().__init__(
            message=message,
            errors={"instructions": [message]},
            details=error_details
        )


class RecipeIngredientsEmptyException(RecipeValidationException):
    """Exception when recipe has no ingredients"""
    
    def __init__(
        self,
        recipe_id: int = None,
        recipe_name: str = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if recipe_name:
            error_details["recipe_name"] = recipe_name
        
        message = "Recipe must have at least one ingredient"
        if recipe_name:
            message = f"Recipe '{recipe_name}' must have at least one ingredient"
        
        super().__init__(
            message=message,
            errors={"ingredients": [message]},
            details=error_details
        )


# ==================== Recipe Permission Exceptions ====================

class RecipePermissionException(RecipeException):
    """Exception for recipe permission errors"""
    
    def __init__(
        self,
        message: str = "Permission denied for recipe operation",
        error_code: ErrorCode = ErrorCode.FORBIDDEN,
        status_code: int = HTTP_403_FORBIDDEN,
        details: Dict[str, Any] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            details=details or {}
        )


class RecipeOwnerPermissionException(RecipePermissionException):
    """Exception when user is not the recipe owner"""
    
    def __init__(
        self,
        recipe_id: int = None,
        user_id: int = None,
        details: Dict[str, Any] = None
    ):
        error_details = details or {}
        
        if recipe_id:
            error_details["recipe_id"] = recipe_id
        if user_id:
            error_details["user_id"] = user_id
        
        message = "You do not have permission to modify this recipe"
        if recipe_id and user_id:
            message = f"User '{user_id}' is not the owner of recipe '{recipe_id}'"
        
        super().__init__(
            message=message,
            status_code=HTTP_403_FORBIDDEN,
            details=error_details
        )