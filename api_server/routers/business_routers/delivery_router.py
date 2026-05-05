# routers/business_routers/delivery_router.py
"""
Delivery router for managing deliveries, tracking, and bulk operations.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query, status
from typing import Optional, List
import logging

from core.api_models import Delivery_API
from core.response_models import (
    SuccessResponseModel,
    PaginatedResponseModel,
    ErrorResponseModel,
    BulkOperationResponseModel,
    get_crud_error_responses
)
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

delivery_router = APIRouter(
    # tags=["business-deliveries"],
    # prefix="/business/deliveries"
)


def get_delivery_service() -> DeliveryService:
    """Dependency to get DeliveryService instance"""
    return DeliveryService()


# ==================== Delivery CRUD Endpoints ====================

@delivery_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create delivery",
    description="Create a new delivery",
    responses={
        201: {
            "description": "Delivery created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid delivery data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Related entity not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_delivery(
    delivery: Delivery_API,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Create a new delivery.
    
    - **delivery**: Delivery details (request body)
    """
    logger.info(f"Creating new delivery for order: {delivery.delivery_placed_order}")
    
    result = delivery_service.create_delivery(delivery)
    
    delivery_id = getattr(result, 'id_delivery', None)
    
    return SuccessResponseModel(
        success=True,
        message="Delivery created successfully",
        data=result,
        details={
            "delivery_id": delivery_id,
            "order_id": delivery.delivery_placed_order,
            "status": delivery.delivery_status
        }
    )


@delivery_router.get(
    "/",
    response_model=SuccessResponseModel,
    summary="Get all deliveries",
    description="Get all deliveries with pagination and filters",
    responses={
        200: {
            "description": "Deliveries retrieved successfully",
            "model": SuccessResponseModel
        },
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
    
    - **provider_id**: Filter by provider ID (query parameter)
    - **order_id**: Filter by order ID (query parameter)
    - **broker_id**: Filter by broker ID (query parameter)
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter)
    """
    logger.info(f"Fetching deliveries - provider:{provider_id}, order:{order_id}, broker:{broker_id}, offset:{offset}, limit:{limit}")
    
    result = delivery_service.get_all_deliveries(provider_id, order_id, broker_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} deliveries",
        details={
            "filters": {
                "provider_id": provider_id if provider_id > 0 else None,
                "order_id": order_id if order_id > 0 else None,
                "broker_id": broker_id if broker_id > 0 else None
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result) if isinstance(result, list) else 0
            }
        }
    )


@delivery_router.get(
    "/status/{status}",
    response_model=SuccessResponseModel,
    summary="Get deliveries by status",
    description="Get deliveries by status",
    responses={
        200: {
            "description": "Deliveries retrieved successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid status",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_deliveries_by_status(
    status: str,  # Path parameter - NO Query()
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get deliveries by status.
    
    - **status**: Delivery status filter (path parameter)
    """
    valid_statuses = ["PENDING", "PROCESSING", "IN_TRANSIT", "DELIVERED", "CANCELLED", "RETURNED"]
    
    if status.upper() not in valid_statuses:
        raise DeliveryValidationFailedException(
            field="status",
            value=status,
            reason=f"Invalid status. Allowed: {', '.join(valid_statuses)}"
        )
    
    logger.info(f"Fetching deliveries with status: {status}")
    
    result = delivery_service.get_deliveries_by_status(status.upper())
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} deliveries with status '{status}'",
        details={
            "status": status,
            "total": len(result) if isinstance(result, list) else 0
        }
    )


