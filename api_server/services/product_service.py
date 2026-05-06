# services/product_service.py
"""
Product service for managing products, images, barcode search, and AI recognition.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import BackgroundTasks
import logging

from core.exceptions.specific.supplier_exceptions import ImageInsertFailedException, ImageUpdateFailedException
from core.api_models import Product_API, ProductImage_API, Iproduct_API
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductInsertFailedException,
    ProductUpdateFailedException,
    ProductDeleteFailedException,
    ProductCategoryNotFoundException,
    ProductFetchNotFoundException,
    ProductImageNotFoundException,
    ProductQuantityNotEnoughException
)
from core.models import Product, ProductImage, Iproduct
from repositories.product_repository import ProductRepository
from repositories.iproduct_repository import IProductRepository
from services.helpers.ai_service import AIService

logger = logging.getLogger(__name__)

# Global subscribers storage
subscribers: Dict[int, List[asyncio.Queue]] = {}


class ProductService:
    """Service for product-related business logic"""
    
    def __init__(self):
        self.product_repo = ProductRepository()
        self.iproduct_repo = IProductRepository()
        self.ai_service = AIService()
    
    # ==================== Product Retrieval Methods ====================
    
    def get_product_by_id(self, product_id: int, full: bool = False) -> Product:
        """
        Get product by ID.
        
        Args:
            product_id: Product ID to retrieve
            full: Whether to load all related data eagerly
            
        Returns:
            Product object
            
        Raises:
            ProductNotFoundException: If product not found
        """
        product = self.product_repo.get_product_by_id(product_id, eager_load=full)
        if not product:
            logger.warning(f"Product not found with ID: {product_id}")
            raise ProductNotFoundException(product_id=product_id)
        
        logger.debug(f"Retrieved product with ID: {product_id}")
        return product
    
    def get_all_products(
        self,
        user_id: int = 0,
        provider_id: int = 0,
        category_id: int = 0,
        offset: int = 0,
        limit: int = 10,
        serialize : bool = False
    ) -> List[Product]:
        """
        Get all products with filters.
        
        Args:
            user_id: Filter by user ID
            provider_id: Filter by provider ID
            category_id: Filter by category ID
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of Product objects
        """
        logger.debug(f"Fetching products - user:{user_id}, provider:{provider_id}, category:{category_id}, offset:{offset}, limit:{limit}")
        return self.product_repo.get_all_products(user_id, provider_id, category_id, offset, limit,serialize)
    
    def get_products_by_category(self, category_id: int, offset: int = 0, limit: int = 10) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category_id: Category ID to filter by
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            List of Product objects
            
        Raises:
            ProductCategoryNotFoundException: If category not found
        """
        # Validate category exists
        category = self.product_repo.get_product_category_by_id(category_id)
        if not category:
            logger.warning(f"Product category not found with ID: {category_id}")
            raise ProductCategoryNotFoundException(category_id=category_id)
        
        logger.debug(f"Fetching products for category {category_id}")
        return self.product_repo.get_products_by_category(category_id, offset, limit)
    
    def get_product_categories(self) -> List:
        """
        Get all product categories.
        
        Returns:
            List of product categories
        """
        logger.debug("Fetching all product categories")
        return self.product_repo.get_product_categories()
    
    # ==================== IProduct Methods ====================
    
    def get_iproduct_by_barcode(self, barcode: str) -> Optional[List[Iproduct]]:
        """
        Get IProduct by barcode.
        
        Args:
            barcode: Product barcode to search
            
        Returns:
            List of Iproduct objects or None
        """
        logger.debug(f"Searching IProduct by barcode: {barcode}")
        return self.iproduct_repo.get_by_barcode(barcode)
    
    def get_iproduct_by_id(self, iproduct_id: int) -> Optional[Iproduct]:
        """
        Get IProduct by ID.
        
        Args:
            iproduct_id: IProduct ID to retrieve
            
        Returns:
            Iproduct object or None
        """
        logger.debug(f"Fetching IProduct with ID: {iproduct_id}")
        return self.iproduct_repo.get_by_id(iproduct_id)
    
    # ==================== AI Recognition Methods ====================
    
    async def recognize_product_from_image(self, image_bytes: bytes, language: str = "fr") -> Iproduct_API:
        """
        Recognize product from image using AI.
        
        Args:
            image_bytes: Image file bytes
            language: Language for recognition (fr/en)
            
        Returns:
            Iproduct_API object with recognized data
        """
        logger.info(f"Recognizing product from image (language={language})")
        
        ai_result, model_name = await self.ai_service.recognize_product_from_image(image_bytes, language)
        
        if not ai_result:
            logger.warning("AI recognition returned no results")
            raise ProductFetchNotFoundException(
                identifier="image",
                search_type="image_recognition"
            )
        
        return self.ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    async def get_product_info_by_barcode(self, barcode: str, language: str = "fr") -> Iproduct_API:
        """
        Get product information by barcode using AI.
        
        Args:
            barcode: Product barcode
            language: Language for recognition
            
        Returns:
            Iproduct_API object with product info
        """
        logger.info(f"Getting product info by barcode: {barcode} (language={language})")
        
        ai_result, model_name = await self.ai_service.generate_product_info_by_barcode(barcode, language)
        
        if not ai_result:
            logger.warning(f"AI returned no results for barcode: {barcode}")
            raise ProductFetchNotFoundException(
                identifier=barcode,
                search_type="barcode_ai"
            )
        
        return self.ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    # ==================== Product Creation Methods ====================
    
    async def create_product(
        self,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
        iproduct: Optional[Iproduct_API] = None
    ) -> Product:
        """
        Create a new product.
        
        Args:
            product_api: Product details
            image: Optional product image
            iproduct: Optional IProduct information
            
        Returns:
            Created Product object
            
        Raises:
            ProductAlreadyExistsException: If product already exists
            ProductCategoryNotFoundException: If category not found
            ProductInsertFailedException: If creation fails
        """
        logger.info(f"Creating new product: {product_api.product_name}")
        
        # Check if product already exists
        if product_api.id_product:
            existing = self.product_repo.get_product_by_id(product_api.id_product)
            if existing:
                logger.warning(f"Product already exists with ID: {product_api.id_product}")
                raise ProductAlreadyExistsException(
                    product_id=product_api.id_product,
                    product_name=product_api.product_name
                )
        
        # Validate category
        product_category = self.product_repo.get_product_category_by_id(product_api.id_product_category)
        if not product_category:
            logger.warning(f"Product category not found with ID: {product_api.id_product_category}")
            raise ProductCategoryNotFoundException(category_id=product_api.id_product_category)
        
        # Build product
        product = self._build_product_model(product_api)
        product.product_category_id = product_category.id_product_category
        
        # Handle image
        if image and image.product_image_url:
            product_image = ProductImage(product_image_url=image.product_image_url)
            product.product_image = [product_image]
        
        # Handle AI product data
        if iproduct:
            await self._handle_iproduct_data(product, iproduct)
        
        # Create product
        try:
            result = self.product_repo.create_product(product)
            logger.info(f"Product created successfully with ID: {result.id_product}")
            return result
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            raise ProductInsertFailedException(
                error=str(e),
                product_name=product_api.product_name
            )
    
    # ==================== Product Update Methods ====================
    
    def update_product(
        self,
        product_id: int,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Product:
        """
        Update an existing product.
        
        Args:
            product_id: Product ID to update
            product_api: Updated product details
            image: Optional updated image
            background_tasks: Background tasks for notifications
            
        Returns:
            Updated Product object
            
        Raises:
            ProductNotFoundException: If product not found
            ProductCategoryNotFoundException: If category not found
            ProductUpdateFailedException: If update fails
        """
        logger.info(f"Updating product with ID: {product_id}")
        
        # Validate category
        product_category = self.product_repo.get_product_category_by_id(product_api.id_product_category)
        if not product_category:
            logger.warning(f"Product category not found with ID: {product_api.id_product_category}")
            raise ProductCategoryNotFoundException(category_id=product_api.id_product_category)
        
        # Get existing product
        product = self.get_product_by_id(product_id)
        
        # Track changes for logging
        changes = []
        if product.product_name != product_api.product_name:
            changes.append(f"name: {product.product_name} -> {product_api.product_name}")
        if product.product_price != product_api.product_price:
            changes.append(f"price: {product.product_price} -> {product_api.product_price}")
        if product.product_quantity != product_api.product_quantity:
            changes.append(f"quantity: {product.product_quantity} -> {product_api.product_quantity}")
        
        # Update fields
        product.product_name = product_api.product_name
        product.product_brand = product_api.product_brand
        product.product_barcode = product_api.product_barcode
        product.product_price = product_api.product_price
        product.product_quantity = product_api.product_quantity
        product.product_quantifier = product_api.product_quantifier
        product.product_description = product_api.product_description
        product.product_category_id = product_category.id_product_category
        product.last_updated = datetime.now()
        
        # Handle image update
        if image and image.product_image_url:
            self._handle_product_image(image, product)
        
        # Update product
        try:
            updated_product = self.product_repo.update_product(product)
            logger.info(f"Product {product_id} updated successfully. Changes: {changes if changes else 'none'}")
            
            # Notify subscribers if background tasks provided
            if background_tasks:
                product_dict = self._product_to_dict(updated_product)
                background_tasks.add_task(self._notify_product_subscribers, product_id, product_dict)
            
            return updated_product
            
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {e}")
            raise ProductUpdateFailedException(
                product_id=product_id,
                error=str(e)
            )
    
    # ==================== Product Deletion Methods ====================
    
    def delete_product(self, product_id: int, force_delete: bool = False) -> bool:
        """
        Delete a product.
        
        Args:
            product_id: Product ID to delete
            force_delete: Force delete even if product has dependencies
            
        Returns:
            True if deletion successful
            
        Raises:
            ProductNotFoundException: If product not found
            ProductDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting product with ID: {product_id} (force={force_delete})")
        
        product = self.get_product_by_id(product_id)
        
        # Check if product has dependencies (e.g., in orders, carts)
        if not force_delete:
            has_dependencies = self._check_product_dependencies(product_id)
            if has_dependencies:
                logger.warning(f"Product {product_id} has dependencies, use force_delete=true")
                raise ProductDeleteFailedException(
                    product_id=product_id,
                    has_dependencies=True,
                    error="Product has existing dependencies (orders, carts)"
                )
        
        try:
            result = self.product_repo.delete_product(product)
            
            if not result:
                raise ProductDeleteFailedException(
                    product_id=product_id,
                    error="Repository returned False"
                )
            
            logger.info(f"Product {product_id} deleted successfully")
            return result
            
        except ProductDeleteFailedException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            raise ProductDeleteFailedException(
                product_id=product_id,
                error=str(e)
            )
    
    def _check_product_dependencies(self, product_id: int) -> bool:
        """
        Check if product has dependencies.
        
        Args:
            product_id: Product ID to check
            
        Returns:
            True if product has dependencies
        """
        # Check if product is in any orders
        order_items = self.product_repo.get_order_items_by_product(product_id)
        if order_items:
            logger.debug(f"Product {product_id} has {len(order_items)} order items")
            return True
        
        # Check if product is in any carts
        cart_items = self.product_repo.get_cart_items_by_product(product_id)
        if cart_items:
            logger.debug(f"Product {product_id} has {len(cart_items)} cart items")
            return True
        
        return False
    
    # ==================== Private Helper Methods ====================
    
    def _build_product_model(self, product_api: Product_API) -> Product:
        """
        Build Product model from API data.
        
        Args:
            product_api: API product data
            
        Returns:
            Product model instance
        """
        return Product(
            product_name=product_api.product_name,
            product_brand=product_api.product_brand,
            product_barcode=product_api.product_barcode,
            product_price=product_api.product_price,
            product_quantifier=product_api.product_quantifier,
            product_quantity=product_api.product_quantity,
            product_description=product_api.product_description,
            product_owner=product_api.product_owner,
            created=datetime.now(),
            last_updated=datetime.now(),
        )
    
    async def _handle_iproduct_data(self, product: Product, iproduct_api: Iproduct_API):
        """
        Handle IProduct data association.
        
        Args:
            product: Product to associate with IProduct
            iproduct_api: IProduct API data
        """
        if iproduct_api.id_iproduct:
            existing_iproduct = self.iproduct_repo.get_by_id(iproduct_api.id_iproduct)
            if existing_iproduct:
                self._update_iproduct(existing_iproduct, iproduct_api)
                product.product_origin = existing_iproduct
            else:
                new_iproduct = self._create_iproduct_from_api(iproduct_api)
                product.product_origin = new_iproduct
        else:
            new_iproduct = self._create_iproduct_from_api(iproduct_api)
            product.product_origin = new_iproduct
        
        logger.debug(f"Associated IProduct with product {product.id_product}")
    
    def _create_iproduct_from_api(self, iproduct_api: Iproduct_API) -> Iproduct:
        """
        Create Iproduct from API data.
        
        Args:
            iproduct_api: IProduct API data
            
        Returns:
            Iproduct model instance
        """
        now = datetime.now()
        
        return Iproduct(
            iproduct_name=iproduct_api.iproduct_name or "Unknown",
            iproduct_barcode=iproduct_api.iproduct_barcode,
            iproduct_brand=iproduct_api.iproduct_brand or "Unknown",
            iproduct_estimated_price=iproduct_api.iproduct_estimated_price or 0.0,
            iproduct_price_currency=iproduct_api.iproduct_price_currency or "DZD",
            iproduct_gluten_status=iproduct_api.iproduct_gluten_status or "unknown",
            iproduct_info_source=iproduct_api.iproduct_info_source or "ai_analysis",
            iproduct_info_confidence=iproduct_api.iproduct_info_confidence or 0.0,
            iproduct_last_price_update=iproduct_api.iproduct_last_price_update or now,
            iproduct_created_at=iproduct_api.iproduct_created_at or now,
            iproduct_last_update=iproduct_api.iproduct_last_update or now.isoformat(),
            iproduct_model_name=iproduct_api.iproduct_model_name,
            iproduct_image_url=iproduct_api.iproduct_image_url
        )
    
    def _update_iproduct(self, existing: Iproduct, new_data: Iproduct_API):
        """
        Update existing Iproduct with new data.
        
        Args:
            existing: Existing Iproduct
            new_data: New Iproduct data
        """
        now = datetime.now()
        
        if new_data.iproduct_name:
            existing.iproduct_name = new_data.iproduct_name
        if new_data.iproduct_brand:
            existing.iproduct_brand = new_data.iproduct_brand
        if new_data.iproduct_estimated_price is not None:
            existing.iproduct_estimated_price = new_data.iproduct_estimated_price
            existing.iproduct_last_price_update = now
        if new_data.iproduct_gluten_status:
            existing.iproduct_gluten_status = new_data.iproduct_gluten_status
        if new_data.iproduct_info_source:
            existing.iproduct_info_source = new_data.iproduct_info_source
        if new_data.iproduct_info_confidence is not None:
            existing.iproduct_info_confidence = new_data.iproduct_info_confidence
        
        existing.iproduct_last_update = now.isoformat()
        self.iproduct_repo.update(existing)
        logger.debug(f"Updated IProduct {existing.id_iproduct}")
    
    def _handle_product_image(self, image: ProductImage_API, product: Product):
        """
        Handle product image creation or update.
        
        Args:
            image: Product image data
            product: Product to associate image with
            
        Raises:
            ImageInsertFailedException: If image creation fails
            ImageUpdateFailedException: If image update fails
        """
        if image.id_product_image == 0:
            new_image = ProductImage(product_image_url=image.product_image_url)
            new_image.product_ref = product
            try:
                self.product_repo.create_product_image(new_image)
                logger.info(f"Created product image for product {product.id_product}")
            except Exception as e:
                logger.error(f"Failed to create product image: {e}")
                raise ImageInsertFailedException(
                    error=str(e),
                    details={"product_id": product.id_product}
                )
        else:
            existing_images = self.product_repo.get_product_image_by_id(image.id_product_image)
            if existing_images:
                existing_image = existing_images[0]
                existing_image.product_image_url = image.product_image_url
                try:
                    self.product_repo.update_product_image(existing_image)
                    logger.info(f"Updated product image {image.id_product_image}")
                except Exception as e:
                    logger.error(f"Failed to update product image: {e}")
                    raise ImageUpdateFailedException(
                        image_id=image.id_product_image,
                        error=str(e)
                    )
    
    def _product_to_dict(self, product: Product) -> Dict[str, Any]:
        """
        Convert product to dictionary for notifications.
        
        Args:
            product: Product to convert
            
        Returns:
            Dictionary representation of product
        """
        product_dict = {}
        for key, value in product.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, 'isoformat'):
                    product_dict[key] = value.isoformat()
                else:
                    product_dict[key] = value
        return product_dict
    
    # ==================== SSE Subscriber Methods ====================
    
    async def _notify_product_subscribers(self, product_id: int, data: Dict[str, Any]):
        """
        Notify SSE subscribers about product updates.
        
        Args:
            product_id: Product ID that was updated
            data: Update data to send
        """
        if product_id not in subscribers:
            return
        
        disconnected_subscribers = []
        
        for queue in subscribers[product_id]:
            try:
                queue.put_nowait(data)
            except (asyncio.QueueFull, RuntimeError):
                disconnected_subscribers.append(queue)
            except Exception as e:
                logger.error(f"Error notifying subscriber for product {product_id}: {e}")
                disconnected_subscribers.append(queue)
        
        # Clean up disconnected subscribers
        for queue in disconnected_subscribers:
            if queue in subscribers[product_id]:
                subscribers[product_id].remove(queue)
        
        if product_id in subscribers and not subscribers[product_id]:
            del subscribers[product_id]
        
        logger.debug(f"Notified {len(subscribers.get(product_id, []))} subscribers for product {product_id}")
    
    def add_subscriber(self, product_id: int, queue: asyncio.Queue):
        """
        Add a subscriber for product updates.
        
        Args:
            product_id: Product ID to subscribe to
            queue: Queue for the subscriber
        """
        if product_id not in subscribers:
            subscribers[product_id] = []
        subscribers[product_id].append(queue)
        logger.debug(f"Added subscriber for product {product_id}. Total: {len(subscribers[product_id])}")
    
    def remove_subscriber(self, product_id: int, queue: asyncio.Queue):
        """
        Remove a subscriber for product updates.
        
        Args:
            product_id: Product ID to unsubscribe from
            queue: Queue of the subscriber
        """
        if product_id in subscribers and queue in subscribers[product_id]:
            subscribers[product_id].remove(queue)
            if not subscribers[product_id]:
                del subscribers[product_id]
            logger.debug(f"Removed subscriber for product {product_id}")