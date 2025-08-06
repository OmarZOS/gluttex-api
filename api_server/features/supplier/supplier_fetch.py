






from core.api_models import Location_API, ProductProvider_API
from core.models import Location, ProductProvider, ProductProviderType, ProviderDetails
import storage.storage_broker as storage_broker



def fetch_supplier_by_id(provider_id: str):
    records = storage_broker.get(ProductProvider,{ProductProvider.id_product_provider:provider_id},None,[{ProductProvider.product_provider_location:[Location.position_wkt,Location.location_name]},ProductProvider.product_provider_type,ProductProvider.product_provider_details])
    # if records == []: return None
    return records

def fetch_suppliers(offset,limit):
    records = storage_broker.get(ProductProvider,{},None,[{ProductProvider.product_provider_location:[Location.position_wkt,Location.location_name]},ProductProvider.product_provider_type,ProductProvider.product_provider_details],offset=offset,limit=limit)
    # if records == []: return None
    return records

def fetch_supplier_categories():
    records = storage_broker.get(ProductProviderType,{},None,[])
    # if records == []: return None
    return records




def fetch_supplier_type_object_by_id(type_id: str):
    records = storage_broker.get(ProductProviderType,{ProductProviderType.id_product_provider_type:type_id},None,[])
    if records == []: return None
    supplier = ProductProviderType(id_product_provider_type = records[0].id_product_provider_type)
    return supplier 





