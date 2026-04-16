# routers/business_operation_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from services.business_operation_service import BusinessOperationService

business_operation_router = APIRouter()

def get_business_operation_service() -> BusinessOperationService:
    return BusinessOperationService()

@business_operation_router.get("/")
def get_business_operations(
    supplier_id: int = Query(0, description="Filter by supplier ID"),
    order_id: int = Query(0, description="Filter by order ID"),
    cart_id: int = Query(0, description="Filter by cart ID"),
    client_id: int = Query(0, description="Filter by client ID"),
    seller_id: int = Query(0, description="Filter by seller ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    operation_service: BusinessOperationService = Depends(get_business_operation_service)
):
    """Get business operations with filters"""
    return operation_service.get_operations(
        supplier_id, order_id, cart_id, client_id, seller_id, offset, limit
    )