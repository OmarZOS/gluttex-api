






from core.api_models import Location_API, ProductProvider_API
from core.models import Address, Location, OrganisationImage, ProductProvider, ProductProviderType, ProviderDetails, ProviderImage, ProviderOrganisation
import storage.storage_broker as storage_broker



def fetch_supplier_by_id(provider_id: str):
    records = storage_broker.get(ProductProvider
                                 ,{ProductProvider.id_product_provider:provider_id}
                                 ,None
                                 ,[
                                     {ProductProvider.product_provider_location:
                                        [Location.position_wkt,Location.location_name,Location.id_location,Location.location_address_id]
                                      }
                                    ,ProductProvider.product_provider_type
                                    ,ProductProvider.product_provider_details
                                    ,ProductProvider.product_provider_org
                                    ,ProductProvider.provider_image
                                    ,ProductProvider.management_rule
                                ])
    
    if(records != []):
        if(records[0].product_provider_location.location_address_id!=None):
            addresses = storage_broker.get(Address
                                    ,{Address.id_address:records[0].product_provider_location.location_address_id}
                                    ,None
                                    ,[
                                        ])
            if (addresses!=[]):
                records[0].product_provider_location.location_address = addresses[0]
        

    # if records == []: return None
    return records

def fetch_only_supplier_by_id(provider_id: str):
    records = storage_broker.get(ProductProvider
                                 ,{ProductProvider.id_product_provider:provider_id}
                                 ,None
                                 ,[
                                     ProductProvider.product_provider_location
                                    ,ProductProvider.product_provider_details
                                    ,ProductProvider.management_rule])
    # if records == []: return None
    return records

def fetch_org_by_id(org_id: str):
    records = storage_broker.get(ProviderOrganisation
    ,{ProviderOrganisation.idprovider_organisation:org_id}
    ,None
    ,[ProviderOrganisation.organisation_image
    ,ProviderOrganisation.product_provider
    ,ProviderOrganisation.management_rule])
    # if records == []: return None
    return records

def fetch_org_by_name(org_name: str):
    records = storage_broker.get(ProviderOrganisation
    ,{ProviderOrganisation.provider_organisation_name:org_name}
    ,None,[])
    # if records == []: return None
    return records

def fetch_supplier_image_by_id(image_id: str):
    records = storage_broker.get(
        ProviderImage
        ,{
            ProviderImage.id_provider_image:image_id
        }
        ,None
        ,None)
    # if records == []: return None
    return records

def fetch_image_by_supplier(provider_id: str):
    records = storage_broker.get(
        ProviderImage
        ,{
            ProviderImage.provider_ref_id:provider_id
        }
        ,None
        ,None)
    # if records == []: return None
    return records


def fetch_organisation_image_by_id(image_id: str):
    records = storage_broker.get(
        OrganisationImage
        ,{
            OrganisationImage.id_org_image:image_id
        }
        ,None
        ,None)
    # if records == []: return None
    return records

def fetch_suppliers(owner_id=0,org_id=0,offset=0,limit=10):
    conditions = {}
    if int(owner_id) != 0:
        conditions[
                ProductProvider.product_provider_owner
            ] = owner_id
    if int(org_id) != 0:
        conditions[
                ProductProvider.product_provider_org_id
            ] = org_id
    
    records = storage_broker.get(
        ProductProvider
        ,conditions=conditions
        ,join_tables=None
        ,eager_load_depth=[
                {
                    ProductProvider.product_provider_location:
                    [

                        Location.id_location,
                        Location.location_address_id,
                        Location.position_wkt
                        ,Location.location_name,
                    ]
                }
                ,ProductProvider.product_provider_type
                ,ProductProvider.product_provider_details
                ,ProductProvider.provider_image
                ,ProductProvider.product_provider_org
            ]
            ,offset=offset
            ,limit=limit
            )
    # if records == []: return None
    return records

def fetch_orgs(offset,limit):
    records = storage_broker.get(ProviderOrganisation,{},None,eager_load_depth=[
                
                ProviderOrganisation.organisation_image
                
            ],offset=offset,limit=limit)
    # if records == []: return None
    return records

def fetch_supplier_categories():
    records = storage_broker.get(ProductProviderType,{},None,[])
    # if records == []: return None
    return records

def fetch_supplier_type_object_by_id(type_id: str):
    records = storage_broker.get(ProductProviderType
                                 ,{
                                     ProductProviderType.id_product_provider_type:type_id
                                     }
                                 ,None
                                 ,[])
    if records == []: return None
    supplier = ProductProviderType(id_product_provider_type = records[0].id_product_provider_type)
    return supplier 






