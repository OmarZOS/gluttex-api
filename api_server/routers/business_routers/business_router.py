from fastapi import APIRouter, BackgroundTasks,  status
from fastapi.encoders import jsonable_encoder
from typing import List
from features.order.order_delete import delete_order
from features.order.order_update import update_order
from core.api_models import OrderedItem_API, PlacedOrder_API

from features.order.order_insert import insert_order
from features.order.order_fetch import fetch_placed_order_details, fetch_placed_orders_by_user
from features.product.product_update import notify_subscribers

business_router = APIRouter()

@business_router.post("/business/order/add")
def insert_placed_order(
    ordered_items: List[OrderedItem_API], 
    submitted_order: PlacedOrder_API, 
    background_tasks: BackgroundTasks
):
    """
    Inserts a placed order and notifies subscribers about stock updates.
    
    Args:
        ordered_items (List[OrderedItem_API]): List of ordered items.
        submitted_order (PlacedOrder_API): The placed order details.
        background_tasks (BackgroundTasks): Task queue for background execution.

    Returns:
        dict: Success message with order details.
    """
    quantities, res = insert_order(ordered_items, submitted_order)
    for index, item in enumerate(ordered_items): 
        background_tasks.add_task(
            notify_subscribers, 
            item.ordered_product_id, 
            {"product_quantity": quantities[index]}
        )
    
    return res


@business_router.get("/business/user/orders/all/{user_id}")
def fetch_every_placed_order_by_user(user_id: int):
    """
    Fetches all placed orders for a specific user.

    Args:
        user_id (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return fetch_placed_orders_by_user(user_id)

@business_router.get("/business/user/orders/{order_id}")
def fetch_every_item_in_order(order_id: int):
    """
    Fetches all items for a specific order_id.

    Args:
        order_id (int): The order's ID.

    Returns:
        list: List of ordered items.
    """
    return fetch_placed_order_details(order_id)


@business_router.put("/business/order/update/{order_id}")
def update_placed_order(
    updated_items: List[OrderedItem_API], 
    updated_order: PlacedOrder_API, 
    ):
    """
    Updates a placed order and notifies subscribers about stock updates.
    
    Args:
        order_id (int): The ID of the order to update.
        updated_items (List[OrderedItem_API]): Updated list of ordered items.
        updated_order (PlacedOrder_API): The updated order details.
        background_tasks (BackgroundTasks): Task queue for background execution.

    Returns:
        dict: Success message with updated order details.
    """
    res = update_order( updated_items, updated_order)
    
    return res

@business_router.delete("/business/order/delete/{order_id}")
def delete_placed_order(
    order_id: int,
):
    """
    Deletes a placed order and notifies subscribers about stock restocking.
    
    Args:
        order_id (int): The ID of the order to delete.
        background_tasks (BackgroundTasks): Task queue for background execution.

    Returns:
        dict: Success message with deletion confirmation.
    """
    
    # Delete the order
    res = delete_order(order_id)
    
    return res

