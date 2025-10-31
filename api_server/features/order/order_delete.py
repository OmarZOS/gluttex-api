# here, we make schema translations

from typing import List, Tuple
from features.order.order_fetch import fetch_order_by_id
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import delete_record_from_api, insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_product_by_id
from features.user.user_fetch import fetch_user_by_id
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
    order_to_delete = fetch_order_by_id(order_id)
    if order_to_delete is None:
        raise APIException(status=HTTP_404_NOT_FOUND, code=ORDER_NOT_EXISTS)

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

    # --- Delete the order ---
    try:
        delete_record_from_api(order_to_delete)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_DELETE_FAILED,
            details=f"Failed to delete order #{order_id}: {str(e)}"
        )

    return True
