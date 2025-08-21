# here, we make schema translations

from core.exception_handler import APIException
from core.messages import *
from features.insertion import delete_record_from_api
from features.product.product_fetch import fetch_product_by_id

def delete_product(product_id: int):
    product = fetch_product_by_id(product_id)
    if product == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=PRODUCT_NOT_EXISTS,message=f"{PRODUCT_DELETE_FAILED}: ")
    # for now, just delete the product, since we don't want to delete person records
    return delete_record_from_api(product)