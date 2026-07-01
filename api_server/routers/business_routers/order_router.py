# routers/business_routers/order_router.py
"""
Order router for handling order-related operations.
Updated to work with the new OrderService that integrates Finance and Inventory microservices.
"""

from fastapi import APIRouter, Depends, BackgroundTasks, Query, status, HTTPException
from typing import List, Optional, Dict, Any
import logging

from services.helpers.auth.auth_dependencies import get_current_user_id
from core.models.api_models import OrderedItem_API, PlacedOrder_API
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.order_exceptions import (
    OrderNotFoundException,
    OrderCreationFailedException,
    OrderUpdateFailedException,
    OrderDeleteFailedException,
    OrderItemsNotFoundException,
    InvalidOrderStatusException,
    OrderConflictException,
    OrderStatusTransitionException
)
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductQuantityNotEnoughException
)
from core.exceptions.handler import UserNotFoundException
from services.order_service import OrderService

logger = logging.getLogger(__name__)

order_router = APIRouter()


def get_order_service() -> OrderService:
    """Dependency to get OrderService instance"""
    return OrderService()


# ==================== Order CRUD Endpoints ====================

@order_router.post(
    "/orders",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Creates a new order with the provided items and order details. Integrates with Finance and Inventory microservices.",
    responses={
        201: {"description": "Order created successfully"},
        400: {"model": ErrorResponseModel, "description": "Bad request - validation error"},
        404: {"model": ErrorResponseModel, "description": "Resource not found"},
        409: {"model": ErrorResponseModel, "description": "Conflict - e.g., insufficient stock"},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
async def create_order(
    ordered_items: List[OrderedItem_API],
    submitted_order: PlacedOrder_API,
    background_tasks: BackgroundTasks,
    payment_method: str = Query("card", description="Payment method: card, cash, bank_transfer"),
    user_id: int = Depends(get_current_user_id),
    order_service: OrderService = Depends(get_order_service),
):
    """
    Create a new order.
    
    Flow:
    1. Validate items
    2. Check inventory availability (SILO)
    3. Create order, invoice, and delivery
    4. Reserve inventory
    5. Process payment
    6. Deduct inventory
    7. Update order status
    """
    logger.info(f"Creating new order for user: {submitted_order.ordering_user_id}")
    
    # Validate input
    if not ordered_items:
        raise OrderCreationFailedException(
            error="Order must have at least one item",
            user_id=submitted_order.ordering_user_id
        )
    
    try:
        submitted_order.ordering_user_id = user_id  # Ensure the order is associated with the authenticated user
        # Create the order using the service
        quantities, order, result = await order_service.create_order(
            items=ordered_items,
            order_data=submitted_order,
            payment_method=payment_method,
            user_id=submitted_order.ordering_user_id
        )
        
        logger.info(f"Order created successfully with ID: {order.id_placed_order}")
        
        # Return response with additional details
        return {
            "order": order,
            "payment_id": result.get('payment_id'),
            "invoice_id": result.get('invoice_id'),
            "payment_status": result.get('payment_status'),
            "inventory_reserved": result.get('inventory_reserved'),
            "inventory_deducted": result.get('inventory_deducted', False)
        }
        
    except UserNotFoundException as e:
        logger.error(f"User not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {submitted_order.ordering_user_id} not found"
        )
    except ProductNotFoundException as e:
        logger.error(f"Product not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {e.product_id} not found"
        )
    except ProductQuantityNotEnoughException as e:
        logger.error(f"Insufficient stock: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Insufficient stock for product {e.product_id}. Available: {e.available}, Requested: {e.requested}"
        )
    except (OrderCreationFailedException, OrderConflictException) as e:
        raise
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise OrderCreationFailedException(
            error=str(e),
            user_id=submitted_order.ordering_user_id
        )


@order_router.get(
    "/orders/user/{user_id}",
    summary="Get user orders",
    description="Get all orders for a specific user with pagination",
    responses={
        200: {"description": "Orders retrieved successfully"},
        404: {"model": ErrorResponseModel},
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
    """
    logger.info(f"Fetching orders for user {user_id} (offset={offset}, limit={limit})")
    
    try:
        orders, total = order_service.get_user_orders(user_id, offset, limit)
        return {
            "data": orders,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": total,
                "next_offset": offset + limit if offset + limit < total else None
            }
        }
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    except Exception as e:
        logger.error(f"Failed to fetch orders for user {user_id}: {e}")
        raise OrderNotFoundException(user_id=user_id, details={"error": str(e)})


@order_router.get(
    "/orders/{order_id}",
    summary="Get order by ID",
    description="Retrieve a specific order by its ID with all details",
    responses={
        200: {"description": "Order retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def get_order(
    order_id: int,
    include_items: bool = Query(True, description="Include ordered items in response"),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get order by ID.
    """
    logger.info(f"Fetching order with ID: {order_id}")
    
    try:
        order = order_service.get_order_by_id(order_id, with_items=include_items)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        # Add additional details if available
        response = {
            "order": order
        }
        
        if include_items and hasattr(order, 'ordered_item'):
            response["items_count"] = len(order.ordered_item)
            
            # Get invoice and delivery details
            try:
                if hasattr(order, 'id_placed_order'):
                    # Fetch invoice
                    invoice = order_service.invoice_repo.get_invoice_by_order(order.id_placed_order)
                    if invoice:
                        response["invoice"] = invoice
                    
                    # Fetch delivery
                    delivery = order_service.delivery_repo.get_by_order(order.id_placed_order)
                    if delivery:
                        response["delivery"] = delivery
            except Exception as e:
                logger.warning(f"Could not fetch associated records: {e}")
        
        return response
        
    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch order {order_id}: {e}")
        raise OrderNotFoundException(order_id=order_id, details={"error": str(e)})


@order_router.get(
    "/orders/{order_id}/items",
    summary="Get order items",
    description="Retrieve all items in a specific order",
    responses={
        200: {"description": "Order items retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def get_order_items(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Get items in an order.
    """
    logger.info(f"Fetching items for order ID: {order_id}")
    
    try:
        order = order_service.get_order_by_id(order_id, with_items=True)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        items = order_service.get_order_items(order_id)
        
        # Get product details for each item
        items_with_details = []
        for item in items:
            item_dict = {
                "id": item.id_ordered_item,
                "product_id": item.ordered_product_id,
                "quantity": item.ordered_quantity,
                "unit_price": item.unit_price,
                "applied_vat": item.applied_vat,
                "total_price": item.ordered_quantity * item.unit_price * (1 + item.applied_vat)
            }
            
            # Get product details if available
            try:
                product = order_service.product_repo.get_product_by_id(item.ordered_product_id)
                if product:
                    item_dict["product_name"] = product.product_name
                    item_dict["product_brand"] = product.product_brand
                    item_dict["product_category"] = product.product_category_id
            except Exception as e:
                logger.warning(f"Could not fetch product {item.ordered_product_id}: {e}")
            
            items_with_details.append(item_dict)
        
        return {
            "order_id": order_id,
            "items": items_with_details,
            "total_items": len(items_with_details)
        }
        
    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch items for order {order_id}: {e}")
        raise OrderItemsNotFoundException(order_id=order_id, details={"error": str(e)})


@order_router.put(
    "/orders/{order_id}",
    summary="Update an order",
    description="Update an existing order. Note: This will release and re-reserve inventory.",
    responses={
        200: {"description": "Order updated successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_order(
    order_id: int,
    updated_items: List[OrderedItem_API],
    updated_order: PlacedOrder_API,
    background_tasks: BackgroundTasks,
    user_id: int = Depends(get_current_user_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update an order.
    """
    logger.info(f"Updating order with ID: {order_id}")
    
    try:
        # Check if order exists
        existing_order = order_service.get_order_by_id(order_id, with_items=False)
        if not existing_order:
            raise OrderNotFoundException(order_id=order_id)
        
        if existing_order.ordering_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this order"
            )

        # Validate status transition if trying to change status
        if updated_order.placed_order_state:
            current_status = getattr(existing_order, 'placed_order_state', 'PENDING')
            try:
                order_service._validate_status_transition(
                    current_status,
                    updated_order.placed_order_state
                )
            except OrderStatusTransitionException as e:
                raise InvalidOrderStatusException(
                    order_id=order_id,
                    current_status=current_status,
                    requested_status=updated_order.placed_order_state,
                    allowed_statuses=list(order_service.STATUS_TRANSITIONS.get(current_status, set()))
                )
        
        # Update the order
        updated_order.id_placed_order = order_id
        result = order_service.update_order(order_id, updated_items, updated_order)
        
        logger.info(f"Order {order_id} updated successfully")
        return result
        
    except (OrderNotFoundException, InvalidOrderStatusException, OrderUpdateFailedException):
        raise
    except OrderStatusTransitionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {e.current_status} to {e.new_status}"
        )
    except Exception as e:
        logger.error(f"Failed to update order {order_id}: {e}")
        raise OrderUpdateFailedException(
            order_id=order_id,
            error=str(e),
            fields_attempted=["items", "status", "details"]
        )


@order_router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an order",
    description="Deletes an order and releases inventory. Also attempts to refund payment if applicable.",
    responses={
        204: {"description": "Order deleted successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def delete_order(
    order_id: int,
    force_delete: bool = Query(False, description="Force delete even if order has items"),
    user_id: int = Depends(get_current_user_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Delete an order.
    This will:
    1. Release inventory back to stock
    2. Delete order items
    3. Delete the order
    4. Attempt to refund payment if applicable
    """
    logger.info(f"Deleting order with ID: {order_id} (force={force_delete})")
    
    try:
        # Get order with items
        order = order_service.get_order_by_id(order_id, with_items=True)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        # Check if order has items
        items = order_service.get_order_items(order_id)
        if items and not force_delete:
            raise OrderDeleteFailedException(
                order_id=order_id,
                error=f"Order has {len(items)} items. Use force_delete=true to delete."
            )
        
        # Delete the order (this will release inventory)
        success = order_service.delete_order(order_id)
        if not success:
            raise OrderDeleteFailedException(order_id=order_id, error="Service returned False")
        
        logger.info(f"Order {order_id} deleted successfully")
        return None  # 204 No Content
        
    except (OrderNotFoundException, OrderDeleteFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to delete order {order_id}: {e}")
        raise OrderDeleteFailedException(order_id=order_id, error=str(e))


@order_router.patch(
    "/orders/{order_id}/status",
    summary="Update order status",
    description="Update only the status of an order. No inventory changes are made.",
    responses={
        200: {"description": "Order status updated successfully"},
        400: {"model": ErrorResponseModel, "description": "Invalid status or transition"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
def update_order_status(
    order_id: int,
    status: str = Query(..., description="New order status"),
    user_id: int = Depends(get_current_user_id),
    order_service: OrderService = Depends(get_order_service)
):
    """
    Update only the status of an order.
    
    Valid statuses and transitions:
    - PENDING → PROCESSING, CANCELLED
    - PROCESSING → SHIPPED, CANCELLED
    - SHIPPED → DELIVERED, CANCELLED, REFUNDED
    - DELIVERED → REFUNDED
    - CANCELLED → (no transitions)
    - REFUNDED → (no transitions)
    """
    valid_statuses = list(order_service.VALID_ORDER_STATUSES)
    
    if status.upper() not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"
        )
    
    logger.info(f"Updating status for order {order_id} to '{status}'")
    
    try:
        # Get current order status
        order = order_service.get_order_by_id(order_id, with_items=False)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        # Update status
        updated_order = order_service.update_order_status(order_id, status.upper())
        
        return {
            "order_id": updated_order.id_placed_order,
            "previous_status": order.placed_order_state,
            "new_status": updated_order.placed_order_state,
            "updated_at": updated_order.placed_order_last_mod
        }
        
    except OrderNotFoundException:
        raise
    except OrderStatusTransitionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition from {e.current_status} to {e.new_status}. Allowed: {', '.join(e.allowed_transitions)}"
        )
    except InvalidOrderStatusException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {e.current_status} to {e.requested_status}"
        )
    except Exception as e:
        logger.error(f"Failed to update status for order {order_id}: {e}")
        raise OrderUpdateFailedException(
            order_id=order_id,
            error=str(e),
            fields_attempted=["status"]
        )


@order_router.get(
    "/orders/{order_id}/inventory-status",
    summary="Check inventory status for order items",
    description="Check current inventory status for all items in an order",
    responses={
        200: {"description": "Inventory status retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True)
    }
)
async def get_order_inventory_status(
    order_id: int,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Check inventory status for all items in an order.
    Useful for verifying stock availability.
    """
    logger.info(f"Checking inventory status for order {order_id}")
    
    try:
        order = order_service.get_order_by_id(order_id, with_items=True)
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        items = order_service.get_order_items(order_id)
        
        # Check inventory for each item
        inventory_status = []
        
        for item in items:
            try:
                status = await order_service.inventory_client.get_stock_status(
                    product_id=item.ordered_product_id
                )
                
                inventory_status.append({
                    "product_id": item.ordered_product_id,
                    "ordered_quantity": item.ordered_quantity,
                    "available_quantity": status.get('available_quantity', 0),
                    "reserved_quantity": status.get('reserved_quantity', 0),
                    "in_stock": status.get('available_quantity', 0) >= item.ordered_quantity
                })
            except Exception as e:
                logger.warning(f"Could not check inventory for product {item.ordered_product_id}: {e}")
                inventory_status.append({
                    "product_id": item.ordered_product_id,
                    "ordered_quantity": item.ordered_quantity,
                    "error": str(e)
                })
        
        return {
            "order_id": order_id,
            "items": inventory_status,
            "all_available": all(item.get('in_stock', False) for item in inventory_status if 'error' not in item)
        }
        
    except OrderNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to check inventory for order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check inventory: {str(e)}"
        )