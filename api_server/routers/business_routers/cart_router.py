"""
Cart router for handling shopping cart operations.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from core.responses.cart_responses import *
from core.exceptions.specific.cart_exceptions import (
    CartServiceException,
    CartNotFoundException,
    CartCreationFailedException,
    CartUpdateFailedException,
    CartDeleteFailedException,
    CartFilterRequiredException,
    CartInvalidStatusException,
    CartItemNotFoundException,
    CartServiceNotFoundException,
    CartPaymentRequiredException
)
from core.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API, Person_API
)
from core.response_models import (
    ErrorResponseModel,
    SuccessResponseModel,
    PaginatedResponseModel,
    get_crud_error_responses
)
from services.cart_service import CartService

logger = logging.getLogger(__name__)



# ==================== Router ====================

cart_router = APIRouter(
    # tags=["business-carts"],
    # prefix="/business"
)


def get_cart_service() -> CartService:
    """Dependency to get CartService instance"""
    return CartService()


# ==================== Cart Listing Endpoints ====================

@cart_router.get(
    "/carts",
    response_model=CartListResponse,
    summary="Get carts with filters",
    description="Retrieve carts filtered by provider, seller, or buyer",
    responses={
        200: {
            "description": "Carts retrieved successfully",
            "model": CartListResponse
        },
        400: {
            "description": "Bad Request - No filters provided",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_carts(
    provider_id: int = Query(0, description="Filter by provider ID"),
    seller_id: int = Query(0, description="Filter by seller ID"),
    buyer_id: int = Query(0, description="Filter by buyer ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get carts with filters.
    
    - **provider_id**: Filter by provider ID
    - **seller_id**: Filter by seller ID  
    - **buyer_id**: Filter by buyer ID
    - **offset**: Pagination offset
    - **limit**: Number of records to return (max 1000)
    """
    logger.info(f"Fetching carts with filters - provider:{provider_id}, seller:{seller_id}, buyer:{buyer_id}")
    
    # Validate at least one filter is provided
    if provider_id == 0 and seller_id == 0 and buyer_id == 0:
        logger.warning("No filters provided for cart listing")
        raise CartFilterRequiredException(
            details={
                "required_filters": ["provider_id", "seller_id", "buyer_id"],
                "provided": {"provider_id": provider_id, "seller_id": seller_id, "buyer_id": buyer_id}
            }
        )
    
    try:
        if provider_id > 0:
            carts = cart_service.get_carts_by_provider(provider_id, offset, limit)
            filter_used = "provider"
            filter_value = provider_id
        elif seller_id > 0:
            carts = cart_service.get_carts_by_seller(seller_id, offset, limit)
            filter_used = "seller"
            filter_value = seller_id
        else:  # buyer_id > 0
            carts = cart_service.get_carts_by_buyer(buyer_id, offset, limit)
            filter_used = "buyer"
            filter_value = buyer_id
        
        logger.info(f"Found {len(carts)} carts for {filter_used} ID: {filter_value}")
        
        return CartListResponse(
            success=True,
            data=carts,
            filter={"type": filter_used, "value": filter_value},
            pagination={"offset": offset, "limit": limit, "total": len(carts)}
        )
        
    except CartFilterRequiredException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch carts: {e}")
        raise CartServiceException(
            message="Failed to retrieve carts",
            details={"error": str(e)}
        )


# ==================== Single Cart Operations ====================

