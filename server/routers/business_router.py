from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import OrderedItem_API, PlacedOrder_API
# from features.business.business_fetch import fetch_all_business, fetch_business_by_id, get_business_categories, get_business_image_by_id, get_businesss_by_category_id
# from features.business.business_insert import insert_business
# from features.business.business_update import update_business
# from features.business.business_delete import delete_business
import asyncio
from typing import List

from features.order.order_insert import insert_order


business_router = APIRouter()
subscribers = {}



@business_router.put("/business/order/add")
def insert_placed_order(ordered_items: List[OrderedItem_API], submitted_order: PlacedOrder_API):
    
    try:
        res = insert_order(ordered_items, submitted_order)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert business."}),
    )
    return res



# @business_router.get("/business/{client_id}/all")
# def get_all_businesss(client_id: int):
#     try:
#         res = JSONResponse(
#         status_code=status.HTTP_200_OK, 
#         content=jsonable_encoder(fetch_all_business(client_id)))
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch businesss."}),
#     )
#     return res
    
    


# @business_router.post("/business/{business_id}")
# def update_business(business_id: int,business: business_API, image: businessImage_API,background_tasks: BackgroundTasks):
    
#     try:
#         res = update_business(business_id,business, image)
#         background_tasks.add_task(notify_subscribers, business_id,{"business_quantity": business.business_quantity,"business_price":business.business_price})
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't update business."}),
#     )
#     return res




# @business_router.get("/business/{business_id}")
# def get_business_by_id(business_id: int):

#     try:
#         res = fetch_business_by_id(business_id)
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch business."}),
#     )
#     return res


# @business_router.delete("/business/delete/{business_id}")
# def delete_business_by_id(business_id: int):

#     try:
#         res = delete_business(business_id)
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete business."}),
#     )
#     return res

# @business_router.get("/business/category/{category_id}")
# def get_businesss_by_category(category_id: int):
#     try:
#         res = get_businesss_by_category_id(category_id)
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get businesss."}),
#     )
#     return res

# @business_router.get("/business/Category/all")
# def get_categories():
#     try:
#         res = get_business_categories()
#     except Exception as e:
#         res = JSONResponse(
#         status_code=status.HTTP_406_NOT_ACCEPTABLE,
#         content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch business."}),
#     )
#     return res

