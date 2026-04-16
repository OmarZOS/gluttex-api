# routers/product_router.py
from fastapi import APIRouter, status, BackgroundTasks, File, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from core.exception_handler import APIException
from core.messages import *
from core.api_models import Iproduct_API, Product_API, ProductImage_API
from services.product_service import ProductService
from services.helpers.ai_service import AIService
import asyncio
import logging

product_router = APIRouter()
logger = logging.getLogger("FastAPIApp")

# Dependency injection
def get_product_service() -> ProductService:
    return ProductService()

def get_ai_service() -> AIService:
    return AIService()

# ----------------- SSE Endpoint for Product Updates -----------------

@product_router.get("/products/observer/{product_id}")
async def product_updates(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Subscribe to real-time product updates via SSE.
    """
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

# ----------------- Product Endpoints -----------------

@product_router.get("/product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}")
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
    return product_service.get_all_products(user_id, provider_id, category_id, offset, limit)

@product_router.get("/product/barcode/{barcode}")
async def get_product_from_barcode(
    barcode: str,
    product_service: ProductService = Depends(get_product_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Search for a product using a barcode.
    DB first, fallback to AI if needed.
    """
    # Try database first
    product = product_service.get_iproduct_by_barcode(barcode)
    
    if product:
        return {"source": "database", "data": product}
    
    # AI fallback if not found in DB
    ai_result, model_name = await ai_service.generate_product_info_by_barcode(barcode)
    
    # Format as Iproduct_API
    iproduct_data = ai_service.format_ai_result_to_iproduct(ai_result, model_name)
    
    return {"source": "ai", "data": [iproduct_data]}

@product_router.get("/product/db/barcode/{barcode}")
async def get_product_barcode(
    barcode: str,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using a barcode from database only.
    """
    product = product_service.get_iproduct_by_barcode(barcode)
    
    if not product:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=PRODUCT_FETCH_NOT_FOUND,
            message=f"{PRODUCT_FETCH_NOT_FOUND}: {barcode}"
        )
    
    return {"source": "database", "data": product}

@product_router.post("/product/search/image")
async def search_product_by_image(
    file: UploadFile = File(...),
    product_service: ProductService = Depends(get_product_service)
):
    """
    Search for a product using an uploaded image.
    Performs OCR/logo detection/AI parsing.
    """
    # Read image bytes
    image_bytes = await file.read()
    
    # Use product service which internally uses AI service
    iproduct_data = await product_service.recognize_product_from_image(image_bytes)
    
    return {"source": "ai", "data": [iproduct_data]}

@product_router.get("/product/{product_id}")
def get_product_by_id(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve a product by ID.
    """
    return product_service.get_product_by_id(product_id)

@product_router.get("/product/category/{category_id}/{offset}/{limit}")
def get_products_by_category(
    category_id: int,
    offset: int,
    limit: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Retrieve products by category with pagination.
    """
    return product_service.get_products_by_category(category_id, offset, limit)

@product_router.get("/product/category/all")
def get_categories(
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch all product categories.
    """
    return product_service.get_product_categories()

# ----------------- Product Image Endpoints -----------------

@product_router.get("/image/product/{image_id}")
def get_product_image(
    image_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Fetch product image by ID.
    """
    images = product_service.product_repo.get_product_image_by_id(image_id)
    if not images:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=PRODUCT_IMAGE_NOT_FOUND,
            message=f"Product image {image_id} not found"
        )
    return images[0]

# ----------------- Product Modification Endpoints -----------------

@product_router.put("/product/{product_id}")
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
    return product_service.update_product(product_id, product, image, background_tasks)

@product_router.post("/product/add")
async def insert_product_details(
    product: Product_API,
    image: ProductImage_API = None,
    iproduct: Iproduct_API = None,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Insert a new product.
    """
    return await product_service.create_product(product, image, iproduct)

@product_router.delete("/product/delete/{product_id}")
def delete_product_by_id(
    product_id: int,
    product_service: ProductService = Depends(get_product_service)
):
    """
    Delete a product by ID.
    """
    success = product_service.delete_product(product_id)
    if not success:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=PRODUCT_NOT_EXISTS,
            message=f"{PRODUCT_DELETE_FAILED}: {product_id}"
        )
    return {"message": f"Product {product_id} deleted successfully"}