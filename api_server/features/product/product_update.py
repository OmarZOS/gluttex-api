


# here, we make schema translations

from datetime import datetime
from core.api_models import Product_API, ProductImage_API
from core.messages import PRODUCT_ALREADY_EXISTS, PRODUCT_CATEGORY_NOT_EXISTS, PRODUCT_NOT_EXISTS, PRODUCT_SUPPLIER_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.product.product_fetch import fetch_product_by_id
from features.supplier.supplier_fetch import fetch_supplier_by_id
from features.product.product_insert import fetch_product_category_object_by_id
import storage.storage_broker as storage_broker

subscribers = {}

async def notify_subscribers(product_id, data):
    if product_id in subscribers:
        for queue in subscribers[product_id]:
            await queue.put(data)



def build_product(product: Product_API):
    return Product(product_name=product.product_name,
                    product_brand=product.product_brand,
                    product_barcode=product.product_barcode,
                    product_price = product.product_price,
                    product_quantity = product.product_quantity,
                    last_updated = datetime.now(),
                    )

def update_product(product_id: int,product_api: Product_API, image: ProductImage_API):
    
    product_category = fetch_product_category_object_by_id(product_api.id_product_category)
    if product_category == None : 
        raise Exception(PRODUCT_CATEGORY_NOT_EXISTS)

    product_suppliers = fetch_supplier_by_id(product_api.product_provider_id)
    if product_suppliers == [] : 
        raise Exception(PRODUCT_SUPPLIER_NOT_EXISTS)
    
    product_old = fetch_product_by_id(product_id)
    if product_old == None : 
        raise Exception(PRODUCT_NOT_EXISTS)
    # print(product_old)
    product_old.product_name = product_api.product_name
    product_old.product_brand = product_api.product_brand
    product_old.product_barcode = product_api.product_barcode
    product_old.product_price = product_api.product_price
    product_old.product_quantity = product_api.product_quantity
    product_old.last_updated = datetime.now()
    product_old.product_description = product_api.product_description


    product_old.product_provider_id = product_suppliers[0].id_product_provider
    product_old.product_category_id = product_category.id_product_category
    
    product = update_record_in_api(product_old)
    if (image.id_product_image==0):
        if (image.product_image_url):
            product_image = ProductImage(product_image_url = image.product_image_url)
            product_image.product_ref_id = product_old.id_product
            code,new_image,msg = insert_or_complete_or_raise(product_image)
    
    return product





