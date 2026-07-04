# services/order_service.py - Updated with correct inventory flow

"""
Order service for managing orders, order items, and stock management.
Updated to use Finance and Inventory microservices.
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import asyncio

from services.location_service import LocationService
from repositories.financial_repository import FinancialRepository
from storage.wrappers.finance_client import FinanceServiceClient
from storage.wrappers.inventory_client import InventoryServiceClient
from core.models.api_models import Delivery_Info_API, OrderedItem_API, PlacedOrder_API
from core.exceptions.handler import UserNotFoundException
from core.exceptions.specific.order_exceptions import (
    OrderNotFoundException,
    OrderDeleteFailedException,
    OrderInsertFailedException,
    OrderUpdateFailedException,
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
        self.location_service = LocationService()


        self.pricing_service = PricingService()
        
        # Initialize microservice clients
        self.finance_client = FinanceServiceClient()
        self.inventory_client = InventoryServiceClient()
        
    
    def _parse_inventory_response(self, response: Dict) -> Dict:
        """
        Parse inventory response to extract stock status by product ID.
        Handles different response formats from the inventory service.
        """
        if not response:
            return {}
        
        result = {}
        
        # Format 1: {"product_id": {"available_quantity": 10, "reserved_quantity": 2, ...}}
        if all(isinstance(v, dict) for v in response.values()):
            return response
        
        # Format 2: {"items": [{"product_id": 1, "available_quantity": 10, ...}]}
        if 'items' in response and isinstance(response['items'], list):
            for item in response['items']:
                product_id = item.get('product_id')
                if product_id:
                    result[str(product_id)] = item
            return result
        
        # Format 3: {"data": [{"product_id": 1, "available_quantity": 10, ...}]}
        if 'data' in response and isinstance(response['data'], list):
            for item in response['data']:
                product_id = item.get('product_id')
                if product_id:
                    result[str(product_id)] = item
            return result
        
        # Format 4: {"results": [{"product_id": 1, "available_quantity": 10, ...}]}
        if 'results' in response and isinstance(response['results'], list):
            for item in response['results']:
                product_id = item.get('product_id')
                if product_id:
                    result[str(product_id)] = item
            return result
        
        # Format 5: Direct mapping with integer keys (convert to string)
        for key, value in response.items():
            try:
                int(key)
                result[str(key)] = value
            except (ValueError, TypeError):
                pass
        
        return result
    
    # ==================== Order Creation Methods ====================
    
    async def create_order(
        self,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API,
        payment_method: str = 'card',
        user_id: int = None,
        delivery_data: Optional[Delivery_Info_API] = None
    ) -> Tuple[List[int], PlacedOrder, Dict]:
        """
        Create a new order with multiple items using microservices.
        
        Flow:
        1. Check inventory availability (SILO) - using product IDs
        2. Create business entities (OrderedItem, PlacedOrder, Invoice, Delivery)
        3. Reserve inventory (SILO) - using ordered item IDs
        4. Confirm payment (Finance)
        5. Confirm/deduct inventory (SILO) - using ordered item IDs
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
        payment_response = None
        
        try:
            # ==================== STEP 1: Check Inventory Availability ====================
            logger.info("Step 1: Checking inventory availability...")
            
            # Prepare product IDs for bulk check
            product_ids = [item.ordered_product_id for item in items]
            
            # Get bulk stock status from inventory service
            availability_response = await self.inventory_client.get_bulk_stock_status(
                product_ids=product_ids
            )
            
            # Parse the response to get stock by product ID
            stock_by_product = self._parse_inventory_response(availability_response)
            logger.info(f"Stock data: {stock_by_product}")
            
            # Verify all items are available
            for item in items:
                product_id = item.ordered_product_id
                stock_status = stock_by_product.get(str(product_id), {})
                available_qty = stock_status.get('available_quantity', 0)
                
                logger.info(f"Product {product_id}: available={available_qty}, requested={item.ordered_quantity}")
                
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
            
            delivery_provider_ids = set()


            for api_item in items:
                # Get product for price calculation
                product = self.product_repo.get_product_by_id(api_item.ordered_product_id)
                if not product:
                    raise ProductNotFoundException(product_id=api_item.ordered_product_id)
                delivery_provider_ids.add(product.product_provider_id)
                # Build item (without saving yet)
                item = self._build_ordered_item_model(api_item)
                item.unit_price = float(product.product_price)
                ordered_items.append(item)
                
                # Calculate total
                order_total_price += item.ordered_quantity * float(product.product_price) * (1 + item.applied_vat)
            
            # Apply order discount
            if order_data.order_discount:
                order_total_price -= order_data.order_discount
            
            # Create PlacedOrder (without items first)
            order_total_price = round(max(0, order_total_price), 2)
            placed_order = PlacedOrder(
                ordering_user_id=ordering_user.id_app_user,
                order_discount=order_data.order_discount or 0,
                placed_order_last_mod=datetime.now(),
                total_price=max(0, order_total_price),
                placed_order_state=self._validate_order_status(order_data.placed_order_state or 'PENDING'),
            )
            placed_order.ordered_item = ordered_items
            
            # Save order to get ID
            created_order = self.order_repo.create_order(placed_order)
            logger.info(f"✅ Created order: {created_order.id_placed_order}")
            
            # Now create OrderedItems with the order reference
            for item in ordered_items:
                item.order_ref = created_order.id_placed_order
                saved_item = self.order_repo.create_order_item(item)
                created_items.append(saved_item)
                logger.info(f"✅ Created order item: {saved_item.id_ordered_item} for product {saved_item.ordered_product_id}")
            
            deliveries = []
            # Create Delivery if data provided
            for provider_id in delivery_provider_ids:
                delivery_address_id =  None
                if delivery_data:
                    if delivery_data.destination_address:
                        if delivery_data.destination_address.id_address>0:
                            delivery_address_id = delivery_data.destination_address.id_address
                        else:
                            # Create new address in the system (assuming a method exists)
                            delivery_address = self.location_service.create_address_from_location(delivery_data.destination_address)
                            delivery_address_id = delivery_address.id_address

                delivery = Delivery(
                    # delivery_invoice_ref=created_invoice.invoice_id,
                    delivery_source_type='placed_order',
                    delivery_address_id = delivery_address_id if delivery_address_id else None,
                    delivery_source_id=created_order.id_placed_order,
                    delivery_provider_id=provider_id,
                    delivery_fee = delivery_data.delivery_fee if delivery_data else 0.0,
                )

                order_total_price += delivery_data.delivery_fee if delivery_data else 0.0
                deliveries.append(delivery)

                # created_delivery = self.delivery_repo.create(delivery)
                # logger.info(f"✅ Created delivery: {created_delivery.id_delivery}")
            
            # Create Invoice
            invoice = Invoice(
                invoice_number=f"INV-{created_order.id_placed_order}-{datetime.now().strftime('%Y%m%d')}",
                invoice_total_amount=order_total_price,
                invoice_status='unpaid',
                invoice_issue_date=datetime.now().date(),
                invoice_due_date=datetime.now().date() + timedelta(days=30),
                invoice_notes=f"Order #{created_order.id_placed_order}",
                invoice_type='invoice',
                invoice_tax_applied=19,
                delivery = deliveries
            )
            created_invoice = self.invoice_repo.create_invoice(invoice)
            logger.info(f"✅ Created invoice: {created_invoice.invoice_id}")


            # ==================== STEP 3: Reserve Inventory (SILO) ====================
            logger.info("Step 3: Reserving inventory...")
            
            # Prepare items for reservation using ordered item IDs
            reserve_items = [
                {
                    "id": item.id_ordered_item,  # Use the ordered item ID
                    "quantity": item.ordered_quantity,
                    "product_id": item.ordered_product_id  # Include product_id for reference
                }
                for item in created_items
            ]
            
            reserve_response = await self.inventory_client.reserve_inventory(
                items=reserve_items,
                item_type='ordered_item'
            )
            
            # Check if reservation was successful
            if isinstance(reserve_response, dict):
                if not reserve_response.get('success', True):
                    raise Exception(f"Inventory reservation failed: {reserve_response}")
                success_count = reserve_response.get('success_count', len(created_items))
                if success_count == 0:
                    raise Exception("Inventory reservation failed: no items reserved")
            else:
                # If response is not a dict, assume success if no exception was raised
                pass
            
            inventory_reserved = True
            logger.info("✅ Inventory reserved successfully")
            
            # ==================== STEP 4: Create and Confirm Payment (Finance) ====================
            logger.info("Step 4: Creating and confirming payment...")
            
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
            
            # ==================== STEP 5: Confirm/Deduct Inventory (SILO) ====================
            logger.info("Step 5: Confirming/deducting inventory...")
            
            # Prepare items for confirmation using ordered item IDs
            confirm_items = [
                {
                    "id": item.id_ordered_item,  # Use the ordered item ID
                    "quantity": item.ordered_quantity,
                    "product_id": item.ordered_product_id  # Include product_id for reference
                }
                for item in created_items
            ]
            
            confirm_response = await self.inventory_client.confirm_inventory(
                items=confirm_items,
                item_type='ordered_item'
            )
            
            # Check if confirmation was successful
            if isinstance(confirm_response, dict):
                if not confirm_response.get('success', True):
                    raise Exception(f"Inventory confirmation failed: {confirm_response}")
            else:
                # If response is not a dict, assume success if no exception was raised
                pass
            
            logger.info("✅ Inventory deducted successfully")
            
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
                payment_id=payment_response.id if payment_response else None
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
            # 1. Release inventory if reserved (using ordered item IDs)
            if inventory_reserved and items:
                try:
                    release_items = [
                        {
                            "id": item.id_ordered_item,  # Use the ordered item ID
                            "quantity": item.ordered_quantity,
                            "product_id": item.ordered_product_id
                        }
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
                    self.delivery_repo.delete(delivery)
                    logger.info("✅ Delivery deleted")
                except Exception as e:
                    logger.error(f"Failed to delete delivery: {e}")
            
            # 4. Delete invoice if created
            if invoice:
                try:
                    self.invoice_repo.delete_invoice(invoice)
                    logger.info("✅ Invoice deleted")
                except Exception as e:
                    logger.error(f"Failed to delete invoice: {e}")
            
            # 5. Delete order items and order
            if items:
                try:
                    for item in items:
                        self.order_repo.delete_order_item(item)
                    logger.info("✅ Order items deleted")
                except Exception as e:
                    logger.error(f"Failed to delete order items: {e}")
            
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
            # Release inventory using SILO (using ordered item IDs)
            release_items = [
                {
                    "id": item.id_ordered_item,  # Use the ordered item ID
                    "quantity": item.ordered_quantity,
                    "product_id": item.ordered_product_id
                }
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
    
    def get_user_orders(self, user_id: int, offset: int = 0, limit: int = 100):
        """Get orders for a specific user."""
        return self.order_repo.get_orders_by_user(user_id, offset, limit)
    
    def get_order_items(self, order_id: int) -> List[OrderedItem]:
        """Get items for an order."""
        return self.order_item_repo.get_items_by_order(order_id)
    
    def update_order(self, order_id: int, items: List[OrderedItem_API], order_data: PlacedOrder_API) -> Dict:
        """Update an existing order."""
        logger.info(f"Updating order {order_id}")
        
        # Get existing order
        existing_order = self.get_order_by_id(order_id, with_items=True)
        
        # Update order details
        if order_data.placed_order_state:
            validated_status = self._validate_order_status(order_data.placed_order_state)
            self._validate_status_transition(existing_order.placed_order_state, validated_status)
            existing_order.placed_order_state = validated_status
        
        if order_data.order_discount is not None:
            existing_order.order_discount = order_data.order_discount
        
        existing_order.placed_order_last_mod = datetime.now()
        
        # Update order
        updated_order = self.order_repo.update_order(existing_order)
        
        # Update items if provided
        if items:
            # Delete existing items
            self.order_item_repo.bulk_delete_by_order(order_id)
            
            # Create new items
            new_items = []
            for api_item in items:
                item = self._build_ordered_item_model(api_item)
                item.order_ref = order_id
                new_items.append(item)
            
            self.order_item_repo.bulk_create(new_items)
        
        return {
            "order": updated_order,
            "items_updated": len(items) if items else 0
        }