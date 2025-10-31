# here, we make schema translations

from typing import List, Tuple
from features.order.order_fetch import fetch_order_by_id
from constants import ORDER_STATUSES
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_product_by_id
from features.user.user_fetch import fetch_user_by_id
from datetime import datetime;


def update_order(api_ordered_items: List[OrderedItem_API], placed_order_api: PlacedOrder_API) -> PlacedOrder:
    """
    Update the status of an existing order.

    Args:
        order_id (int): ID of the order to update.
        new_status (str): New status value (e.g., 'pending', 'paid', 'delivered', 'cancelled').

    Returns:
        PlacedOrder: The updated order object.

    Raises:
        APIException: If order does not exist or update fails.
    """

    # --- Fetch order ---
    existing_order = fetch_order_by_id(order_id)
    if existing_order is None:
        raise APIException(status=HTTP_404_NOT_FOUND, code=ORDER_NOT_EXISTS)

    # --- Validate status ---
    valid_statuses = ORDER_STATUSES
    if new_status.lower() not in valid_statuses:
        raise APIException(
            status=HTTP_422_UNPROCESSABLE_ENTITY,
            code=INVALID_ORDER_STATUS,
            details=f"Invalid status '{new_status}'. Allowed: {', '.join(valid_statuses)}"
        )

    # --- Apply update ---
    existing_order.payment_status = new_status.lower()
    existing_order.placed_order_last_mod = datetime.now()

    # --- Persist update ---
    try:
        updated_order = update_record_in_api(existing_order)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_UPDATE_FAILED,
            details=f"Failed to update order #{order_id}: {str(e)}"
        )

    return updated_order
