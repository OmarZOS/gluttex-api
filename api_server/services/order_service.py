# services/order_service.py
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from fastapi import BackgroundTasks
from core.api_models import OrderedItem_API, PlacedOrder_API
from core.exception_handler import APIException
from core.messages import *
from core.models import PlacedOrder, OrderedItem, Product
from repositories.order_repository import OrderRepository, OrderItemRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from services.pricing_service import PricingService
from communication.publisher import send_to_product_subscribers

class OrderService:
    """Service for order-related business logic"""
    
    VALID_ORDER_STATUSES = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED']
    
    def __init__(self):
        self.order_repo = OrderRepository()
        self.order_item_repo = OrderItemRepository()
        self.product_repo = ProductRepository()
        self.user_repo = UserRepository()
        self.pricing_service = PricingService()
    
    def _build_ordered_item_model(self, api_item: OrderedItem_API) -> OrderedItem:
        """Build OrderedItem model from API data"""
        item = OrderedItem(
            ordered_product_id=api_item.ordered_product_id,
            ordered_quantity=api_item.ordered_quantity,
            applied_vat=api_item.applied_vat,
            unit_price=api_item.unit_price
        )
        if api_item.order_ref > 0:
            item.order_ref = api_item.order_ref
        return item
    
    def _validate_product_stock(self, product_id: int, requested_quantity: int) -> Product:
        """Validate product stock and return product"""
        product = self.product_repo.get_product_by_id(product_id)
        if not product:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PRODUCT_NOT_EXISTS,
                details=f"Product #{product_id} does not exist"
            )
        
        if product.product_quantity < requested_quantity:
            raise APIException(
                status=HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                code=PRODUCT_QUANTITY_NOT_ENOUGH,
                details=f"Not enough stock for product #{product_id}. Available: {product.product_quantity}, Requested: {requested_quantity}"
            )
        
        return product
    
    def _update_product_stock(self, product: Product, quantity: int, operation: str = 'decrease') -> None:
        """Update product stock (increase or decrease)"""
        if operation == 'decrease':
            product.product_quantity -= quantity
        else:
            product.product_quantity += quantity
        
        self.product_repo.update_product(product)
        
        # Notify subscribers about stock update
        try:
            send_to_product_subscribers(
                {'product_quantity': product.product_quantity},
                product.id_product
            )
        except Exception as e:
            # Log but don't fail the operation
            print(f"Failed to notify product subscribers: {e}")
    
    def _restore_order_items_stock(self, items: List[OrderedItem]) -> None:
        """Restore stock for all items in an order"""
        for item in items:
            product = self.product_repo.get_product_by_id(item.ordered_product_id)
            if product:
                self._update_product_stock(product, item.ordered_quantity, 'increase')
    
    def get_order_by_id(self, order_id: int, with_items: bool = True) -> PlacedOrder:
        """Get order by ID"""
        order = self.order_repo.get_order_by_id(order_id, with_items)
        if not order:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=ORDER_NOT_EXISTS,
                details=f"Order #{order_id} does not exist"
            )
        return order
    
    def get_user_orders(self, user_id: int, offset: int = 0, limit: int = 100) -> List[PlacedOrder]:
        """Get all orders for a user"""
        # Validate user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=APPUSER_NOT_EXISTS,
                details=f"User #{user_id} does not exist"
            )
        
        return self.order_repo.get_user_orders(user_id, offset, limit)
    
    def get_order_items(self, order_id: int) -> List[OrderedItem]:
        """Get all items for an order"""
        order = self.get_order_by_id(order_id, with_items=False)
        return self.order_repo.get_order_items(order_id)
    
    def get_orders_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Product]:
        """Get orders containing products from a specific provider"""
        return self.order_repo.get_orders_by_provider_products(provider_id, offset, limit)
    
    def create_order_item(self, api_item: OrderedItem_API) -> OrderedItem:
        """Create a single order item"""
        # Build item model
        item = self._build_ordered_item_model(api_item)
        
        # Validate product stock
        product = self._validate_product_stock(item.ordered_product_id, item.ordered_quantity)
        
        # Update product stock
        self._update_product_stock(product, item.ordered_quantity, 'decrease')
        
        # Create order item
        try:
            return self.order_item_repo.create(item)
        except Exception as e:
            # Rollback stock change if item creation fails
            self._update_product_stock(product, item.ordered_quantity, 'increase')
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORDER_ITEM_INSERT_FAILED,
                details=f"Failed to insert ordered item: {str(e)}"
            )
    
    def create_order(
        self,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API
    ) -> Tuple[List[int], PlacedOrder]:
        """Create a new order with multiple items"""
        
        # Validate user
        ordering_user = self.user_repo.get_by_id(order_data.ordering_user_id)
        if not ordering_user:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=APPUSER_NOT_EXISTS,
                details=f"User #{order_data.ordering_user_id} does not exist"
            )
        
        # Validate and process items
        ordered_items: List[OrderedItem] = []
        ordered_products: List[Product] = []
        order_total_price: float = 0
        
        for api_item in items:
            # Build item
            item = self._build_ordered_item_model(api_item)
            
            # Validate product stock
            product = self._validate_product_stock(item.ordered_product_id, item.ordered_quantity)
            
            # Update stock temporarily (will be committed with order)
            product.product_quantity -= item.ordered_quantity
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
            placed_order_state=order_data.placed_order_state or 'PENDING',
            payment_status=order_data.payment_status or 'PENDING',
            payment_method=order_data.payment_method,
            payment_ref=order_data.payment_ref
        )
        placed_order.ordered_item = ordered_items
        
        # Save order and update stock
        try:
            final_order = self.order_repo.create_order(placed_order)
            
            # Update product stock in database
            for product in ordered_products:
                self.product_repo.update_product(product)
                send_to_product_subscribers(
                    {'product_quantity': product.product_quantity},
                    product.id_product
                )
            
            return [p.product_quantity for p in ordered_products], final_order
            
        except Exception as e:
            # Rollback stock changes if order creation fails
            for product in ordered_products:
                product.product_quantity += 1  # Revert the temporary decrease
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORDER_INSERT_CONFLICT,
                details=f"Failed to create order: {str(e)}"
            )
    
    async def update_order(
        self,
        order_id: int,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API
    ) -> Dict[str, Any]:
        """Update an existing order"""
        
        # Validate order exists
        existing_order = await self.get_order_by_id(order_id, with_items=True)
        
        # Validate order status if being updated
        if order_data.placed_order_state:
            if order_data.placed_order_state.upper() not in self.VALID_ORDER_STATUSES:
                raise APIException(
                    status=HTTP_422_UNPROCESSABLE_ENTITY,
                    code=INVALID_ORDER_STATUS,
                    details=f"Invalid status '{order_data.placed_order_state}'. Allowed: {', '.join(self.VALID_ORDER_STATUSES)}"
                )
        
        # If items are being updated, restore old stock and create new items
        if items:
            # Restore stock from old items
            self._restore_order_items_stock(existing_order.ordered_item)
            
            # Delete old items
            self.order_item_repo.bulk_delete_by_order(order_id)
            
            # Create new items
            for item in items:
                item.order_ref = order_id
                await self.create_order_item(item)  # Note: make this async if needed
        
        # Update order fields
        update_fields = {
            'ordered_timestamp': order_data.ordered_timestamp,
            'order_discount': order_data.order_discount,
            'payment_status': order_data.payment_status,
            'payment_ref': order_data.payment_ref,
            'placed_order_state': order_data.placed_order_state,
            'payment_method': order_data.payment_method,
            'ordering_user_id': order_data.ordering_user_id,
            'placed_order_last_mod': datetime.now()
        }
        
        for field, value in update_fields.items():
            if value is not None and hasattr(existing_order, field):
                setattr(existing_order, field, value)
        
        # Recalculate total price if needed
        if items:
            new_total = self.pricing_service.calculate_order_total(
                existing_order.ordered_item,
                existing_order.order_discount or 0
            )
            existing_order.total_price = new_total
        
        # Save updated order
        try:
            updated_order = self.order_repo.update_order(existing_order)
            
            return {
                "status": "success",
                "message": f"Order #{order_id} updated successfully",
                "order_id": order_id,
                "updated_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORDER_UPDATE_FAILED,
                details=f"Failed to update order #{order_id}: {str(e)}"
            )
    
    def delete_order(self, order_id: int) -> bool:
        """Delete an order and restore product quantities"""
        
        # Get order with items
        order = self.get_order_by_id(order_id, with_items=True)
        
        # Restore product stock
        try:
            self._restore_order_items_stock(order.ordered_item)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=PRODUCT_QUANTITY_RESTORE_FAILED,
                details=f"Failed to restore product stock: {str(e)}"
            )
        
        # Delete order items
        self.order_item_repo.bulk_delete_by_order(order_id)
        
        # Delete order
        try:
            basic_order = self.order_repo.get_order_basic(order_id)
            if basic_order:
                return self.order_repo.delete_order(basic_order)
            return False
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=ORDER_DELETE_FAILED,
                details=f"Failed to delete order #{order_id}: {str(e)}"
            )
    
    def update_order_status(self, order_id: int, new_status: str) -> PlacedOrder:
        """Update only the order status"""
        
        if new_status.upper() not in self.VALID_ORDER_STATUSES:
            raise APIException(
                status=HTTP_422_UNPROCESSABLE_ENTITY,
                code=INVALID_ORDER_STATUS,
                details=f"Invalid status '{new_status}'. Allowed: {', '.join(self.VALID_ORDER_STATUSES)}"
            )
        
        order = self.get_order_by_id(order_id, with_items=False)
        order.placed_order_state = new_status.upper()
        order.placed_order_last_mod = datetime.now()
        
        return self.order_repo.update_order(order)
    
    def get_order_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get order statistics"""
        stats = self.order_repo.get_order_status_stats(user_id)
        
        return {
            "total_orders": sum(stats.values()),
            "status_breakdown": stats,
            "user_id": user_id
        }