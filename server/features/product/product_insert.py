
# here, we make schema translations

from core.api_models import Product_API, ProductImage_API
from core.messages import PRODUCT_ALREADY_EXISTS, PRODUCT_CATEGORY_NOT_EXISTS, PRODUCT_NOT_EXISTS
from core.models import *
from features.insertion import insert_or_complete_or_raise
from features.product.product_fetch import fetch_product_by_id
from features.supplier.supplier_fetch import fetch_supplier_by_id
import storage.storage_broker as storage_broker



def fetch_product_category_object_by_id(category_id: str):
    record = storage_broker.get(ProductCategory,{ProductCategory.id_product_category:category_id},None,[])
    if record == []:
        return None
    supplier = ProductCategory(id_product_category = record[0].id_product_category)
    return supplier 

def build_product(product: Product_API):
    return Product(product_name=product.product_name,
                    product_brand=product.product_brand,
                    product_barcode=product.product_barcode)

def insert_product(product_api: Product_API, image: ProductImage_API):
    
    product_old = fetch_product_by_id(product_api.id_product)
    if product_old != None : 
        raise Exception(PRODUCT_ALREADY_EXISTS)

    product_category = fetch_product_category_object_by_id(product_api.id_product_category)
    if product_category == None : 
        raise Exception(PRODUCT_CATEGORY_NOT_EXISTS)

    product_suppliers = fetch_supplier_by_id(product_api.product_provider_id)
    if product_suppliers == [] : 
        raise Exception(PRODUCT_NOT_EXISTS)

    product = build_product(product_api)

    product.product_provider_id = product_suppliers[0].id_product_provider
    product.product_category_id = product_category.id_product_category
    


    code,product,msg = insert_or_complete_or_raise(product)
    if (code == 1): return msg
    
    return product

