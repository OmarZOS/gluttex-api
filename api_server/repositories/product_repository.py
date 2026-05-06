from typing import Optional, List, Dict, Any
from core.models import (
    Product, Iproduct, ProductCategory, ProductImage, 
    ProductProvider, ProductReaction
)
import storage.storage_broker as storage_broker

class ProductRepository:
    """Repository for Product-related database operations"""
    
    def get_product_by_id(self, product_id: int, eager_load: bool = False) -> Optional[Product]:
        """Get product by ID with optional eager loading"""
        if eager_load:
            records = storage_broker.get(
                Product,
                {Product.id_product: product_id},
                [],
                [Product.product_reaction, Product.product_category, Product.product_provider, Product.product_image]
            )
        else:
            records = storage_broker.get(
                Product,
                {Product.id_product: product_id},
                [],
                []
            )
        return records[0] if records else None
    
    def get_all_products(
        self, 
        user_id: int = 0, 
        provider_id: int = 0,
        category_id: int = 0,
        offset: int = 0, 
        limit: int = 10,
        serialize : bool = False,
    ) -> List[Product]:
        """Get all products with filters"""
        conditions = {}
        if user_id != 0:
            conditions[Product.product_owner] = user_id
        if category_id != 0:
            conditions[Product.product_category_id] = category_id
        if provider_id != 0:
            conditions[Product.product_provider_id] = provider_id

        return storage_broker.get(
            Product,
            conditions=conditions,
            join_tables=[],
            eager_load_depth=[
                Product.product_category,
                Product.product_provider,
                {Product.product_image: [
                    ProductImage.id_product_image,
                    ProductImage.product_image_url
                ]}
            ],
            offset=offset,
            limit=limit,
            serialize=serialize
        )
    
    def get_products_by_category(self, category_id: int, offset: int = 0, limit: int = 10) -> List[Product]:
        """Get products by category ID"""
        return storage_broker.get(
            Product,
            {Product.product_category_id: category_id},
            [ProductCategory, ProductProvider],
            [Product.product_image, Product.product_category, Product.product_provider],
            None,
            offset,
            limit,
            serialize=True
        )
    
    def create_product(self, product: Product) -> Product:
        """Create a new product"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(product)
    
    def update_product(self, product: Product) -> Product:
        """Update an existing product"""
        from features.insertion import update_record_in_api
        return update_record_in_api(product)
    
    def delete_product(self, product: Product) -> bool:
        """Delete a product"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(product)
    
    def get_product_categories(self) -> List[ProductCategory]:
        """Get all product categories"""
        return storage_broker.get(ProductCategory,serialize=True)
    
    def get_product_category_by_id(self, category_id: str) -> Optional[ProductCategory]:
        """Get product category by ID"""
        records = storage_broker.get(ProductCategory, {ProductCategory.id_product_category: category_id})
        return records[0] if records else None
    
    def get_product_image_by_id(self, image_id: int) -> List[ProductImage]:
        """Get product image by ID"""
        return storage_broker.get(ProductImage, {ProductImage.id_product_image: image_id})
    
    def create_product_image(self, image: ProductImage) -> ProductImage:
        """Create a product image"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(image)
    
    def update_product_image(self, image: ProductImage) -> ProductImage:
        """Update a product image"""
        from features.insertion import update_record_in_api
        return update_record_in_api(image)
