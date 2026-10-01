# repositories/product_repository.py
from typing import Optional, List
from sqlalchemy import or_,not_

from core.models.models import (
    NamingContribution,
    Product,
    Iproduct,
    ProductCategory,
    ProductImage,
    ProductProvider,
    ProductReaction,
)
import storage.storage_broker as storage_broker


def _visible_filter():
    """
    SQLAlchemy clause that matches rows visible to buyers.

    Treats a NULL `product_visibility` as visible: rows that predate the
    visibility column are public by default. Anything else must be the
    literal `'VISIBLE'`.
    """
    return or_(
        Product.product_visibility.is_(None),
        Product.product_visibility == 'VISIBLE'
    )


class ProductRepository:
    """Repository for Product-related database operations."""

    # ==================== Product reads ====================

    def get_product_by_id(
        self,
        product_id: int,
        eager_load: bool = False,
        include_hidden: bool = True,
    ) -> Optional[Product]:
        """
        Get a product by ID.

        `include_hidden` defaults to True so the editor can always open a
        product by id, even when it's hidden. Pass False to treat a hidden
        product as if it doesn't exist.
        """
        conditions = [Product.id_product == product_id]
        
        if not include_hidden:
            conditions.append(_visible_filter())

        eager = (
            [
                Product.product_reaction,
                Product.product_category,
                Product.product_provider,
                Product.product_image,
                {Product.product_origin: [{Iproduct:[Iproduct.naming_contribution]}]},
            ]
            if eager_load
            else []
        )

        records = storage_broker.get(
            Product,
            conditions,
            [],
            eager,
        )
        return records[0] if records else None

    def get_products_by_ids(
        self,
        product_ids: List[int],
        eager_load: bool = False,
        include_hidden: bool = True,
    ) -> List[Product]:
        """
        Get products by a list of IDs.

        `include_hidden` defaults to True because callers that already
        have the ids usually want them back regardless of visibility
        (basket items, order history, cart references).
        """
        if not product_ids:
            return []

        conditions = [Product.id_product.in_(product_ids)]
        conditions.append(not_(Product.product_visibility == "DELETED"))
        if not include_hidden:
            conditions.append(_visible_filter())

        eager = (
            [
                Product.product_reaction,
                Product.product_category,
                Product.product_provider,
                Product.product_image,
                {Product.product_origin: [{Iproduct:[Iproduct.naming_contribution]}]},
            ]
            if eager_load
            else []
        )

        return storage_broker.get(
            Product,
            conditions,
            [],
            eager,
        )

    def get_all_products(
        self,
        user_id: int = 0,
        provider_id: int = 0,
        category_id: int = 0,
        offset: int = 0,
        limit: int = 10,
        serialize: bool = False,
        include_hidden: bool = False,
    ) -> List[Product]:
        """
        Get all products with filters.

        `include_hidden` defaults to False so the public catalog never
        surfaces hidden products. Editors that need everything must opt in
        explicitly.
        """
        conditions = []
        conditions.append(not_(Product.product_visibility == "DELETED"))

        if user_id != 0:
            conditions.append(Product.product_owner == user_id)
        if category_id != 0:
            conditions.append(Product.product_category_id == category_id)
        if provider_id != 0:
            conditions.append(Product.product_provider_id == provider_id)
        if not include_hidden:
            conditions.append(_visible_filter())

        return storage_broker.get(
            Product,
            conditions=conditions,
            join_tables=[],
            eager_load_depth=[
                Product.product_category,
                Product.product_provider,
                {
                    Product.product_image: [
                        ProductImage.id_product_image,
                        ProductImage.product_image_url,
                    ]
                },
                {Product.product_origin: [{Iproduct.naming_contribution:[NamingContribution]}]},
            ],
            offset=offset,
            limit=limit,
        )

    def get_products_by_category(
        self,
        category_id: int,
        offset: int = 0,
        limit: int = 10,
        include_hidden: bool = False,
    ) -> List[Product]:
        """Get products by category ID."""
        conditions = [Product.product_category_id == category_id]
        conditions.append(not_(Product.product_visibility == "DELETED"))
        if not include_hidden:
            conditions.append(_visible_filter())

        return storage_broker.get(
            Product,
            conditions,
            [ProductCategory, ProductProvider],
            [
                Product.product_image,
                Product.product_category,
                Product.product_provider,
                {Product.product_origin: [{Iproduct:[Iproduct.naming_contribution]}]},
            ],
            None,
            offset,
            limit,
            serialize=True,
        )

    # ==================== Product writes ====================

    def create_product(self, product: Product) -> Product:
        """Create a new product."""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(product)

    def update_product(self, product: Product) -> Product:
        """Update an existing product."""
        from features.insertion import update_record_in_api
        return update_record_in_api(product)

    def delete_product(self, product: Product) -> bool:
        """Delete a product."""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(product)

    # ==================== Categories ====================

    def get_product_categories(self) -> List[ProductCategory]:
        """Get all product categories."""
        return storage_broker.get(ProductCategory,None,None,[ProductCategory.naming_contribution])

    def get_product_category_by_id(
        self, category_id: str
    ) -> Optional[ProductCategory]:
        """Get product category by ID."""
        records = storage_broker.get(
            ProductCategory,
            {ProductCategory.id_product_category: category_id},
            None,
            [ProductCategory.naming_contribution]
        )
        return records[0] if records else None

    # ==================== Images ====================

    def get_product_image_by_id(self, image_id: int) -> List[ProductImage]:
        """Get product image by ID."""
        return storage_broker.get(
            ProductImage,
            {ProductImage.id_product_image: image_id},
        )

    def create_product_image(self, image: ProductImage) -> ProductImage:
        """Create a product image."""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(image)

    def update_product_image(self, image: ProductImage) -> ProductImage:
        """Update a product image."""
        from features.insertion import update_record_in_api
        return update_record_in_api(image)