
# here, we make schema translations

from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_product_by_id
from features.user.user_fetch import fetch_user_by_id
from datetime import datetime

from storage import storage_broker;




def fetch_placed_orders_by_user(user_id):
    return storage_broker.get(PlacedOrder
                              ,{PlacedOrder.ordering_user_id :user_id}
                              ,[OrderedItem]
                              ,[PlacedOrder.ordered_item]
                              ,None
                              )

