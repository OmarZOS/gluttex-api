
# here, we make schema translations

from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *

from storage import storage_broker;




def fetch_placed_orders_by_user(user_id,order_id = 0):
    return storage_broker.get(PlacedOrder
                              ,{PlacedOrder.ordering_user_id :user_id}
                              ,[OrderedItem]
                              ,None
                              ,None
                              )

def fetch_placed_order_details(order_id ):
    return storage_broker.get(OrderedItem
                              ,{OrderedItem.order_ref :order_id}
                              ,[]
                              ,[OrderedItem.ordered_product]
                              ,None
                              )

def fetch_order_by_id(order_id):
    return storage_broker.get(PlacedOrder
                              ,{PlacedOrder.id_placed_order :order_id}
                              ,[]
                              ,None
                              ,None
                              )
