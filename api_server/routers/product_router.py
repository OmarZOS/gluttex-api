from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
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

@product_router.get("/product/all/{offset}/{limit}")
def get_all_products(offset: int, limit: int):
    """
    Fetch all products with pagination.
    """
    try:
        return fetch_all_product(offset, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch products: {str(e)}"
        )

@product_router.get("/product/{product_id}")
def get_product_by_id(product_id: int):
    """
    Retrieve a product by ID.
    """
    try:
        return fetch_product_by_id(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch product: {str(e)}"
        )

@product_router.get("/product/category/{category_id}/{offset}/{limit}")
def get_products_by_category(category_id: int, offset: int, limit: int):
    """
    Retrieve products by category with pagination.
    """
    try:
        return get_products_by_category_id(category_id, offset, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch products by category: {str(e)}"
        )

@product_router.get("/product/category/all")
def get_categories():
    """
    Fetch all product categories.
    """
    try:
        return get_product_categories()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch product categories: {str(e)}"
        )

# ----------------- Product Image Endpoints -----------------

@product_router.get("/image/product/{image_id}")
def get_product_image(image_id: int):
    """
    Fetch product image by ID.
    """
    try:
        return get_product_image_by_id(image_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch image: {str(e)}"
        )

# ----------------- Product Modification Endpoints -----------------

@product_router.post("/product/{product_id}")
def update_product_details(
    product_id: int, 
    product: Product_API, 
    image: ProductImage_API, 
    background_tasks: BackgroundTasks
):
    """
    Update product details and notify subscribers.
    """
    try:
        res = update_product(product_id, product, image)
        background_tasks.add_task(
            notify_subscribers, 
            product_id, 
            {"product_quantity": product.product_quantity, "product_price": product.product_price}
        )
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update product: {str(e)}"
        )

@product_router.put("/product/add")
async def insert_product_details(product: Product_API, image: ProductImage_API):
    """
    Insert a new product.
    """
    try:
        return await  insert_product(product, image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert product: {str(e)}"
        )

@product_router.delete("/product/delete/{product_id}")
def delete_product_by_id(product_id: int):
    """
    Delete a product by ID.
    """
    try:
        return delete_product(product_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete product: {str(e)}"
        )
