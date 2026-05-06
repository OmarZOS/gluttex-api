# routers/business_routers/product_router.py
"""
Product router for managing products, barcode search, image recognition, and SSE updates.
"""

from fastapi import APIRouter, status, BackgroundTasks, File, UploadFile, Depends, Query
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from typing import Optional, List
import asyncio
import logging

from core.api_models import Iproduct_API, Product_API, ProductImage_API
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductFetchNotFoundException,
    ProductImageNotFoundException,
    ProductDeleteFailedException,
    ProductInsertFailedException
)
from services.product_service import ProductService
from services.helpers.ai_service import AIService

logger = logging.getLogger(__name__)

product_router = APIRouter()


# ==================== Dependency Injection ====================

def get_product_service() -> ProductService:
    return ProductService()


def get_ai_service() -> AIService:
    return AIService()


# ==================== SSE Endpoint for Product Updates ====================

@product_router.get(
    "/products/observer/{product_id}",
    summary="Subscribe to product updates",
    description="Server-Sent Events endpoint for real-time product updates",
    responses={
        200: {
            "description": "SSE stream established",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "description": "Server-Sent Events data stream"
                    }
                }
            }
        },
        404: {"model": ErrorResponseModel}
    }
)
async def product_updates(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Subscribe to real-time product updates via SSE.
    """
    logger.info(f"SSE subscription established for product {product_id}")
    
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise ProductNotFoundException(product_id=product_id)
    
    async def event_publisher():
        queue = asyncio.Queue()
        product_service.add_subscriber(product_id, queue)
        try:
            while True:
                data = await queue.get()
                yield {"event": "update", "data": jsonable_encoder(data)}
        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled for product {product_id}")
        finally:
            product_service.remove_subscriber(product_id, queue)
    
    return EventSourceResponse(event_publisher())


# ==================== Product Listing Endpoints ====================

@product_router.get(
    "/products/{user_id}/{provider_id}/{category_id}/{offset}/{limit}",
    # response_model=List[Product_API],
    summary="Get all products",
    description="Fetch all products with pagination and filters",
    responses={200: {"description": "Products retrieved successfully"}, **get_crud_error_responses(include_404=True)}
)
def get_all_products(
    user_id: int,
    provider_id: int,
    category_id: int,
    offset: int,
    limit: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch all products with pagination.
    """
    logger.info(f"Fetching products - user:{user_id}, provider:{provider_id}, category:{category_id}, offset:{offset}, limit:{limit}")
    return product_service.get_all_products(user_id, provider_id, category_id, offset, limit)


@product_router.get(
    "/products/category/all",
    # response_model=List[ProductCategory_API],
    summary="Get all categories",
    description="Fetch all product categories",
    responses={200: {"description": "Categories retrieved successfully"}}
)
def get_categories(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch all product categories.
    """
    logger.info("Fetching all product categories")
    return product_service.get_product_categories()


@product_router.get(
    "/products/category/{category_id}/{offset}/{limit}",
    # response_model=List[Product_API],
    summary="Get products by category",
    description="Retrieve products by category with pagination",
    responses={
        200: {"description": "Products retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def get_products_by_category(
    category_id: int,
    offset: int,
    limit: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve products by category with pagination.
    """
    logger.info(f"Fetching products for category {category_id} (offset={offset}, limit={limit})")
    return product_service.get_products_by_category(category_id, offset, limit)


@product_router.get(
    "/products/{product_id}",
    # response_model=Product_API,
    summary="Get product by ID",
    description="Retrieve a product by its ID",
    responses={
        200: {"description": "Product retrieved successfully"},
        404: {"model": ErrorResponseModel}
    }
)
def get_product_by_id(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve a product by ID.
    """
    logger.info(f"Fetching product with ID: {product_id}")
    
    result = product_service.get_product_by_id(product_id)
    if not result:
        raise ProductNotFoundException(product_id=product_id)
    
    return result


# ==================== Barcode Search Endpoints ====================

@product_router.get(
    "/products/barcode/{barcode}",
    # response_model=List[Iproduct_API],
    summary="Search product by barcode",
    description="Search for a product using a barcode. DB first, fallback to AI if needed.",
    responses={
        200: {"description": "Product found"},
        404: {"model": ErrorResponseModel}
    }
)
async def get_product_from_barcode(
    barcode: str,
    product_service: ProductService = Depends(get_product_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Search for a product using a barcode. DB first, fallback to AI if needed.
    """
    logger.info(f"Searching for product with barcode: {barcode}")
    
    # Try database first
    product = product_service.get_iproduct_by_barcode(barcode)
    if product:
        logger.info(f"Product found in database for barcode {barcode}")
        return product
    
    # AI fallback if not found in DB
    logger.info(f"Product not found in DB, trying AI for barcode {barcode}")
    ai_result, model_name = await ai_service.generate_product_info_by_barcode(barcode)
    
    if not ai_result:
        raise ProductFetchNotFoundException(identifier=barcode, search_type="barcode")
    
    iproduct_data = ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    return [iproduct_data]


@product_router.get(
    "/products/db/barcode/{barcode}",
    # response_model=Iproduct_API,
    summary="Search product by barcode (DB only)",
    description="Search for a product using a barcode from database only",
    responses={
        200: {"description": "Product found"},
        404: {"model": ErrorResponseModel}
    }
)
async def get_product_barcode_db_only(
    barcode: str,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using a barcode from database only.
    """
    logger.info(f"Searching database for product with barcode: {barcode}")
    
    product = product_service.get_iproduct_by_barcode(barcode)
    if not product:
        raise ProductFetchNotFoundException(identifier=barcode, search_type="barcode_database")
    
    return product


# ==================== Image Recognition Endpoint ====================

@product_router.post(
    "/products/search/image",
    status_code=status.HTTP_200_OK,
    # response_model=List[Iproduct_API],
    summary="Search product by image",
    description="Search for a product using an uploaded image.",
    responses={
        200: {"description": "Product recognized successfully"},
        400: {"model": ErrorResponseModel},
        422: {"model": ErrorResponseModel}
    }
)
async def search_product_by_image(
    file: UploadFile = File(..., description="Product image file"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using an uploaded image.
    """
    logger.info(f"Processing image search for file: {file.filename}")
    
    if not file.content_type or not file.content_type.startswith('image/'):
        raise ProductInsertFailedException(error="File must be an image", product_name=file.filename)
    
    image_bytes = await file.read()
    if not image_bytes:
        raise ProductInsertFailedException(error="Empty image file", product_name=file.filename)
    
    iproduct_data = await product_service.recognize_product_from_image(image_bytes)
    logger.info(f"Image search completed for {file.filename}")
    
    return [iproduct_data]


# ==================== Product Image Endpoints ====================

@product_router.get(
    "/products/image/{image_id}",
    # response_model=ProductImage_API,
    summary="Get product image",
    description="Fetch product image by ID",
    responses={
        200: {"description": "Image retrieved successfully"},
        404: {"model": ErrorResponseModel}
    }
)
def get_product_image(
    image_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch product image by ID.
    """
    logger.info(f"Fetching product image with ID: {image_id}")
    
    images = product_service.product_repo.get_product_image_by_id(image_id)
    if not images:
        raise ProductImageNotFoundException(image_id=image_id)
    
    return images[0]


# ==================== Product Modification Endpoints ====================

@product_router.put(
    "/products/{product_id}",
    # response_model=Product_API,
    summary="Update product",
    description="Update product details and notify subscribers",
    responses={
        200: {"description": "Product updated successfully"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel}
    }
)
def update_product_details(
    product_id: int,
    product: Product_API,
    image: ProductImage_API,
    background_tasks: BackgroundTasks,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Update product details and notify subscribers.
    """
    logger.info(f"Updating product with ID: {product_id}")
    return product_service.update_product(product_id, product, image, background_tasks)


@product_router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    # response_model=Product_API,
    summary="Create product",
    description="Insert a new product",
    responses={
        201: {"description": "Product created successfully"},
        400: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel}
    }
)
async def insert_product_details(
    product: Product_API,
    image: Optional[ProductImage_API] = None,
    iproduct: Optional[Iproduct_API] = None,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Insert a new product.
    """
    logger.info(f"Creating new product: {product.product_name}")
    return await product_service.create_product(product, image, iproduct)


@product_router.delete(
    "/products/delete/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Delete a product by ID",
    responses={
        204: {"description": "Product deleted successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel}
    }
)
def delete_product_by_id(
    product_id: int,
    force_delete: bool = Query(False, description="Force delete even if product has dependencies"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Delete a product by ID.
    """
    logger.info(f"Deleting product with ID: {product_id} (force={force_delete})")
    
    success = product_service.delete_product(product_id, force_delete)
    if not success:
        raise ProductDeleteFailedException(product_id=product_id, error="Product not found or cannot be deleted")
    
    return None  # 204 No Content