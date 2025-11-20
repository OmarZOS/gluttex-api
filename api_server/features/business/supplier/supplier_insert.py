
from core.exception_handler import APIException
from core.api_models import Location_API, OrganisationImage_API, ProductProvider_API, ProviderImage_API, ProviderOrganisation_API
from core.messages import *
from core.models import OrganisationImage, ProductProvider, ProductProviderType, ProviderDetails, ProviderImage, ProviderOrganisation
from features.insertion import insert_or_complete_or_raise
from features.business.location.location_insert import build_location
from features.business.supplier.supplier_fetch import fetch_org_by_id, fetch_org_by_name, fetch_supplier_by_id, fetch_supplier_type_object_by_id


def build_supplier_details(provider: ProductProvider_API):

    details = ProviderDetails(
        provider_name = provider.provider_name,
        provider_contact_info = provider.provider_contact_info)
    if provider.idprovider_details_id != 0:
        details.idprovider_details_id= provider.idprovider_details_id
    return details

def build_provider_object(provider: ProductProvider_API,location:Location_API):

    supplier_type = fetch_supplier_type_object_by_id(provider.id_product_provider_type)
    if supplier_type == None:
        raise APIException(status=HTTP_404_NOT_FOUND,code=SUPPLIER_TYPE_NOT_EXISTS,message=f"{SUPPLIER_TYPE_NOT_EXISTS}: {provider.id_product_provider_type}")

    new_supplier = ProductProvider()

    new_supplier.product_provider_type_id = supplier_type.id_product_provider_type
    new_supplier.product_provider_owner = provider.id_provider_owner
    
    new_supplier.product_provider_location = build_location(location)
    new_supplier.product_provider_details = build_supplier_details(provider)
    
    if (provider.id_provider_organisation == 0):
        new_supplier.product_provider_org = ProviderOrganisation(provider_organisation_name=provider.provider_organisation_name
                                                                 ,provider_organisation_desc = provider.provider_organisation_desc)
    else:
        new_supplier.product_provider_org_id= provider.id_provider_organisation
    return new_supplier



def insert_supplier(provider: ProductProvider_API,location:Location_API, image: ProviderImage_API):

    if fetch_supplier_by_id(provider.id_product_provider) != []:
        raise APIException(status=HTTP_409_CONFLICT,code=SUPPLIER_INSERT_FAILED,message=f"{SUPPLIER_INSERT_FAILED}: {provider.id_product_provider}")
    
    new_supplier = build_provider_object(provider,location)

    if (image.provider_image_url):
        # inserted_image_url = await upload_image("recipe",recipe_api.recipe_owner_id,uuid.uuid4(),image.recipe_image_url)
        _image = ProviderImage(provider_image_url  = image.provider_image_url)
        new_supplier.provider_image = [_image]


    try:
        end_supplier = insert_or_complete_or_raise(new_supplier)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=SUPPLIER_INSERT_FAILED,message=SUPPLIER_INSERT_FAILED,details=f"{str(e)}")
    
    return end_supplier

def insert_org(org: ProviderOrganisation_API,org_image: OrganisationImage_API):

    if fetch_org_by_name(org.provider_organisation_name) != []:
        raise APIException(status= HTTP_409_CONFLICT,code=ORG_ALREADY_EXISTS,message=f"{ORG_ALREADY_EXISTS}: {org.provider_organisation_name}")
    

    model_org = ProviderOrganisation(
        # idprovider_organisation = org.id_provider_organisation,
        provider_organisation_name = org.provider_organisation_name,
        provider_organisation_desc = org.provider_organisation_desc
    )

    if (org_image.org_image_url):
        # inserted_image_url = await upload_image("recipe",recipe_api.recipe_owner_id,uuid.uuid4(),image.recipe_image_url)
        _image = OrganisationImage(org_image_url  = org_image.org_image_url)
        model_org.organisation_image = [_image]

    try:
        end_org = insert_or_complete_or_raise(model_org)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=PRODUCT_UPDATE_FAILED,message=PRODUCT_UPDATE_FAILED,details=f"{str(e)}")


    return end_org