# services/order_service.py
"""
Order service for managing orders, order items, and stock management.
Updated to use Finance and Inventory microservices.
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio

from repositories.financial_repository import FinancialRepository
from storage.wrappers.finance_client import FinanceServiceClient
from storage.wrappers.inventory_client import InventoryServiceClient
from core.models.api_models import OrderedItem_API, PlacedOrder_API
from core.exceptions.handler import UserNotFoundException
from core.exceptions.specific.order_exceptions import (
    OrderNotFoundException,
    OrderInsertFailedException,
    OrderUpdateFailedException,
    OrderDeleteFailedException,
    OrderItemInsertFailedException,
    OrderItemDeleteFailedException,
    InvalidOrderStatusException,
    OrderStatusTransitionException
)
from core.exceptions.specific.product_exceptions import (
    ProductNotFoundException,
    ProductQuantityNotEnoughException
)
from core.messages import *
from core.models.models import PlacedOrder, OrderedItem, Product, Invoice, Delivery
from repositories.order_repository import OrderRepository, OrderItemRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from repositories.delivery_repository import DeliveryRepository
from services.pricing_service import PricingService
from communication.publisher import send_to_product_subscribers
from core.models.finance_models import PaymentCreate, PaymentRefund, PaymentConfirm
from core.models.inventory_models import InventoryItem

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order-related business logic with microservice integration"""

    # Valid order statuses and allowed transitions
    VALID_ORDER_STATUSES = {'PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED'}
    
    # Allowed status transitions
    STATUS_TRANSITIONS = {
        'PENDING': {'PROCESSING', 'CANCELLED'},
        'PROCESSING': {'SHIPPED', 'CANCELLED'},
        'SHIPPED': {'DELIVERED', 'CANCELLED', 'REFUNDED'},
        'DELIVERED': {'REFUNDED'},
        'CANCELLED': set(),
        'REFUNDED': set()
    }
    
    DEFAULT_PAGINATION_LIMIT = 100
    MAX_PAGINATION_LIMIT = 500

    def __init__(self):
        self.order_repo = OrderRepository()
        self.order_item_repo = OrderItemRepository()
        self.product_repo = ProductRepository()
        self.user_repo = UserRepository()
        self.invoice_repo = FinancialRepository()
        self.delivery_repo = DeliveryRepository()
        self.pricing_service = PricingService()
        
        # Initialize microservice clients
        self.finance_client = FinanceServiceClient()
        self.inventory_client = InventoryServiceClient()
        
    
    # ==================== Order Creation Methods ====================
    
    async def create_order(
        self,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API,
        payment_method: str = 'card',
        user_id: int = None,
        delivery_data: Optional[Dict] = None
    ) -> Tuple[List[int], PlacedOrder, Dict]:
        """
        Create a new order with multiple items using microservices.
        
        Flow:
        1. Check inventory availability (SILO)
        2. Create business entities (OrderedItem, PlacedOrder, Invoice, Delivery)
        3. Reserve inventory (SILO)
        4. Confirm payment (Finance)
        5. Deduct inventory (SILO)
        """
        logger.info(f"Creating new order for user: {order_data.ordering_user_id}")
        
        # Validate user
        ordering_user = self.user_repo.get_by_id(order_data.ordering_user_id)
        if not ordering_user:
            raise UserNotFoundException(user_id=order_data.ordering_user_id)
        
        # Set user_id for payment if not provided
        if not user_id:
            user_id = order_data.ordering_user_id
        
        # Track created entities for rollback
        created_order = None
        created_invoice = None
        created_delivery = None
        created_items = []
        inventory_reserved = False
        payment_created = False
        
        try:
            # ==================== STEP 1: Check Inventory Availability ====================
            logger.info("Step 1: Checking inventory availability...")
            
            # Prepare inventory check items
            check_items = [
                {
                    "id": item.ordered_product_id,
                    "quantity": item.ordered_quantity
                }
                for item in items
            ]
            
            # Check and reserve in one operation (this is just a check)
            availability_response = await self.inventory_client.get_bulk_stock_status(
                product_ids=[item.ordered_product_id for item in items]
            )
            
            # Verify all items are available
            for item in items:
                product_id = item.ordered_product_id
                stock_status = availability_response.get(str(product_id), {})
                available_qty = stock_status.get('available_quantity', 0)
                
                if available_qty < item.ordered_quantity:
                    raise ProductQuantityNotEnoughException(
                        product_id=product_id,
                        requested=item.ordered_quantity,
                        available=available_qty
                    )
            
            logger.info("✅ Inventory availability check passed")
            
            # ==================== STEP 2: Create Business Entities ====================
            logger.info("Step 2: Creating business entities...")
            
            # Build ordered items and calculate total
            ordered_items: List[OrderedItem] = []
            order_total_price: float = 0
            
            for api_item in items:
                # Build item
                item = self._build_ordered_item_model(api_item)
                ordered_items.append(item)
                created_items.append(item)
                
                # Get product for price calculation
                product = self.product_repo.get_product_by_id(api_item.ordered_product_id)
                if product:
                    item.unit_price = float(product.product_price)
                    order_total_price += item.ordered_quantity * float(product.product_price) * (1 + item.applied_vat)
                else:
                    raise ProductNotFoundException(product_id=api_item.ordered_product_id)
            
            # Apply order discount
            if order_data.order_discount:
                order_total_price -= order_data.order_discount
            
            # Create PlacedOrder
            placed_order = PlacedOrder(
                ordering_user_id=ordering_user.id_app_user,
                order_discount=order_data.order_discount or 0,
                placed_order_last_mod=datetime.now(),
                total_price=max(0, order_total_price),
                placed_order_state=self._validate_order_status(order_data.placed_order_state or 'PENDING'),
            )
            placed_order.ordered_item = ordered_items
            
            # Save order
            created_order = self.order_repo.create_order(placed_order)
            logger.info(f"✅ Created order: {created_order.id_placed_order}")
            
            # Create Invoice
            invoice = Invoice(
                invoice_number=f"INV-{created_order.id_placed_order}-{datetime.now().strftime('%Y%m%d')}",
                invoice_total_amount=order_total_price,
                invoice_status='unpaid',
                invoice_issue_date=datetime.now().date(),
                invoice_due_date=datetime.now().date() + timedelta(days=30),
                invoice_notes=f"Order #{created_order.id_placed_order}",
                invoice_type='invoice',
                invoice_tax_applied=1
            )
            created_invoice = self.invoice_repo.create_invoice(invoice)
            logger.info(f"✅ Created invoice: {created_invoice.invoice_id}")
            
            # Create Delivery if data provided
            if delivery_data:
                delivery = Delivery(
                    delivery_order_ref=created_order.id_placed_order,
                    delivery_address=delivery_data.get('address'),
                    delivery_city=delivery_data.get('city'),
                    delivery_country=delivery_data.get('country', 'DZ'),
                    delivery_phone=delivery_data.get('phone'),
                    delivery_status='pending',
                    delivery_notes=delivery_data.get('notes')
                )
                created_delivery = self.delivery_repo.create(delivery)
                logger.info(f"✅ Created delivery: {created_delivery.id_delivery}")
            
            # ==================== STEP 3: Reserve Inventory (SILO) ====================
            logger.info("Step 3: Reserving inventory...")
            
            reserve_items = [
                {"id": item.ordered_product_id, "quantity": item.ordered_quantity}
                for item in items
            ]
            
            reserve_response = await self.inventory_client.reserve_inventory(
                items=reserve_items,
                item_type='ordered_item'
            )
            
            if not reserve_response.get('success', False):
                raise Exception(f"Inventory reservation failed: {reserve_response}")
            
            inventory_reserved = True
            logger.info(f"✅ Inventory reserved: {reserve_response.get('success_count', 0)} items")
            
            # ==================== STEP 4: Confirm Payment (Finance) ====================
            logger.info("Step 4: Confirming payment...")
            
            # Create payment
            payment_data = PaymentCreate(
                invoice_id=created_invoice.invoice_id,
                amount=order_total_price,
                payment_method=payment_method,
                user_id=user_id,
                notes=f"Order #{created_order.id_placed_order} payment",
                payment_type='payment'
            )
            
            payment_response = await self.finance_client.create_payment(payment_data)
            payment_created = True
            logger.info(f"✅ Payment created: {payment_response.id}")
            
            # Confirm payment with transaction details
            transaction_details = {
                'reference': f'ORD-{created_order.id_placed_order}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'order_id': created_order.id_placed_order,
                'invoice_id': created_invoice.invoice_id,
                'payment_method': payment_method,
                'notes': f'Payment for order #{created_order.id_placed_order}'
            }
            
            confirmed_payment = await self.finance_client.confirm_payment(
                payment_id=payment_response.id,
                transaction_details=transaction_details
            )
            
            # Update invoice status to paid
            created_invoice.invoice_status = 'paid'
            self.invoice_repo.update_invoice(created_invoice)
            
            logger.info(f"✅ Payment confirmed: {confirmed_payment.id} - Status: {confirmed_payment.status}")
            
            # ==================== STEP 5: Deduct Inventory (SILO) ====================
            logger.info("Step 5: Deducting inventory...")
            
            confirm_items = [
                {"id": item.ordered_product_id, "quantity": item.ordered_quantity}
                for item in items
            ]
            
            confirm_response = await self.inventory_client.confirm_inventory(
                items=confirm_items,
                item_type='ordered_item'
            )
            
            if not confirm_response.get('success', False):
                raise Exception(f"Inventory confirmation failed: {confirm_response}")
            
            logger.info(f"✅ Inventory deducted: {confirm_response.get('success_count', 0)} items")
            
            # ==================== SUCCESS ====================
            # Update order status to PROCESSING
            created_order.placed_order_state = 'PROCESSING'
            created_order.placed_order_last_mod = datetime.now()
            created_order = self.order_repo.update_order(created_order)
            
            result = {
                'order_id': created_order.id_placed_order,
                'invoice_id': created_invoice.invoice_id,
                'payment_id': confirmed_payment.id,
                'payment_status': confirmed_payment.status,
                'inventory_reserved': inventory_reserved,
                'inventory_deducted': True
            }
            
            logger.info(f"✅ Order {created_order.id_placed_order} created successfully!")
            return [p.ordered_quantity for p in created_items], created_order, result
            
        except Exception as e:
            logger.error(f"Order creation failed at step: {e}")
            
            # ==================== ROLLBACK LOGIC ====================
            await self._rollback_order_creation(
                order=created_order,
                invoice=created_invoice,
                delivery=created_delivery,
                items=created_items,
                inventory_reserved=inventory_reserved,
                payment_created=payment_created,
                payment_id=payment_response.id if 'payment_response' in locals() else None
            )
            
            raise
            
    async def _rollback_order_creation(
        self,
        order: Optional[PlacedOrder],
        invoice: Optional[Invoice],
        delivery: Optional[Delivery],
        items: List[OrderedItem],
        inventory_reserved: bool = False,
        payment_created: bool = False,
        payment_id: Optional[int] = None
    ):
        """
        Rollback order creation in case of failure.
        """
        logger.info(f"🔄 Rolling back order creation...")
        
        try:
            # 1. Release inventory if reserved
            if inventory_reserved and items:
                try:
                    release_items = [
                        {"id": item.ordered_product_id, "quantity": item.ordered_quantity}
                        for item in items
                    ]
                    await self.inventory_client.release_inventory(
                        items=release_items,
                        item_type='ordered_item'
                    )
                    logger.info("✅ Inventory released")
                except Exception as e:
                    logger.error(f"Failed to release inventory: {e}")
            
            # 2. Refund payment if created
            if payment_created and payment_id:
                try:
                    refund_data = PaymentRefund(
                        amount=order.total_price if order else 0,
                        reason=f'Order creation failed - Rollback'
                    )
                    await self.finance_client.refund_payment(payment_id, refund_data)
                    logger.info("✅ Payment refunded")
                except Exception as e:
                    logger.error(f"Failed to refund payment: {e}")
            
            # 3. Delete delivery if created
            if delivery:
                try:
                    self.delivery_repo.delete(delivery.id_delivery)
                    logger.info("✅ Delivery deleted")
                except Exception as e:
                    logger.error(f"Failed to delete delivery: {e}")
            
            # 4. Delete invoice if created
            if invoice:
                try:
                    self.invoice_repo.delete_invoice(invoice.invoice_id)
                    logger.info("✅ Invoice deleted")
                except Exception as e:
                    logger.error(f"Failed to delete invoice: {e}")
            
            # 5. Delete order if created
            if order:
                try:
                    self.order_repo.delete_order(order)
                    logger.info("✅ Order deleted")
                except Exception as e:
                    logger.error(f"Failed to delete order: {e}")
            
            logger.info("✅ Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    def update_order_status(self, order_id: int, new_status: str) -> PlacedOrder:
        """Update only the order status (no stock changes needed)"""
        validated_status = self._validate_order_status(new_status)
        order = self.get_order_by_id(order_id, with_items=False)
        self._validate_status_transition(order.placed_order_state, validated_status)
        
        order.placed_order_state = validated_status
        order.placed_order_last_mod = datetime.now()
        
        return self.order_repo.update_order(order)
    
    def delete_order(self, order_id: int) -> bool:
        """
        Delete an order and restore product quantities.
        Uses microservices for inventory restoration.
        """
        logger.info(f"Deleting order with ID: {order_id}")
        
        # Get order with items
        order = self.get_order_by_id(order_id, with_items=True)
        
        try:
            # Release inventory using SILO
            release_items = [
                {"id": item.ordered_product_id, "quantity": item.ordered_quantity}
                for item in order.ordered_item
            ]
            
            # Async call to release inventory
            asyncio.create_task(
                self.inventory_client.release_inventory(
                    items=release_items,
                    item_type='ordered_item'
                )
            )
            
            # Delete order items and order
            self.order_item_repo.bulk_delete_by_order(order_id)
            basic_order = self.order_repo.get_order_basic(order_id)
            if basic_order:
                result = self.order_repo.delete_order(basic_order)
                logger.info(f"Order {order_id} deleted successfully")
                return result
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete order {order_id}: {e}")
            raise OrderDeleteFailedException(order_id=order_id, error=str(e))
    
    # ==================== Private Helper Methods ====================
    
    def _build_ordered_item_model(self, api_item: OrderedItem_API) -> OrderedItem:
        """Build OrderedItem model from API data."""
        item = OrderedItem(
            ordered_product_id=api_item.ordered_product_id,
            ordered_quantity=api_item.ordered_quantity,
            applied_vat=api_item.applied_vat,
            unit_price=api_item.unit_price
        )
        if api_item.order_ref and api_item.order_ref > 0:
            item.order_ref = api_item.order_ref
        return item
    
    def _validate_order_status(self, status: str) -> str:
        """Validate and normalize order status."""
        if not status:
            return 'PENDING'
        
        normalized = status.upper()
        if normalized not in self.VALID_ORDER_STATUSES:
            logger.warning(f"Invalid order status: {status}")
            raise InvalidOrderStatusException(
                status=status,
                valid_statuses=list(self.VALID_ORDER_STATUSES)
            )
        
        return normalized
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> None:
        """Validate status transition."""
        if new_status == current_status:
            return
        
        allowed_transitions = self.STATUS_TRANSITIONS.get(current_status, set())
        
        if new_status not in allowed_transitions:
            logger.warning(f"Invalid status transition from {current_status} to {new_status}")
            raise OrderStatusTransitionException(
                current_status=current_status,
                new_status=new_status,
                allowed_transitions=list(allowed_transitions)
            )
    
    def get_order_by_id(self, order_id: int, with_items: bool = True) -> PlacedOrder:
        """Get order by ID."""
        if with_items:
            order = self.order_repo.get_order_by_id(order_id)
        else:
            order = self.order_repo.get_order_basic(order_id)
        
        if not order:
            raise OrderNotFoundException(order_id=order_id)
        
        return order