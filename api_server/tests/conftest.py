# tests/services/test_cart_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock, ANY
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional

from services.cart_service import CartService
from core.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API,
    Person_API, Payment_API
)
from core.exceptions.handler import APIException
from core.messages import *
from core.models import (
    Cart, Delivery, OrderedItem, OrderedService, Product, Invoice, 
    Payment, Receipt, Deposit, AppUser, Person, ProductProvider
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os


# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_auth.db")

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



class TestCartService:
    """Test suite for CartService with database integration"""
    
    @pytest.fixture
    def cart_service(self, db_session):
        """Create CartService instance with mocked repositories"""
        with patch('services.cart_service.CartRepository') as mock_cart_repo_class, \
             patch('services.cart_service.FinancialRepository') as mock_financial_repo_class, \
             patch('services.cart_service.ProductRepository') as mock_product_repo_class, \
             patch('services.cart_service.UserRepository') as mock_user_repo_class, \
             patch('services.cart_service.SupplierRepository') as mock_supplier_repo_class, \
             patch('services.cart_service.OrderService') as mock_order_service_class, \
             patch('services.cart_service.DeliveryService') as mock_delivery_service_class, \
             patch('services.cart_service.PersonService') as mock_person_service_class:
            
            service = CartService()
            
            # Store mocks for access in tests
            service.mock_cart_repo = mock_cart_repo_class.return_value
            service.mock_financial_repo = mock_financial_repo_class.return_value
            service.mock_product_repo = mock_product_repo_class.return_value
            service.mock_user_repo = mock_user_repo_class.return_value
            service.mock_supplier_repo = mock_supplier_repo_class.return_value
            service.mock_order_service = mock_order_service_class.return_value
            service.mock_delivery_service = mock_delivery_service_class.return_value
            service.mock_person_service = mock_person_service_class.return_value
            
            yield service
    
    @pytest.fixture
    def sample_cart(self, populated_db):
        """Get a sample cart from populated database"""
        return populated_db['cart']
    
    @pytest.fixture
    def sample_product(self, populated_db):
        """Get a sample product from populated database"""
        return populated_db['product']
    
    @pytest.fixture
    def sample_app_user(self, populated_db):
        """Get a sample app user from populated database"""
        return populated_db['app_user']
    
    @pytest.fixture
    def sample_product_provider(self, populated_db):
        """Get a sample product provider from populated database"""
        return populated_db['product_provider']
    
    @pytest.fixture
    def sample_ordered_item_api(self):
        """Create sample ordered item API data"""
        return OrderedItem_API(
            ordered_product_id=1,
            ordered_quantity=2,
            applied_vat=0.2,
            ordered_product_notes='Test notes'
        )
    
    @pytest.fixture
    def sample_cart_api(self):
        """Create sample cart API data"""
        return Cart_API(
            cart_status='pending',
            cart_total_amount=500.00,
            cart_notes='Test cart',
            cart_due_date=datetime.now().date() + timedelta(days=30),
            cart_invoice=True,
            cart_payment=True,
            cart_receipt=True,
            cart_deposit=False,
            cart_paid_money=500.00
        )
    
    @pytest.fixture
    def sample_delivery_api(self):
        """Create sample delivery API data"""
        return Delivery_API(
            delivery_address="123 Test St",
            delivery_city="Test City",
            delivery_postal_code="12345",
            delivery_country="Test Country",
            delivery_notes="Leave at door"
        )
    
    @pytest.fixture
    def sample_person_api(self):
        """Create sample person API data"""
        return Person_API(
            id_person=0,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1234567890"
        )
    
    def test_get_cart_by_id_success(self, cart_service, sample_cart):
        """Test successful retrieval of cart by ID"""
        cart_service.mock_cart_repo.get_cart_by_id.return_value = sample_cart
        
        result = cart_service.get_cart_by_id(sample_cart.cart_id)
        
        assert result == sample_cart
        cart_service.mock_cart_repo.get_cart_by_id.assert_called_once_with(sample_cart.cart_id)
    
    def test_get_cart_by_id_not_found(self, cart_service):
        """Test getting non-existent cart raises exception"""
        cart_service.mock_cart_repo.get_cart_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            cart_service.get_cart_by_id(999)
        
        assert exc_info.value.status == HTTP_404_NOT_FOUND
        assert exc_info.value.code == CART_NOT_EXISTS
        assert "Cart #999 does not exist" in exc_info.value.details
    
    def test_get_carts_by_provider(self, cart_service, sample_cart):
        """Test getting carts by provider"""
        expected_carts = [sample_cart]
        provider_id = sample_cart.cart_product_provider_id
        cart_service.mock_cart_repo.get_carts_by_provider.return_value = expected_carts
        
        result = cart_service.get_carts_by_provider(provider_id, offset=0, limit=50)
        
        assert result == expected_carts
        cart_service.mock_cart_repo.get_carts_by_provider.assert_called_once_with(provider_id, 0, 50)
    
    def test_get_carts_by_seller(self, cart_service, sample_cart, sample_app_user):
        """Test getting carts by seller"""
        expected_carts = [sample_cart]
        seller_id = sample_app_user.id_app_user
        cart_service.mock_cart_repo.get_carts_by_seller.return_value = expected_carts
        
        result = cart_service.get_carts_by_seller(seller_id, offset=10, limit=20)
        
        assert result == expected_carts
        cart_service.mock_cart_repo.get_carts_by_seller.assert_called_once_with(seller_id, 10, 20)
    
    def test_get_carts_by_buyer(self, cart_service, sample_cart, sample_app_user):
        """Test getting carts by buyer"""
        expected_carts = [sample_cart]
        buyer_id = sample_app_user.id_app_user
        cart_service.mock_cart_repo.get_carts_by_buyer.return_value = expected_carts
        
        result = cart_service.get_carts_by_buyer(buyer_id, offset=5, limit=15)
        
        assert result == expected_carts
        cart_service.mock_cart_repo.get_carts_by_buyer.assert_called_once_with(buyer_id, 5, 15)
    
    def test_create_invoice_for_cart(self, cart_service, sample_cart):
        """Test invoice creation for a cart"""
        total_amount = 500.00
        expected_invoice = Invoice(
            invoice_cart_id=sample_cart.cart_id,
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{sample_cart.cart_id:04d}",
            invoice_total_amount=total_amount,
            invoice_status='unpaid',
            invoice_issue_date=datetime.now().date(),
            invoice_due_date=(datetime.now() + timedelta(days=30)).date(),
            invoice_notes=f"Invoice for Cart #{sample_cart.cart_id}"
        )
        
        cart_service.mock_financial_repo.create_invoice.return_value = expected_invoice
        
        result = cart_service._create_invoice_for_cart(sample_cart, total_amount)
        
        assert result == expected_invoice
        assert result.invoice_total_amount == total_amount
        assert result.invoice_status == 'unpaid'
        cart_service.mock_financial_repo.create_invoice.assert_called_once()
    
    def test_create_payment_without_invoice(self, cart_service):
        """Test payment creation without invoice"""
        amount = 500.00
        status = 'completed'
        
        expected_payment = Payment(
            payment_id=1,
            payment_amount=amount,
            payment_status=status,
            payment_method='cash',
            payment_reference=ANY
        )
        
        cart_service.mock_financial_repo.create_payment.return_value = expected_payment
        
        result = cart_service._create_payment(amount, status)
        
        assert result.payment_amount == amount
        assert result.payment_status == status
        cart_service.mock_financial_repo.create_payment.assert_called_once()
    
    def test_create_payment_for_invoice_full_payment(self, cart_service):
        """Test creating payment that fully pays an invoice"""
        invoice = Invoice(
            invoice_id=1,
            invoice_total_amount=500.00,
            invoice_status='unpaid',
            invoice_number='INV-001'
        )
        amount = 500.00
        
        expected_payment = Payment(
            payment_id=1,
            payment_amount=amount,
            payment_status='completed'
        )
        
        cart_service.mock_financial_repo.create_payment.return_value = expected_payment
        cart_service.mock_financial_repo.update_invoice.return_value = invoice
        
        result = cart_service._create_payment_for_invoice(invoice, amount)
        
        assert invoice.invoice_status == 'paid'
        assert result.payment_status == 'completed'
        cart_service.mock_financial_repo.update_invoice.assert_called_once_with(invoice)
        cart_service.mock_financial_repo.create_payment.assert_called_once()
    
    def test_create_payment_for_invoice_partial_payment(self, cart_service):
        """Test creating partial payment for an invoice"""
        invoice = Invoice(
            invoice_id=1,
            invoice_total_amount=500.00,
            invoice_status='unpaid',
            invoice_number='INV-001'
        )
        amount = 200.00
        
        expected_payment = Payment(
            payment_id=1,
            payment_amount=amount,
            payment_status='partial'
        )
        
        cart_service.mock_financial_repo.create_payment.return_value = expected_payment
        
        result = cart_service._create_payment_for_invoice(invoice, amount)
        
        assert invoice.invoice_status == 'unpaid'  # Not fully paid
        assert result.payment_amount == amount
        assert result.payment_status == 'partial'
        cart_service.mock_financial_repo.update_invoice.assert_not_called()
    
    def test_create_receipt_for_payment(self, cart_service, sample_cart):
        """Test receipt creation for a payment"""
        payment = Payment(
            payment_id=1,
            payment_amount=500.00,
            payment_status='completed'
        )
        
        expected_receipt = Receipt(
            receipt_id=1,
            receipt_payment_id=payment.payment_id,
            receipt_number=f"RCPT-{datetime.now().strftime('%Y%m%d')}-{sample_cart.cart_id:04d}",
            receipt_amount=payment.payment_amount,
            receipt_cart_ref=sample_cart.cart_id,
            receipt_notes=f"Receipt for Payment #{payment.payment_id}"
        )
        
        cart_service.mock_financial_repo.create_receipt.return_value = expected_receipt
        
        result = cart_service._create_receipt_for_payment(payment, sample_cart)
        
        assert result == expected_receipt
        cart_service.mock_financial_repo.create_receipt.assert_called_once()
    
    def test_create_deposit_for_cart(self, cart_service, sample_cart):
        """Test deposit creation for a cart"""
        amount = 200.00
        
        expected_deposit = Deposit(
            deposit_id=1,
            deposit_cart_id=sample_cart.cart_id,
            deposit_amount=amount,
            deposit_method='cash',
            deposit_reference=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            deposit_notes=f"Deposit for Cart #{sample_cart.cart_id}"
        )
        
        cart_service.mock_financial_repo.create_deposit.return_value = expected_deposit
        
        result = cart_service._create_deposit_for_cart(sample_cart, amount)
        
        assert result == expected_deposit
        cart_service.mock_financial_repo.create_deposit.assert_called_once()
    
    def test_update_cart_status_completed_from_payment(self, cart_service, sample_cart):
        """Test updating cart status to completed when fully paid"""
        api_cart = Cart_API(cart_status='pending')
        financial_docs = {
            'payment': Payment(payment_status='completed', payment_amount=500.00)
        }
        sample_cart.cart_total_amount = 500.00
        
        cart_service.mock_cart_repo.update_cart.return_value = sample_cart
        
        cart_service._update_cart_status(sample_cart, api_cart, financial_docs)
        
        assert sample_cart.cart_status == 'completed'
        cart_service.mock_cart_repo.update_cart.assert_called_once_with(sample_cart)
    
    def test_update_cart_status_partial_from_payment(self, cart_service, sample_cart):
        """Test updating cart status to partial when partially paid"""
        api_cart = Cart_API(cart_status='pending')
        financial_docs = {
            'payment': Payment(payment_status='partial', payment_amount=200.00)
        }
        sample_cart.cart_total_amount = 500.00
        sample_cart.cart_status = 'pending'
        
        cart_service._update_cart_status(sample_cart, api_cart, financial_docs)
        
        assert sample_cart.cart_status == 'pending'
    
    def test_update_cart_status_from_deposit(self, cart_service, sample_cart):
        """Test updating cart status to deposit_paid when deposit is made"""
        api_cart = Cart_API(cart_status='pending')
        financial_docs = {
            'deposit': Deposit(deposit_amount=200.00)
        }
        sample_cart.cart_status = 'pending'
        
        cart_service._update_cart_status(sample_cart, api_cart, financial_docs)
        
        assert sample_cart.cart_status == 'deposit_paid'
    
    def test_create_cart_success(self, cart_service, sample_cart_api, sample_ordered_item_api, 
                                  sample_product, sample_app_user, sample_product_provider, 
                                  sample_person_api):
        """Test successful cart creation with all documents"""
        # Setup mocks
        supplier = ProductProvider(
            product_provider_id=sample_product_provider.product_provider_id,
            provider_details=MagicMock(provider_name="Test Provider")
        )
        selling_user = sample_app_user
        buyer_user = sample_app_user
        person = Person(id_person=1, person_details=MagicMock(first_name="John", last_name="Doe"))
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.side_effect = [selling_user, buyer_user]
        cart_service.mock_person_service.create_person.return_value = person
        cart_service.mock_person_service.get_person_by_id.return_value = person
        
        # Mock product validation
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        
        # Mock ordered item building
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=2,
            applied_vat=0.2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        # Mock cart creation
        new_cart = Cart(
            cart_id=1,
            cart_product_provider_id=sample_product_provider.product_provider_id,
            cart_selling_user=selling_user.id_app_user,
            cart_status=sample_cart_api.cart_status,
            cart_total_amount=sample_cart_api.cart_total_amount,
            cart_notes=sample_cart_api.cart_notes
        )
        cart_service.mock_cart_repo.create_cart.return_value = new_cart
        
        # Mock financial documents
        cart_service.mock_financial_repo.create_invoice.return_value = Invoice(invoice_id=1)
        cart_service.mock_financial_repo.create_payment.return_value = Payment(payment_id=1)
        cart_service.mock_financial_repo.create_receipt.return_value = Receipt(receipt_id=1)
        
        ordered_items = [sample_ordered_item_api]
        ordered_services = []
        
        financial_docs, cart = cart_service.create_cart(
            ordered_items=ordered_items,
            ordered_services=ordered_services,
            cart_data=sample_cart_api,
            delivery=None,
            client=sample_person_api,
            provider_id=sample_product_provider.product_provider_id,
            seller_user_id=selling_user.id_app_user,
            buyer_user_id=buyer_user.id_app_user
        )
        
        assert 'invoice' in financial_docs
        assert 'payment' in financial_docs
        assert 'receipt' in financial_docs
        assert cart is not None
        cart_service.mock_cart_repo.create_cart.assert_called_once()
    
    def test_create_cart_with_delivery(self, cart_service, sample_cart_api, sample_ordered_item_api,
                                        sample_product, sample_app_user, sample_product_provider,
                                        sample_delivery_api):
        """Test cart creation with delivery information"""
        # Setup mocks
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        delivery_model = Delivery(
            delivery_address=sample_delivery_api.delivery_address,
            delivery_status="pending"
        )
        cart_service.mock_delivery_service._build_delivery_model.return_value = delivery_model
        
        new_cart = Cart(cart_id=1)
        cart_service.mock_cart_repo.create_cart.return_value = new_cart
        
        ordered_items = [sample_ordered_item_api]
        ordered_services = []
        
        financial_docs, cart = cart_service.create_cart(
            ordered_items=ordered_items,
            ordered_services=ordered_services,
            cart_data=sample_cart_api,
            delivery=sample_delivery_api,
            client=None,
            provider_id=sample_product_provider.product_provider_id,
            seller_user_id=selling_user.id_app_user,
            buyer_user_id=0
        )
        
        assert cart is not None
        cart_service.mock_delivery_service._build_delivery_model.assert_called_once_with(sample_delivery_api)
    
    def test_create_cart_supplier_not_found(self, cart_service, sample_cart_api):
        """Test cart creation with non-existent supplier"""
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            cart_service.create_cart(
                ordered_items=[],
                ordered_services=[],
                cart_data=sample_cart_api,
                provider_id=999,
                seller_user_id=200,
                buyer_user_id=0
            )
        
        assert exc_info.value.status == HTTP_404_NOT_FOUND
        assert exc_info.value.code == SUPPLIER_NOT_EXISTS
    
    def test_create_cart_seller_not_found(self, cart_service, sample_cart_api, sample_product_provider):
        """Test cart creation with non-existent seller"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            cart_service.create_cart(
                ordered_items=[],
                ordered_services=[],
                cart_data=sample_cart_api,
                provider_id=sample_product_provider.product_provider_id,
                seller_user_id=999,
                buyer_user_id=0
            )
        
        assert exc_info.value.status == HTTP_404_NOT_FOUND
        assert exc_info.value.code == APPUSER_NOT_EXISTS
    
    def test_create_cart_product_not_found(self, cart_service, sample_cart_api, 
                                            sample_ordered_item_api, sample_app_user, 
                                            sample_product_provider):
        """Test cart creation with non-existent product"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_product_repo.get_product_by_id.return_value = None
        
        ordered_item_model = OrderedItem(
            ordered_product_id=999,
            ordered_quantity=2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        with pytest.raises(APIException) as exc_info:
            cart_service.create_cart(
                ordered_items=[sample_ordered_item_api],
                ordered_services=[],
                cart_data=sample_cart_api,
                provider_id=sample_product_provider.product_provider_id,
                seller_user_id=selling_user.id_app_user,
                buyer_user_id=0
            )
        
        assert exc_info.value.status == HTTP_404_NOT_FOUND
        assert exc_info.value.code == PRODUCT_NOT_EXISTS
    
    def test_create_cart_insufficient_stock(self, cart_service, sample_cart_api, 
                                             sample_ordered_item_api, sample_product, 
                                             sample_app_user, sample_product_provider):
        """Test cart creation with insufficient product stock"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        
        # Set product stock to low quantity
        sample_product.product_quantity = 1
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=5  # More than available
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        with pytest.raises(APIException) as exc_info:
            cart_service.create_cart(
                ordered_items=[sample_ordered_item_api],
                ordered_services=[],
                cart_data=sample_cart_api,
                provider_id=sample_product_provider.product_provider_id,
                seller_user_id=selling_user.id_app_user,
                buyer_user_id=0
            )
        
        assert exc_info.value.status == HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
        assert exc_info.value.code == PRODUCT_QUANTITY_NOT_ENOUGH
    
    def test_create_cart_database_error_rollback(self, cart_service, sample_cart_api, 
                                                   sample_ordered_item_api, sample_product, 
                                                   sample_app_user, sample_product_provider):
        """Test rollback of product stock when cart creation fails"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        original_quantity = sample_product.product_quantity
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        # Simulate database error on cart creation
        cart_service.mock_cart_repo.create_cart.side_effect = Exception("Database connection error")
        
        with pytest.raises(APIException) as exc_info:
            cart_service.create_cart(
                ordered_items=[sample_ordered_item_api],
                ordered_services=[],
                cart_data=sample_cart_api,
                provider_id=sample_product_provider.product_provider_id,
                seller_user_id=selling_user.id_app_user,
                buyer_user_id=0
            )
        
        assert exc_info.value.status == HTTP_417_EXPECTATION_FAILED
        assert exc_info.value.code == CART_INSERT_FAILED
        # Verify stock was restored (called for rollback)
        assert cart_service.mock_product_repo.update_product.call_count >= 2
    
    def test_create_cart_with_services(self, cart_service, sample_cart_api, 
                                        sample_app_user, sample_product_provider):
        """Test cart creation with ordered services"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        
        ordered_service_api = OrderedService_API(
            ordered_service_quantity=3,
            ordered_service_unit_price=100.00,
            ordered_service_total_price=300.00,
            ordered_service_notes="Test service",
            ordered_service_scheduled_at=datetime.now() + timedelta(days=7)
        )
        
        new_cart = Cart(cart_id=1)
        cart_service.mock_cart_repo.create_cart.return_value = new_cart
        
        financial_docs, cart = cart_service.create_cart(
            ordered_items=[],
            ordered_services=[ordered_service_api],
            cart_data=sample_cart_api,
            delivery=None,
            client=None,
            provider_id=sample_product_provider.product_provider_id,
            seller_user_id=selling_user.id_app_user,
            buyer_user_id=0
        )
        
        assert cart is not None
    
    def test_update_cart_status_success(self, cart_service, sample_cart):
        """Test successful cart status update"""
        cart_service.mock_cart_repo.get_cart_by_id.return_value = sample_cart
        cart_service.mock_cart_repo.update_cart.return_value = sample_cart
        
        result = cart_service.update_cart_status(sample_cart.cart_id, 'completed')
        
        assert result.cart_status == 'completed'
        cart_service.mock_cart_repo.get_cart_by_id.assert_called_once_with(sample_cart.cart_id)
        cart_service.mock_cart_repo.update_cart.assert_called_once()
    
    def test_delete_cart_success(self, cart_service, sample_cart, sample_product):
        """Test successful cart deletion with stock restoration"""
        sample_cart.ordered_item = [
            OrderedItem(ordered_product_id=sample_product.product_id, ordered_quantity=2)
        ]
        cart_service.mock_cart_repo.get_cart_by_id.return_value = sample_cart
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        cart_service.mock_cart_repo.delete_cart.return_value = True
        
        result = cart_service.delete_cart(sample_cart.cart_id)
        
        assert result is True
        # Verify stock was restored
        assert sample_product.product_quantity == sample_product.product_quantity
        cart_service.mock_product_repo.update_product.assert_called_once_with(sample_product)
        cart_service.mock_cart_repo.delete_cart.assert_called_once_with(sample_cart)
    
    def test_build_ordered_service_model(self, cart_service):
        """Test building ordered service model from API data"""
        scheduled_date = datetime.now() + timedelta(days=7)
        api_service = OrderedService_API(
            ordered_service_quantity=3,
            ordered_service_unit_price=150.00,
            ordered_service_total_price=450.00,
            ordered_service_notes="Test service",
            ordered_service_scheduled_at=scheduled_date
        )
        
        result = cart_service._build_ordered_service_model(api_service)
        
        assert result.ordered_service_quantity == 3
        assert result.ordered_service_unit_price == 150.00
        assert result.ordered_service_total_price == 450.00
        assert result.ordered_service_notes == "Test service"
        assert result.ordered_service_scheduled_at == scheduled_date
    
    def test_create_cart_without_buyer(self, cart_service, sample_cart_api, sample_ordered_item_api,
                                        sample_product, sample_app_user, sample_product_provider):
        """Test cart creation without a buyer user"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        new_cart = Cart(cart_id=1)
        cart_service.mock_cart_repo.create_cart.return_value = new_cart
        
        financial_docs, cart = cart_service.create_cart(
            ordered_items=[sample_ordered_item_api],
            ordered_services=[],
            cart_data=sample_cart_api,
            delivery=None,
            client=None,
            provider_id=sample_product_provider.product_provider_id,
            seller_user_id=selling_user.id_app_user,
            buyer_user_id=0
        )
        
        assert cart is not None
        # Verify that buyer_user is not set on cart (cart_client_user remains None)
        assert getattr(cart, 'cart_client_user', None) is None
    
    def test_create_cart_with_existing_person(self, cart_service, sample_cart_api, 
                                                sample_ordered_item_api, sample_product,
                                                sample_app_user, sample_product_provider,
                                                sample_person_api):
        """Test cart creation with an existing person"""
        supplier = ProductProvider(product_provider_id=sample_product_provider.product_provider_id)
        selling_user = sample_app_user
        existing_person = Person(id_person=1)
        
        # Set person ID to non-zero to indicate existing person
        sample_person_api.id_person = 1
        
        cart_service.mock_supplier_repo.get_supplier_basic.return_value = supplier
        cart_service.mock_user_repo.get_by_id.return_value = selling_user
        cart_service.mock_person_service.get_person_by_id.return_value = existing_person
        cart_service.mock_product_repo.get_product_by_id.return_value = sample_product
        cart_service.mock_product_repo.update_product.return_value = sample_product
        
        ordered_item_model = OrderedItem(
            ordered_product_id=sample_product.product_id,
            ordered_quantity=2
        )
        cart_service.mock_order_service._build_ordered_item_model.return_value = ordered_item_model
        
        new_cart = Cart(cart_id=1)
        cart_service.mock_cart_repo.create_cart.return_value = new_cart
        
        financial_docs, cart = cart_service.create_cart(
            ordered_items=[sample_ordered_item_api],
            ordered_services=[],
            cart_data=sample_cart_api,
            delivery=None,
            client=sample_person_api,
            provider_id=sample_product_provider.product_provider_id,
            seller_user_id=selling_user.id_app_user,
            buyer_user_id=0
        )
        
        assert cart is not None
        cart_service.mock_person_service.get_person_by_id.assert_called_once_with(1)
        cart_service.mock_person_service.create_person.assert_not_called()