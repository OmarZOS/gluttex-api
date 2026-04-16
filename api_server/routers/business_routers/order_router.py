# routers/order_router.py (updated - remove duplicates)
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from typing import List, Optional
from core.exception_handler import APIException
from core.api_models import OrderedItem_API, PlacedOrder_API
from services.order_service import OrderService
from core.messages import HTTP_404_NOT_FOUND, ORDER_NOT_EXISTS
from core.api_models import OrderedItem_API, PlacedOrder_API
from services.order_service import OrderService

order_router = APIRouter()

def get_order_service() -> OrderService:
    return OrderService()

# Keep only unique endpoints that aren't in business_router
@order_router.post("/add")
def create_order(
    ordered_items: List[OrderedItem_API],
    submitted_order: PlacedOrder_API,
    background_tasks: BackgroundTasks,
    order_service: OrderService = Depends(get_order_service)
):
    """Create a new order"""
    quantities, order = order_service.create_order(ordered_items, submitted_order)
    
    for index, item in enumerate(ordered_items):
        background_tasks.add_task(
            order_service._notify_product_subscribers,
            item.ordered_product_id,
            {"product_quantity": quantities[index]}
        )
    
    return order

@order_router.get("/user/{user_id}")
def get_user_orders(
    user_id: int,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    order_service: OrderService = Depends(get_order_service)
):
    """Get orders by user"""
    return order_service.get_user_orders(user_id, offset, limit)

@order_router.get("/{order_id}")
def get_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """Get order by ID"""
    return order_service.get_order_by_id(order_id)

@order_router.get("/{order_id}/items")
def get_order_items(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """Get items in order"""
    return order_service.get_order_items(order_id)

@order_router.put("/{order_id}")
def update_order(
    order_id: int,
    updated_items: List[OrderedItem_API],
    updated_order: PlacedOrder_API,
    order_service: OrderService = Depends(get_order_service)
):
    """Update an order"""
    updated_order.id_placed_order = order_id
    return order_service.update_order(order_id, updated_items, updated_order)

@order_router.delete("/{order_id}")
def delete_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """Delete an order"""
    success = order_service.delete_order(order_id)
    if not success:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=ORDER_NOT_EXISTS,
            details=f"Order #{order_id} not found"
        )
    return {"message": f"Order #{order_id} deleted successfully"}