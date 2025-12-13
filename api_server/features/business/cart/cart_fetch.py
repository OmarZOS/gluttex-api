
# here, we make schema translations

from core.persistent_models import BusinessOperation
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *

from storage import storage_broker;

def fetch_cart(provider_id: int = 0,seller_id: int = 0,cart_id: int = 0,client_id: int = 0,person_id: int = 0,offset :int = 0,limit:int = 0):
    conditions = {}
    eager_fields = [Cart.invoice,Cart.receipt,Cart.deposit]
    
    if provider_id != 0 :
        conditions[Cart.cart_product_provider_id] = provider_id
    if seller_id != 0 :
        conditions[Cart.cart_selling_user] = seller_id
    if cart_id != 0 :
        conditions[Cart.cart_id] = cart_id
        eager_fields.extend(
            [
                
                {Cart.ordered_item:[

                    OrderedItem.id_ordered_item,
                    OrderedItem.ordered_product_id,
                    OrderedItem.ordered_quantity,
                    OrderedItem.applied_vat,
                    OrderedItem.order_ref,
                    OrderedItem.unit_price,
                    OrderedItem.product_discount,
                    OrderedItem.ordered_product,
                ]},
                Cart.app_user_ ,
                Cart.app_user,
                Cart.ordered_service,
                {
                    Cart.invoice:[
                        Invoice.payment
                        ]
                }
                ,
                {
                    Cart.receipt:[
                        Receipt.receipt_payment
                        ]
                }
                ,
                {
                    Cart.person:[
                        Person.person_details
                        ]
                },
            ])
    if client_id != 0 :
        conditions[Cart.cart_client_user] = client_id
    if person_id != 0 :
        conditions[Cart.cart_person_ref] = person_id
    
    # supplier_id,user_id, offset ,limit
        
    return storage_broker.get(Cart
                              ,conditions
                              ,[]
                              ,eager_fields
                              ,offset=offset
                              ,limit=limit
                              )


def touch_cart(cart_id: int):
    
    # supplier_id,user_id, offset ,limit
        
    cart_list = storage_broker.get(Cart
                              ,{Cart.cart_id:cart_id}
                              ,[]
                              ,None
                              )
    if cart_list == []:
        return None     
    return cart_list[0]


def fetch_business_operations(supplier_id:int = 0,order_id : int = 0,cart_id: int = 0, client: int = 0, seller_id:int = 0, offset: int = 0, limit: int = 0):
    
    conditions = {}
    result = {}

    if supplier_id!=0:
        conditions[BusinessOperation.supplier_id] = supplier_id
    if order_id!=0:
        conditions[BusinessOperation.order_id] = order_id
    if cart_id!=0:
        conditions[BusinessOperation.cart_id] = cart_id
    if client!=0:
        conditions[BusinessOperation.client] = client
    if seller_id!=0:
        conditions[BusinessOperation.seller_id] = seller_id

    return storage_broker.get(BusinessOperation
                            ,conditions
                            ,[]
                            ,[]
                            ,None
                            )

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