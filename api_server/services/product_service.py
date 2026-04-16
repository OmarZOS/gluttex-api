# services/product_service.py
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import BackgroundTasks
from core.api_models import Product_API, ProductImage_API, Iproduct_API
from core.exception_handler import APIException
from core.messages import *
from core.models import Product, ProductImage, Iproduct
from repositories.product_repository import ProductRepository
from repositories.iproduct_repository import IProductRepository
from services.helpers.ai_service import AIService

# Global subscribers storage
subscribers: Dict[int, List[asyncio.Queue]] = {}

class ProductService:
    """Service for product-related business logic"""
    
    def __init__(self):
        self.product_repo = ProductRepository()
        self.iproduct_repo = IProductRepository()
        self.ai_service = AIService()
    
    def get_product_by_id(self, product_id: int, full: bool = False) -> Product:
        """Get product by ID"""
        product = self.product_repo.get_product_by_id(product_id, eager_load=full)
        if not product:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_NOT_EXISTS,
                message=f"{PRODUCT_DELETE_FAILED}: {product_id}"
            )
        return product
    
    def get_all_products(
        self,
        user_id: int = 0,
        provider_id: int = 0,
        category_id: int = 0,
        offset: int = 0,
        limit: int = 10
    ) -> List[Product]:
        """Get all products with filters"""
        return self.product_repo.get_all_products(user_id, provider_id, category_id, offset, limit)
    
    def get_products_by_category(self, category_id: int, offset: int = 0, limit: int = 10) -> List[Product]:
        """Get products by category"""
        return self.product_repo.get_products_by_category(category_id, offset, limit)
    
    def get_product_categories(self) -> List:
        """Get all product categories"""
        return self.product_repo.get_product_categories()
    
    async def create_product(
        self,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
        iproduct: Optional[Iproduct_API] = None
    ) -> Product:
        """Create a new product"""
        
        # Check if product already exists
        if product_api.id_product and self.product_repo.get_product_by_id(product_api.id_product):
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=PRODUCT_ALREADY_EXISTS,
                details=f"Product {product_api.id_product} already exists"
            )
        
        # Validate category
        product_category = self.product_repo.get_product_category_by_id(product_api.id_product_category)
        if not product_category:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_CATEGORY_NOT_EXISTS,
                message=PRODUCT_CATEGORY_NOT_EXISTS,
                details=""
            )
        
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
            return self.product_repo.create_product(product)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=PRODUCT_INSERT_FAILED,
                details=str(e)
            )
    
    def update_product(
        self,
        product_id: int,
        product_api: Product_API,
        image: Optional[ProductImage_API] = None,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> Product:
        """Update an existing product"""
        
        # Validate category
        product_category = self.product_repo.get_product_category_by_id(product_api.id_product_category)
        if not product_category:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_CATEGORY_NOT_EXISTS,
                message=PRODUCT_CATEGORY_NOT_EXISTS,
                details=""
            )
        
        # Get existing product
        product = self.get_product_by_id(product_id)
        
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
            
            # Notify subscribers if background tasks provided
            if background_tasks:
                product_dict = self._product_to_dict(updated_product)
                background_tasks.add_task(self._notify_product_subscribers, product_id, product_dict)
            
            return updated_product
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=PRODUCT_UPDATE_FAILED,
                details=str(e)
            )
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        product = self.get_product_by_id(product_id)
        return self.product_repo.delete_product(product)
    
    def get_iproduct_by_barcode(self, barcode: str) -> Optional[List[Iproduct]]:
        """Get IProduct by barcode"""
        return self.iproduct_repo.get_by_barcode(barcode)
    
    def get_iproduct_by_id(self, iproduct_id: int) -> Optional[Iproduct]:
        """Get IProduct by ID"""
        return self.iproduct_repo.get_by_id(iproduct_id)
    
    async def recognize_product_from_image(self, image_bytes: bytes, language: str = "fr") -> Iproduct_API:
        """Recognize product from image using AI"""
        ai_result, model_name = await self.ai_service.recognize_product_from_image(image_bytes, language)
        return self.ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    async def get_product_info_by_barcode(self, barcode: str, language: str = "fr") -> Iproduct_API:
        """Get product information by barcode using AI"""
        ai_result, model_name = await self.ai_service.generate_product_info_by_barcode(barcode, language)
        return self.ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    # Private helper methods
    def _build_product_model(self, product_api: Product_API) -> Product:
        """Build Product model from API data"""
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
        """Handle IProduct data association"""
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
    
    def _create_iproduct_from_api(self, iproduct_api: Iproduct_API) -> Iproduct:
        """Create Iproduct from API data"""
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
        """Update existing Iproduct with new data"""
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
    
    def _handle_product_image(self, image: ProductImage_API, product: Product):
        """Handle product image creation or update"""
        if image.id_product_image == 0:
            new_image = ProductImage(product_image_url=image.product_image_url)
            new_image.product_ref = product
            try:
                self.product_repo.create_product_image(new_image)
            except Exception as e:
                raise APIException(
                    status=HTTP_403_FORBIDDEN,
                    code=IMAGE_INSERT_FAILED,
                    message=IMAGE_INSERT_FAILED,
                    details=str(e)
                )
        else:
            existing_images = self.product_repo.get_product_image_by_id(image.id_product_image)
            if existing_images:
                existing_image = existing_images[0]
                existing_image.product_image_url = image.product_image_url
                try:
                    self.product_repo.update_product_image(existing_image)
                except Exception as e:
                    raise APIException(
                        status=HTTP_417_EXPECTATION_FAILED,
                        code=IMAGE_UPDATE_FAILED,
                        message=IMAGE_UPDATE_FAILED,
                        details=str(e)
                    )
    
    def _product_to_dict(self, product: Product) -> Dict[str, Any]:
        """Convert product to dictionary for notifications"""
        product_dict = {}
        for key, value in product.__dict__.items():
            if not key.startswith('_'):
                if hasattr(value, 'isoformat'):
                    product_dict[key] = value.isoformat()
                else:
                    product_dict[key] = value
        return product_dict
    
    async def _notify_product_subscribers(self, product_id: int, data: Dict[str, Any]):
        """Notify SSE subscribers about product updates"""
        if product_id not in subscribers:
            return
        
        disconnected_subscribers = []
        
        for queue in subscribers[product_id]:
            try:
                queue.put_nowait(data)
            except (asyncio.QueueFull, RuntimeError):
                disconnected_subscribers.append(queue)
            except Exception as e:
                print(f"Error notifying subscriber for product {product_id}: {e}")
                disconnected_subscribers.append(queue)
        
        # Clean up disconnected subscribers
        for queue in disconnected_subscribers:
            if queue in subscribers[product_id]:
                subscribers[product_id].remove(queue)
        
        if product_id in subscribers and not subscribers[product_id]:
            del subscribers[product_id]
    
    def add_subscriber(self, product_id: int, queue: asyncio.Queue):
        """Add a subscriber for product updates"""
        if product_id not in subscribers:
            subscribers[product_id] = []
        subscribers[product_id].append(queue)
    
    def remove_subscriber(self, product_id: int, queue: asyncio.Queue):
        """Remove a subscriber for product updates"""
        if product_id in subscribers and queue in subscribers[product_id]:
            subscribers[product_id].remove(queue)
            if not subscribers[product_id]:
                del subscribers[product_id]