# routers/business_router.py
"""
Main business router for legacy/compatibility endpoints.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional, Dict, Any
import logging

from core.exceptions.specific.finance_exceptions import FinancialItemNotFoundException, PaymentCreationFailedException
from core.models.api_models import (
    Cart_API, Delivery_API, Payment_API, Deposit_API, AdditionalFee_API,
    OrderedItem_API, OrderedService_API, Person_API, PlacedOrder_API,
    ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
)
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.cart_exceptions import (
    CartCreationFailedException,
    CartNotFoundException
)
from services.cart_service import CartService
from services.financial_service import FinancialService

logger = logging.getLogger(__name__)

# Create main business router
business_router = APIRouter()


# Dependency injection for remaining endpoints
def get_cart_service() -> CartService:
    return CartService()


def get_financial_service() -> FinancialService:
    return FinancialService()


# ==================== Response Models ====================


# ==================== Cart Endpoints ====================

@business_router.post(
    "/business/cart",
    status_code=status.HTTP_201_CREATED,
    # response_model=CreateCartResponse,
    summary="Create cart",
    description="Creates a new cart with ordered items and services",
    responses={
        201: {"description": "Cart created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def add_cart(
    api_ordered_items: List[OrderedItem_API],
    api_provided_services: List[OrderedService_API],
    api_cart: Optional[Cart_API] = None,
    delivery: Optional[Delivery_API] = None,
    client: Optional[Person_API] = None,
    provider_id: int = Query(0, description="Provider ID"),
    seller_user_id: int = Query(0, description="Seller user ID"),
    buyer_user_id: int = Query(0, description="Buyer user ID"),
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Creates a new cart with ordered items and services.
    """
    logger.info(f"Creating cart via legacy endpoint - provider:{provider_id}, seller:{seller_user_id}")
    
    if not api_ordered_items and not api_provided_services:
        raise CartCreationFailedException(
            error="Cart must have at least one item or service",
            provider_id=provider_id,
            seller_id=seller_user_id
        )
    
    try:
        financial_docs, cart = cart_service.create_cart(
            api_ordered_items,
            api_provided_services,
            api_cart,
            delivery,
            client,
            provider_id,
            seller_user_id,
            buyer_user_id
        )
        
        logger.info(f"Cart created successfully via legacy endpoint with ID: {cart.cart_id}")
        
        return cart
        
    except (CartCreationFailedException, CartNotFoundException):
        raise
    except Exception as e:
        logger.error(f"Failed to create cart via legacy endpoint: {e}")
        raise CartCreationFailedException(
            error=str(e),
            provider_id=provider_id,
            seller_id=seller_user_id
        )


# ==================== Financial Endpoints ====================

@business_router.post(
    "/business/payment",
    status_code=status.HTTP_201_CREATED,
    # response_model=FinancialItemResponse,
    summary="Add financial item",
    description="Adds a financial item (payment, deposit, or fee)",
    responses={
        201: {"description": "Financial item created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def add_payment(
    payment: Optional[Payment_API] = None,
    deposit: Optional[Deposit_API] = None,
    fee: Optional[AdditionalFee_API] = None,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Adds a financial item (payment, deposit, or fee).
    """
    if not payment and not deposit and not fee:
        raise PaymentCreationFailedException(
            error="At least one of payment, deposit, or fee must be provided"
        )
    
    item_type = "payment" if payment else "deposit" if deposit else "fee"
    logger.info(f"Adding financial item via legacy endpoint - type: {item_type}")
    
    try:
        result = financial_service.create_financial_item(payment, deposit, fee)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to add financial item via legacy endpoint: {e}")
        raise PaymentCreationFailedException(
            error=str(e),
            details={"item_type": item_type}
        )


@business_router.get(
    "/business/doc/{supplier_id}/{person_id}/{client_id}/{seller_id}/{cart_id}/{order_id}/{deposit_id}/{invoice_id}/{offset}/{limit}",
    # response_model=FinancialDocumentsResponse,
    summary="Get financial documents",
    description="Fetches financial documents based on filters",
    responses={
        200: {"description": "Financial documents retrieved successfully"},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_403=False)
    }
)
def get_finances(
    supplier_id: int,
    person_id: int,
    client_id: int,
    seller_id: int,
    cart_id: int,
    order_id: int,
    deposit_id: int,
    invoice_id: int,
    offset: int,
    limit: int,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Fetches financial documents based on filters.
    
    All parameters are path parameters (use 0 to ignore).
    """
    actual_limit = min(limit, 100)
    
    logger.info(f"Fetching financial documents via legacy endpoint - offset:{offset}, limit:{actual_limit}")
    
    try:
        result = financial_service.get_financial_items(
            supplier_id if supplier_id > 0 else None,
            person_id if person_id > 0 else None,
            client_id if client_id > 0 else None,
            seller_id if seller_id > 0 else None,
            cart_id if cart_id > 0 else None,
            order_id if order_id > 0 else None,
            deposit_id if deposit_id > 0 else None,
            invoice_id if invoice_id > 0 else None,
            offset,
            actual_limit
        )
        
        filters = {
            "supplier_id": supplier_id if supplier_id > 0 else None,
            "person_id": person_id if person_id > 0 else None,
            "client_id": client_id if client_id > 0 else None,
            "seller_id": seller_id if seller_id > 0 else None,
            "cart_id": cart_id if cart_id > 0 else None,
            "order_id": order_id if order_id > 0 else None,
            "deposit_id": deposit_id if deposit_id > 0 else None,
            "invoice_id": invoice_id if invoice_id > 0 else None
        }
        
        pagination = {
            "offset": offset,
            "limit": actual_limit,
            "total": len(result) if isinstance(result, list) else 0
        }
        
        # if not result:
        #     logger.info(f"No financial documents found for the given filters")
        #     return FinancialDocumentsResponse(
        #         data=[],
        #         filters=filters,
        #         pagination=pagination
        #     )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to fetch financial documents via legacy endpoint: {e}")
        raise FinancialItemNotFoundException(details={"error": str(e)})