from fastapi import APIRouter,  status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from core.models import Product
from storage.storage_broker import search_records
from core.api_models import Product_API, ProductImage_API
from features.product.product_fetch import (
    fetch_all_product, fetch_product_by_id, get_product_categories, 
    get_product_image_by_id, get_products_by_category_id
)
from features.product.product_insert import insert_product
from features.product.product_update import notify_subscribers, update_product, subscribers
from features.product.product_delete import delete_product
import asyncio
import logging

product_router = APIRouter()
logger = logging.getLogger("FastAPIApp")

# ----------------- SSE Endpoint for Product Updates -----------------

@product_router.get("/products/observer/{product_id}")
async def product_updates(product_id: int):
    """
    Subscribe to real-time product updates via SSE.
    """
    async def event_publisher():
        queue = asyncio.Queue()
        subscribers.setdefault(product_id, []).append(queue)
        try:
            while True:
                data = await queue.get()
                yield {"event": "update", "data": data}
        finally:
            subscribers[product_id].remove(queue)

    return EventSourceResponse(event_publisher())

# ----------------- Product Endpoints -----------------

@product_router.get("/product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}")
def get_all_products(user_id: int, provider_id: int, category_id: int, offset: int, limit: int):
    """
    Fetch all products with pagination.
    """
    return fetch_all_product(user_id, provider_id, category_id, offset, limit)

@product_router.get("/product/{product_id}")
def get_product_by_id(product_id: int):
    """
    Retrieve a product by ID.
    """
    return fetch_product_by_id(product_id)

@product_router.get("/product/category/{category_id}/{offset}/{limit}")
def get_products_by_category(category_id: int, offset: int, limit: int):
    """
    Retrieve products by category with pagination.
    """
    return get_products_by_category_id(category_id, offset, limit)

@product_router.get("/product/category/all")
def get_categories():
    """
    Fetch all product categories.
    """
    return get_product_categories()

# ----------------- Product Image Endpoints -----------------

@product_router.get("/image/product/{image_id}")
def get_product_image(image_id: int):
    """
    Fetch product image by ID.
    """
    return get_product_image_by_id(image_id)

# ----------------- Product Modification Endpoints -----------------

@product_router.put("/product/{product_id}")
def update_product_details(
    product_id: int, 
    product: Product_API, 
    image: ProductImage_API, 
    background_tasks: BackgroundTasks
):
    """
    Update product details and notify subscribers.
    """
    res = update_product(product_id, product, image,background_tasks)
    return res

@product_router.post("/product/add")
async def insert_product_details(product: Product_API, image: ProductImage_API):
    """
    Insert a new product.
    """
    return await  insert_product(product, image)

@product_router.delete("/product/delete/{product_id}")
def delete_product_by_id(product_id: int):
    """
    Delete a product by ID.
    """
    return delete_product(product_id)

