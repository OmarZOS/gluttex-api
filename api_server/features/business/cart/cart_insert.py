# here, we make schema translations

from typing import List, Tuple
from features.business.cart.cart_update import update_cart_status
from features.business.cart.service.service_insert import build_ordered_service, build_service
from features.business.supplier.supplier_fetch import touch_supplier
from features.medical.person.person_fetch import fetch_only_person_by_id
from features.medical.person.person_insert import generate_person_object
from features.business.order.order_insert import build_ordered_item
from communication.publisher import send_to_product_subscribers
from core.exception_handler import APIException
from core.api_models import Cart_API, OrderedItem_API, OrderedService_API, Payment_API, Person_API, PlacedOrder_API, ProvidedService_API
from core.messages import *
from core.models import *
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.product.product_fetch import fetch_product_by_id
from features.app.user.user_fetch import fetch_user_by_id, touch_user
from datetime import datetime, timedelta;





def insert_cart(api_ordered_items: List[OrderedItem_API], 
                api_provided_services: List[OrderedService_API],
                api_cart: Cart_API, 
                client: Person_API = None,
                provider_id: int = 0, 
                seller_user_id: int = 0, 
                buyer_user_id: int = 0):
    """
    Insert a new cart into the system with optional financial documents.
    
    Args:
        api_ordered_items: List of ordered products
        api_provided_services: List of ordered services
        api_cart: Cart data including financial flags
        client: Person data for the client
        provider_id: Product provider ID
        seller_user_id: User ID of the seller
        buyer_user_id: User ID of the buyer
    
    Returns:
        Updated product quantities and final cart with financial documents
    
    Raises:
        APIException: If validation fails or insertion conflicts
    """
    # --- Validate supplier ---
    supplier = touch_supplier(provider_id)
    if supplier is None:
        raise APIException(status=HTTP_404_NOT_FOUND, code=SUPPLIER_NOT_EXISTS)
    
    # --- Validate seller user ---
    selling_user = touch_user(seller_user_id)
    if selling_user is None:
        raise APIException(status=HTTP_404_NOT_FOUND, code=APPUSER_NOT_EXISTS)
    
    # --- Validate buyer/user ---
    buyer_user = None
    if buyer_user_id != 0:
        buyer_user = touch_user(buyer_user_id)
    
    # --- Handle client/person ---
    person_obj = None
    if client is not None:
        if client.id_person == 0:
            person_obj = generate_person_object(client)
        else:
            person_obj = fetch_only_person_by_id(client.id_person)
        
    
    if (buyer_user is None) and (person_obj is None):
        raise APIException(status=HTTP_404_NOT_FOUND, code=CLIENT_NOT_EXISTS)
    
    # --- Validate products & build ordered items ---
    ordered_items: List[OrderedItem] = []
    ordered_products: List[Product] = []
    order_total_price: float = 0.0
    
    for api_ordered_item in api_ordered_items:
        ordered_item = build_ordered_item(api_ordered_item)
        
        # Fetch product
        ordered_product = fetch_product_by_id(ordered_item.ordered_product_id)
        if ordered_product is None:
            raise APIException(status=HTTP_404_NOT_FOUND, code=PRODUCT_NOT_EXISTS)
        
        # Validate stock
        if ordered_product.product_quantity < ordered_item.ordered_quantity:
            raise APIException(
                status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                code=PRODUCT_QUANTITY_NOT_ENOUGH,
                details=PRODUCT_QUANTITY_NOT_ENOUGH
            )
        
        ordered_items.append(ordered_item)
        ordered_products.append(ordered_product)
    
    # --- Update product stock & calculate total price ---
    updated_quantities: List[int] = []
    
    for ordered_item, ordered_product in zip(ordered_items, ordered_products):
        # Update quantity
        ordered_product.product_quantity -= ordered_item.ordered_quantity
        updated_quantities.append(ordered_product.product_quantity)
        
        # Calculate item price
        item_price = ordered_item.ordered_quantity * float(ordered_product.product_price)
        if ordered_item.applied_vat:
            item_price *= (1 + ordered_item.applied_vat)
        order_total_price += item_price
        
        # Update product in database
        try:
            update_record_in_api(ordered_product)
            send_to_product_subscribers(
                {'product_quantity': ordered_product.product_quantity},
                ordered_product.id_product
            )
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=PRODUCT_QUANTITY_NOT_ENOUGH,
                message=IMAGE_INSERT_FAILED,
                details=f"{str(e)}"
            )
    
    # --- Build ordered services ---
    ordered_services = []
    service_total_price: float = 0.0
    
    for api_provided_service in api_provided_services:
        service = build_ordered_service(api_provided_service)
        ordered_services.append(service)
        
        # Calculate service price
        service_price = api_provided_service.ordered_service_quantity * float(api_provided_service.ordered_service_unit_price)
        service_total_price += service_price
    
    # --- Calculate final total ---
    final_total_price = order_total_price + service_total_price
    
    # Use API cart total if provided, otherwise use calculated total
    if api_cart.cart_total_amount :
        final_total_price = api_cart.cart_total_amount
    
    # --- Create cart object ---
    cart = Cart(
        cart_product_provider_id=provider_id,
        cart_selling_user=selling_user.id_app_user,
        cart_status=api_cart.cart_status,
        cart_total_amount=final_total_price,
        cart_notes=api_cart.cart_notes,
    )
    
    # Set optional relationships
    if buyer_user is not None:
        cart.cart_client_user = buyer_user.id_app_user
    print("Adding the new guy1")
    if person_obj is not None:
        if cart.cart_person_ref == 0:
            cart.cart_person_ref = person_obj.id_person
        else:
            cart.person = person_obj
    
    if len(ordered_services) > 0:
        cart.ordered_service = ordered_services
    
    # print("sqsqs")

    if len(ordered_items) > 0:
        cart.ordered_item = ordered_items
    
    # --- Handle financial documents based on API flags ---
    financial_documents = {}
    
    try:
        # Insert cart first
        cart = insert_or_complete_or_raise(cart)
        invoice = None
        # Generate invoice if requested
        if api_cart.cart_invoice:
            invoice = create_invoice_for_cart(cart, final_total_price)
            financial_documents['invoice'] = invoice
            
        # Generate payment if requested
        if api_cart.cart_payment and api_cart.cart_paid_money > 0:
            if invoice != None:
                payment = create_payment_for_invoice(
                    invoice, 
                    api_cart.cart_paid_money
                )
            else:
                status = "partial" if api_cart.cart_paid_money < api_cart.cart_total_amount else "completed" 
                payment = create_payment(api_cart.cart_paid_money,status)
            financial_documents['payment'] = payment
            
            # Generate receipt if requested
            if api_cart.cart_receipt:
                receipt = create_receipt_for_payment(payment, cart)
                financial_documents['receipt'] = receipt
        # Handle deposit if no payment but deposit flag is set
        if api_cart.cart_deposit and api_cart.cart_paid_money > 0:
            deposit = create_deposit_for_cart(
                cart, 
                api_cart.cart_paid_money, 
                api_cart
            )
            financial_documents['deposit'] = deposit
            
            # Generate receipt for deposit if requested
            if api_cart.cart_receipt:
                receipt = create_receipt_for_deposit(deposit, cart)
                financial_documents['receipt'] = receipt
        
        # Update cart status based on payment/deposit
        update_cart_status(cart, api_cart, financial_documents)
        
        return financial_documents,cart
        
    except Exception as e:
        # Rollback product quantities if cart insertion fails
        for ordered_product, original_quantity in zip(ordered_products, updated_quantities):
            try:
                ordered_product.product_quantity = original_quantity + ordered_item.ordered_quantity
                update_record_in_api(ordered_product)
            except:
                pass  # Log but don't fail
        
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=ORDER_INSERT_CONFLICT,
            details=f"Failed to insert cart: {str(e)}"
        )


