"""
Cart router for handling shopping cart operations.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

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
    get_crud_error_responses
)
from services.cart_service import CartService

logger = logging.getLogger(__name__)


# ==================== Router ====================

cart_router = APIRouter()


def get_cart_service() -> CartService:
    """Dependency to get CartService instance"""
    return CartService()


# ==================== Response Models ====================

class CartListResponse(BaseModel):
    """Response model for cart list"""
    data: List[Cart_API]
    filter: Dict[str, Any]
    pagination: Dict[str, Any]


class CreateCartResponse(BaseModel):
    """Response model for cart creation"""
    cart_id: int
    financial_documents: Dict[str, bool]
    cart: Cart_API
    summary: Dict[str, Any]
    warning: Optional[str] = None


class UpdateCartStatusResponse(BaseModel):
    """Response model for cart status update"""
    data: Cart_API
    cart_id: int
    new_status: str
    previous_status: Optional[str] = None


class DeleteCartResponse(BaseModel):
    """Response model for cart deletion"""
    cart_id: int
    force_deleted: bool


class CartSummaryResponse(BaseModel):
    """Response model for cart summary"""
    cart_id: int
    cart_status: str
    items: Dict[str, Any]
    services: Dict[str, Any]
    total_amount: float
    currency: str
    delivery: Optional[Dict[str, Any]] = None


# ==================== Cart Listing Endpoints ====================

@cart_router.get(
    "/carts",
    # response_model=CartListResponse,
    summary="Get carts with filters",
    description="Retrieve carts filtered by provider, seller, or buyer",
    responses={
        200: {"description": "Carts retrieved successfully"},
        400: {"model": ErrorResponseModel},
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
    """
    logger.info(f"Fetching carts with filters - provider:{provider_id}, seller:{seller_id}, buyer:{buyer_id}")
    
    if provider_id == 0 and seller_id == 0 and buyer_id == 0:
        raise CartFilterRequiredException(
            details={
                "required_filters": ["provider_id", "seller_id", "buyer_id"],
                "provided": {"provider_id": provider_id, "seller_id": seller_id, "buyer_id": buyer_id}
            }
        )
    
    try:
        if provider_id > 0:
            carts = cart_service.get_carts_by_provider(provider_id, offset, limit)
            filter_used = {"type": "provider", "value": provider_id}
        elif seller_id > 0:
            carts = cart_service.get_carts_by_seller(seller_id, offset, limit)
            filter_used = {"type": "seller", "value": seller_id}
        else:
            carts = cart_service.get_carts_by_buyer(buyer_id, offset, limit)
            filter_used = {"type": "buyer", "value": buyer_id}
        
        logger.info(f"Found {len(carts)} carts")
        
        return CartListResponse(
            data=carts,
            filter=filter_used,
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
    # response_model=Cart_API,
    summary="Get cart by ID",
    description="Retrieve a specific cart by its ID",
    responses={
        200: {"description": "Cart retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get cart by ID.
    """
    logger.info(f"Fetching cart with ID: {cart_id}")
    
    try:
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        return cart
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch cart {cart_id}: {e}")
        raise CartNotFoundException(cart_id=cart_id, details={"error": str(e)})


@cart_router.post(
    "/carts",
    status_code=status.HTTP_201_CREATED,
    # response_model=CreateCartResponse,
    summary="Create a new cart",
    description="Creates a new cart with items, services, and delivery information",
    responses={
        # 201: {"description": "Cart created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
        417: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def create_cart(
    ordered_items: List[OrderedItem_API] = None,
    ordered_services: List[OrderedService_API]= None,
    cart: Cart_API = None,
    delivery: Optional[Delivery_API] = None,
    client: Optional[Person_API] = None,
    provider_id: int = Query(..., description="Provider ID"),
    seller_user_id: int = Query(..., description="Seller user ID"),
    buyer_user_id: int = Query(0, description="Buyer user ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Create a new cart.
    """
    logger.info(f"Creating new cart for provider {provider_id}, seller {seller_user_id}")
    
    if not ordered_items and not ordered_services:
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
        
        # response = CreateCartResponse(
        #     cart_id=created_cart.cart_id,
        #     financial_documents={
        #         "has_invoice": 'invoice' in financial_docs,
        #         "has_payment": 'payment' in financial_docs,
        #         "has_receipt": 'receipt' in financial_docs,
        #         "has_deposit": 'deposit' in financial_docs
        #     },
        #     cart=created_cart,
        #     summary={
        #         "items_count": len(ordered_items),
        #         "services_count": len(ordered_services),
        #         "total_amount": getattr(created_cart, 'cart_total_amount', 0)
        #     }
        # )
        
        # if financial_docs.get('payment_required'):
        #     response.warning = "Payment required to complete cart"
        
        return created_cart
        
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
    # response_model=UpdateCartStatusResponse,
    summary="Update cart status",
    description="Update the status of a cart",
    responses={
        200: {"description": "Cart status updated successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
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
    """
    logger.info(f"Updating status for cart {cart_id} to '{status}'")
    
    valid_statuses = ["PENDING", "PROCESSING", "COMPLETED", "CANCELLED", "REFUNDED"]
    if status.upper() not in valid_statuses:
        raise CartInvalidStatusException(
            cart_id=cart_id,
            requested_status=status,
            allowed_statuses=valid_statuses
        )
    
    try:
        existing_cart = cart_service.get_cart_by_id(cart_id)
        if not existing_cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        updated_cart = cart_service.update_cart_status(cart_id, status.upper())
        
        logger.info(f"Cart {cart_id} status updated to '{status}'")
        return UpdateCartStatusResponse(
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
    # response_model=DeleteCartResponse,
    summary="Delete a cart",
    description="Deletes a cart and all its associated items and services",
    responses={
        200: {"description": "Cart deleted successfully"},
        404: {"model": ErrorResponseModel},
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
    """
    logger.info(f"Deleting cart with ID: {cart_id} (force={force_delete})")
    
    try:
        existing_cart = cart_service.get_cart_by_id(cart_id)
        if not existing_cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        has_items = hasattr(existing_cart, 'cart_items') and existing_cart.cart_items
        has_services = hasattr(existing_cart, 'cart_services') and existing_cart.cart_services
        
        if (has_items or has_services) and not force_delete:
            raise CartDeleteFailedException(
                cart_id=cart_id,
                error="Cart has items and/or services. Use force_delete=true to delete."
            )
        
        success = cart_service.delete_cart(cart_id)
        if not success:
            raise CartDeleteFailedException(cart_id=cart_id, error="Service returned False")
        
        logger.info(f"Cart {cart_id} deleted successfully")
        return DeleteCartResponse(
            cart_id=cart_id,
            force_deleted=force_delete
        )
        
    except (CartNotFoundException, CartDeleteFailedException):
        raise
    except Exception as e:
        logger.error(f"Failed to delete cart {cart_id}: {e}")
        raise CartDeleteFailedException(cart_id=cart_id, error=str(e))


# ==================== Cart Item Operations ====================

@cart_router.get(
    "/carts/{cart_id}/items",
    # response_model=List[OrderedItem_API],
    summary="Get cart items",
    description="Retrieve all items in a specific cart",
    responses={
        200: {"description": "Items retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_items(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get items in a cart.
    """
    logger.info(f"Fetching items for cart ID: {cart_id}")
    
    try:
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        items = cart_service.get_cart_items(cart_id)
        return items if items else []
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch items for cart {cart_id}: {e}")
        raise CartItemNotFoundException(cart_id=cart_id, details={"error": str(e)})


@cart_router.get(
    "/carts/{cart_id}/services",
    # response_model=List[OrderedService_API],
    summary="Get cart services",
    description="Retrieve all services in a specific cart",
    responses={
        200: {"description": "Services retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_services(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get services in a cart.
    """
    logger.info(f"Fetching services for cart ID: {cart_id}")
    
    try:
        cart = cart_service.get_cart_by_id(cart_id)
        if not cart:
            raise CartNotFoundException(cart_id=cart_id)
        
        services = cart_service.get_cart_services(cart_id)
        return services if services else []
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch services for cart {cart_id}: {e}")
        raise CartServiceNotFoundException(cart_id=cart_id, details={"error": str(e)})


# ==================== Cart Summary Endpoints ====================

@cart_router.get(
    "/carts/{cart_id}/summary",
    # response_model=CartSummaryResponse,
    summary="Get cart summary",
    description="Get a summary of the cart including totals and counts",
    responses={
        200: {"description": "Cart summary retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=False)
    }
)
def get_cart_summary(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Get cart summary with totals and counts.
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
        
        summary = CartSummaryResponse(
            cart_id=cart_id,
            cart_status=getattr(cart, 'cart_status', 'UNKNOWN'),
            items={
                "count": len(items),
                "total_amount": total_items_amount
            },
            services={
                "count": len(services),
                "total_amount": total_services_amount
            },
            total_amount=total_items_amount + total_services_amount,
            currency="DZD"
        )
        
        if hasattr(cart, 'cart_delivery') and cart.cart_delivery:
            summary.delivery = {
                "has_delivery": True,
                "delivery_fee": getattr(cart.cart_delivery, 'delivery_fee', 0),
                "status": getattr(cart.cart_delivery, 'delivery_status', 'PENDING')
            }
        
        logger.info(f"Cart {cart_id} summary: {summary.total_amount} total")
        return summary
        
    except CartNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch summary for cart {cart_id}: {e}")
        raise CartServiceException(
            message="Failed to retrieve cart summary",
            details={"cart_id": cart_id, "error": str(e)}
        )