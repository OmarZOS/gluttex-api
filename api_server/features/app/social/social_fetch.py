


from core.exception_handler import APIException
from core.messages import *
from core.models import *
import storage.storage_broker as storage_broker
from sqlalchemy import func


def get_product_reaction_by_id(id : int):
    data = storage_broker.get(
        ProductReaction,
        {ProductReaction.id_product_reaction:id},
        None,
        [
        ]
    )
    
    if data == []:
        return None

    return data[0]

def get_product_reaction_by_user(id_user : int,id_product : int):
    data = storage_broker.get(
        ProductReaction,
        {ProductReaction.reacted_on_product:id_product,
         ProductReaction.product_reacting_user:id_user},
        None,
        [
        ]
    )
    if data == []:
        return None
    return data[0]

def get_recipe_reaction_by_user(id_user : int,id_recipe : int):
    data = storage_broker.get(
        RecipeReaction,
        {RecipeReaction.reacted_on_recipe:id_recipe,
         RecipeReaction.recipe_reacting_user:id_user},
        None,
        [
        ]
    )
    if data == []:
        return None
    return data[0]

def get_comment_reaction_by_user(id_user : int,id_comment : int):
    data = storage_broker.get(
        CommentReaction,
        {CommentReaction.reacted_on_comment:id_comment,
         CommentReaction.comment_reacting_user:id_user},
        None,
        [
        ]
    )
    if data == []:
        return None
    return data[0]

def get_provider_reaction_by_user(id_user : int,id_provider : int):
    data = storage_broker.get(
        ProviderReaction,
        {ProviderReaction.reacted_on_provider:id_provider,
         ProviderReaction.product_reacting_user:id_user},
        None,
        [
        ]
    )
    if data == []:
        return None
    return data[0]

def fetch_notifications(notification_user_ref, offset, limit):
    # Build conditions dynamically
    conditions = {}

    if int(notification_user_ref) !=0:
        conditions[Notification.notification_user_ref] = int(notification_user_ref)

    # Fetch data
    rule_list = storage_broker.get(
        Notification,
        conditions,
        None,
        [],
        offset,
        limit,
    )

    return rule_list


def fetch_full_person_by_id(person_id):

    # Fetch data
    rule_list = storage_broker.get(
        Person,
        {Person.id_person : person_id},
        None,
        [Person.person_details ],
    )

    return rule_list