def create_invoice_for_cart(cart: Cart, total_amount: float) -> Invoice:
    """Create an invoice for the cart."""
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{cart.cart_id:04d}"
    
    invoice = Invoice(
        invoice_cart_id=cart.cart_id,
        invoice_number=invoice_number,
        invoice_total_amount=total_amount,
        invoice_status='unpaid',
        invoice_issue_date=datetime.now().date(),
        invoice_due_date=(datetime.now() + timedelta(days=30)).date(),
        invoice_notes=f"Invoice for Cart #{cart.cart_id}"
    )
    
    return insert_or_complete_or_raise(invoice)

def create_payment(payment: Payment_API):
    payment_method = payment.payment_method  # Default, could be from API
    payment_status = payment.payment_status
    payment_amount = payment.payment_amount
    payment_reference = payment.payment_reference
    payment_notes = payment.payment_notes

    new_payment = Payment(
        payment_amount=payment_amount,
        payment_method=payment_method,
        payment_status=payment_status,
        payment_reference=payment_reference,
        payment_notes=payment_notes
    )
    if (payment.payment_invoice_id):
        new_payment.payment_invoice_id = payment.payment_invoice_id

    return new_payment


def create_payment_for_invoice(invoice: Invoice, amount: float) -> Payment:
    """Create a payment for an invoice."""
    payment_method = "card"  # Default, could be from API
    
    payment_status = 'completed' if round(amount,2) >= float(invoice.invoice_total_amount) else 'partial'

    payment = Payment(
        payment_invoice_id=invoice.invoice_id,
        payment_amount=amount,
        payment_method=payment_method,
        payment_status=payment_status,
        payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        payment_notes=f"Payment for Invoice {invoice.invoice_number}"
    )
    
    # Update invoice status if fully paid
    if round(amount,2) >= float(invoice.invoice_total_amount):
        invoice.invoice_status = 'paid'
        update_record_in_api(invoice)
    
    return insert_or_complete_or_raise(payment)

