# here, we make schema translations

from typing import List, Tuple
from features.business.order.order_delete import delete_order_items
from features.business.order.order_insert import insert_order_item
from features.business.order.order_fetch import fetch_order_by_id
from constants import ORDER_STATUSES
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id
from datetime import datetime;





def update_order(api_ordered_items: List[OrderedItem_API], placed_order_api: PlacedOrder_API) -> dict:
    """
    Update an existing order with new items and order details.

    Args:
        api_ordered_items (List[OrderedItem_API]): Updated list of ordered items.
        placed_order_api (PlacedOrder_API): Updated order details.

    Returns:
        dict: Success message with updated order details.

    Raises:
        APIException: If order does not exist or update fails.
    """

    # --- Validate order exists ---
    existing_orders = fetch_order_by_id(placed_order_api.id_placed_order)
    if existing_orders is None or len(existing_orders) == 0:
        raise APIException(
            status=HTTP_404_NOT_FOUND, 
            code=ORDER_NOT_EXISTS,
            details=f"Order #{placed_order_api.id_placed_order} does not exist"
        )
    
    # Get the first order from the list
    existing_order = existing_orders[0]

    # --- Validate order status if provided ---
    if placed_order_api.placed_order_state:
        valid_statuses = ORDER_STATUSES
        if placed_order_api.placed_order_state.upper() not in valid_statuses:
            raise APIException(
                status=HTTP_422_UNPROCESSABLE_ENTITY,
                code=INVALID_ORDER_STATUS,
                details=f"Invalid status '{placed_order_api.placed_order_state}'. Allowed: {', '.join(valid_statuses)}"
            )

    # --- Update order details ---
    try:
        # Update the main order record
        update_data = {}
        
        # Only update fields that are provided (not None)
        if placed_order_api.ordered_timestamp is not None:
            update_data['ordered_timestamp'] = placed_order_api.ordered_timestamp
        if placed_order_api.order_discount is not None:
            update_data['order_discount'] = placed_order_api.order_discount
        if placed_order_api.payment_status is not None:
            update_data['payment_status'] = placed_order_api.payment_status.lower()
        if placed_order_api.payment_ref is not None:
            update_data['payment_ref'] = placed_order_api.payment_ref
        if placed_order_api.placed_order_state is not None:
            update_data['placed_order_state'] = placed_order_api.placed_order_state.lower()
        if placed_order_api.payment_method is not None:
            update_data['payment_method'] = placed_order_api.payment_method
        if placed_order_api.ordering_user_id is not None:
            update_data['ordering_user_id'] = placed_order_api.ordering_user_id
        
        # Always update last modification timestamp
        update_data['placed_order_last_mod'] = datetime.now()
        
        # --- Update ordered items ---
        if api_ordered_items:
            # First, restore stock from old items
            for old_item in existing_order.ordered_item:
                product = fetch_product_by_id(old_item.ordered_product_id)
                if product:
                    product.product_quantity += old_item.ordered_quantity
                    update_record_in_api(product)
            
            # Delete old ordered items
            delete_order_items(placed_order_api.id_placed_order)
            
            # Insert new ordered items
            for item in api_ordered_items:
                # Ensure each item references the correct order
                item.order_ref = placed_order_api.id_placed_order
                insert_order_item(item)
        # Apply updates to existing order
        for field, value in update_data.items():
            setattr(existing_order, field, value)
        
        # Update the order in database
        updated_order = update_record_in_api(existing_order)
        
        # Return success response
        return {
            "status": "success",
            "message": f"Order #{placed_order_api.id_placed_order} updated successfully",
            "order_id": placed_order_api.id_placed_order,
            "updated_timestamp": update_data['placed_order_last_mod'].isoformat() if hasattr(update_data['placed_order_last_mod'], 'isoformat') else str(update_data['placed_order_last_mod'])
        }
        
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_UPDATE_FAILED,
            details=f"Failed to update order #{placed_order_api.id_placed_order}: {str(e)}"
        )