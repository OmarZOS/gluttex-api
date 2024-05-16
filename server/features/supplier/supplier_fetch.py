






from server.core.api_models import Location_API, ProductProvider_API
from server.core.models import ProductProvider, ProductProviderType, ProviderDetails
import server.storage.storage_broker as storage_broker



def fetch_supplier_by_id(provider_id: str):
    records = storage_broker.get(ProductProvider,{ProductProvider.id_product_provider:provider_id},None,[])
    if records == []: return None
    return records[0]

def fetch_supplier_type_object_by_id(type_id: str):
    records = storage_broker.get(ProductProviderType,{ProductProviderType.id_product_provider_type:type_id},None,[])
    if records == []: return None
    supplier = ProductProviderType(id_product_provider_type = records[0].id_product_provider_type)
    return supplier 





