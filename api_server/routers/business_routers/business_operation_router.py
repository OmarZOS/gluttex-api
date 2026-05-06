# routers/business_operation_router.py
"""
Business operation router for retrieving business operation data.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Optional, List, Any
import logging

from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.business_exceptions import (
    BusinessOperationNotFoundException,
    BusinessOperationServiceException
)
from services.business_operation_service import BusinessOperationService

logger = logging.getLogger(__name__)

business_operation_router = APIRouter()


def get_business_operation_service() -> BusinessOperationService:
    """Dependency to get BusinessOperationService instance"""
    return BusinessOperationService()


# ==================== Response Model ====================



@business_operation_router.get(
    "/",
    # response_model=BusinessOperationsResponse,
    summary="Get business operations",
    description="Get business operations with filters",
    responses={
        200: {"description": "Business operations retrieved successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False, include_403=False)
    }
)
def get_business_operations(
    supplier_id: int = Query(0, description="Filter by supplier ID"),
    order_id: int = Query(0, description="Filter by order ID"),
    cart_id: int = Query(0, description="Filter by cart ID"),
    client_id: int = Query(0, description="Filter by client ID"),
    seller_id: int = Query(0, description="Filter by seller ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return (max 1000)"),
    operation_service: BusinessOperationService = Depends(get_business_operation_service)
):
    """
    Get business operations with filters.
    
    - **supplier_id**: Filter by supplier ID (query parameter)
    - **order_id**: Filter by order ID (query parameter)
    - **cart_id**: Filter by cart ID (query parameter)
    - **client_id**: Filter by client ID (query parameter)
    - **seller_id**: Filter by seller ID (query parameter)
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter, max 1000)
    """
    logger.info(f"Fetching business operations - supplier:{supplier_id}, order:{order_id}, cart:{cart_id}, client:{client_id}, seller:{seller_id}, offset:{offset}, limit:{limit}")
    
    filters_provided = any([
        supplier_id > 0,
        order_id > 0,
        cart_id > 0,
        client_id > 0,
        seller_id > 0
    ])
    
    if not filters_provided:
        logger.info("No filters provided, returning all business operations")
    
    try:
        result = operation_service.get_operations(
            supplier_id if supplier_id > 0 else None,
            order_id if order_id > 0 else None,
            cart_id if cart_id > 0 else None,
            client_id if client_id > 0 else None,
            seller_id if seller_id > 0 else None,
            offset,
            limit
        )
        
        filters = {
            "supplier_id": supplier_id if supplier_id > 0 else None,
            "order_id": order_id if order_id > 0 else None,
            "cart_id": cart_id if cart_id > 0 else None,
            "client_id": client_id if client_id > 0 else None,
            "seller_id": seller_id if seller_id > 0 else None
        }
        
        pagination = {
            "offset": offset,
            "limit": limit,
            "total": len(result) if isinstance(result, list) else 0
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch business operations: {e}")
        raise BusinessOperationServiceException(
            message="Failed to retrieve business operations",
            details={"error": str(e)}
        )