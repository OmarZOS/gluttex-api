
from server.core.api_models import Product_API
from server.core.models import  Product, ProductCategory
import server.storage.storage_broker as storage_broker




def fetch_product_by_id(prod_id: int):
    records = storage_broker.get(Product,{Product.id_product:prod_id},[])
    if records == []:
        return None
    return records[0]

def fetch_product_object_by_id(product_id: str):
    
    record = storage_broker.get(Product,{Product.id_product:product_id},None,[])
    if record == []:
        return None
    product = product(id_product=record[0].id_product,
                product_details_id=record[0].product_details_id, 
                product_blood_type_id=record[0].product_blood_type_id, 
                product_location_id=record[0].product_location_id,
                )
    return product

# def fetch_products_by_category(Category_id: int):
#     return storage_broker.get(Category,{Category.categoryId:Category_id},[])

def get_products_by_category_id(category_id: int):
    return storage_broker.get(Product,{Product.product_category_id:category_id},[])


def get_product_categories():
    return storage_broker.get(ProductCategory)


def fetch_all_product():
    return storage_broker.get(Product)
