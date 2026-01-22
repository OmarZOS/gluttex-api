






from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from features.business.staff.staff_update import answer_staff
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

