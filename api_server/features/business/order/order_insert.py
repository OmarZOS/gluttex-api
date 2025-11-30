# here, we make schema translations

from typing import List, Tuple
from communication.publisher import send_to_product_subscribers
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id
from datetime import datetime;


def insert_order_item(api_ordered_item: OrderedItem_API) -> OrderedItem:
    """
    Insert a single ordered item into the system.

    Args:
        api_ordered_item (OrderedItem_API): The ordered item to insert.

    Returns:
        OrderedItem: The created ordered item.

    Raises:
        APIException: If product doesn't exist, stock is insufficient, or insertion fails.
    """
    try:
        # Convert API model to internal model
        ordered_item = build_ordered_item(api_ordered_item)
        
        # Validate product exists
        ordered_product = fetch_product_by_id(ordered_item.ordered_product_id)
        if ordered_product is None:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_NOT_EXISTS,
                details=f"Product #{ordered_item.ordered_product_id} does not exist"
            )
        
        # Validate stock availability
        if ordered_product.product_quantity < ordered_item.ordered_quantity:
            raise APIException(
                status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                code=PRODUCT_QUANTITY_NOT_ENOUGH,
                details=f"Not enough stock for product #{ordered_item.ordered_product_id}. Available: {ordered_product.product_quantity}, Requested: {ordered_item.ordered_quantity}"
            )
        
        # Update product stock
        ordered_product.product_quantity -= ordered_item.ordered_quantity
        update_record_in_api(ordered_product)
        
        # Notify subscribers about stock update
        send_to_product_subscribers(
            {'product_quantity': ordered_product.product_quantity},
            ordered_product.id_product
        )
        
        # Insert the ordered item
        inserted_item = insert_or_complete_or_raise(ordered_item)
        
        return inserted_item
        
    except APIException:
        # Re-raise API exceptions as-is
        raise
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_ITEM_INSERT_FAILED,
            details=f"Failed to insert ordered item: {str(e)}"
        )


def build_ordered_item(api_ordered_item: OrderedItem_API) -> OrderedItem:
    """
    Convert API ordered item into internal OrderedItem model.
    """
    return OrderedItem(
        ordered_product_id=api_ordered_item.ordered_product_id,
        order_ref=api_ordered_item.order_ref,
        ordered_quantity=api_ordered_item.ordered_quantity,
        applied_vat=api_ordered_item.applied_vat,
        unit_price=api_ordered_item.unit_price
    )


def insert_order(api_ordered_items: List[OrderedItem_API], placed_order_api: PlacedOrder_API) -> Tuple[List[int], PlacedOrder]:
    """
    Insert a new order into the system.

    Args:
        api_ordered_items (List[OrderedItem_API]): Items from the API request.
        placed_order_api (PlacedOrder_API): The placed order metadata.

    Returns:
        Tuple[List[int], PlacedOrder]: Updated product quantities and final placed order.

    Raises:
        Exception: If product/user does not exist or stock is insufficient.
    """

    # --- Validate user ---
    ordering_user = fetch_user_by_id(placed_order_api.ordering_user_id)
    if ordering_user is None:
        raise APIException(status= HTTP_404_NOT_FOUND,code = APPUSER_NOT_EXISTS)

    ordered_items: List[OrderedItem] = []
    ordered_products: List[Product] = []

    # --- Validate products & build ordered items ---
    for api_ordered_item in api_ordered_items:
        ordered_item = build_ordered_item(api_ordered_item)

        # Fetch product
        ordered_product = fetch_product_by_id(ordered_item.ordered_product_id)
        if ordered_product is None:
            raise APIException(status= HTTP_404_NOT_FOUND,code=PRODUCT_NOT_EXISTS)

        # Validate stock
        if ordered_product.product_quantity < ordered_item.ordered_quantity:
            raise APIException(status= HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,code=PRODUCT_QUANTITY_NOT_ENOUGH,details=PRODUCT_QUANTITY_NOT_ENOUGH)

        ordered_items.append(ordered_item)
        ordered_products.append(ordered_product)    

    # --- Update product stock & calculate total price ---
    order_total_price: float = 0
    updated_quantities: List[int] = []

    for ordered_item, ordered_product in zip(ordered_items, ordered_products):
        ordered_product.product_quantity -= ordered_item.ordered_quantity
        updated_quantities.append(ordered_product.product_quantity)

        # Update product stock in API
        try:
            update_record_in_api(ordered_product)
            send_to_product_subscribers({'product_quantity':ordered_product.product_quantity},ordered_product.id_product)
        except Exception as e:
            raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=PRODUCT_QUANTITY_NOT_ENOUGH,message=IMAGE_INSERT_FAILED,details=f"{str(e)}")

        # Add to total price
        order_total_price += ordered_item.ordered_quantity * float(ordered_product.product_price) * (1 + ordered_item.applied_vat)

    # --- Create final order object ---
    placed_order = PlacedOrder(
        ordering_user_id=ordering_user.id_app_user,
        ordered_timestamp=datetime.now(),
        order_discount=placed_order_api.order_discount,
        payment_ref = placed_order_api.payment_ref,
        placed_order_last_mod = datetime.now(),
        placed_order_state = placed_order_api.placed_order_state,
        payment_status = placed_order_api.payment_status,
        payment_method = placed_order_api.payment_method,
        total_price=order_total_price
    )
    placed_order.ordered_item = ordered_items

    # --- Persist order ---
    try:
        final_order = insert_or_complete_or_raise(placed_order)
        
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=ORDER_INSERT_CONFLICT,details=f"{str(e)}")


    return updated_quantities, final_order