@delivery_router.get(
    "/stats",
    response_model=SuccessResponseModel,
    summary="Get delivery statistics",
    description="Get delivery statistics",
    responses={
        200: {
            "description": "Statistics retrieved successfully",
            "model": SuccessResponseModel
        },
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
    
    result = delivery_service.get_delivery_stats()
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message="Delivery statistics retrieved successfully",
        details={
            "total_deliveries": result.get("total", 0),
            "by_status": result.get("by_status", {})
        }
    )


@delivery_router.get(
    "/{delivery_id}",
    response_model=SuccessResponseModel,
    summary="Get delivery by ID",
    description="Get delivery by ID",
    responses={
        200: {
            "description": "Delivery retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_delivery(
    delivery_id: int,  # Path parameter - NO Query()
    eager_load: bool = Query(True, description="Load related data"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get delivery by ID.
    
    - **delivery_id**: Delivery ID to fetch (path parameter)
    - **eager_load**: Load related data (query parameter)
    """
    logger.info(f"Fetching delivery with ID: {delivery_id} (eager_load={eager_load})")
    
    result = delivery_service.get_delivery_by_id(delivery_id, eager_load)
    
    if not result:
        raise DeliveryNotFoundException(delivery_id=delivery_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Delivery {delivery_id} retrieved successfully",
        details={"eager_load": eager_load}
    )


@delivery_router.put(
    "/{delivery_id}",
    response_model=SuccessResponseModel,
    summary="Update delivery",
    description="Update an existing delivery",
    responses={
        200: {
            "description": "Delivery updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data or cannot update",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery(
    delivery_id: int,  # Path parameter - NO Query()
    delivery: Delivery_API,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update an existing delivery.
    
    - **delivery_id**: Delivery ID to update (path parameter)
    - **delivery**: Updated delivery data (request body)
    """
    logger.info(f"Updating delivery with ID: {delivery_id}")
    
    result = delivery_service.update_delivery(delivery_id, delivery, background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Delivery {delivery_id} updated successfully",
        data=result,
        details={
            "delivery_id": delivery_id,
            "status": getattr(result, 'delivery_status', None)
        }
    )


@delivery_router.patch(
    "/{delivery_id}/status",
    response_model=SuccessResponseModel,
    summary="Update delivery status",
    description="Update only the delivery status",
    responses={
        200: {
            "description": "Delivery status updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid status transition",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_status(
    delivery_id: int,  # Path parameter - NO Query()
    background_tasks: BackgroundTasks,
    status: str = Query(..., description="New delivery status"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery status.
    
    - **delivery_id**: Delivery ID to update (path parameter)
    - **status**: New status value (query parameter)
    """
    logger.info(f"Updating status for delivery {delivery_id} to '{status}'")
    
    result = delivery_service.update_delivery_status(delivery_id, status, background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Delivery {delivery_id} status updated to '{status}'",
        data=result,
        details={
            "delivery_id": delivery_id,
            "new_status": status
        }
    )


@delivery_router.patch(
    "/{delivery_id}/address",
    response_model=SuccessResponseModel,
    summary="Update delivery address",
    description="Update only the delivery address",
    responses={
        200: {
            "description": "Delivery address updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid address",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_address(
    delivery_id: int,  # Path parameter - NO Query()
    background_tasks: BackgroundTasks,
    address_id: int = Query(..., description="New address ID"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery address.
    
    - **delivery_id**: Delivery ID to update (path parameter)
    - **address_id**: New address ID (query parameter)
    """
    logger.info(f"Updating address for delivery {delivery_id} to address {address_id}")
    
    result = delivery_service.update_delivery_address(delivery_id, address_id, background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Delivery {delivery_id} address updated successfully",
        data=result,
        details={
            "delivery_id": delivery_id,
            "new_address_id": address_id
        }
    )


@delivery_router.patch(
    "/{delivery_id}/tracking",
    response_model=SuccessResponseModel,
    summary="Update delivery tracking",
    description="Update the current tracking location of a delivery",
    responses={
        200: {
            "description": "Delivery tracking updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid tracking update",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_delivery_tracking(
    delivery_id: int,  # Path parameter - NO Query()
    background_tasks: BackgroundTasks,
    current_address_id: int = Query(..., description="Current tracking address ID"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update the current tracking location of a delivery.
    
    - **delivery_id**: Delivery ID to update (path parameter)
    - **current_address_id**: Current tracking address ID (query parameter)
    """
    logger.info(f"Updating tracking for delivery {delivery_id} to address {current_address_id}")
    
    result = delivery_service.update_delivery_tracking(delivery_id, current_address_id, background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Delivery {delivery_id} tracking updated successfully",
        data=result,
        details={
            "delivery_id": delivery_id,
            "current_address_id": current_address_id
        }
    )


@delivery_router.delete(
    "/{delivery_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete delivery",
    description="Delete a delivery",
    responses={
        200: {
            "description": "Delivery deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete delivery",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_delivery(
    delivery_id: int,  # Path parameter - NO Query()
    force_delete: bool = Query(False, description="Force delete even if delivery is in transit"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Delete a delivery.
    
    - **delivery_id**: Delivery ID to delete (path parameter)
    - **force_delete**: Force delete even if delivery is in transit (query parameter)
    """
    logger.info(f"Deleting delivery with ID: {delivery_id} (force={force_delete})")
    
    result = delivery_service.delete_delivery(delivery_id, force_delete)
    
    return SuccessResponseModel(
        success=True,
        message=f"Delivery {delivery_id} deleted successfully",
        data=result,
        details={
            "delivery_id": delivery_id,
            "force_deleted": force_delete
        }
    )


# ==================== Bulk Operations ====================

@delivery_router.post(
    "/bulk/delete",
    response_model=SuccessResponseModel,
    summary="Bulk delete deliveries",
    description="Delete multiple deliveries matching criteria",
    responses={
        200: {
            "description": "Deliveries deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid criteria",
            "model": ErrorResponseModel
        },
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
    
    - **provider_id**: Filter by provider ID (query parameter)
    - **order_id**: Filter by order ID (query parameter)
    - **status**: Filter by status (query parameter)
    - **force_delete**: Force delete deliveries (query parameter)
    """
    logger.info(f"Bulk deleting deliveries - provider:{provider_id}, order:{order_id}, status:{status}, force:{force_delete}")
    
    result = delivery_service.bulk_delete_deliveries(provider_id, order_id, status, force_delete)
    
    return SuccessResponseModel(
        success=True,
        message=f"Deleted {result.get('deleted_count', 0)} deliveries",
        data=result,
        details={
            "filters": {
                "provider_id": provider_id if provider_id > 0 else None,
                "order_id": order_id if order_id > 0 else None,
                "status": status
            },
            "force_deleted": force_delete
        }
    )


@delivery_router.post(
    "/bulk/update-status",
    response_model=SuccessResponseModel,
    summary="Bulk update delivery status",
    description="Update status for multiple deliveries",
    responses={
        200: {
            "description": "Status updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid status or delivery IDs",
            "model": ErrorResponseModel
        },
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
    
    - **delivery_ids**: List of delivery IDs to update (request body)
    - **status**: New status value (query parameter)
    """
    valid_statuses = ["PENDING", "PROCESSING", "IN_TRANSIT", "DELIVERED", "CANCELLED", "RETURNED"]
    
    if status.upper() not in valid_statuses:
        raise DeliveryValidationFailedException(
            field="status",
            value=status,
            reason=f"Invalid status. Allowed: {', '.join(valid_statuses)}"
        )
    
    logger.info(f"Bulk updating status for {len(delivery_ids)} deliveries to '{status}'")
    
    result = delivery_service.bulk_update_status(delivery_ids, status.upper(), background_tasks)
    
    return SuccessResponseModel(
        success=True,
        message=f"Updated {result.get('updated_count', 0)} deliveries to status '{status}'",
        data=result,
        details={
            "total_processed": len(delivery_ids),
            "updated_count": result.get('updated_count', 0),
            "failed_count": result.get('failed_count', 0),
            "new_status": status
        }
    )