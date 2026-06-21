# repositories/reaction_repository.py
from typing import Optional, List, Union
from core.models import (
    ProductReaction, RecipeReaction, ProviderReaction, 
    CommentReaction, Product, Recipe, ProductProvider, Comment, AppUser
)
import storage.storage_broker as storage_broker


class ReactionRepository:
    """Repository for reaction-related database operations"""
    
    # ==================== Product Reactions ====================
    
    def get_product_reactions_by_user(self, user_id: int) -> List[ProductReaction]:
        """Get all product reactions by a user"""
        return storage_broker.get(
            ProductReaction,
            conditions={ProductReaction.product_reacting_user: user_id}
        )
    
    def get_product_reaction_by_user(self, user_id: int, product_id: int) -> Optional[ProductReaction]:
        """Get a specific product reaction by user and product"""
        reactions = storage_broker.get(
            ProductReaction,
            conditions={
                ProductReaction.product_reacting_user: user_id,
                ProductReaction.reacted_on_product: product_id
            }
        )
        return reactions[0] if reactions else None
    
    def get_product_reactions_by_target(self, product_id: int) -> List[ProductReaction]:
        """Get all product reactions for a product"""
        return storage_broker.get(
            ProductReaction,
            conditions={ProductReaction.reacted_on_product: product_id}
        )
    
    def create_product_reaction(self, reaction: ProductReaction) -> ProductReaction:
        """Create a product reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    # ==================== Recipe Reactions ====================
    
    def get_recipe_reactions_by_user(self, user_id: int) -> List[RecipeReaction]:
        """Get all recipe reactions by a user"""
        return storage_broker.get(
            RecipeReaction,
            conditions={RecipeReaction.recipe_reacting_user: user_id}
        )
    
    def get_recipe_reaction_by_user(self, user_id: int, recipe_id: int) -> Optional[RecipeReaction]:
        """Get a specific recipe reaction by user and recipe"""
        reactions = storage_broker.get(
            RecipeReaction,
            conditions={
                RecipeReaction.recipe_reacting_user: user_id,
                RecipeReaction.reacted_on_recipe: recipe_id
            }
        )
        return reactions[0] if reactions else None
    
    def get_recipe_reactions_by_target(self, recipe_id: int) -> List[RecipeReaction]:
        """Get all recipe reactions for a recipe"""
        return storage_broker.get(
            RecipeReaction,
            conditions={RecipeReaction.reacted_on_recipe: recipe_id}
        )
    
    def create_recipe_reaction(self, reaction: RecipeReaction) -> RecipeReaction:
        """Create a recipe reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    # ==================== Provider Reactions ====================
    
    def get_provider_reactions_by_user(self, user_id: int) -> List[ProviderReaction]:
        """Get all provider reactions by a user"""
        return storage_broker.get(
            ProviderReaction,
            conditions={ProviderReaction.provider_reacting_user: user_id}
        )
    
    def get_provider_reaction_by_user(self, user_id: int, provider_id: int) -> Optional[ProviderReaction]:
        """Get a specific provider reaction by user and provider"""
        reactions = storage_broker.get(
            ProviderReaction,
            conditions={
                ProviderReaction.provider_reacting_user: user_id,
                ProviderReaction.reacted_on_provider: provider_id
            }
        )
        return reactions[0] if reactions else None
    
    def get_provider_reactions_by_target(self, provider_id: int) -> List[ProviderReaction]:
        """Get all provider reactions for a provider"""
        return storage_broker.get(
            ProviderReaction,
            conditions={ProviderReaction.reacted_on_provider: provider_id}
        )
    
    def create_provider_reaction(self, reaction: ProviderReaction) -> ProviderReaction:
        """Create a provider reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    # ==================== Comment Reactions ====================
    
    def get_comment_reactions_by_user(self, user_id: int) -> List[CommentReaction]:
        """Get all comment reactions by a user"""
        return storage_broker.get(
            CommentReaction,
            conditions={CommentReaction.comment_reacting_user: user_id}
        )
    
    def get_comment_reaction_by_user(self, user_id: int, comment_id: int) -> Optional[CommentReaction]:
        """Get a specific comment reaction by user and comment"""
        reactions = storage_broker.get(
            CommentReaction,
            conditions={
                CommentReaction.comment_reacting_user: user_id,
                CommentReaction.reacted_on_comment: comment_id
            }
        )
        return reactions[0] if reactions else None
    
    def get_comment_reactions_by_target(self, comment_id: int) -> List[CommentReaction]:
        """Get all comment reactions for a comment"""
        return storage_broker.get(
            CommentReaction,
            conditions={CommentReaction.reacted_on_comment: comment_id}
        )
    
    def create_comment_reaction(self, reaction: CommentReaction) -> CommentReaction:
        """Create a comment reaction"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(reaction)
    
    # ==================== Generic Methods ====================
    
    def get_all_reactions_by_user(self, user_id: int) -> List[Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]]:
        """Get all reactions by a user across all types"""
        reactions = []
        reactions.extend(self.get_product_reactions_by_user(user_id))
        reactions.extend(self.get_recipe_reactions_by_user(user_id))
        reactions.extend(self.get_provider_reactions_by_user(user_id))
        reactions.extend(self.get_comment_reactions_by_user(user_id))
        return reactions
    
    def update_reaction(self, reaction: Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]) -> Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]:
        """Update a reaction"""
        from features.insertion import update_record_in_api
        return update_record_in_api(reaction)
    
    def delete_reaction(self, reaction: Union[ProductReaction, RecipeReaction, ProviderReaction, CommentReaction]) -> bool:
        """Delete a reaction"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(reaction)
    
    # ==================== Existence Checks ====================
    
    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        users = storage_broker.get(AppUser, conditions={AppUser.id_app_user: user_id})
        return len(users) > 0
    
    def product_exists(self, product_id: int) -> bool:
        """Check if a product exists"""
        products = storage_broker.get(Product, conditions={Product.id_product: product_id})
        return len(products) > 0
    
    def recipe_exists(self, recipe_id: int) -> bool:
        """Check if a recipe exists"""
        recipes = storage_broker.get(Recipe, conditions={Recipe.id_recipe: recipe_id})
        return len(recipes) > 0
    
    def provider_exists(self, provider_id: int) -> bool:
        """Check if a provider exists"""
        providers = storage_broker.get(ProductProvider, conditions={ProductProvider.id_product_provider: provider_id})
        return len(providers) > 0
    
    def comment_exists(self, comment_id: int) -> bool:
        """Check if a comment exists"""
        comments = storage_broker.get(Comment, conditions={Comment.idcomment: comment_id})
        return len(comments) > 0