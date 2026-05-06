# routers/business_routers/delivery_router.py
"""
Delivery router for managing deliveries, tracking, and bulk operations.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query, status
from typing import Optional, List
import logging

from core.api_models import Delivery_API
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.delivery_exceptions import (
    DeliveryNotFoundException,
    DeliveryCreationFailedException,
    DeliveryUpdateFailedException,
    DeliveryDeleteFailedException,
    DeliveryValidationFailedException,
    DeliveryCannotBeUpdatedException,
    DeliveryBulkUpdateFailedException,
    DeliveryBulkDeleteFailedException
)
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)

delivery_router = APIRouter()


def get_delivery_service() -> DeliveryService:
    """Dependency to get DeliveryService instance"""
    return DeliveryService()


# ==================== Delivery CRUD Endpoints ====================

@delivery_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    # response_model=Delivery_API,
    summary="Create delivery",
    description="Create a new delivery",
    responses={
        201: {"description": "Delivery created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_delivery(
    delivery: Delivery_API,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Create a new delivery.
    """
    logger.info(f"Creating new delivery for order: {delivery.delivery_placed_order}")
    return delivery_service.create_delivery(delivery)


@delivery_router.get(
    "/",
    # response_model=List[Delivery_API],
    summary="Get all deliveries",
    description="Get all deliveries with pagination and filters",
    responses={
        200: {"description": "Deliveries retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_all_deliveries(
    provider_id: int = Query(0, description="Filter by provider ID"),
    order_id: int = Query(0, description="Filter by order ID"),
    broker_id: int = Query(0, description="Filter by broker ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get all deliveries with pagination and filters.
    """
    logger.info(f"Fetching deliveries - provider:{provider_id}, order:{order_id}, broker:{broker_id}, offset:{offset}, limit:{limit}")
    return delivery_service.get_all_deliveries(provider_id, order_id, broker_id, offset, limit)


@delivery_router.get(
    "/status/{status}",
    # response_model=List[Delivery_API],
    summary="Get deliveries by status",
    description="Get deliveries by status",
    responses={
        200: {"description": "Deliveries retrieved successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def get_deliveries_by_status(
    status: str,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get deliveries by status.
    """
    valid_statuses = ["PENDING", "PROCESSING", "IN_TRANSIT", "DELIVERED", "CANCELLED", "RETURNED"]
    
    if status.upper() not in valid_statuses:
        raise DeliveryValidationFailedException(
            field="status",
            value=status,
            reason=f"Invalid status. Allowed: {', '.join(valid_statuses)}"
        )
    
    logger.info(f"Fetching deliveries with status: {status}")
    return delivery_service.get_deliveries_by_status(status.upper())


@delivery_router.get(
    "/stats",
    # response_model=dict,
    summary="Get delivery statistics",
    description="Get delivery statistics",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_delivery_stats(
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get delivery statistics.
    """
    logger.info("Fetching delivery statistics")
    return delivery_service.get_delivery_stats()


@delivery_router.get(
    "/{delivery_id}",
    # response_model=Delivery_API,
    summary="Get delivery by ID",
    description="Get delivery by ID",
    responses={
        200: {"description": "Delivery retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_delivery(
    delivery_id: int,
    eager_load: bool = Query(True, description="Load related data"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get delivery by ID.
    """
    logger.info(f"Fetching delivery with ID: {delivery_id} (eager_load={eager_load})")
    
    result = delivery_service.get_delivery_by_id(delivery_id, eager_load)
    if not result:
        raise DeliveryNotFoundException(delivery_id=delivery_id)
    
    return result


@delivery_router.put(
    "/{delivery_id}",
    # response_model=Delivery_API,
    summary="Update delivery",
    description="Update an existing delivery",
    responses={
        200: {"description": "Delivery updated successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery(
    delivery_id: int,
    delivery: Delivery_API,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update an existing delivery.
    """
    logger.info(f"Updating delivery with ID: {delivery_id}")
    return delivery_service.update_delivery(delivery_id, delivery, background_tasks)


@delivery_router.patch(
    "/{delivery_id}/status",
    # response_model=Delivery_API,
    summary="Update delivery status",
    description="Update only the delivery status",
    responses={
        200: {"description": "Delivery status updated successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_status(
    delivery_id: int,
    background_tasks: BackgroundTasks,
    status: str = Query(..., description="New delivery status"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery status.
    """
    logger.info(f"Updating status for delivery {delivery_id} to '{status}'")
    return delivery_service.update_delivery_status(delivery_id, status, background_tasks)


@delivery_router.patch(
    "/{delivery_id}/address",
    # response_model=Delivery_API,
    summary="Update delivery address",
    description="Update only the delivery address",
    responses={
        200: {"description": "Delivery address updated successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_address(
    delivery_id: int,
    background_tasks: BackgroundTasks,
    address_id: int = Query(..., description="New address ID"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery address.
    """
    logger.info(f"Updating address for delivery {delivery_id} to address {address_id}")
    return delivery_service.update_delivery_address(delivery_id, address_id, background_tasks)


@delivery_router.patch(
    "/{delivery_id}/tracking",
    # response_model=Delivery_API,
    summary="Update delivery tracking",
    description="Update the current tracking location of a delivery",
    responses={
        200: {"description": "Delivery tracking updated successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_tracking(
    delivery_id: int,
    background_tasks: BackgroundTasks,
    current_address_id: int = Query(..., description="Current tracking address ID"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update the current tracking location of a delivery.
    """
    logger.info(f"Updating tracking for delivery {delivery_id} to address {current_address_id}")
    return delivery_service.update_delivery_tracking(delivery_id, current_address_id, background_tasks)


@delivery_router.delete(
    "/{delivery_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete delivery",
    description="Delete a delivery",
    responses={
        204: {"description": "Delivery deleted successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def delete_delivery(
    delivery_id: int,
    force_delete: bool = Query(False, description="Force delete even if delivery is in transit"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Delete a delivery.
    """
    logger.info(f"Deleting delivery with ID: {delivery_id} (force={force_delete})")
    delivery_service.delete_delivery(delivery_id, force_delete)
    return None  # 204 No Content


# ==================== Bulk Operations ====================

@delivery_router.post(
    "/bulk/delete",
    # response_model=dict,
    summary="Bulk delete deliveries",
    description="Delete multiple deliveries matching criteria",
    responses={
        200: {"description": "Deliveries deleted successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def bulk_delete_deliveries(
    provider_id: int = Query(0, description="Filter by provider ID"),
    order_id: int = Query(0, description="Filter by order ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    force_delete: bool = Query(False, description="Force delete deliveries"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Delete multiple deliveries matching criteria.
    """
    logger.info(f"Bulk deleting deliveries - provider:{provider_id}, order:{order_id}, status:{status}, force:{force_delete}")
    return delivery_service.bulk_delete_deliveries(provider_id, order_id, status, force_delete)


@delivery_router.post(
    "/bulk/update-status",
    # response_model=List[Delivery_API],
    summary="Bulk update delivery status",
    description="Update status for multiple deliveries",
    responses={
        200: {"description": "Status updated successfully"},
        400: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def bulk_update_status(
    delivery_ids: List[int],
    background_tasks: BackgroundTasks,
    status: str = Query(..., description="New status for deliveries"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update status for multiple deliveries.
    """
    valid_statuses = ["PENDING", "PROCESSING", "IN_TRANSIT", "DELIVERED", "CANCELLED", "RETURNED"]
    
    if status.upper() not in valid_statuses:
        raise DeliveryValidationFailedException(
            field="status",
            value=status,
            reason=f"Invalid status. Allowed: {', '.join(valid_statuses)}"
        )
    
    logger.info(f"Bulk updating status for {len(delivery_ids)} deliveries to '{status}'")
    return delivery_service.bulk_update_status(delivery_ids, status.upper(), background_tasks)