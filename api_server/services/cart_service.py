# services/cart_service.py
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from core.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API,
    Person_API, Payment_API
)
from core.exception_handler import APIException
from core.messages import *
from core.models import Cart, Delivery, OrderedItem, OrderedService, Product, Invoice, Payment, Receipt, Deposit
from repositories.cart_repository import CartRepository, FinancialRepository
from repositories.product_repository import ProductRepository
from services.person_service import PersonService
from repositories.user_repository import UserRepository
from repositories.supplier_repository import SupplierRepository
from services.order_service import OrderService
from services.delivery_service import DeliveryService

class CartService:
    """Service for cart-related business logic"""
    
    def __init__(self):
        self.cart_repo = CartRepository()
        self.financial_repo = FinancialRepository()
        self.product_repo = ProductRepository()
        self.user_repo = UserRepository()
        self.supplier_repo = SupplierRepository()
        self.order_service = OrderService()
        self.delivery_service = DeliveryService()
        self.person_service = PersonService()
    
    def get_cart_by_id(self, cart_id: int) -> Cart:
        """Get cart by ID"""
        cart = self.cart_repo.get_cart_by_id(cart_id)
        if not cart:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=CART_NOT_EXISTS,
                details=f"Cart #{cart_id} does not exist"
            )
        return cart
    
    def get_carts_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by provider"""
        return self.cart_repo.get_carts_by_provider(provider_id, offset, limit)
    
    def get_carts_by_seller(self, seller_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by seller"""
        return self.cart_repo.get_carts_by_seller(seller_id, offset, limit)
    
    def get_carts_by_buyer(self, buyer_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by buyer"""
        return self.cart_repo.get_carts_by_buyer(buyer_id, offset, limit)
    
    def _create_invoice_for_cart(self, cart: Cart, total_amount: float) -> Invoice:
        """Create an invoice for the cart"""
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
        
        return self.financial_repo.create_invoice(invoice)
    
    def _create_payment(self, amount: float, status: str, invoice_id: Optional[int] = None) -> Payment:
        """Create a payment"""
        payment = Payment(
            payment_amount=amount,
            payment_method="cash",
            payment_status=status,
            payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        
        if invoice_id:
            payment.payment_invoice_id = invoice_id
        
        return self.financial_repo.create_payment(payment)
    
    def _create_payment_for_invoice(self, invoice: Invoice, amount: float) -> Payment:
        """Create a payment for an invoice"""
        payment_status = 'completed' if round(amount, 2) >= float(invoice.invoice_total_amount) else 'partial'
        
        payment = Payment(
            payment_invoice_id=invoice.invoice_id,
            payment_amount=amount,
            payment_method="card",
            payment_status=payment_status,
            payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            payment_notes=f"Payment for Invoice {invoice.invoice_number}"
        )
        
        # Update invoice status if fully paid
        if round(amount, 2) >= float(invoice.invoice_total_amount):
            invoice.invoice_status = 'paid'
            self.financial_repo.update_invoice(invoice)
        
        return self.financial_repo.create_payment(payment)
    
    def _create_receipt_for_payment(self, payment: Payment, cart: Cart) -> Receipt:
        """Create a receipt for a payment"""
        receipt = Receipt(
            receipt_payment_id=payment.payment_id,
            receipt_number=f"RCPT-{datetime.now().strftime('%Y%m%d')}-{cart.cart_id:04d}",
            receipt_amount=payment.payment_amount,
            receipt_cart_ref=cart.cart_id,
            receipt_notes=f"Receipt for Payment #{payment.payment_id}"
        )
        
        return self.financial_repo.create_receipt(receipt)
    
    def _create_deposit_for_cart(self, cart: Cart, amount: float) -> Deposit:
        """Create a deposit for a cart"""
        deposit = Deposit(
            deposit_cart_id=cart.cart_id,
            deposit_amount=amount,
            deposit_method="cash",
            deposit_reference=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            deposit_notes=f"Deposit for Cart #{cart.cart_id}"
        )
        
        return self.financial_repo.create_deposit(deposit)
    
    def _update_cart_status(self, cart: Cart, api_cart: Cart_API, financial_docs: Dict[str, Any]) -> None:
        """Update cart status based on financial documents"""
        new_status = api_cart.cart_status
        
        # If payment was made, update status
        if 'payment' in financial_docs:
            payment = financial_docs['payment']
            if payment.payment_status == 'completed':
                if float(payment.payment_amount) >= round(cart.cart_total_amount, 2):
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
            self.cart_repo.update_cart(cart)
    
    def create_cart(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
        cart_data: Cart_API,
        delivery: Optional[Delivery_API] = None,
        client: Optional[Person_API] = None,
        provider_id: int = 0,
        seller_user_id: int = 0,
        buyer_user_id: int = 0
    ) -> Tuple[Dict[str, Any], Cart]:
        """Create a new cart with financial documents"""
        
        # Validate supplier
        supplier = self.supplier_repo.get_supplier_basic(provider_id)
        if not supplier:
            raise APIException(status=HTTP_404_NOT_FOUND, code=SUPPLIER_NOT_EXISTS)
        
        # Validate seller
        selling_user = self.user_repo.get_by_id(seller_user_id)
        if not selling_user:
            raise APIException(status=HTTP_404_NOT_FOUND, code=APPUSER_NOT_EXISTS)
        
        # Validate buyer (optional)
        buyer_user = None
        if buyer_user_id != 0:
            buyer_user = self.user_repo.get_by_id(buyer_user_id)
        
        # Handle client/person
        person_obj = None
        if client:
            if client.id_person == 0:
                person_obj = self.person_service.create_person(client)
            else:
                person_obj = self.person_service.get_person_by_id(client.id_person)
        
        # Validate and process products
        ordered_items_models = []
        ordered_products = []
        order_total_price = 0.0
        
        for api_item in ordered_items:
            # Build ordered item
            ordered_item = self.order_service._build_ordered_item_model(api_item)
            
            # Validate product stock
            product = self.product_repo.get_product_by_id(ordered_item.ordered_product_id)
            if not product:
                raise APIException(status=HTTP_404_NOT_FOUND, code=PRODUCT_NOT_EXISTS)
            
            if product.product_quantity < ordered_item.ordered_quantity:
                raise APIException(
                    status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                    code=PRODUCT_QUANTITY_NOT_ENOUGH,
                    details=PRODUCT_QUANTITY_NOT_ENOUGH
                )
            
            # Update stock
            product.product_quantity -= ordered_item.ordered_quantity
            self.product_repo.update_product(product)
            
            ordered_items_models.append(ordered_item)
            ordered_products.append(product)
            
            # Calculate price
            item_price = ordered_item.ordered_quantity * float(product.product_price)
            if ordered_item.applied_vat:
                item_price *= (1 + ordered_item.applied_vat)
            order_total_price += item_price
        
        # Calculate service total
        service_total_price = sum(
            s.ordered_service_quantity * float(s.ordered_service_unit_price)
            for s in ordered_services
        )
        
        # Calculate final total
        final_total_price = order_total_price + service_total_price
        if cart_data.cart_total_amount:
            final_total_price = cart_data.cart_total_amount
        
        # Create cart
        cart = Cart(
            cart_product_provider_id=provider_id,
            cart_selling_user=selling_user.id_app_user,
            cart_status=cart_data.cart_status,
            cart_total_amount=final_total_price,
            cart_notes=cart_data.cart_notes,
        )
        
        if cart_data.cart_due_date:
            cart.cart_due_date = cart_data.cart_due_date
        
        # Set relationships
        if buyer_user:
            cart.cart_client_user = buyer_user.id_app_user
        if person_obj:
            cart.cart_person_ref = person_obj.id_person
        if ordered_services:
            cart.ordered_service = [self._build_ordered_service_model(s) for s in ordered_services]
        if ordered_items_models:
            cart.ordered_item = ordered_items_models
        
        # Handle delivery
        if delivery:
            delivery_obj = self.delivery_service._build_delivery_model(delivery)
            cart.delivery = delivery_obj
        else:
            cart.delivery = Delivery()
        
        # Save cart
        try:
            cart = self.cart_repo.create_cart(cart)
        except Exception as e:
            # Rollback product stock changes
            for product in ordered_products:
                product.product_quantity += 1
                self.product_repo.update_product(product)
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=CART_INSERT_FAILED,
                details=f"Failed to create cart: {str(e)}"
            )
        
        # Create financial documents
        financial_documents = {}
        
        # Create invoice if requested
        if cart_data.cart_invoice:
            invoice = self._create_invoice_for_cart(cart, final_total_price)
            financial_documents['invoice'] = invoice
        
        # Create payment if requested
        if cart_data.cart_payment and cart_data.cart_paid_money > 0:
            if 'invoice' in financial_documents:
                payment = self._create_payment_for_invoice(
                    financial_documents['invoice'],
                    cart_data.cart_paid_money
                )
            else:
                status = "partial" if cart_data.cart_paid_money < cart_data.cart_total_amount else "completed"
                payment = self._create_payment(cart_data.cart_paid_money, status)
            
            financial_documents['payment'] = payment
            
            # Create receipt if requested
            if cart_data.cart_receipt:
                receipt = self._create_receipt_for_payment(payment, cart)
                financial_documents['receipt'] = receipt
        
        # Create deposit if requested
        if cart_data.cart_deposit and cart_data.cart_paid_money > 0:
            deposit = self._create_deposit_for_cart(cart, cart_data.cart_paid_money)
            financial_documents['deposit'] = deposit
        
        # Update cart status
        self._update_cart_status(cart, cart_data, financial_documents)
        
        return financial_documents, cart
    
    def _build_ordered_service_model(self, api_service: OrderedService_API) -> OrderedService:
        """Build OrderedService model from API data"""
        service = OrderedService(
            ordered_service_quantity=api_service.ordered_service_quantity,
            ordered_service_unit_price=api_service.ordered_service_unit_price,
            ordered_service_total_price=api_service.ordered_service_total_price,
            ordered_service_notes=api_service.ordered_service_notes,
        )
        
        if api_service.ordered_service_scheduled_at:
            service.ordered_service_scheduled_at = api_service.ordered_service_scheduled_at
        
        return service
    
    def update_cart_status(self, cart_id: int, new_status: str) -> Cart:
        """Update cart status"""
        cart = self.get_cart_by_id(cart_id)
        cart.cart_status = new_status
        return self.cart_repo.update_cart(cart)
    
    def delete_cart(self, cart_id: int) -> bool:
        """Delete a cart"""
        cart = self.get_cart_by_id(cart_id)
        
        # Restore product stock if needed
        for item in cart.ordered_item or []:
            product = self.product_repo.get_product_by_id(item.ordered_product_id)
            if product:
                product.product_quantity += item.ordered_quantity
                self.product_repo.update_product(product)
        
        return self.cart_repo.delete_cart(cart)