def create_payment(amount: float,status:str) -> Payment:
    """Create a payment for an invoice."""
    payment_method = "cash"  # Default, could be from API
    
    payment_status = status

    payment = Payment(
        # payment_invoice_id=invoice.invoice_id,
        payment_amount=amount,
        payment_method=payment_method,
        payment_status=payment_status,
        payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        # payment_notes=f"Payment for Invoice {invoice.invoice_number}"
    )
    
    
    return insert_or_complete_or_raise(payment)


def create_receipt_for_payment(payment: Payment, cart: Cart) -> Receipt:
    """Create a receipt for a payment."""
    receipt = Receipt(
        receipt_payment_id=payment.payment_id,
        receipt_number=f"RCPT-{datetime.now().strftime('%Y%m%d')}-{cart.cart_id:04d}",
        receipt_amount=payment.payment_amount,
        receipt_cart_ref=cart.cart_id,
        receipt_notes=f"Receipt for Payment #{payment.payment_id}"
    )
    
    return insert_or_complete_or_raise(receipt)


def create_deposit_for_cart(cart: Cart, amount: float, api_cart: Cart_API) -> Deposit:
    """Create a deposit for a cart."""
    deposit_method = "cash"  # Default, could be from API
    
    deposit = Deposit(
        deposit_cart_id=cart.cart_id,
        deposit_amount=amount,
        deposit_method=deposit_method,
        deposit_reference=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        deposit_notes=f"Deposit for Cart #{cart.cart_id}"
    )
    
    return insert_or_complete_or_raise(deposit)


def create_receipt_for_deposit(deposit: Deposit, cart: Cart) -> Receipt:
    """Create a receipt for a deposit."""
    receipt = Receipt(
        receipt_number=f"DEP-RCPT-{datetime.now().strftime('%Y%m%d')}-{cart.cart_id:04d}",
        receipt_amount=deposit.deposit_amount,
        receipt_cart_ref=cart.cart_id,
        receipt_notes=f"Receipt for Deposit #{deposit.deposit_id}",
        # No payment reference for deposit receipts
    )
    
    receipt = insert_or_complete_or_raise(receipt)
    
    # Link receipt to deposit
    deposit.deposit_receipt_id = receipt.receipt_id
    update_record_in_api(deposit)
    
    return receipt

