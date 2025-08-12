


from core.api_models import Location_API, ProductProvider_API
from core.messages import PRODUCT_SUPPLIER_ALREADY_EXISTS
from core.models import ProductProvider, ProductProviderType, ProviderDetails
from features.insertion import insert_or_complete_or_raise
from features.location.location_insert import build_location
from features.supplier.supplier_fetch import fetch_supplier_by_id, fetch_supplier_type_object_by_id


def build_supplier_details(provider: ProductProvider_API):

    details = ProviderDetails(provider_name = provider.provider_name,
                                provider_contact_info = provider.provider_contact_info)
    
    return details

def build_provider_object(provider: ProductProvider_API,location:Location_API):

    supplier_type = fetch_supplier_type_object_by_id(provider.id_product_provider_type)

    new_supplier = ProductProvider()

    new_supplier.product_provider_type_id = supplier_type.id_product_provider_type
    new_supplier.product_provider_owner = provider.id_provider_owner
    new_supplier.product_provider_location = build_location(location)
    new_supplier.product_provider_details = build_supplier_details(provider)

    return new_supplier


def insert_supplier(provider: ProductProvider_API,location:Location_API):

    if fetch_supplier_by_id(provider.id_product_provider) != []:
        raise Exception(PRODUCT_SUPPLIER_ALREADY_EXISTS)
    
    new_supplier = build_provider_object(provider,location)

    code,end_supplier,msg = insert_or_complete_or_raise(new_supplier)
    if (code == 1): raise Exception(msg) 
    return end_supplier
