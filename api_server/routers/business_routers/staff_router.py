






from fastapi import APIRouter,  status, BackgroundTasks, File, UploadFile
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from features.app.notification.notification_update import answer_staff
from features.business.staff.staff_delete import delete_rule
from features.business.staff.staff_update import update_staff
from core.api_models import ManagementRule_API
from features.business.staff.staff_add import insert_rule
from storage.storage_broker import search_records
from features.business.staff.staff_fetch import *
import asyncio
import logging

staff_router = APIRouter()
logger = logging.getLogger("FastAPIApp")

# ----------------- staff Endpoints -----------------

@staff_router.get("/staff/{org_id}/{provider_id}/{user_id}/{rule_id}/{offset}/{limit}")
def get_staff(org_id: int,provider_id: int, user_id: int,rule_id:int, offset: int, limit: int):
    """
    Fetch staffs with pagination.
    """
    return fetch_staff(org_id,provider_id,user_id,rule_id, offset, limit)

# @staff_router.get("/staff/barcode/{barcode}")
# async def get_staff_from_barcode(barcode: str):
#     """
#     Search for a staff using a barcode.
#     DB first, fallback to AI if needed.
#     """
#     staff = fetch_istaff_by_barcode(barcode)

#     if staff:
#         return {"source": "database", "data": staff}

#     # AI fallback if not found in DB
#     ai_data,model_name = await ai_generate_staff_info_by_barcode(barcode)
    
#     # Format as Istaff_API
#     istaff_data = format_ai_result_to_istaff(ai_data, model_name)

#     return {"source": "ai", "data": [istaff_data]}


# @staff_router.post("/staff/search/image")
# async def search_staff_by_image(file: UploadFile = File(...)):
#     """
#     Search for a staff using an uploaded image.
#     Performs OCR/logo detection/AI parsing.
#     """
#     # Read image bytes
#     image_bytes = await file.read()

#     ai_result,model_name = await ai_recognize_staff_from_image(image_bytes)

#     # Format as Istaff_API
#     istaff_data = format_ai_result_to_istaff(ai_result, model_name)

#     return {"source": "ai", "data": [istaff_data]}

# @staff_router.get("/staff/{staff_id}")
# def get_staff_by_id(staff_id: int):
#     """
#     Retrieve a staff by ID.
#     """
#     return fetch_staff_by_id(staff_id)

# @staff_router.get("/staff/category/{category_id}/{offset}/{limit}")
# def get_staffs_by_category(category_id: int, offset: int, limit: int):
#     """
#     Retrieve staffs by category with pagination.
#     """
#     return get_staffs_by_category_id(category_id, offset, limit)

# @staff_router.get("/staff/category/all")
# def get_categories():
#     """
#     Fetch all staff categories.
#     """
#     return get_staff_categories()

# # ----------------- staff Image Endpoints -----------------

# @staff_router.get("/image/staff/{image_id}")
# def get_staff_image(image_id: int):
#     """
#     Fetch staff image by ID.
#     """
#     return get_staff_image_by_id(image_id)

# # ----------------- staff Modification Endpoints -----------------

@staff_router.put("/staff/{staff_id}")
def update_staff_details(
    staff: ManagementRule_API):
    """
    Update staff details and notify subscribers.
    """
    res = update_staff(staff)
    return res

@staff_router.put("/rule/answer/{staff_id}")
def answer_staff_invitation(staff_id,
    answer: int):
    """
    Update staff details and notify subscribers.
    """
    res = answer_staff(staff_id,answer)
    return res

@staff_router.post("/staff/add")
def insert_staff_details(rule: ManagementRule_API):
    """
    Insert a new staff.
    """
    return  insert_rule(rule)

@staff_router.delete("/staff/delete/{staff_id}")
def delete_staff_by_id(staff_id: int):
    """
    Delete a staff by ID.
    """
    return delete_rule(staff_id)

