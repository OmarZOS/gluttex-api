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
from core.response_models import (
    SuccessResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductFetchNotFoundException,
    ProductImageNotFoundException,
    ProductDeleteFailedException,
    ProductInsertFailedException,
    ProductUpdateFailedException,
    ProductCategoryNotFoundException,
    ProductAlreadyExistsException
)
from services.product_service import ProductService
from services.helpers.ai_service import AIService

logger = logging.getLogger(__name__)

product_router = APIRouter(
    # tags=["products"],
    # prefix="/api"
)


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
                    },
                    "example": {
                        "event": "update",
                        "data": {
                            "product_id": 123,
                            "product_quantity": 50,
                            "updated_at": "2024-01-01T12:00:00Z"
                        }
                    }
                }
            }
        },
        404: {
            "description": "Product not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_403=False)
    }
)
async def product_updates(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Subscribe to real-time product updates via SSE.
    
    - **product_id**: Product ID to subscribe to (path parameter)
    """
    logger.info(f"SSE subscription established for product {product_id}")
    
    # Verify product exists
    product = product_service.get_product_by_id(product_id)
    if not product:
        logger.warning(f"Product {product_id} not found for SSE subscription")
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

# NOTE: user_id, provider_id, category_id, offset, limit are ALL path parameters
# They cannot use Query() - they are extracted directly from the URL path
@product_router.get(
    "/products/{user_id}/{provider_id}/{category_id}/{offset}/{limit}",
    response_model=SuccessResponseModel,
    summary="Get all products",
    description="Fetch all products with pagination and filters",
    responses={
        200: {
            "description": "Products retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_all_products(
    user_id: int,
    provider_id: int,
    category_id: int,
    offset: int,  # Path parameter - NO Query() wrapper
    limit: int,   # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch all products with pagination.
    
    - **user_id**: User ID filter (use 0 to ignore) - path parameter
    - **provider_id**: Provider ID filter (use 0 to ignore) - path parameter
    - **category_id**: Category ID filter (use 0 to ignore) - path parameter
    - **offset**: Pagination offset - path parameter
    - **limit**: Number of records to return (max 100) - path parameter
    """
    logger.info(f"Fetching products - user:{user_id}, provider:{provider_id}, category:{category_id}, offset:{offset}, limit:{limit}")
    
    result = product_service.get_all_products(user_id, provider_id, category_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'products'}",
        details={
            "filters": {
                "user_id": user_id if user_id > 0 else None,
                "provider_id": provider_id if provider_id > 0 else None,
                "category_id": category_id if category_id > 0 else None
            },
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@product_router.get(
    "/products/category/all",
    response_model=SuccessResponseModel,
    summary="Get all categories",
    description="Fetch all product categories",
    responses={
        200: {
            "description": "Categories retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_categories(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch all product categories.
    """
    logger.info("Fetching all product categories")
    
    result = product_service.get_product_categories()
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'categories'}"
    )


# NOTE: category_id, offset, limit are ALL path parameters
@product_router.get(
    "/products/category/{category_id}/{offset}/{limit}",
    response_model=SuccessResponseModel,
    summary="Get products by category",
    description="Retrieve products by category with pagination",
    responses={
        200: {
            "description": "Products retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Category not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_products_by_category(
    category_id: int,
    offset: int,  # Path parameter - NO Query() wrapper
    limit: int,   # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve products by category with pagination.
    
    - **category_id**: Category ID to filter by - path parameter
    - **offset**: Pagination offset - path parameter
    - **limit**: Number of records to return (max 100) - path parameter
    """
    logger.info(f"Fetching products for category {category_id} (offset={offset}, limit={limit})")
    
    result = product_service.get_products_by_category(category_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'products'} in category {category_id}",
        details={
            "category_id": category_id,
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@product_router.get(
    "/products/{product_id}",
    response_model=SuccessResponseModel,
    summary="Get product by ID",
    description="Retrieve a product by its ID",
    responses={
        200: {
            "description": "Product retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_product_by_id(
    product_id: int,  # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve a product by ID.
    
    - **product_id**: Product ID to fetch (path parameter)
    """
    logger.info(f"Fetching product with ID: {product_id}")
    
    result = product_service.get_product_by_id(product_id)
    
    if not result:
        raise ProductNotFoundException(product_id=product_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Product {product_id} retrieved successfully"
    )


# ==================== Barcode Search Endpoints ====================

@product_router.get(
    "/products/barcode/{barcode}",
    response_model=SuccessResponseModel,
    summary="Search product by barcode",
    description="Search for a product using a barcode. DB first, fallback to AI if needed.",
    responses={
        200: {
            "description": "Product found",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Product not found in DB or AI",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
async def get_product_from_barcode(
    barcode: str,  # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Search for a product using a barcode.
    DB first, fallback to AI if needed.
    
    - **barcode**: Product barcode to search (path parameter)
    """
    logger.info(f"Searching for product with barcode: {barcode}")
    
    # Try database first
    product = product_service.get_iproduct_by_barcode(barcode)
    
    if product:
        logger.info(f"Product found in database for barcode {barcode}")
        return SuccessResponseModel(
            success=True,
            data=product,
            message="Product found in database",
            details={"source": "database", "barcode": barcode}
        )
    
    # AI fallback if not found in DB
    logger.info(f"Product not found in DB, trying AI for barcode {barcode}")
    ai_result, model_name = await ai_service.generate_product_info_by_barcode(barcode)
    
    if not ai_result:
        raise ProductFetchNotFoundException(
            identifier=barcode,
            search_type="barcode"
        )
    
    # Format as Iproduct_API
    iproduct_data = ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    return SuccessResponseModel(
        success=True,
        data=[iproduct_data],
        message="Product information generated by AI",
        details={"source": "ai", "model": model_name, "barcode": barcode}
    )


@product_router.get(
    "/products/db/barcode/{barcode}",
    response_model=SuccessResponseModel,
    summary="Search product by barcode (DB only)",
    description="Search for a product using a barcode from database only",
    responses={
        200: {
            "description": "Product found",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
async def get_product_barcode_db_only(
    barcode: str,  # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using a barcode from database only.
    
    - **barcode**: Product barcode to search (path parameter)
    """
    logger.info(f"Searching database for product with barcode: {barcode}")
    
    product = product_service.get_iproduct_by_barcode(barcode)
    
    if not product:
        logger.warning(f"Product not found in database for barcode {barcode}")
        raise ProductFetchNotFoundException(
            identifier=barcode,
            search_type="barcode_database"
        )
    
    return SuccessResponseModel(
        success=True,
        data=product,
        message="Product found in database",
        details={"source": "database", "barcode": barcode}
    )


# ==================== Image Recognition Endpoint ====================

@product_router.post(
    "/products/search/image",
    response_model=SuccessResponseModel,
    status_code=status.HTTP_200_OK,
    summary="Search product by image",
    description="Search for a product using an uploaded image. Performs OCR/logo detection/AI parsing.",
    responses={
        200: {
            "description": "Product recognized successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid image",
            "model": ErrorResponseModel
        },
        422: {
            "description": "Validation Error",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
async def search_product_by_image(
    file: UploadFile = File(..., description="Product image file"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using an uploaded image.
    Performs OCR/logo detection/AI parsing.
    
    - **file**: Product image file (JPEG, PNG, etc.) - form parameter
    """
    logger.info(f"Processing image search for file: {file.filename}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        logger.warning(f"Invalid file type: {file.content_type}")
        raise ProductInsertFailedException(
            error="File must be an image",
            product_name=file.filename
        )
    
    # Read image bytes
    image_bytes = await file.read()
    
    if not image_bytes:
        logger.warning("Empty image file received")
        raise ProductInsertFailedException(
            error="Empty image file",
            product_name=file.filename
        )
    
    # Use product service which internally uses AI service
    iproduct_data = await product_service.recognize_product_from_image(image_bytes)
    
    logger.info(f"Image search completed for {file.filename}")
    
    return SuccessResponseModel(
        success=True,
        data=[iproduct_data],
        message="Product recognized from image",
        details={"source": "ai", "filename": file.filename}
    )


# ==================== Product Image Endpoints ====================

@product_router.get(
    "/products/image/{image_id}",
    response_model=SuccessResponseModel,
    summary="Get product image",
    description="Fetch product image by ID",
    responses={
        200: {
            "description": "Image retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_product_image(
    image_id: int,  # Path parameter - NO Query() wrapper
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch product image by ID.
    
    - **image_id**: Product image ID to fetch (path parameter)
    """
    logger.info(f"Fetching product image with ID: {image_id}")
    
    images = product_service.product_repo.get_product_image_by_id(image_id)
    
    if not images:
        logger.warning(f"Product image {image_id} not found")
        raise ProductImageNotFoundException(image_id=image_id)
    
    return SuccessResponseModel(
        success=True,
        data=images[0],
        message=f"Product image {image_id} retrieved successfully"
    )


# ==================== Product Modification Endpoints ====================

@product_router.put(
    "/products/{product_id}",
    response_model=SuccessResponseModel,
    summary="Update product",
    description="Update product details and notify subscribers",
    responses={
        200: {
            "description": "Product updated successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def update_product_details(
    product_id: int,  # Path parameter - NO Query() wrapper
    product: Product_API,
    image: ProductImage_API,
    background_tasks: BackgroundTasks,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Update product details and notify subscribers.
    
    - **product_id**: Product ID to update (path parameter)
    - **product**: Updated product details (request body)
    - **image**: Updated product image (request body)
    """
    logger.info(f"Updating product with ID: {product_id}")
    
    result = product_service.update_product(product_id, product, image, background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Product {product_id} updated successfully",
        data=result,
        details={
            "product_id": product_id,
            "subscribers_notified": True
        }
    )


@product_router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create product",
    description="Insert a new product",
    responses={
        201: {
            "description": "Product created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Product already exists",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False, include_409=True)
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
    
    - **product**: Product details (request body)
    - **image**: Optional product image (request body)
    - **iproduct**: Optional IProduct information (request body)
    """
    logger.info(f"Creating new product: {product.product_name}")
    
    result = await product_service.create_product(product, image, iproduct)
    
    # Get the created product ID
    product_id = getattr(result, 'id_product', None)
    
    return SuccessResponseModel(
        success=True,
        message="Product created successfully",
        data=result,
        details={
            "product_id": product_id,
            "product_name": product.product_name,
            "has_image": image is not None,
            "has_iproduct": iproduct is not None
        }
    )


@product_router.delete(
    "/products/delete/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete product",
    description="Delete a product by ID",
    responses={
        200: {
            "description": "Product deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete product with dependencies",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_product_by_id(
    product_id: int,  # Path parameter - NO Query() wrapper
    force_delete: bool = Query(False, description="Force delete even if product has dependencies"),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Delete a product by ID.
    
    - **product_id**: Product ID to delete (path parameter)
    - **force_delete**: Force delete even if product has dependencies (query parameter)
    """
    logger.info(f"Deleting product with ID: {product_id} (force={force_delete})")
    
    success = product_service.delete_product(product_id, force_delete)
    
    if not success:
        raise ProductDeleteFailedException(
            product_id=product_id,
            error="Product not found or cannot be deleted"
        )
    
    return SuccessResponseModel(
        success=True,
        message=f"Product {product_id} deleted successfully",
        data={"product_id": product_id, "force_deleted": force_delete}
    )