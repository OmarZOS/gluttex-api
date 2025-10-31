
# here, we make schema translations

import uuid
from core.exception_handler import APIException
from features.media_net import upload_image
from core.api_models import Product_API, ProductImage_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.product.product_fetch import fetch_product_by_id
from features.supplier.supplier_fetch import fetch_supplier_by_id
import storage.storage_broker as storage_broker
from datetime import datetime;


def fetch_product_category_object_by_id(category_id: str):
    record = storage_broker.get(ProductCategory,{ProductCategory.id_product_category:category_id},None,[])
    if record == []:
        return None
    supplier = ProductCategory(id_product_category = record[0].id_product_category)
    return supplier 

def build_product(product: Product_API):
    return Product(product_name=product.product_name,
                    product_brand=product.product_brand,
                    product_barcode=product.product_barcode,
                    product_price = product.product_price,
                    product_quantifier = product.product_quantifier,
                    product_quantity = product.product_quantity,
                    product_description = product.product_description,
                    product_owner = product.product_owner,
                    created = datetime.now(),
                    last_updated = datetime.now(),
                    )

async def insert_product(product_api: Product_API, image: ProductImage_API):
    
    product_old = fetch_product_by_id(product_api.id_product)
    if product_old != None : 
        raise APIException(status= HTTP_409_CONFLICT,code=PRODUCT_ALREADY_EXISTS,details="")

    product_category = fetch_product_category_object_by_id(product_api.id_product_category)
    if product_category == None : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=PRODUCT_CATEGORY_NOT_EXISTS,message=PRODUCT_CATEGORY_NOT_EXISTS,details="")

    product_suppliers = fetch_supplier_by_id(product_api.product_provider_id)
    if product_suppliers == [] : 
        raise APIException(status= HTTP_404_NOT_FOUND,code=PRODUCT_SUPPLIER_NOT_EXISTS,message=PRODUCT_SUPPLIER_NOT_EXISTS,details="")

    product = build_product(product_api)

    product.product_provider_id = product_suppliers[0].id_product_provider
    product.product_category_id = product_category.id_product_category
    
    if (image.product_image_url):
        inserted_image_url = image.product_image_url
        # if (image.id_product_image==0):
        product_image = ProductImage(product_image_url  = inserted_image_url)
        product.product_image = [product_image]
    
    try:
        product = insert_or_complete_or_raise(product)
    except Exception as e:
        raise APIException(status= HTTP_417_EXPECTATION_FAILED,code=PRODUCT_INSERT_FAILED,details=f"{str(e)}")    
    return product

