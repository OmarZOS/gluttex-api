
from core.models import  Product, ProductCategory, ProductImage, ProductProvider, ProductProviderType
import storage.storage_broker as storage_broker

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

def get_products_by_category_id(category_id: int,offset: int,limit: int):
    return storage_broker.get(Product,{Product.product_category_id:category_id},[ProductCategory,ProductProvider],[Product.product_category,Product.product_provider],None,offset,limit)

def get_product_image_by_id(image_id: int):
    return storage_broker.get(ProductImage,{ProductImage.id_product_image:image_id},[],None,[])

def get_product_categories():
    return storage_broker.get(ProductCategory)

def fetch_all_product(offset, limit):
    
    return storage_broker.get(Product,conditions=None,join_tables=[ProductCategory],eager_load_depth= 
                              [
        Product.product_category, 
        Product.product_provider, 
        {Product.product_image: [ProductImage.id_product_image],}  # Nested eager load for specific fields
    ],offset=offset, limit=limit)
