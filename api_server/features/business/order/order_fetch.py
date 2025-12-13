
# here, we make schema translations

from core.persistent_models import BusinessOperation
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *
from storage import storage_broker;




def fetch_placed_orders(user_id, offset ,limit):
    conditions = {}
    # if supplier_id!=0:
    #     conditions[PlacedOrder.] = supplier_id
    if user_id!=0:
        conditions[PlacedOrder.ordering_user_id] = user_id

    # supplier_id,user_id, offset ,limit
        
    return storage_broker.get(PlacedOrder
                              ,{PlacedOrder.ordering_user_id :user_id}
                              ,[OrderedItem]
                              ,None
                              ,
                              offset=offset,
                              limit=limit
                              )



# def fetch_business_operations(supplier_id:int = 0,order_id : int = 0,cart_id: int = 0, client: int = 0, seller_id:int = 0, offset: int = 0, limit: int = 0):
    
#     conditions = {}
#     result = {}


#     if supplier_id!=0:
#         conditions[BusinessOperation.supplier_id] = supplier_id
#     if order_id!=0:
#         conditions[BusinessOperation.order_id] = order_id
#     if cart_id!=0:
#         conditions[BusinessOperation.cart_id] = cart_id
#     if client!=0:
#         conditions[BusinessOperation.client_id] = client
#     if seller_id!=0:
#         conditions[BusinessOperation.seller_id] = seller_id


    
#     return storage_broker.get(BusinessOperation
#                             ,conditions
#                             ,[]
#                             ,[]
#                             ,None
#                             )

    # if supplier_id!=0:
    #     conditions[PlacedOrder.] = supplier_id
    # if user_id!=0:
    #     conditions[PlacedOrder.ordering_user_id] = user_id

    # supplier_id,user_id, offset ,limit
    


def fetch_placed_order_details(order_id):
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
                              ,[PlacedOrder.ordered_item]
                              ,None
                              )

def fetch_only_order_by_id(order_id):
    return storage_broker.get(PlacedOrder
                              ,{PlacedOrder.id_placed_order :order_id}
                              ,[]
                              ,[]
                              ,None
                              )