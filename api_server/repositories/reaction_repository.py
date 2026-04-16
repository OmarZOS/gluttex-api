# repositories/reaction_repository.py
from typing import Optional, List, Union
from core.models import (
    ProductReaction, RecipeReaction, ProviderReaction, 
    CommentReaction
)
from constants import ReactionType
import storage.storage_broker as storage_broker

class ReactionRepository:
    """Repository for all reaction-related database operations"""
    
    def get_product_reaction_by_id(self, reaction_id: int) -> Optional[ProductReaction]:
        """Get product reaction by ID"""
        data = storage_broker.get(
            ProductReaction,
            {ProductReaction.id_product_reaction: reaction_id},
            None,
            []
        )
        return data[0] if data else None
    
    def get_product_reaction_by_user(self, user_id: int, product_id: int) -> Optional[ProductReaction]:
        """Get product reaction by user and product"""
        data = storage_broker.get(
            ProductReaction,
            {
                ProductReaction.reacted_on_product: product_id,
                ProductReaction.product_reacting_user: user_id
            },
            None,
            []
        )
        return data[0] if data else None
    
    def get_recipe_reaction_by_user(self, user_id: int, recipe_id: int) -> Optional[RecipeReaction]:
        """Get recipe reaction by user and recipe"""
        data = storage_broker.get(
            RecipeReaction,
            {
                RecipeReaction.reacted_on_recipe: recipe_id,
                RecipeReaction.recipe_reacting_user: user_id
            },
            None,
            []
        )
        return data[0] if data else None
    
    def get_comment_reaction_by_user(self, user_id: int, comment_id: int) -> Optional[CommentReaction]:
        """Get comment reaction by user and comment"""
        data = storage_broker.get(
            CommentReaction,
            {
                CommentReaction.reacted_on_comment: comment_id,
                CommentReaction.comment_reacting_user: user_id
            },
            None,
            []
        )
        return data[0] if data else None
    
    def get_provider_reaction_by_user(self, user_id: int, provider_id: int) -> Optional[ProviderReaction]:
        """Get provider reaction by user and provider"""
        data = storage_broker.get(
            ProviderReaction,
            {
                ProviderReaction.reacted_on_provider: provider_id,
                ProviderReaction.product_reacting_user: user_id
            },
            None,
            []
        )
        return data[0] if data else None
    
    def create_product_reaction(self, reaction: ProductReaction) -> ProductReaction:
        """Create a product reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    def create_recipe_reaction(self, reaction: RecipeReaction) -> RecipeReaction:
        """Create a recipe reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    def create_provider_reaction(self, reaction: ProviderReaction) -> ProviderReaction:
        """Create a provider reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    def create_comment_reaction(self, reaction: CommentReaction) -> CommentReaction:
        """Create a comment reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    def update_reaction(self, reaction: Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]) -> Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]:
        """Update any reaction type"""
        from features.insertion import update_record_in_api
        return update_record_in_api(reaction)
    
    def delete_reaction(self, reaction: Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]) -> bool:
        """Delete any reaction type"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(reaction)
    
    def get_reaction_stats(self, target_type: str, target_id: int) -> dict:
        """Get reaction statistics for a target"""
        # This would aggregate reactions for a specific target
        # Implementation depends on your specific needs
        pass
