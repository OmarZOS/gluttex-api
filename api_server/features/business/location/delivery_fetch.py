
# schema translations for Location

from features.business.location.location_fetch import build_address_from_delivery
from storage import storage_broker
from core.exception_handler import APIException
from core.messages import *
from core.api_models import Delivery_API, Location_API
from core.models import Address, Delivery
from features.insertion import insert_or_complete_or_raise, update_record_in_api


# Constants for error codes (define these in your constants module)
DELIVERY_INSERT_FAILED = "DELIVERY_INSERT_FAILED"

def fetch_delivery(provider_id: int = 0,order_id: int = 0,broker_id: int = 0,offset :int = 0,limit:int = 0) :
    
    conditions = {}

    if provider_id!=0:
        conditions[Delivery.delivery_provider_id] = provider_id 
    if order_id!=0:
        conditions[Delivery.delivery_placed_order] = order_id 
    if broker_id!=0:
        conditions[Delivery.delivery_broker_id] = broker_id  

    # supplier_id,user_id, offset ,limit
        
    return storage_broker.get(Delivery
                              ,conditions
                              ,[]
                              ,[
                                Delivery.cart
                                ,Delivery.placed_order
                                ,Delivery.delivery_provider
                                ,Delivery.delivery_broker
                                
                                ]
                              ,offset=offset
                              ,limit=limit
                              )