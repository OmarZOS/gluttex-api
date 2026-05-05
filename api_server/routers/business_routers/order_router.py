# routers/business_routers/order_router.py
"""
Order router for handling order-related operations.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query, status
from typing import List, Optional
import logging

from core.api_models import OrderedItem_API, PlacedOrder_API
from core.response_models import (
    SuccessResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)
from core.exceptions.specific.order_exceptions import (
    OrderNotFoundException,
    OrderCreationFailedException,
    OrderUpdateFailedException,
    OrderDeleteFailedException,
    OrderItemsNotFoundException,
    InvalidOrderStatusException,
    OrderConflictException
)
from services.order_service import OrderService

logger = logging.getLogger(__name__)

order_router = APIRouter(
    # tags=["business-orders"],
    # prefix="/business"
)


def get_order_service() -> OrderService:
    """Dependency to get OrderService instance"""
    return OrderService()


# ==================== Order CRUD Endpoints ====================

@order_router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create a new order",
    description="Creates a new order with the provided items and order details",
    responses={
        201: {
            "description": "Order created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Product or user not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Insufficient stock or order conflict",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_order(
    ordered_items: List[OrderedItem_API],
    submitted_order: PlacedOrder_API,
    background_tasks: BackgroundTasks,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Create a new order.
    
    - **ordered_items**: List of items to order
    - **submitted_order**: Order details
    """
    logger.info(f"Creating new order for user: {submitted_order.ordering_user_id}")
    
    # Validate order has items
    if not ordered_items:
        logger.warning("Attempted to create order with no items")
        raise OrderCreationFailedException(
            error="Order must have at least one item",
            user_id=submitted_order.ordering_user_id
        )
    
    try:
        quantities, order = order_service.create_order(ordered_items, submitted_order)
        
        # Add background tasks for product subscribers
        for index, item in enumerate(ordered_items):
            if index < len(quantities):
                background_tasks.add_task(
                    order_service._notify_product_subscribers,
                    item.ordered_product_id,
                    {"product_quantity": quantities[index]}
                )
        
        logger.info(f"Order created successfully with ID: {order.id_placed_order}")
        
        return SuccessResponseModel(
            success=True,
            message="Order created successfully",
            data=order,
            details={
                "order_id": order.id_placed_order,
                "items_count": len(ordered_items),
                "total_amount": getattr(order, 'order_discount', 0),
                "subscribers_notified": True
            }
        )
        
    except (OrderCreationFailedException, OrderConflictException):
        raise
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise OrderCreationFailedException(
            error=str(e),
            user_id=submitted_order.ordering_user_id
        )


