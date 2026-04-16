# routers/business_router.py
from fastapi import APIRouter, Depends
from typing import List, Optional
from core.api_models import (
    Cart_API, Delivery_API, Payment_API, Deposit_API, AdditionalFee_API,
    OrderedItem_API, OrderedService_API, Person_API, PlacedOrder_API,
    ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API
)
from core.exception_handler import APIException
from core.messages import *

# Import routers to attach
from routers.business_routers.order_router import order_router
from routers.business_routers.cart_router import cart_router
from routers.business_routers.delivery_router import delivery_router
from routers.business_routers.service_router import service_router
from routers.business_routers.financial_router import financial_router
from routers.business_routers.business_operation_router import business_operation_router

# Import services for remaining direct endpoints
from services.cart_service import CartService
from services.financial_service import FinancialService

# Create main business router
business_router = APIRouter()


# Dependency injection for remaining endpoints
def get_cart_service() -> CartService:
    return CartService()

def get_financial_service() -> FinancialService:
    return FinancialService()

# ==================== REMAINING DIRECT ENDPOINTS ====================

@business_router.post("/business/cart/add")
def add_cart(
    api_ordered_items: List[OrderedItem_API],
    api_provided_services: List[OrderedService_API],
    api_cart: Cart_API = None,
    delivery: Delivery_API = None,
    client: Person_API = None,
    provider_id: int = 0,
    seller_user_id: int = 0,
    buyer_user_id: int = 0,
    cart_service: CartService = Depends(get_cart_service)
):
    """
    Creates a new cart with ordered items and services.
    """
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
    
    return {
        "message": "Cart created successfully",
        "cart_id": cart.cart_id,
        "financial_documents": {
            "has_invoice": 'invoice' in financial_docs,
            "has_payment": 'payment' in financial_docs,
            "has_receipt": 'receipt' in financial_docs,
            "has_deposit": 'deposit' in financial_docs
        },
        "cart": cart
    }

@business_router.post("/business/payment/add")
def add_payment(
    payment: Payment_API = None,
    deposit: Deposit_API = None,
    fee: AdditionalFee_API = None,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Adds a financial item (payment, deposit, or fee).
    """
    return financial_service.create_financial_item(payment, deposit, fee)

@business_router.get("/business/doc/{supplier_id}/{person_id}/{client_id}/{seller_id}/{cart_id}/{order_id}/{deposit_id}/{invoice_id}/{offset}/{limit}")
def get_finances(
    supplier_id: int = 0,
    person_id: int = 0,
    client_id: int = 0,
    seller_id: int = 0,
    cart_id: int = 0,
    order_id: int = 0,
    deposit_id: int = 0,
    invoice_id: int = 0,
    offset: int = 0,
    limit: int = 10,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Fetches financial documents based on filters.
    """
    return financial_service.get_financial_items(
        supplier_id, person_id, client_id, seller_id,
        cart_id, order_id, deposit_id, invoice_id,
        offset, limit
    )