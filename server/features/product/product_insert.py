
# here, we make schema translations

from core.api_models import Product_API
from core.models import *
from features.insertion import insert_or_complete_or_raise


def insert_category(prod: Product_API):
    start_category = Category(categoryId=prod.categoryId,
                            categoryName=prod.categoryName,
                            description=prod.category_description)
    code,end_category,msg = insert_or_complete_or_raise(start_category)
    if (code == 1): return msg
    return end_category

def insert_supplier(prod: Product_API):
    start_supplier = ProductSupplier(supplierId=prod.supplierId,
                               supplierName=prod.supplierName)
    code,end_supplier,msg = insert_or_complete_or_raise(start_supplier)
    if (code == 1): return msg
    return end_supplier


def insert_product(prod: Product_API):
    
    category = insert_category(prod)
    
    supplier = insert_supplier(prod)

    product = Product(productId=prod.productId,
                        productName=prod.productName,
                        description=prod.description,
                        price=prod.price,
                        availability=prod.availability,
                        Category_=[category],
                        ProductSupplier=[supplier]
                        )
    code,product,msg = insert_or_complete_or_raise(product)
    if (code == 1): return msg
    
    return "Insertion successfull."