@order_router.get(
    "/orders/user/{user_id}",
    response_model=SuccessResponseModel,
    summary="Get user orders",
    description="Get all orders for a specific user with pagination",
    responses={
        200: {
            "description": "Orders retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "User not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_user_orders(
    user_id: int,
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get orders by user.
    
    - **user_id**: User ID to fetch orders for
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter, max 1000)
    """
    logger.info(f"Fetching orders for user {user_id} (offset={offset}, limit={limit})")
    
    try:
        orders = order_service.get_user_orders(user_id, offset, limit)
        
        return SuccessResponseModel(
            success=True,
            data=orders,
            message=f"Found {len(orders) if isinstance(orders, list) else 0} orders for user {user_id}",
            details={
                "user_id": user_id,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total": len(orders) if isinstance(orders, list) else 0
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch orders for user {user_id}: {e}")
        raise OrderNotFoundException(user_id=user_id, details={"error": str(e)})


@order_router.get(
    "/orders/{order_id}",
    response_model=SuccessResponseModel,
    summary="Get order by ID",
    description="Retrieve a specific order by its ID",
    responses={
        200: {
            "description": "Order retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_order(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get order by ID.
    
    - **order_id**: Order ID to fetch (path parameter)
    """
    logger.info(f"Fetching order with ID: {order_id}")
    
    try:
        order = order_service.get_order_by_id(order_id)
        
        if not order:
            logger.warning(f"Order with ID {order_id} not found")
            raise OrderNotFoundException(order_id=order_id)
        
        logger.info(f"Successfully retrieved order {order_id}")
        return SuccessResponseModel(
            success=True,
            data=order,
            message=f"Order {order_id} retrieved successfully"
        )
        
    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch order {order_id}: {e}")
        raise OrderNotFoundException(order_id=order_id, details={"error": str(e)})


@order_router.get(
    "/orders/{order_id}/items",
    response_model=SuccessResponseModel,
    summary="Get order items",
    description="Retrieve all items in a specific order",
    responses={
        200: {
            "description": "Order items retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_order_items(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get items in an order.
    
    - **order_id**: Order ID to fetch items for (path parameter)
    """
    logger.info(f"Fetching items for order ID: {order_id}")
    
    try:
        # First check if order exists
        order = order_service.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        items = order_service.get_order_items(order_id)
        
        if not items:
            logger.info(f"No items found for order {order_id}")
            return SuccessResponseModel(
                success=True,
                message=f"No items found in order {order_id}",
                data=[],
                details={"order_id": order_id, "total_items": 0}
            )
        
        logger.info(f"Found {len(items)} items in order {order_id}")
        return SuccessResponseModel(
            success=True,
            data=items,
            message=f"Found {len(items)} items in order {order_id}",
            details={
                "order_id": order_id,
                "total_items": len(items)
            }
        )
        
    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch items for order {order_id}: {e}")
        raise OrderItemsNotFoundException(order_id=order_id, details={"error": str(e)})


@order_router.put(
    "/orders/{order_id}",
    response_model=SuccessResponseModel,
    summary="Update an order",
    description="Update an existing order with new items and details",
    responses={
        200: {
            "description": "Order updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid status transition",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_order(
    order_id: int,
    updated_items: List[OrderedItem_API],
    updated_order: PlacedOrder_API,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update an order.
    
    - **order_id**: ID of order to update (path parameter)
    - **updated_items**: New items for the order
    - **updated_order**: Updated order details
    """
    logger.info(f"Updating order with ID: {order_id}")
    
    try:
        # Verify order exists
        existing_order = order_service.get_order_by_id(order_id)
        if not existing_order:
            raise OrderNotFoundException(order_id=order_id)
        
        # Check if status transition is valid
        if updated_order.placed_order_state:
            current_status = getattr(existing_order, 'placed_order_state', None)
            if current_status and not order_service.is_valid_status_transition(
                current_status, 
                updated_order.placed_order_state
            ):
                logger.warning(f"Invalid status transition for order {order_id}: {current_status} -> {updated_order.placed_order_state}")
                raise InvalidOrderStatusException(
                    order_id=order_id,
                    current_status=current_status,
                    requested_status=updated_order.placed_order_state
                )
        
        # Update order
        updated_order.id_placed_order = order_id
        result = order_service.update_order(order_id, updated_items, updated_order)
        
        logger.info(f"Order {order_id} updated successfully")
        return SuccessResponseModel(
            success=True,
            message=f"Order {order_id} updated successfully",
            data=result,
            details={
                "order_id": order_id,
                "items_updated": len(updated_items),
                "status_changed": updated_order.placed_order_state is not None
            }
        )
        
    except (OrderNotFoundException, InvalidOrderStatusException, OrderUpdateFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to update order {order_id}: {e}")
        raise OrderUpdateFailedException(
            order_id=order_id,
            error=str(e),
            fields_attempted=["items", "status", "details"]
        )


@order_router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete an order",
    description="Deletes an order and all its associated items",
    responses={
        200: {
            "description": "Order deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete order with items",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_order(
    order_id: int,
    force_delete: bool = Query(False, description="Force delete even if order has items"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Delete an order.
    
    - **order_id**: ID of order to delete (path parameter)
    - **force_delete**: Force delete even if order has items (query parameter)
    """
    logger.info(f"Deleting order with ID: {order_id} (force={force_delete})")
    
    try:
        # Verify order exists
        order = order_service.get_order_by_id(order_id)
        if not order:
            logger.warning(f"Order with ID {order_id} not found")
            raise OrderNotFoundException(order_id=order_id)
        
        # Check if order has items
        items = order_service.get_order_items(order_id)
        if items and not force_delete:
            logger.warning(f"Order {order_id} has {len(items)} items. Use force_delete=true to delete.")
            return SuccessResponseModel(
                success=False,
                message=f"Order has {len(items)} items. Use force_delete=true to delete anyway.",
                data={
                    "order_id": order_id,
                    "item_count": len(items),
                    "force_required": True
                }
            )
        
        # Delete order
        success = order_service.delete_order(order_id, delete_items=force_delete)
        
        if not success:
            raise OrderDeleteFailedException(
                order_id=order_id,
                error="Service returned False"
            )
        
        logger.info(f"Order {order_id} deleted successfully")
        return SuccessResponseModel(
            success=True,
            message=f"Order #{order_id} deleted successfully",
            data={
                "order_id": order_id,
                "force_deleted": force_delete,
                "items_deleted": len(items) if items else 0
            }
        )
        
    except (OrderNotFoundException, OrderDeleteFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to delete order {order_id}: {e}")
        raise OrderDeleteFailedException(
            order_id=order_id,
            error=str(e)
        )


@order_router.patch(
    "/orders/{order_id}/status",
    response_model=SuccessResponseModel,
    summary="Update order status",
    description="Update only the status of an order",
    responses={
        200: {
            "description": "Order status updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid status",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_order_status(
    order_id: int,
    status: str = Query(..., description="New order status"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update only the status of an order.
    
    - **order_id**: Order ID to update (path parameter)
    - **status**: New status value (query parameter)
    """
    valid_statuses = ["PENDING", "PROCESSING", "CONFIRMED", "SHIPPED", "DELIVERED", "CANCELLED", "REFUNDED"]
    
    if status.upper() not in valid_statuses:
        raise InvalidOrderStatusException(
            order_id=order_id,
            requested_status=status,
            allowed_statuses=valid_statuses
        )
    
    logger.info(f"Updating status for order {order_id} to '{status}'")
    
    try:
        order = order_service.update_order_status(order_id, status.upper())
        
        return SuccessResponseModel(
            success=True,
            message=f"Order status updated to '{status}'",
            data=order,
            details={
                "order_id": order_id,
                "new_status": status.upper(),
                "previous_status": getattr(order, 'placed_order_state', None)
            }
        )
        
    except OrderNotFoundException:
        raise
    except InvalidOrderStatusException:
        raise
    except Exception as e:
        logger.error(f"Failed to update status for order {order_id}: {e}")
        raise OrderUpdateFailedException(
            order_id=order_id,
            error=str(e),
            fields_attempted=["status"]
        )