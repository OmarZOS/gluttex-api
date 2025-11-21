


from features.app.social.social_fetch import get_comment_reaction_by_user, get_product_reaction_by_user, get_provider_reaction_by_user, get_recipe_reaction_by_user
from constants import *
from features.app.notification.notification_fetch import touch_notification_by_id
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from core.api_models import  ReactionBase
# from features.business.staff.staff_fetch import touch_notification_by_id
from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func

from datetime import datetime

def build_reaction(reaction,type:ReactionType):
    if type == ReactionType.product:
         return ProductReaction(
            product_reacting_user=reaction.user_id ,
            product_reaction_ref=reaction.reaction_id,
            reacted_on_product=reaction.target_id,
            product_reaction_value=reaction.value,
         )
    if type == ReactionType.provider:
         return ProviderReaction(
            product_reacting_user=reaction.user_id ,
            product_reaction_ref=reaction.reaction_id,
            reacted_on_provider=reaction.target_id,
            provider_reaction_value=reaction.value,
         )
    if type == ReactionType.recipe:
         return RecipeReaction(
            product_reacting_user=reaction.user_id ,
            product_reaction_ref=reaction.reaction_id,
            reacted_on_recipe=reaction.target_id,
         )
    if type == ReactionType.comment:
         return CommentReaction(
            product_reacting_user=reaction.user_id ,
            product_reaction_ref=reaction.reaction_id,
            reacted_on_comment=reaction.target_id,
        )

def is_valid_reaction_for_type(reaction_id: int, type: ReactionType) -> bool:
    if type == ReactionType.product:
        return reaction_id in PRODUCT_REACTION_IDS
    if type == ReactionType.recipe:
        return reaction_id in RECIPE_REACTION_IDS
    if type == ReactionType.provider:
        return reaction_id in PROVIDER_REACTION_IDS
    if type == ReactionType.comment:
        return reaction_id in COMMENT_REACTION_IDS
    return False



def change_reaction_for_type(reaction:ReactionBase, type,value):
    if type == ReactionType.product:
        reaction.product_reaction_ref = value
    if type == ReactionType.recipe:
        reaction.recipe_reaction_ref = value
    if type == ReactionType.provider:
        reaction.provider_reaction_ref = value
    if type == ReactionType.comment:
        reaction.comment_reaction_ref = value
    return reaction


def handle_reaction(reaction:ReactionBase):
    # 2. Check if already exists
    type = reaction.type
    reference_id = reaction.target_id
    

    # 1. Validate reaction_id is allowed for that type
    if not is_valid_reaction_for_type(reaction.reaction_id, type):
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code="REACTION_NOT_ALLOWED",
            details=f"Reaction ID {reaction.reaction_id} not allowed for {type.value}"
        )

    reaction_exists =  (
        get_product_reaction_by_user(reaction.user_id ,reference_id ) if type == ReactionType.product else
        get_recipe_reaction_by_user(reaction.user_id,reference_id) if type == ReactionType.recipe else
        get_provider_reaction_by_user(reaction.user_id,reference_id) if type == ReactionType.provider else
        get_comment_reaction_by_user(reaction.user_id,reference_id)
    )

    if reaction_exists:
        return update_record_in_api(change_reaction_for_type(reaction_exists,type,reaction.reaction_id))

    # 3. Build the appropriate reaction object
    built_reaction = build_reaction(reaction, type)

    # 4. Insert
    inserted = insert_or_complete_or_raise(built_reaction)

    return inserted












