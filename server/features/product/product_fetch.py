
from core.models import Category, Product
import storage.storage_broker as storage_broker

def fetch_product_by_id(prod_id: int):
    return storage_broker.get(Product,{Product.productId:prod_id},[])

def fetch_products_by_category(Category_id: int):
    return storage_broker.get(Category,{Category.categoryId:Category_id},[])

def fetch_all_product():
    return storage_broker.get(Product)
