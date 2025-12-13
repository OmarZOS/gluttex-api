from fastapi import APIRouter, BackgroundTasks,  status
from fastapi.encoders import jsonable_encoder
from typing import List
from features.business.finance.payment_insert import insert_financial_item
from features.business.cart.cart_insert import insert_cart
from features.business.cart.cart_fetch import fetch_cart
from features.business.cart.service.service_fetch import fetch_services
# from features.business.cart.service.service_insert import insert_service
from features.business.order.order_delete import delete_order
from features.business.order.order_update import update_order
from core.api_models import AdditionalFee_API, Cart_API, Deposit_API, Payment_API,  OrderedItem_API, OrderedService_API, Person_API, PlacedOrder_API, ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API

from features.business.order.order_insert import insert_order
from features.business.cart.cart_fetch import fetch_business_operations
from features.business.order.order_fetch import  fetch_placed_order_details, fetch_placed_orders
from features.business.product.product_update import notify_subscribers

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



@business_router.get("/business/user/{user_id}/{offset}/{limit}")
def fetch_every_placed_order_by_user(user_id: int, offset: int, limit: int):
    """
    Fetches all placed orders for a specific user.

    Args:
        user_id (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return fetch_placed_orders(user_id, offset ,limit)

@business_router.get("/business/order/{supplier_id}/{order_id}/{cart_id}/{client}/{seller_id}/{offset}/{limit}")
def fetch_business_ops(supplier_id:int,order_id : int,cart_id: int, client: int, seller_id:int, offset: int, limit: int):
    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return fetch_business_operations(supplier_id,order_id,cart_id, client,seller_id, offset ,limit)


@business_router.get("/business/order/orders/{order_id}")
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
    res = update_order(updated_items, updated_order)

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

# @business_router.post("/business/service/add")
# def insert_provided_service(
#     provided_service: ProvidedService_API = None, 
#     resource_requirement: ServiceResourceRequirement_API = None, 
#     staff_requirement: ServiceStaffRequirement_API = None
# ):
#     return insert_service(
#         provided_service,resource_requirement,staff_requirement
#     )

@business_router.get("/business/service/{service_id}/{category_id}/{provider_id}/{offset}/{limit}")
def fetch_service(service_id:int = 0,category_id:int = 0,provider_id:int = 0,offset :int = 0,limit:int = 0):
    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return fetch_services(service_id,category_id,provider_id, offset ,limit)

@business_router.get("/business/cart/{provider_id}/{seller_id}/{cart_id}/{client_id}/{person_id}/{offset}/{limit}")
def fetch_carts(provider_id: int = 0,seller_id: int = 0,cart_id: int = 0,client_id: int = 0,person_id: int = 0,offset :int = 0,limit:int = 0):


    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return fetch_cart(provider_id,seller_id,cart_id, client_id ,person_id, offset ,limit)

@business_router.post("/business/cart/add")
def add_cart(api_ordered_items: List[OrderedItem_API], 
                api_provided_services: List[OrderedService_API],
                api_cart: Cart_API = None, 
                client: Person_API = None,
                provider_id: int = 0, 
                seller_user_id: int = 0, 
                buyer_user_id: int = 0):
    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return insert_cart(api_ordered_items, 
                        api_provided_services,
                        api_cart, 
                        client,
                        provider_id,
                        seller_user_id,
                        buyer_user_id)


@business_router.post("/business/payment/add")
def add_payment(payment: Payment_API = None,deposit : Deposit_API= None, fee : AdditionalFee_API =None):
    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    return insert_financial_item(payment,deposit, fee)



