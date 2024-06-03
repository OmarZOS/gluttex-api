# here, we make schema translations

from core.messages import PRODUCT_NOT_EXISTS
from features.insertion import delete_record_from_api
from features.product.product_fetch import fetch_product_by_id

def delete_product(product_id: int):
    nutzers = fetch_product_by_id(product_id)
    if nutzers == []:
        raise Exception(PRODUCT_NOT_EXISTS)
    # for now, just delete the product, since we don't want to delete person records
    return delete_record_from_api(nutzers)