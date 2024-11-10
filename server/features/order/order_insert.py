
# here, we make schema translations

from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_product_by_id
from features.user.user_fetch import fetch_user_by_id
from datetime import datetime;



def build_ordered_item(api_ordered_item: OrderedItem_API):
    ordered_item = OrderedItem(
        ordered_product_id = api_ordered_item.ordered_product_id,
        ordering_user_id = api_ordered_item.ordering_user_id,
        order_ref = api_ordered_item.order_ref,
        ordered_quantity = api_ordered_item.ordered_quantity,
        applied_vat = api_ordered_item.applied_vat,
        unit_price = api_ordered_item.unit_price)
    return ordered_item

def insert_order(api_ordered_items: list[OrderedItem_API],placed_order: PlacedOrder_API):
    ordered_items = []
    ordered_products = []
    for api_ordered_item in api_ordered_items:
        ordered_item = build_ordered_item(api_ordered_item)
        
        ordered_product = fetch_product_by_id(ordered_item.ordered_product_id)
        if ordered_product == None : 
            raise Exception(PRODUCT_NOT_EXISTS)
        
        if ordered_product.product_quantity < ordered_item.ordered_quantity : 
            raise Exception(PRODUCT_QUANTITY_NOT_ENOUGH)

        ordering_user = fetch_user_by_id(ordered_item.ordering_user_id)
        if ordering_user == []: 
            raise Exception(APPUSER_NOT_EXISTS)
        
        ordered_items.append(ordered_item)
        ordered_products.append(ordered_product)


    for ordered_item,ordered_product in zip(ordered_items,ordered_products):
        ordered_product.product_quantity = ordered_product.product_quantity - ordered_item.ordered_quantity
        update_record_in_api(ordered_product)


    placed_order = PlacedOrder(ordered_timestamp = datetime.now(), 
                    order_discount = placed_order.order_discount)

    placed_order.ordered_item = ordered_items

    code,final_order,msg = insert_or_complete_or_raise(placed_order)
    if (code == 1): return msg

    return final_order

