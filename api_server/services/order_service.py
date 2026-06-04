# services/order_service.py
"""
Order service for managing orders, order items, and stock management.
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import logging

from services.helpers.stock_manager import StockManager, StockTransaction
from core.api_models import OrderedItem_API, PlacedOrder_API
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
from core.models import PlacedOrder, OrderedItem, Product
from repositories.order_repository import OrderRepository, OrderItemRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from services.pricing_service import PricingService
from communication.publisher import send_to_product_subscribers

logger = logging.getLogger(__name__)


# services/order_service.py (refactored)

class OrderService:
    """Service for order-related business logic"""
    

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
        self.pricing_service = PricingService()
        
        # Use StockManager for all stock operations
        self.stock_manager = StockManager(self.product_repo)
    
    # ==================== Order Creation Methods ====================
    
    async def create_order(
        self,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API
    ) -> Tuple[List[int], PlacedOrder]:
        """
        Create a new order with multiple items.
        Uses StockManager for atomic stock operations.
        """
        logger.info(f"Creating new order for user: {order_data.ordering_user_id}")
        
        # Validate user
        ordering_user = self.user_repo.get_by_id(order_data.ordering_user_id)
        if not ordering_user:
            raise UserNotFoundException(user_id=order_data.ordering_user_id)
        
        # Start a stock transaction
        with StockTransaction(self.stock_manager) as tx:
            # Build items and validate stock
            ordered_items: List[OrderedItem] = []
            ordered_products: List[Product] = []
            order_total_price: float = 0
            
            for api_item in items:
                # Build item
                item = self._build_ordered_item_model(api_item)
                
                # Validate and decrease stock using StockManager
                product = self.stock_manager.validate_product_stock(
                    item.ordered_product_id, 
                    item.ordered_quantity
                )
                self.stock_manager.decrease_stock(product, item.ordered_quantity)
                
                ordered_items.append(item)
                ordered_products.append(product)
                
                # Calculate price contribution
                order_total_price += item.ordered_quantity * float(product.product_price) * (1 + item.applied_vat)
            
            # Apply order discount
            if order_data.order_discount:
                order_total_price -= order_data.order_discount
            
            # Create order object
            placed_order = PlacedOrder(
                ordering_user_id=ordering_user.id_app_user,
                order_discount=order_data.order_discount or 0,
                placed_order_last_mod=datetime.now(),
                total_price=max(0, order_total_price),
                placed_order_state=self._validate_order_status(order_data.placed_order_state or 'PENDING'),
            )
            placed_order.ordered_item = ordered_items
            
            # Save order
            try:
                final_order = self.order_repo.create_order(placed_order)
                
                # All stock operations are automatically committed when exiting the context
                logger.info(f"Order created successfully with ID: {final_order.id_placed_order}")
                return [p.product_quantity for p in ordered_products], final_order
                
            except Exception as e:
                # StockManager will auto-rollback due to exception in context
                logger.error(f"Failed to create order: {e}")
                raise OrderInsertFailedException(
                    error=str(e),
                    user_id=order_data.ordering_user_id
                )
    
    def update_order_status(self, order_id: int, new_status: str) -> PlacedOrder:
        """Update only the order status (no stock changes needed)"""
        # No stock operations here, so no StockManager needed
        validated_status = self._validate_order_status(new_status)
        order = self.get_order_by_id(order_id, with_items=False)
        self._validate_status_transition(order.placed_order_state, validated_status)
        
        order.placed_order_state = validated_status
        order.placed_order_last_mod = datetime.now()
        
        return self.order_repo.update_order(order)
    
    def delete_order(self, order_id: int) -> bool:
        """
        Delete an order and restore product quantities.
        Uses StockManager for atomic stock restoration.
        """
        logger.info(f"Deleting order with ID: {order_id}")
        
        # Get order with items
        order = self.get_order_by_id(order_id, with_items=True)
        
        # Use StockManager to restore stock
        with StockTransaction(self.stock_manager) as tx:
            for item in order.ordered_item:
                product = self.product_repo.get_product_by_id(item.ordered_product_id)
                if product:
                    self.stock_manager.increase_stock(product, item.ordered_quantity)
            
            # Delete order items and order
            try:
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
        """
        Build OrderedItem model from API data.
        
        Args:
            api_item: API order item data
            
        Returns:
            OrderedItem model instance
        """
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
        """
        Validate and normalize order status.
        
        Args:
            status: Status to validate
            
        Returns:
            Normalized status string
            
        Raises:
            InvalidOrderStatusException: If status is invalid
        """
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
        """
        Validate status transition.
        
        Args:
            current_status: Current order status
            new_status: New order status
            
        Raises:
            OrderStatusTransitionException: If transition not allowed
        """
        if new_status == current_status:
            return
        
        allowed_transitions = self.STATUS_TRANSITIONS.get(current_status, set())
        
        if new_status not in allowed_transitions:
            logger.warning(
                f"Invalid status transition from {current_status} to {new_status}"
            )
            raise OrderStatusTransitionException(
                current_status=current_status,
                new_status=new_status,
                allowed_transitions=list(allowed_transitions)
            )
    
    def _validate_pagination_params(self, offset: int, limit: int) -> Tuple[int, int]:
        """
        Validate and normalize pagination parameters.
        
        Args:
            offset: Pagination offset
            limit: Maximum number of records
            
        Returns:
            Tuple of (normalized_offset, normalized_limit)
        """
        offset = max(0, offset)
        limit = min(self.MAX_PAGINATION_LIMIT, max(1, limit))
        return offset, limit
    


    # Remove these methods as they're now in StockManager:
    # - _validate_product_stock
    # - _update_product_stock
    # - _restore_order_items_stock
    # - _notify_product_subscribers