# here, we make schema translations

from typing import List, Tuple
from features.business.order.order_delete import delete_order_items
from features.business.order.order_insert import insert_order_item
from features.business.order.order_fetch import fetch_order_by_id
from constants import ORDER_STATUSES
from core.exception_handler import APIException
from core.api_models import Cart_API, OrderedItem_API, PlacedOrder_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id
from datetime import datetime;



def update_cart_status(cart: Cart, api_cart: Cart_API, financial_docs: dict):
    """Update cart status based on financial documents."""
    new_status = api_cart.cart_status
    
    # If payment was made, update status
    if 'payment' in financial_docs:
        payment = financial_docs['payment']
        if payment.payment_status == 'completed':
            if float(payment.payment_amount) >= round(cart.cart_total_amount,2):
                new_status = 'completed'
            else:
                new_status = 'partial'
        elif payment.payment_status == 'partial':
            new_status = 'pending'
    
    # If deposit was made
    elif 'deposit' in financial_docs:
        new_status = 'deposit_paid'
    
    # Update cart status if changed
    if new_status != cart.cart_status:
        cart.cart_status = new_status
        update_record_in_api(cart)




