# services/reaction_service.py
import logging
from typing import Union, Optional, Dict, Any
from constants import ReactionType, PRODUCT_REACTION_IDS, RECIPE_REACTION_IDS, PROVIDER_REACTION_IDS, COMMENT_REACTION_IDS
from core.api_models import ReactionBase
from core.exceptions.handler import APIException
from core.messages import *
from core.models import (
    ProductReaction, RecipeReaction, ProviderReaction, 
    CommentReaction
)
from repositories.reaction_repository import ReactionRepository

logger = logging.getLogger("FastAPIApp")

class ReactionService:
    """Service for reaction-related business logic"""
    
    def __init__(self):
        self.reaction_repo = ReactionRepository()
    
    def _is_valid_reaction_for_type(self, reaction_id: int, reaction_type: ReactionType) -> bool:
        """Check if reaction ID is valid for the given type"""
        if reaction_type == ReactionType.product:
            return reaction_id in PRODUCT_REACTION_IDS
        elif reaction_type == ReactionType.recipe:
            return reaction_id in RECIPE_REACTION_IDS
        elif reaction_type == ReactionType.provider:
            return reaction_id in PROVIDER_REACTION_IDS
        elif reaction_type == ReactionType.comment:
            return reaction_id in COMMENT_REACTION_IDS
        return False
    
    def _build_reaction_model(self, reaction: ReactionBase, reaction_type: ReactionType):
        """Build the appropriate reaction model based on type"""
        if reaction_type == ReactionType.product:
            return ProductReaction(
                product_reacting_user=reaction.user_id,
                product_reaction_ref=reaction.reaction_id,
                reacted_on_product=reaction.target_id,
                product_reaction_value=reaction.value,
            )
        elif reaction_type == ReactionType.provider:
            return ProviderReaction(
                product_reacting_user=reaction.user_id,
                product_reaction_ref=reaction.reaction_id,
                reacted_on_provider=reaction.target_id,
                provider_reaction_value=reaction.value,
            )
        elif reaction_type == ReactionType.recipe:
            return RecipeReaction(
                product_reacting_user=reaction.user_id,
                product_reaction_ref=reaction.reaction_id,
                reacted_on_recipe=reaction.target_id,
            )
        elif reaction_type == ReactionType.comment:
            return CommentReaction(
                product_reacting_user=reaction.user_id,
                product_reaction_ref=reaction.reaction_id,
                reacted_on_comment=reaction.target_id,
            )
        else:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code="INVALID_REACTION_TYPE",
                details=f"Unknown reaction type: {reaction_type}"
            )
    
    def _update_existing_reaction(self, existing_reaction, reaction_type: ReactionType, new_reaction_id: int):
        """Update an existing reaction with new values"""
        if reaction_type == ReactionType.product:
            existing_reaction.product_reaction_ref = new_reaction_id
        elif reaction_type == ReactionType.recipe:
            existing_reaction.recipe_reaction_ref = new_reaction_id
        elif reaction_type == ReactionType.provider:
            existing_reaction.provider_reaction_ref = new_reaction_id
        elif reaction_type == ReactionType.comment:
            existing_reaction.comment_reaction_ref = new_reaction_id
        
        return existing_reaction
    
    def _get_existing_reaction(self, reaction: ReactionBase, reaction_type: ReactionType):
        """Get existing reaction if it exists"""
        if reaction_type == ReactionType.product:
            return self.reaction_repo.get_product_reaction_by_user(
                reaction.user_id, reaction.target_id
            )
        elif reaction_type == ReactionType.recipe:
            return self.reaction_repo.get_recipe_reaction_by_user(
                reaction.user_id, reaction.target_id
            )
        elif reaction_type == ReactionType.provider:
            return self.reaction_repo.get_provider_reaction_by_user(
                reaction.user_id, reaction.target_id
            )
        elif reaction_type == ReactionType.comment:
            return self.reaction_repo.get_comment_reaction_by_user(
                reaction.user_id, reaction.target_id
            )
        return None
    
    def _create_new_reaction(self, reaction: ReactionBase, reaction_type: ReactionType):
        """Create a new reaction"""
        built_reaction = self._build_reaction_model(reaction, reaction_type)
        
        if reaction_type == ReactionType.product:
            return self.reaction_repo.create_product_reaction(built_reaction)
        elif reaction_type == ReactionType.recipe:
            return self.reaction_repo.create_recipe_reaction(built_reaction)
        elif reaction_type == ReactionType.provider:
            return self.reaction_repo.create_provider_reaction(built_reaction)
        elif reaction_type == ReactionType.comment:
            return self.reaction_repo.create_comment_reaction(built_reaction)
        
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code="REACTION_CREATION_FAILED",
            details=f"Failed to create reaction of type {reaction_type}"
        )
    
    def handle_reaction(self, reaction: ReactionBase):
        """
        Handle reaction creation or update
        """
        reaction_type = reaction.type
        target_id = reaction.target_id
        
        # Validate reaction ID is allowed for the type
        if not self._is_valid_reaction_for_type(reaction.reaction_id, reaction_type):
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code="REACTION_NOT_ALLOWED",
                details=f"Reaction ID {reaction.reaction_id} not allowed for {reaction_type.value}"
            )
        
        # Check if reaction already exists
        existing_reaction = self._get_existing_reaction(reaction, reaction_type)
        
        if existing_reaction:
            # Update existing reaction
            updated_reaction = self._update_existing_reaction(
                existing_reaction, reaction_type, reaction.reaction_id
            )
            return self.reaction_repo.update_reaction(updated_reaction)
        
        # Create new reaction
        return self._create_new_reaction(reaction, reaction_type)
    
    def get_user_reaction_on_target(
        self, 
        user_id: int, 
        target_id: int, 
        reaction_type: ReactionType
    ) -> Optional[Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]]:
        """Get a user's reaction on a specific target"""
        if reaction_type == ReactionType.product:
            return self.reaction_repo.get_product_reaction_by_user(user_id, target_id)
        elif reaction_type == ReactionType.recipe:
            return self.reaction_repo.get_recipe_reaction_by_user(user_id, target_id)
        elif reaction_type == ReactionType.provider:
            return self.reaction_repo.get_provider_reaction_by_user(user_id, target_id)
        elif reaction_type == ReactionType.comment:
            return self.reaction_repo.get_comment_reaction_by_user(user_id, target_id)
        return None
    
    def delete_user_reaction(
        self, 
        user_id: int, 
        target_id: int, 
        reaction_type: ReactionType
    ) -> bool:
        """Delete a user's reaction on a target"""
        reaction = self.get_user_reaction_on_target(user_id, target_id, reaction_type)
        if reaction:
            return self.reaction_repo.delete_reaction(reaction)
        return False
    
    def get_reaction_summary(self, target_type: str, target_id: int) -> Dict[str, Any]:
        """Get summary of reactions for a target"""
        # This would aggregate reactions
        # Implementation depends on your specific requirements
        pass