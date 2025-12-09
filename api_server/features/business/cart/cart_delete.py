# here, we make schema translations

from typing import List, Tuple
from features.business.order.order_fetch import fetch_only_order_by_id, fetch_order_by_id
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import delete_record_from_api, insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id
from datetime import datetime;


def delete_order(order_id: int) -> bool:
    """
    Delete an order and restore product quantities.

    Args:
        order_id (int): ID of the order to delete.

    Returns:
        bool: True if deletion was successful.

    Raises:
        APIException: If order does not exist or deletion fails.
    """

    # --- Fetch order ---
    existing_orders = fetch_order_by_id(order_id)
    if existing_orders is None or len(existing_orders) == 0:
        raise APIException(status=HTTP_404_NOT_FOUND, code=ORDER_NOT_EXISTS)

    # Get the first order from the list
    order_to_delete = existing_orders[0]

    # --- Restore product stock ---
    try:
        for ordered_item in order_to_delete.ordered_item:
            product = fetch_product_by_id(ordered_item.ordered_product_id)
            if product:
                product.product_quantity += ordered_item.ordered_quantity
                update_record_in_api(product)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=PRODUCT_QUANTITY_RESTORE_FAILED,
            details=f"Failed to restore product stock: {str(e)}"
        )

    deletion_target =  fetch_only_order_by_id(order_id)[0]

    # --- Delete the order ---
    try:
        delete_record_from_api(deletion_target)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_DELETE_FAILED,
            details=f"Failed to delete order #{order_id}: {str(e)}"
        )

    return True



def delete_order_items(order_id: int) -> bool:
    """
    Delete all ordered items for a given order.

    Args:
        order_id (int): ID of the order whose items should be deleted.

    Returns:
        bool: True if deletion was successful.

    Raises:
        APIException: If deletion fails.
    """
    try:
        # Fetch the order to get its items
        existing_orders = fetch_order_by_id(order_id)
        if existing_orders is None or len(existing_orders) == 0:
            raise APIException(
                status=HTTP_404_NOT_FOUND, 
                code=ORDER_NOT_EXISTS,
                details=f"Order #{order_id} does not exist"
            )
        
        # Get the first order from the list
        existing_order = existing_orders[0]
        
        # Delete each ordered item
        for ordered_item in existing_order.ordered_item:
            delete_record_from_api(ordered_item)
            
        return True
        
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_ITEMS_DELETE_FAILED,
            details=f"Failed to delete items for order #{order_id}: {str(e)}"
        )