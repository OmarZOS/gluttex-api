# services/cart_service.py
"""
Service for cart-related business logic including cart creation,
financial document management, and stock handling.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta

from core.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API,
    Person_API, Payment_API
)
from core.exceptions.specific.cart_exceptions import (
    CartServiceException,
    CartNotFoundException,
    CartCreationFailedException,
    CartUpdateFailedException,
    CartDeleteFailedException,
    CartSupplierNotFoundException,
    CartSellerNotFoundException,
    CartBuyerNotFoundException,
    CartProductNotFoundException,
    CartStockRollbackException,
    CartInvoiceCreationException,
    CartPaymentCreationException,
    CartReceiptCreationException,
    CartDepositCreationException,
)
from core.exceptions.handler import (ProductNotFoundException,
    InsufficientStockException)
from core.models import Cart, Delivery, OrderedItem, OrderedService, Product, Invoice, Payment, Receipt, Deposit
from repositories.cart_repository import CartRepository, FinancialRepository
from repositories.product_repository import ProductRepository
from services.person_service import PersonService
from repositories.user_repository import UserRepository
from repositories.supplier_repository import SupplierRepository
from services.order_service import OrderService
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


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
    
    # ==================== Cart Retrieval Methods ====================
    
    def get_cart_by_id(self, cart_id: int) -> Cart:
        """
        Get cart by ID.
        
        Args:
            cart_id: Cart ID to retrieve
            
        Returns:
            Cart object
            
        Raises:
            CartNotFoundException: If cart not found
        """
        cart = self.cart_repo.get_cart_by_id(cart_id)
        if not cart:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise CartNotFoundException(cart_id=cart_id)
        
        logger.debug(f"Retrieved cart {cart_id}")
        return cart
    
    def get_carts_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by provider ID"""
        logger.debug(f"Fetching carts for provider {provider_id} (offset={offset}, limit={limit})")
        return self.cart_repo.get_carts_by_provider(provider_id, offset, limit)
    
    def get_carts_by_seller(self, seller_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by seller ID"""
        logger.debug(f"Fetching carts for seller {seller_id} (offset={offset}, limit={limit})")
        return self.cart_repo.get_carts_by_seller(seller_id, offset, limit)
    
    def get_carts_by_buyer(self, buyer_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by buyer ID"""
        logger.debug(f"Fetching carts for buyer {buyer_id} (offset={offset}, limit={limit})")
        return self.cart_repo.get_carts_by_buyer(buyer_id, offset, limit)
    
    # ==================== Financial Document Creation ====================
    
    def _create_invoice_for_cart(self, cart: Cart, total_amount: float) -> Invoice:
        """
        Create an invoice for the cart.
        
        Args:
            cart: Cart object
            total_amount: Total amount for invoice
            
        Returns:
            Created Invoice object
            
        Raises:
            CartInvoiceCreationException: If invoice creation fails
        """
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
        
        try:
            result = self.financial_repo.create_invoice(invoice)
            logger.info(f"Created invoice {invoice_number} for cart {cart.cart_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create invoice for cart {cart.cart_id}: {e}")
            raise CartInvoiceCreationException(
                cart_id=cart.cart_id,
                error=str(e)
            )
    
    def _create_payment(self, amount: float, status: str, invoice_id: Optional[int] = None) -> Payment:
        """
        Create a payment.
        
        Args:
            amount: Payment amount
            status: Payment status (completed, partial, pending)
            invoice_id: Optional invoice ID to associate payment with
            
        Returns:
            Created Payment object
            
        Raises:
            CartPaymentCreationException: If payment creation fails
        """
        payment = Payment(
            payment_amount=amount,
            payment_method="cash",
            payment_status=status,
            payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        )
        
        if invoice_id:
            payment.payment_invoice_id = invoice_id
        
        try:
            result = self.financial_repo.create_payment(payment)
            logger.info(f"Created payment of {amount} with status '{status}'")
            return result
        except Exception as e:
            logger.error(f"Failed to create payment: {e}")
            raise CartPaymentCreationException(
                amount=amount,
                error=str(e)
            )
    
    def _create_payment_for_invoice(self, invoice: Invoice, amount: float) -> Payment:
        """
        Create a payment for an invoice.
        
        Args:
            invoice: Invoice object
            amount: Payment amount
            
        Returns:
            Created Payment object
        """
        payment_status = 'completed' if round(amount, 2) >= float(invoice.invoice_total_amount) else 'partial'
        
        payment = Payment(
            payment_invoice_id=invoice.invoice_id,
            payment_amount=amount,
            payment_method="card",
            payment_status=payment_status,
            payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            payment_notes=f"Payment for Invoice {invoice.invoice_number}"
        )
        
        try:
            # Update invoice status if fully paid
            if round(amount, 2) >= float(invoice.invoice_total_amount):
                invoice.invoice_status = 'paid'
                self.financial_repo.update_invoice(invoice)
                logger.info(f"Invoice {invoice.invoice_number} marked as paid")
            
            result = self.financial_repo.create_payment(payment)
            logger.info(f"Created payment of {amount} for invoice {invoice.invoice_number}")
            return result
        except Exception as e:
            logger.error(f"Failed to create payment for invoice {invoice.invoice_number}: {e}")
            raise CartPaymentCreationException(
                cart_id=invoice.invoice_cart_id,
                amount=amount,
                error=str(e)
            )
    
    def _create_receipt_for_payment(self, payment: Payment, cart: Cart) -> Receipt:
        """
        Create a receipt for a payment.
        
        Args:
            payment: Payment object
            cart: Cart object
            
        Returns:
            Created Receipt object
        """
        receipt = Receipt(
            receipt_payment_id=payment.payment_id,
            receipt_number=f"RCPT-{datetime.now().strftime('%Y%m%d')}-{cart.cart_id:04d}",
            receipt_amount=payment.payment_amount,
            receipt_cart_ref=cart.cart_id,
            receipt_notes=f"Receipt for Payment #{payment.payment_id}"
        )
        
        try:
            result = self.financial_repo.create_receipt(receipt)
            logger.info(f"Created receipt for payment {payment.payment_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create receipt for payment {payment.payment_id}: {e}")
            raise CartReceiptCreationException(
                cart_id=cart.cart_id,
                payment_id=payment.payment_id,
                error=str(e)
            )
    
    def _create_deposit_for_cart(self, cart: Cart, amount: float) -> Deposit:
        """
        Create a deposit for a cart.
        
        Args:
            cart: Cart object
            amount: Deposit amount
            
        Returns:
            Created Deposit object
        """
        deposit = Deposit(
            deposit_cart_id=cart.cart_id,
            deposit_amount=amount,
            deposit_method="cash",
            deposit_reference=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            deposit_notes=f"Deposit for Cart #{cart.cart_id}"
        )
        
        try:
            result = self.financial_repo.create_deposit(deposit)
            logger.info(f"Created deposit of {amount} for cart {cart.cart_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create deposit for cart {cart.cart_id}: {e}")
            raise CartDepositCreationException(
                cart_id=cart.cart_id,
                amount=amount,
                error=str(e)
            )
    
    def _update_cart_status(self, cart: Cart, api_cart: Cart_API, financial_docs: Dict[str, Any]) -> None:
        """
        Update cart status based on financial documents.
        
        Args:
            cart: Cart object to update
            api_cart: API cart data
            financial_docs: Created financial documents
        """
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
            logger.info(f"Cart {cart.cart_id} status updated to '{new_status}'")
    
    # ==================== Cart Creation ====================
    
    def _validate_cart_creation(
        self,
        provider_id: int,
        seller_user_id: int,
        ordered_items: List[OrderedItem_API]
    ) -> Tuple[Any, Any, List[Tuple[Product, OrderedItem_API]]]:
        """
        Validate all entities needed for cart creation.
        
        Returns:
            Tuple of (supplier, selling_user, validated_products)
            
        Raises:
            CartSupplierNotFoundException: If supplier not found
            CartSellerNotFoundException: If seller not found
            CartProductNotFoundException: If product not found
            InsufficientStockException: If insufficient stock
        """
        # Validate supplier
        supplier = self.supplier_repo.get_supplier_basic(provider_id)
        if not supplier:
            logger.warning(f"Supplier not found with ID: {provider_id}")
            raise CartSupplierNotFoundException(provider_id=provider_id)
        
        # Validate seller
        selling_user = self.user_repo.get_by_id(seller_user_id)
        if not selling_user:
            logger.warning(f"Seller not found with ID: {seller_user_id}")
            raise CartSellerNotFoundException(seller_id=seller_user_id)
        
        # Validate products and stock
        validated_products = []
        for api_item in ordered_items:
            product = self.product_repo.get_product_by_id(api_item.ordered_product_id)
            if not product:
                logger.warning(f"Product not found with ID: {api_item.ordered_product_id}")
                raise CartProductNotFoundException(product_id=api_item.ordered_product_id)
            
            if product.product_quantity < api_item.ordered_quantity:
                logger.warning(f"Insufficient stock for product {product.product_name}: requested {api_item.ordered_quantity}, available {product.product_quantity}")
                raise InsufficientStockException(
                    product_name=product.product_name,
                    requested=api_item.ordered_quantity,
                    available=product.product_quantity
                )
            
            validated_products.append((product, api_item))
        
        return supplier, selling_user, validated_products
    
    def _process_cart_items(
        self,
        validated_products: List[Tuple[Product, OrderedItem_API]],
        ordered_services: List[OrderedService_API]
    ) -> Tuple[List[OrderedItem], List[Product], float, float]:
        """
        Process cart items, update stock, and calculate totals.
        
        Returns:
            Tuple of (ordered_items_models, ordered_products, order_total_price, service_total_price)
        """
        ordered_items_models = []
        ordered_products = []
        order_total_price = 0.0
        
        # Process products
        for product, api_item in validated_products:
            # Build ordered item
            ordered_item = self.order_service._build_ordered_item_model(api_item)
            
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
        
        return ordered_items_models, ordered_products, order_total_price, service_total_price
    
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
        """
        Create a new cart with financial documents.
        
        Args:
            ordered_items: List of items to add to cart
            ordered_services: List of services to add to cart
            cart_data: Cart details
            delivery: Optional delivery information
            client: Optional client information
            provider_id: Provider ID
            seller_user_id: Seller user ID
            buyer_user_id: Buyer user ID (0 for anonymous)
            
        Returns:
            Tuple of (financial_documents, created_cart)
            
        Raises:
            Various cart-related exceptions
        """
        logger.info(f"Creating cart for provider {provider_id}, seller {seller_user_id}")
        
        # Validate cart has content
        if not ordered_items and not ordered_services:
            raise CartCreationFailedException(
                error="Cart must have at least one item or service",
                provider_id=provider_id,
                seller_id=seller_user_id
            )
        
        # Validate all entities
        supplier, selling_user, validated_products = self._validate_cart_creation(
            provider_id, seller_user_id, ordered_items
        )
        
        # Validate buyer (optional)
        buyer_user = None
        if buyer_user_id != 0:
            buyer_user = self.user_repo.get_by_id(buyer_user_id)
            if not buyer_user:
                logger.warning(f"Buyer not found with ID: {buyer_user_id}")
                raise CartBuyerNotFoundException(buyer_id=buyer_user_id)
        
        # Handle client/person
        person_obj = None
        if client:
            if client.id_person == 0:
                person_obj = self.person_service.create_person(client)
            else:
                person_obj = self.person_service.get_person_by_id(client.id_person)
        
        # Process items and calculate totals
        ordered_items_models, ordered_products, order_total_price, service_total_price = self._process_cart_items(
            validated_products, ordered_services
        )
        
        # Calculate final total
        final_total_price = order_total_price + service_total_price
        if cart_data.cart_total_amount:
            final_total_price = cart_data.cart_total_amount
        
        # Create cart object
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
            logger.info(f"Cart created with ID: {cart.cart_id}")
        except Exception as e:
            # Rollback product stock changes
            logger.error(f"Failed to create cart, rolling back stock: {e}")
            for product in ordered_products:
                try:
                    product.product_quantity += 1
                    self.product_repo.update_product(product)
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback stock for product {product.id_product}: {rollback_error}")
            
            raise CartCreationFailedException(
                error=str(e),
                provider_id=provider_id,
                seller_id=seller_user_id,
                buyer_id=buyer_user_id if buyer_user_id > 0 else None
            )
        
        # Create financial documents
        financial_documents = self._create_financial_documents(cart, cart_data, final_total_price)
        
        # Update cart status
        self._update_cart_status(cart, cart_data, financial_documents)
        
        logger.info(f"Cart {cart.cart_id} creation completed with financial docs: {list(financial_documents.keys())}")
        return financial_documents, cart
    
    def _create_financial_documents(
        self,
        cart: Cart,
        cart_data: Cart_API,
        final_total_price: float
    ) -> Dict[str, Any]:
        """
        Create financial documents for the cart.
        
        Args:
            cart: Created cart object
            cart_data: Cart API data
            final_total_price: Final total price
            
        Returns:
            Dictionary of created financial documents
        """
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
        
        return financial_documents
    
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
    
    # ==================== Cart Update Methods ====================
    
    def update_cart_status(self, cart_id: int, new_status: str) -> Cart:
        """
        Update cart status.
        
        Args:
            cart_id: Cart ID to update
            new_status: New status value
            
        Returns:
            Updated cart object
        """
        logger.info(f"Updating cart {cart_id} status to '{new_status}'")
        cart = self.get_cart_by_id(cart_id)
        cart.cart_status = new_status
        
        try:
            result = self.cart_repo.update_cart(cart)
            logger.info(f"Cart {cart_id} status updated successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to update cart {cart_id} status: {e}")
            raise CartUpdateFailedException(
                cart_id=cart_id,
                error=str(e),
                fields_attempted=["cart_status"]
            )
    
    def delete_cart(self, cart_id: int) -> bool:
        """
        Delete a cart and restore product stock.
        
        Args:
            cart_id: Cart ID to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            CartNotFoundException: If cart not found
            CartDeleteFailedException: If deletion fails
        """
        logger.info(f"Deleting cart {cart_id}")
        cart = self.get_cart_by_id(cart_id)
        
        # Restore product stock if needed
        restored_count = 0
        for item in cart.ordered_item or []:
            try:
                product = self.product_repo.get_product_by_id(item.ordered_product_id)
                if product:
                    product.product_quantity += item.ordered_quantity
                    self.product_repo.update_product(product)
                    restored_count += 1
                    logger.debug(f"Restored {item.ordered_quantity} units of product {product.id_product}")
            except Exception as e:
                logger.error(f"Failed to restore stock for product {item.ordered_product_id}: {e}")
                raise CartStockRollbackException(
                    cart_id=cart_id,
                    product_id=item.ordered_product_id,
                    error=str(e)
                )
        
        logger.info(f"Restored stock for {restored_count} products")
        
        try:
            result = self.cart_repo.delete_cart(cart)
            logger.info(f"Cart {cart_id} deleted successfully")
            return result
        except Exception as e:
            logger.error(f"Failed to delete cart {cart_id}: {e}")
            raise CartDeleteFailedException(
                cart_id=cart_id,
                error=str(e)
            )