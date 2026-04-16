from fastapi import APIRouter, Depends, BackgroundTasks, Query
from typing import Optional, List
from core.api_models import Delivery_API
from core.exception_handler import APIException
from core.messages import *
from services.delivery_service import DeliveryService

delivery_router = APIRouter()

def get_delivery_service() -> DeliveryService:
    return DeliveryService()

@delivery_router.post("/")
def create_delivery(
    delivery: Delivery_API,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Create a new delivery.
    """
    return delivery_service.create_delivery(delivery)

@delivery_router.get("/")
def get_all_deliveries(
    provider_id: int = Query(0, description="Filter by provider ID"),
    order_id: int = Query(0, description="Filter by order ID"),
    broker_id: int = Query(0, description="Filter by broker ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get all deliveries with pagination and filters.
    """
    return delivery_service.get_all_deliveries(provider_id, order_id, broker_id, offset, limit)

@delivery_router.get("/status/{status}")
def get_deliveries_by_status(
    status: str,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get deliveries by status.
    """
    return delivery_service.get_deliveries_by_status(status)

@delivery_router.get("/stats")
def get_delivery_stats(
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get delivery statistics.
    """
    return delivery_service.get_delivery_stats()

@delivery_router.get("/{delivery_id}")
def get_delivery(
    delivery_id: int,
    eager_load: bool = Query(True, description="Load related data"),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Get delivery by ID.
    """
    return delivery_service.get_delivery_by_id(delivery_id, eager_load)

@delivery_router.put("/{delivery_id}")
def update_delivery(
    delivery_id: int,
    delivery: Delivery_API,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update an existing delivery.
    """
    return delivery_service.update_delivery(delivery_id, delivery, background_tasks)

@delivery_router.patch("/{delivery_id}/status")
def update_delivery_status(
    delivery_id: int,
    status: str,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery status.
    """
    return delivery_service.update_delivery_status(delivery_id, status, background_tasks)

@delivery_router.patch("/{delivery_id}/address")
def update_delivery_address(
    delivery_id: int,
    address_id: int,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update only the delivery address.
    """
    return delivery_service.update_delivery_address(delivery_id, address_id, background_tasks)

@delivery_router.patch("/{delivery_id}/tracking")
def update_delivery_tracking(
    delivery_id: int,
    current_address_id: int,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update the current tracking location of a delivery.
    """
    return delivery_service.update_delivery_tracking(delivery_id, current_address_id, background_tasks)

@delivery_router.delete("/{delivery_id}")
def delete_delivery(
    delivery_id: int,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Delete a delivery.
    """
    return delivery_service.delete_delivery(delivery_id)

@delivery_router.post("/bulk/delete")
def bulk_delete_deliveries(
    provider_id: int = Query(0),
    order_id: int = Query(0),
    status: Optional[str] = Query(None),
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Delete multiple deliveries matching criteria.
    """
    return delivery_service.bulk_delete_deliveries(provider_id, order_id, status)

@delivery_router.post("/bulk/update-status")
def bulk_update_status(
    delivery_ids: List[int],
    status: str,
    background_tasks: BackgroundTasks,
    delivery_service: DeliveryService = Depends(get_delivery_service)
):
    """
    Update status for multiple deliveries.
    """
    return delivery_service.bulk_update_status(delivery_ids, status, background_tasks)