from features.location.location_update import update_location
from core.exception_handler import APIException
from core.api_models import Location_API, OrganisationImage_API, ProductProvider_API, ProviderImage_API
from core.messages import *
from core.models import OrganisationImage, ProductProvider, ProviderDetails, ProviderImage, ProviderOrganisation
from features.insertion import insert_or_complete_or_raise, update_record_in_api
# from features.location.location_insert import build_location
from features.supplier.supplier_fetch import (
    fetch_org_by_id,
    fetch_org_by_name,
    fetch_organisation_image_by_id,
    fetch_supplier_by_id,
    fetch_supplier_image_by_id,
    fetch_supplier_type_object_by_id,
)


def build_supplier_details(provider: ProductProvider_API) -> ProviderDetails:
    """
    Build a ProviderDetails object from API data.
    """
    details = ProviderDetails(
        provider_name=provider.provider_name,
        provider_contact_info=provider.provider_contact_info,
    )
    if provider.idprovider_details_id != 0:
        details.idprovider_details_id = provider.idprovider_details_id
    return details


def build_provider_object(provider: ProductProvider_API) -> ProductProvider:
    """
    Build a ProductProvider object from API data.
    """
    supplier_type = fetch_supplier_type_object_by_id(provider.id_product_provider_type)
    if supplier_type is None:
        raise APIException(status= HTTP_404_NOT_FOUND,code=SUPPLIER_TYPE_NOT_EXISTS,message=f"{SUPPLIER_TYPE_NOT_EXISTS}: {provider.id_product_provider_type}")

    new_supplier = ProductProvider()
    new_supplier.product_provider_type_id = supplier_type.id_product_provider_type
    new_supplier.product_provider_owner = provider.id_provider_owner
    # If you want to attach location later, uncomment and pass Location_API
    # new_supplier.product_provider_location = build_location(location)
    new_supplier.product_provider_details = build_supplier_details(provider)

    return new_supplier


def update_supplier(provider: ProductProvider_API, image: ProviderImage_API, location: Location_API):
    """
    Update an existing supplier and optionally handle provider image.
    """
    # Validate supplier type
    if fetch_supplier_type_object_by_id(provider.id_product_provider_type) is None:
        raise APIException(status= HTTP_404_NOT_FOUND,code=PRODUCT_CATEGORY_NOT_EXISTS,message=PRODUCT_CATEGORY_NOT_EXISTS,details=PRODUCT_CATEGORY_NOT_EXISTS)

    # Fetch old supplier
    suppliers_old = fetch_supplier_by_id(provider.id_product_provider)
    if not suppliers_old:
        raise APIException(status= HTTP_404_NOT_FOUND,code=SUPPLIER_NOT_EXISTS,message=SUPPLIER_NOT_EXISTS,details=SUPPLIER_NOT_EXISTS)

    supplier_old = suppliers_old[0]
    supplier_old.product_provider_details.provider_name  = provider.provider_name
    supplier_old.product_provider_details.provider_contact_info  = provider.provider_contact_info
    supplier_old.product_provider_type_id = provider.id_product_provider_type
    supplier_old.product_provider_org_id = provider.id_provider_organisation
    # Update provider image if needed
    code, msg = 0, None
    if image.provider_image_url:
        if image.id_provider_image == 0:
            _image = ProviderImage(provider_image_url=image.provider_image_url)
            _image.provider_ref = supplier_old
            try:
                insert_or_complete_or_raise(_image)
            except Exception as e:
                raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=IMAGE_INSERT_FAILED,message=IMAGE_INSERT_FAILED,details=f"{str(e)}")
        else:
            same_image = fetch_supplier_image_by_id(image.id_provider_image)[0]
            same_image.provider_image_url = image.provider_image_url
            try:
                update_record_in_api(same_image)
            except Exception as e:
                raise APIException(status= HTTP_409_CONFLICT,code=IMAGE_UPDATE_FAILED,details=f"{str(e)}")
    
    # if location.id_location != 0:
    supplier_old.product_provider_location_id = update_location(location.id_location, location).id_location

    # Update supplier record
    try:
        return update_record_in_api(supplier_old)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=SUPPLIER_UPDATE_FAILED,message=f"{SUPPLIER_UPDATE_FAILED}: {provider.id_product_provider}",details=f"{str(e)}")

def update_organisation(org: ProviderOrganisation, image: OrganisationImage_API):
    """
    Update an existing organisation and optionally handle organisation image.
    """

    # Fetch old supplier
    orgs_old = fetch_org_by_id(org.id_provider_organisation)
    # Validate supplier type
    if  orgs_old == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=ORGANISAION_NOT_FOUND)

    org_old = orgs_old[0]
    if (org_old.provider_organisation_name != org.provider_organisation_name):
        if fetch_org_by_name(org.provider_organisation_name) !=[]:
            raise APIException(status= HTTP_409_CONFLICT,code=ORGANISAION_NAME_USED)

    org_old.provider_organisation_name = org.provider_organisation_name
    org_old.provider_organisation_desc = org.provider_organisation_desc
    # Update provider image if needed
    code, msg = 0, None
    if image.org_image_url:
        if image.id_org_image == 0:
            _image = OrganisationImage(org_image_url=image.org_image_url)
            _image.org_ref_id = org_old.idprovider_organisation
            try:
                insert_or_complete_or_raise(_image)
            except Exception as e:
                raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=IMAGE_INSERT_FAILED,message=IMAGE_INSERT_FAILED,details=f"{str(e)}")
        else:
            same_image = fetch_organisation_image_by_id(image.id_org_image)[0]
            same_image.org_image_url = image.org_image_url
            try:
                update_record_in_api(same_image)
            except Exception as e:
                raise APIException(status= HTTP_409_CONFLICT,code=IMAGE_UPDATE_FAILED,details=f"{str(e)}")
    # Update supplier record
    try:
        return update_record_in_api(org_old)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=ORG_UPDATE_FAILED,message=f"{ORG_UPDATE_FAILED}: {org.idprovider_organisation}",details=f"{str(e)}")