@cart_router.get(
    "/carts/{cart_id}",
    response_model=SuccessResponseModel,
    summary="Get cart by ID",
    description="Retrieve a specific cart by its ID",
    responses={
        200: {
            "description": "Cart retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Cart not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get cart by ID.
    
    - **cart_id**: Cart ID to fetch
    """
    logger.info(f"Fetching cart with ID: {cart_id}")
    
    try:
        cart = cart_service.get_cart_by_id(cart_id)
        
        if not cart:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise CartNotFoundException(cart_id=cart_id)
        
        logger.info(f"Successfully retrieved cart {cart_id}")
        return SuccessResponseModel(
            success=True,
            data=cart,
            message=f"Cart {cart_id} retrieved successfully"
        )
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch cart {cart_id}: {e}")
        raise CartNotFoundException(
            cart_id=cart_id,
            details={"error": str(e)}
        )


@cart_router.post(
    "/carts",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateCartResponse,
    summary="Create a new cart",
    description="Creates a new cart with items, services, and delivery information",
    responses={
        201: {
            "description": "Cart created successfully",
            "model": CreateCartResponse
        },
        400: {
            "description": "Bad Request - No items or services",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Supplier or seller not found",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Insufficient stock",
            "model": ErrorResponseModel
        },
        417: {
            "description": "Expectation Failed - Creation failed",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def create_cart(
    ordered_items: List[OrderedItem_API],
    ordered_services: List[OrderedService_API],
    cart: Cart_API,
    delivery: Optional[Delivery_API] = None,
    client: Optional[Person_API] = None,
    provider_id: int = Query(..., description="Provider ID"),
    seller_user_id: int = Query(..., description="Seller user ID"),
    buyer_user_id: int = Query(0, description="Buyer user ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Create a new cart.
    
    - **ordered_items**: List of items to add to cart
    - **ordered_services**: List of services to add to cart
    - **cart**: Cart details
    - **delivery**: Optional delivery information
    - **client**: Optional client information
    - **provider_id**: Provider ID (required)
    - **seller_user_id**: Seller user ID (required)
    - **buyer_user_id**: Buyer user ID (0 for anonymous)
    """
    logger.info(f"Creating new cart for provider {provider_id}, seller {seller_user_id}")
    
    # Validate cart has at least one item or service
    if not ordered_items and not ordered_services:
        logger.warning("Attempted to create cart with no items or services")
        raise CartCreationFailedException(
            error="Cart must have at least one item or service",
            provider_id=provider_id,
            seller_id=seller_user_id,
            buyer_id=buyer_user_id if buyer_user_id > 0 else None
        )
    
    try:
        financial_docs, created_cart = cart_service.create_cart(
            ordered_items, ordered_services, cart, delivery,
            client, provider_id, seller_user_id, buyer_user_id
        )
        
        logger.info(f"Cart created successfully with ID: {created_cart.cart_id}")
        
        response = CreateCartResponse(
            success=True,
            message="Cart created successfully",
            cart_id=created_cart.cart_id,
            financial_documents={
                "has_invoice": 'invoice' in financial_docs,
                "has_payment": 'payment' in financial_docs,
                "has_receipt": 'receipt' in financial_docs,
                "has_deposit": 'deposit' in financial_docs
            },
            cart=created_cart,
            summary={
                "items_count": len(ordered_items),
                "services_count": len(ordered_services),
                "total_amount": getattr(created_cart, 'cart_total_amount', 0)
            }
        )
        
        # Add warning if payment is required
        if financial_docs.get('payment_required'):
            response.warning = "Payment required to complete cart"
        
        return response
        
    except (CartCreationFailedException, CartPaymentRequiredException):
        raise
    except Exception as e:
        logger.error(f"Failed to create cart: {e}")
        raise CartCreationFailedException(
            error=str(e),
            provider_id=provider_id,
            seller_id=seller_user_id,
            buyer_id=buyer_user_id if buyer_user_id > 0 else None
        )


@cart_router.patch(
    "/carts/{cart_id}/status",
    response_model=UpdateCartStatusResponse,
    summary="Update cart status",
    description="Update the status of a cart (e.g., PENDING, COMPLETED, CANCELLED)",
    responses={
        200: {
            "description": "Cart status updated successfully",
            "model": UpdateCartStatusResponse
        },
        400: {
            "description": "Bad Request - Invalid status",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Cart not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def update_cart_status(
    cart_id: int,
    status: str = Query(..., description="New cart status (PENDING, PROCESSING, COMPLETED, CANCELLED, REFUNDED)"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Update cart status.
    
    - **cart_id**: Cart ID to update
    - **status**: New status value
    """
    logger.info(f"Updating status for cart {cart_id} to '{status}'")
    
    # Validate status value
    valid_statuses = ["PENDING", "PROCESSING", "COMPLETED", "CANCELLED", "REFUNDED"]
    if status.upper() not in valid_statuses:
        raise CartInvalidStatusException(
            cart_id=cart_id,
            requested_status=status,
            allowed_statuses=valid_statuses
        )
    
    try:
        # First check if cart exists
        existing_cart = cart_service.get_cart_by_id(cart_id)
        if not existing_cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        updated_cart = cart_service.update_cart_status(cart_id, status.upper())
        
        logger.info(f"Cart {cart_id} status updated to '{status}'")
        return UpdateCartStatusResponse(
            success=True,
            message=f"Cart status updated to '{status}'",
            data=updated_cart,
            cart_id=cart_id,
            new_status=status.upper(),
            previous_status=getattr(existing_cart, 'cart_status', None)
        )
        
    except (CartNotFoundException, CartInvalidStatusException, CartUpdateFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to update status for cart {cart_id}: {e}")
        raise CartUpdateFailedException(
            cart_id=cart_id,
            error=str(e),
            fields_attempted=["status"]
        )


@cart_router.delete(
    "/carts/{cart_id}",
    status_code=status.HTTP_200_OK,
    response_model=DeleteCartResponse,
    summary="Delete a cart",
    description="Deletes a cart and all its associated items and services",
    responses={
        200: {
            "description": "Cart deleted successfully",
            "model": DeleteCartResponse
        },
        404: {
            "description": "Cart not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def delete_cart(
    cart_id: int,
    force_delete: bool = Query(False, description="Force delete even if cart has items or services"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Delete a cart.
    
    - **cart_id**: Cart ID to delete
    - **force_delete**: Force delete even if cart has items/services
    """
    logger.info(f"Deleting cart with ID: {cart_id} (force={force_delete})")
    
    try:
        # First check if cart exists
        existing_cart = cart_service.get_cart_by_id(cart_id)
        if not existing_cart:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise CartNotFoundException(cart_id=cart_id)
        
        # Check if cart has items or services
        has_items = hasattr(existing_cart, 'cart_items') and existing_cart.cart_items
        has_services = hasattr(existing_cart, 'cart_services') and existing_cart.cart_services
        
        if (has_items or has_services) and not force_delete:
            logger.warning(f"Cart {cart_id} has items/services. Use force_delete=true to delete.")
            return DeleteCartResponse(
                success=False,
                message="Cart has items and/or services. Use force_delete=true to delete anyway.",
                cart_id=cart_id,
                force_deleted=False
            )
        
        # Delete cart
        success = cart_service.delete_cart(cart_id)
        
        if not success:
            raise CartDeleteFailedException(
                cart_id=cart_id,
                error="Service returned False"
            )
        
        logger.info(f"Cart {cart_id} deleted successfully")
        return DeleteCartResponse(
            success=True,
            message=f"Cart #{cart_id} deleted successfully",
            cart_id=cart_id,
            force_deleted=force_delete
        )
        
    except (CartNotFoundException, CartDeleteFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to delete cart {cart_id}: {e}")
        raise CartDeleteFailedException(
            cart_id=cart_id,
            error=str(e)
        )


# ==================== Cart Item Operations ====================

@cart_router.get(
    "/carts/{cart_id}/items",
    response_model=SuccessResponseModel,
    summary="Get cart items",
    description="Retrieve all items in a specific cart",
    responses={
        200: {
            "description": "Items retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Cart or items not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_items(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get items in a cart.
    
    - **cart_id**: Cart ID to fetch items for
    """
    logger.info(f"Fetching items for cart ID: {cart_id}")
    
    try:
        # Check if cart exists
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        items = cart_service.get_cart_items(cart_id)
        
        if not items:
            logger.info(f"No items found in cart {cart_id}")
            return SuccessResponseModel(
                success=True,
                message="No items found in cart",
                data=[],
                details={"cart_id": cart_id, "total_items": 0}
            )
        
        logger.info(f"Found {len(items)} items in cart {cart_id}")
        return SuccessResponseModel(
            success=True,
            data=items,
            details={"cart_id": cart_id, "total_items": len(items)}
        )
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch items for cart {cart_id}: {e}")
        raise CartItemNotFoundException(
            cart_id=cart_id,
            details={"error": str(e)}
        )


@cart_router.get(
    "/carts/{cart_id}/services",
    response_model=SuccessResponseModel,
    summary="Get cart services",
    description="Retrieve all services in a specific cart",
    responses={
        200: {
            "description": "Services retrieved successfully",
            "model": SuccessResponseModel
        },
        404: {
            "description": "Cart or services not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_services(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get services in a cart.
    
    - **cart_id**: Cart ID to fetch services for
    """
    logger.info(f"Fetching services for cart ID: {cart_id}")
    
    try:
        # Check if cart exists
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        services = cart_service.get_cart_services(cart_id)
        
        if not services:
            logger.info(f"No services found in cart {cart_id}")
            return SuccessResponseModel(
                success=True,
                message="No services found in cart",
                data=[],
                details={"cart_id": cart_id, "total_services": 0}
            )
        
        logger.info(f"Found {len(services)} services in cart {cart_id}")
        return SuccessResponseModel(
            success=True,
            data=services,
            details={"cart_id": cart_id, "total_services": len(services)}
        )
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch services for cart {cart_id}: {e}")
        raise CartServiceNotFoundException(
            cart_id=cart_id,
            details={"error": str(e)}
        )


# ==================== Cart Summary Endpoints ====================

@cart_router.get(
    "/carts/{cart_id}/summary",
    response_model=CartSummaryResponse,
    summary="Get cart summary",
    description="Get a summary of the cart including totals and counts",
    responses={
        200: {
            "description": "Cart summary retrieved successfully",
            "model": CartSummaryResponse
        },
        404: {
            "description": "Cart not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_summary(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get cart summary with totals and counts.
    
    - **cart_id**: Cart ID to get summary for
    """
    logger.info(f"Fetching summary for cart ID: {cart_id}")
    
    try:
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        items = cart_service.get_cart_items(cart_id)
        services = cart_service.get_cart_services(cart_id)
        
        total_items_amount = sum(
            getattr(item, 'unit_price', 0) * getattr(item, 'ordered_quantity', 1) 
            for item in items
        )
        total_services_amount = sum(
            getattr(service, 'ordered_service_total_price', 0) 
            for service in services
        )
        
        summary_data = {
            "cart_id": cart_id,
            "cart_status": getattr(cart, 'cart_status', 'UNKNOWN'),
            "items": {
                "count": len(items),
                "total_amount": total_items_amount
            },
            "services": {
                "count": len(services),
                "total_amount": total_services_amount
            },
            "total_amount": total_items_amount + total_services_amount,
            "currency": "DZD"
        }
        
        # Add delivery info if available
        if hasattr(cart, 'cart_delivery') and cart.cart_delivery:
            summary_data["delivery"] = {
                "has_delivery": True,
                "delivery_fee": getattr(cart.cart_delivery, 'delivery_fee', 0),
                "status": getattr(cart.cart_delivery, 'delivery_status', 'PENDING')
            }
        
        logger.info(f"Cart {cart_id} summary: {summary_data['total_amount']} total")
        return CartSummaryResponse(**summary_data)
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch summary for cart {cart_id}: {e}")
        raise CartServiceException(
            message="Failed to retrieve cart summary",
            details={"cart_id": cart_id, "error": str(e)}
        )