# routers/cart_router.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from core.exception_handler import APIException
from core.messages import CART_NOT_EXISTS, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from core.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API, Person_API
)
from services.cart_service import CartService

cart_router = APIRouter()

def get_cart_service() -> CartService:
    return CartService()

@cart_router.get("/")
def get_carts(
    provider_id: int = Query(0, description="Filter by provider ID"),
    seller_id: int = Query(0, description="Filter by seller ID"),
    buyer_id: int = Query(0, description="Filter by buyer ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    cart_service: CartService = Depends(get_cart_service)
):
    """Get carts with filters"""
    if provider_id > 0:
        return cart_service.get_carts_by_provider(provider_id, offset, limit)
    elif seller_id > 0:
        return cart_service.get_carts_by_seller(seller_id, offset, limit)
    elif buyer_id > 0:
        return cart_service.get_carts_by_buyer(buyer_id, offset, limit)
    else:
        raise APIException(
            status=HTTP_400_BAD_REQUEST,
            code="FILTER_REQUIRED",
            details="At least one filter (provider_id, seller_id, or buyer_id) is required"
        )

@cart_router.get("/{cart_id}")
def get_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """Get cart by ID"""
    return cart_service.get_cart_by_id(cart_id)

@cart_router.post("/")
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
    """Create a new cart"""
    financial_docs, created_cart = cart_service.create_cart(
        ordered_items, ordered_services, cart, delivery,
        client, provider_id, seller_user_id, buyer_user_id
    )
    
    return {
        "message": "Cart created successfully",
        "cart_id": created_cart.cart_id,
        "financial_documents": {
            "has_invoice": 'invoice' in financial_docs,
            "has_payment": 'payment' in financial_docs,
            "has_receipt": 'receipt' in financial_docs,
            "has_deposit": 'deposit' in financial_docs
        },
        "cart": created_cart
    }

@cart_router.patch("/{cart_id}/status")
def update_cart_status(
    cart_id: int,
    status: str,
    cart_service: CartService = Depends(get_cart_service)
):
    """Update cart status"""
    return cart_service.update_cart_status(cart_id, status)

@cart_router.delete("/{cart_id}")
def delete_cart(
    cart_id: int,
    cart_service: CartService = Depends(get_cart_service)
):
    """Delete a cart"""
    success = cart_service.delete_cart(cart_id)
    if not success:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=CART_NOT_EXISTS,
            details=f"Cart #{cart_id} not found"
        )
    return {"message": f"Cart #{cart_id} deleted successfully"}