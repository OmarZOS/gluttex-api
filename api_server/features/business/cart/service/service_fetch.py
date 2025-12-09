from core.persistent_models import BusinessOperation, BusinessOperationWithTotals
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.messages import APPUSER_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_QUANTITY_NOT_ENOUGH
from core.models import *
from storage import storage_broker;


def fetch_services(service_id:int = 0,category_id:int = 0,provider_id:int = 0,offset :int = 0,limit:int = 0):
    conditions = {}
    eager_load_fields = []
    if service_id !=0:
        conditions[ProvidedService.provided_service_id] = service_id
        eager_load_fields.extend([ProvidedService.service_resource_requirement,ProvidedService.service_staff_requirement])
    if category_id !=0:
        conditions[ProvidedService.provided_service_category_id] = category_id
    if provider_id !=0:
        conditions[ProvidedService.provided_service_product_provider_id] = provider_id

    return storage_broker.get(ProvidedService
                              ,conditions
                              ,[]
                              ,eager_load_fields
                              ,offset=offset
                              ,limit=limit
                              )

    
def fetch_business_operations(supplier_id:int = 0,order_id : int = 0,cart_id: int = 0, client: int = 0, seller_id:int = 0, offset: int = 0, limit: int = 0):
    conditions = {}


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
    
    return storage_broker.get(BusinessOperationWithTotals
                            ,conditions
                            ,[]
                            ,[]
                            ,None
                            )









