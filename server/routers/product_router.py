from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from starlette.background import BackgroundTasks
from core.api_models import Product_API, ProductImage_API
from features.product.product_fetch import fetch_all_product, fetch_product_by_id, get_product_categories, get_product_image_by_id, get_products_by_category_id
from features.product.product_insert import insert_product
from features.product.product_update import update_product
from features.product.product_delete import delete_product
from time import sleep
import asyncio


product_router = APIRouter()
subscribers = {}


# Add a subscriber to the product-specific channel
async def notify_subscribers(product_id,data):
    if product_id in subscribers:
        for queue in subscribers[product_id]:
            await queue.put(data)

# SSE endpoint for clients to listen to
@product_router.get("/products/{product_id}/subscribe")
async def product_updates(product_id: int):
    async def event_publisher():
        queue = asyncio.Queue()
        if product_id not in subscribers:
            subscribers[product_id] = []
        subscribers[product_id].append(queue)
        try:
            while True:
                data = await queue.get()
                yield {"event": "update", "data": data}
        finally:
            subscribers[product_id].remove(queue)

    return EventSourceResponse(event_publisher())

@product_router.get("/Product/all")
def get_all_Products():
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(fetch_all_product()))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch products."}),
    )
    return res
   
@product_router.get("/image/product/{image_id}")
def getProductImage(image_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_product_image_by_id(image_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch image."}),
    )
    return res
    


@product_router.post("/product/{product_id}")
def update_Product(product_id: int,product: Product_API, image: ProductImage_API,background_tasks: BackgroundTasks):
    
    try:
        res = update_product(product_id,product, image)
        background_tasks.add_task(notify_subscribers, product_id,{"product_quantity": product.product_quantity,"product_price":product.product_price})
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't update product."}),
    )
    return res

@product_router.put("/product/add")
def insert_Product(product: Product_API, image: ProductImage_API):
    
    try:
        res = insert_product(product, image)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert product."}),
    )
    return res



@product_router.get("/product/{Product_id}")
def get_Product_by_id(Product_id: int):

    try:
        res = fetch_product_by_id(Product_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch product."}),
    )
    return res


@product_router.delete("/Product/delete/{Product_id}")
def delete_Product_by_id(Product_id: int):

    try:
        res = delete_product(Product_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete product."}),
    )
    return res

@product_router.get("/product/category/{category_id}")
def get_products_by_category(category_id: int):
    try:
        res = get_products_by_category_id(category_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get products."}),
    )
    return res

@product_router.get("/product/Category/all")
def get_categories():
    try:
        res = get_product_categories()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch product."}),
    )
    return res

