# here, we make schema translations

from features.supplier.supplier_fetch import fetch_image_by_supplier, fetch_only_supplier_by_id
from core.exception_handler import APIException
from core.api_models import AppUser_API
from core.messages import *
from core.models import AppUser
from features.insertion import delete_record_from_api

def delete_supplier(supplier: int):
    
    suppliers = fetch_only_supplier_by_id(supplier)
    if suppliers == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=APPUSER_NOT_EXISTS,message=f"{USER_FETCH_NOT_FOUND}: {user.id_app_user}")
    for img in fetch_image_by_supplier(suppliers[0].id_product_provider):
        delete_record_from_api(img)
    
    # for now, just delete the user, since we don't want to delete person records
    return delete_record_from_api(suppliers[0])