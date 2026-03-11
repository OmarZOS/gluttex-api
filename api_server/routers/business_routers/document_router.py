import json
from fastapi import APIRouter, BackgroundTasks,  status
from fastapi.encoders import jsonable_encoder
from typing import List
from document.generator import get_renderer
from document.invoice_data import InvoiceGenerator
from features.business.finance.payment_fetch import fetch_financial_item
from features.business.finance.payment_insert import insert_financial_item
from features.business.cart.cart_insert import insert_cart
from features.business.cart.cart_fetch import fetch_cart
from features.business.cart.service.service_fetch import fetch_services
# from features.business.cart.service.service_insert import insert_service
from features.business.order.order_delete import delete_order
from features.business.order.order_update import update_order
from core.api_models import AdditionalFee_API, Cart_API, Deposit_API, Payment_API,  OrderedItem_API, OrderedService_API, Person_API, PlacedOrder_API, ProvidedService_API, ServiceResourceRequirement_API, ServiceStaffRequirement_API

from features.business.order.order_insert import insert_order
from features.business.cart.cart_fetch import fetch_business_operations
from features.business.order.order_fetch import  fetch_items_order, fetch_placed_order_details, fetch_placed_orders
from features.business.product.product_update import notify_subscribers
from fastapi.responses import HTMLResponse


document_router = APIRouter()




@document_router.get("/document/cart/invoice/{provider_id}/{seller_id}/{cart_id}/{client_id}/{person_id}")
def fetch_cart_invoice(provider_id: int = 0,seller_id: int = 0,cart_id: int = 0,client_id: int = 0,person_id: int = 0):
    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """

    cart = fetch_cart(provider_id,seller_id,cart_id, client_id ,person_id, 0 ,1)
    invoice  = InvoiceGenerator.from_json(InvoiceGenerator.cart_to_json(cart[0]) )
    return HTMLResponse(content=get_renderer().render_compact_invoice(invoice), status_code=200)

@document_router.get("/document/cart/receipt/{provider_id}/{seller_id}/{cart_id}/{client_id}/{person_id}")
def fetch_cart_receipt(provider_id: int = 0,seller_id: int = 0,cart_id: int = 0,client_id: int = 0,person_id: int = 0):

    """
    Fetches all placed orders for a specific user.

    Args:
        client (int): The user's ID.

    Returns:
        list: List of placed orders.
    """
    cart = fetch_cart(provider_id,seller_id,cart_id, client_id ,person_id, 0 ,1)
    invoice  = InvoiceGenerator.from_json(InvoiceGenerator.cart_to_json(cart[0]) )
    return HTMLResponse(content=get_renderer().render_compact_receipt(invoice), status_code=200)


