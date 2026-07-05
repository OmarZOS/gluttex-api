# services/cart_service.py - Complete fixed version

"""
Service for cart-related business logic including cart creation,
financial document management, and stock handling using Inventory microservice.
"""

import logging
import random
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from decimal import Decimal

from repositories.order_repository import OrderRepository
from repositories.financial_repository import FinancialRepository
from repositories.cart_repository import CartRepository, ServiceRepository
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository
from repositories.supplier_repository import SupplierRepository

from services.person_service import PersonService
from services.order_service import OrderService
from services.delivery_service import DeliveryService
from services.pricing_service import PricingService

from storage.wrappers.inventory_client import InventoryServiceClient
from storage.wrappers.finance_client import FinanceServiceClient

from core.models.api_models import (
    Cart_API, OrderedItem_API, OrderedService_API, Delivery_API,
    Person_API, Payment_API
)
from core.models.models import Cart, Delivery, OrderedItem, OrderedService, Product, Invoice, Payment, ProductConsumption, ProvidedService

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
from core.exceptions.handler import (
    ProductNotFoundException,
    InsufficientStockException,
    ServiceNotFoundException
)
from core.exceptions.specific.product_exceptions import ProductQuantityNotEnoughException

logger = logging.getLogger(__name__)


class CartService:
    """Service for cart-related business logic with microservice integration"""

    def __init__(self):
        self.cart_repo = CartRepository()
        self.financial_repo = FinancialRepository()
        self.product_repo = ProductRepository()
        self.user_repo = UserRepository()
        self.supplier_repo = SupplierRepository()
        self.service_repo = ServiceRepository()
        self.order_service = OrderService()
        self.invoice_repo = FinancialRepository()
        self.delivery_service = DeliveryService()
        self.person_service = PersonService()
        self.pricing_service = PricingService()

        self.order_repo = OrderRepository()
        
        # Initialize microservice clients
        self.inventory_client = InventoryServiceClient()
        self.finance_client = FinanceServiceClient()

    def _safe_float(self, value) -> float:
        """Safely convert any value to float, handling Decimal and other types."""
        if value is None:
            return 0.0
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        if hasattr(value, '__float__'):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        return 0.0

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
        
        # Format 4: Direct mapping with integer keys
        for key, value in response.items():
            try:
                int(key)
                result[str(key)] = value
            except (ValueError, TypeError):
                pass
        
        return result

    # ==================== Cart Retrieval Methods ====================
    
    def get_cart_by_id(self, cart_id: int, eager_load: bool = True) -> Cart:
        """Get cart by ID with relationships"""
        cart = self.cart_repo.get_cart_by_id(cart_id, eager_load=eager_load)
        if not cart:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise CartNotFoundException(cart_id=cart_id)
        
        # Force load relationships to avoid session issues
        try:
            if hasattr(cart, 'ordered_item') and cart.ordered_item:
                for item in cart.ordered_item:
                    _ = item.id_ordered_item
                    _ = item.ordered_product_id
            if hasattr(cart, 'ordered_service') and cart.ordered_service:
                for service in cart.ordered_service:
                    _ = service.ordered_service_id
        except Exception as e:
            logger.warning(f"Error loading cart relationships: {e}")
            # Re-fetch with eager loading
            cart = self.cart_repo.get_cart_by_id(cart_id, eager_load=True)
            if not cart:
                raise CartNotFoundException(cart_id=cart_id)
        
        logger.debug(f"Retrieved cart {cart_id}")
        return cart
    
    def get_carts_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by provider ID"""
        return self.cart_repo.get_carts_by_provider(provider_id, offset, limit)
    
    def get_carts_by_seller(self, seller_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by seller ID"""
        return self.cart_repo.get_carts_by_seller(seller_id, offset, limit)
    
    def get_carts_by_buyer(self, buyer_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        """Get carts by buyer ID"""
        return self.cart_repo.get_carts_by_buyer(buyer_id, offset, limit)

    def list_carts(self, 
                provider_id: int = 0,
                seller_id: int = 0,
                buyer_id: int = 0,
                status: str = None,
                offset: int = 0, 
                limit: int = 100) -> List[Cart]:
        """Get carts by buyer ID"""
        return self.cart_repo.list_carts(provider_id, seller_id, buyer_id, status, offset, limit)

    def get_cart_summary(self, cart_id: int) -> Dict[str, Any]:
        """Get cart summary with totals"""
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        
        subtotal = 0.0
        item_count = 0
        service_count = 0
        
        # Calculate product totals
        if cart.ordered_item:
            for item in cart.ordered_item:
                subtotal += self._safe_float(item.ordered_quantity) * self._safe_float(item.unit_price)
                item_count += 1
        
        # Calculate service totals
        if cart.ordered_service:
            for service in cart.ordered_service:
                subtotal += self._safe_float(service.ordered_service_total_price)
                service_count += 1
        
        return {
            'cart_id': cart_id,
            'subtotal': round(subtotal, 2),
            'total': round(self._safe_float(cart.cart_total_amount or subtotal), 2),
            'item_count': item_count,
            'service_count': service_count,
            'status': cart.cart_status,
            'created_at': cart.cart_created_at
        }

    def get_cart_items(self, cart_id: int) -> List[Dict[str, Any]]:
        """Get all items in a cart with product details"""
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        
        items = []
        if cart.ordered_item:
            for item in cart.ordered_item:
                product = self.product_repo.get_product_by_id(item.ordered_product_id)
                items.append({
                    'id': item.id_ordered_item,
                    'product_id': item.ordered_product_id,
                    'product_name': product.product_name if product else 'Unknown',
                    'quantity': self._safe_float(item.ordered_quantity),
                    'unit_price': self._safe_float(item.unit_price),
                    'total_price': self._safe_float(item.ordered_quantity) * self._safe_float(item.unit_price),
                    'applied_vat': self._safe_float(item.applied_vat),
                    'product_discount': self._safe_float(item.product_discount or 0)
                })
        
        return items

    def get_cart_services(self, cart_id: int) -> List[Dict[str, Any]]:
        """Get all services in a cart with details"""
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        
        services = []
        if cart.ordered_service:
            for service in cart.ordered_service:
                service_obj = self.service_repo.get_service_by_id(service.ordered_service_service_id)
                services.append({
                    'id': service.ordered_service_id,
                    'service_id': service.ordered_service_service_id,
                    'service_name': service_obj.provided_service_name if service_obj else 'Unknown',
                    'quantity': self._safe_float(service.ordered_service_quantity),
                    'unit_price': self._safe_float(service.ordered_service_unit_price),
                    'total_price': self._safe_float(service.ordered_service_total_price),
                    'scheduled_at': service.ordered_service_scheduled_at,
                    'notes': service.ordered_service_notes
                })
        
        return services

    # ==================== Cart Creation ====================
    async def create_cart(
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
        Create a new cart with inventory validation and resource management.
        """
        logger.info(f"Creating cart for provider {provider_id}, seller {seller_user_id}")
        
        # Validate cart has content
        if not ordered_items and not ordered_services:
            raise CartCreationFailedException(
                error="Cart must have at least one item or service",
                provider_id=provider_id,
                seller_id=seller_user_id
            )
        
        # ==================== STEP 1: Validate Entities ====================
        logger.info("Step 1: Validating entities...")
        await self._validate_entities(provider_id, seller_user_id, buyer_user_id)
        
        # ==================== STEP 2: Load Products and Services ====================
        logger.info("Step 2: Loading products and services...")
        products, services = await self._load_products_and_services(
            ordered_items, ordered_services
        )
        
        # ==================== STEP 3: Build Reservation Plan ====================
        logger.info("Step 3: Building reservation plan...")
        reservation_plan, item_details = await self._build_reservation_plan(
            ordered_items, ordered_services, products, services
        )
        
        # ==================== STEP 4: Validate Inventory Availability ====================
        logger.info("Step 4: Validating inventory availability...")
        await self._validate_inventory_availability(reservation_plan)
        
        # ==================== STEP 5: Build Cart ====================
        logger.info("Step 5: Building cart...")
        cart, total_price, person_obj = await self._build_cart(
            ordered_items=ordered_items,
            ordered_services=ordered_services,
            cart_data=cart_data,
            products=products,
            services=services,
            item_details=item_details,
            provider_id=provider_id,
            seller_user_id=seller_user_id,
            buyer_user_id=buyer_user_id,
            client=client
        )
        
        # ==================== STEP 6: Persist Cart ====================
        logger.info("Step 6: Persisting cart...")
        cart, created_items, created_services = await self._persist_cart(
            cart, total_price, person_obj
        )
        
        # ==================== STEP 7: Reserve Inventory with Real IDs ====================
        logger.info("Step 7: Reserving inventory...")
        await self._reserve_inventory_with_real_ids(
            reservation_plan, 
            created_items, 
            [consumption for service in created_services for consumption in service.product_consumption]
        )
        
        logger.info(f"Cart {cart.cart_id} creation completed")
        return {}, cart


    async def _build_cart(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
        cart_data: Cart_API,
        products: Dict[int, Any],
        services: Dict[int, Any],
        item_details: Dict[int, Dict],
        provider_id: int,
        seller_user_id: int,
        buyer_user_id: int,
        client: Optional[Person_API]
    ) -> Tuple[Cart, float, Optional[Any]]:
        """
        Build cart object and calculate total price.
        
        REMOVED: reservation_result parameter since we're now reserving after persistence.
        """
        
        # Calculate totals
        total_price = 0.0
        ordered_item_models = []
        
        # Build ordered items
        for item in ordered_items:
            product_id = item.ordered_product_id
            product = products.get(product_id)
            
            if not product:
                continue
            
            unit_price = self._safe_float(product.product_price)
            item_total = item.ordered_quantity * unit_price
            
            # Apply VAT
            if item.applied_vat:
                item_total *= (1 + self._safe_float(item.applied_vat))
            
            total_price += item_total
            
            ordered_item = OrderedItem(
                ordered_product_id=product_id,
                ordered_quantity=item.ordered_quantity,
                applied_vat=self._safe_float(item.applied_vat),
                unit_price=unit_price,
                reserved_quantity=item.ordered_quantity
            )



            if item.order_ref and item.order_ref > 0:
                ordered_item.order_ref = item.order_ref
            
            ordered_item_models.append(ordered_item)
        
        # Build ordered services
        ordered_service_models = []
        for service_api in ordered_services:
            service_id = service_api.ordered_service_service_id
            service = services.get(service_id)
            
            if not service:
                continue
            
            unit_price = (
                self._safe_float(service.provided_service_final_price) or 
                self._safe_float(service.provided_service_base_price) or 
                0.0
            )
            
            service_total = service_api.ordered_service_quantity * unit_price
            total_price += service_total
            
            ordered_service = OrderedService(
                ordered_service_service_id=service_id,
                ordered_service_quantity=service_api.ordered_service_quantity,
                ordered_service_unit_price=unit_price,
                ordered_service_total_price=service_total,
                ordered_service_notes=service_api.ordered_service_notes,
                ordered_service_delivery_status='pending'
            )

            reqs = self.service_repo.get_service_resource_requirements(service_id)

            consumptions = [
                ProductConsumption(
                    consumed_product_id=req.service_resource_requirement_product_ref,
                    resource_req_ref=req.service_resource_requirement_id,
                    product_reserved_quantity=0
                )
                for req in reqs
                if req.service_resource_requirement_is_consumable
            ]

            ordered_service.product_consumption = consumptions

            
            if service_api.ordered_service_scheduled_at:
                ordered_service.ordered_service_scheduled_at = service_api.ordered_service_scheduled_at
            
            ordered_service_models.append(ordered_service)
        
        # Handle client/person
        person_obj = None
        if client:
            if client.id_person == 0:
                person_obj = self.person_service.refresh_or_insert_person(client)
            else:
                person_obj = self.person_service.get_person_by_id(client.id_person)
        
        # Create cart object
        now = datetime.now()
        final_total_price = round(self._safe_float(cart_data.cart_total_amount or total_price), 2)
        
        cart = Cart(
            cart_product_provider_id=provider_id,
            cart_selling_user=seller_user_id,
            cart_person_ref=person_obj.id_person if person_obj else None,
            cart_status=cart_data.cart_status or 'open',
            cart_total_amount=final_total_price,
            cart_notes=cart_data.cart_notes or '',
            cart_created_at=now,
            cart_updated_at=now,
        )
        
        if buyer_user_id:
            cart.cart_client_user = buyer_user_id
        
        if cart_data.cart_due_date:
            cart.cart_due_date = cart_data.cart_due_date
        
        # Store models on cart
        cart.ordered_item = ordered_item_models
        cart.ordered_service = ordered_service_models
        
        return cart, final_total_price, person_obj


    async def _validate_inventory_availability(self, reservation_plan: Dict[int, Dict]) -> None:
        """
        Check inventory availability WITHOUT reserving.
        Uses the bulk stock status endpoint.
        """
        if not reservation_plan:
            return
        
        product_ids = list(reservation_plan.keys())
        
        # Get bulk stock status
        availability_response = await self.inventory_client.get_bulk_stock_status(
            product_ids=product_ids
        )
        
        # Parse response - the client already parses it for us
        stock_by_product = availability_response
        
        # Check each product
        for product_id, plan in reservation_plan.items():
            stock_data = stock_by_product.get(str(product_id), {})
            available_qty = stock_data.get('available_quantity', 0)
            requested_qty = plan["quantity"]
            
            if available_qty < requested_qty:
                raise InsufficientStockException(
                    product_id=product_id,
                    requested=requested_qty,
                    available=available_qty
                )
        
        logger.info("✅ Inventory availability check passed")


    async def _reserve_inventory_with_real_ids(
        self,
        reservation_plan: Dict[int, Dict],
        created_items: List[OrderedItem],
        consumptions: List[ProductConsumption]
    ) -> None:
        """
        Reserve inventory using the real ordered_item IDs from the database.
        """
        if not reservation_plan:
            logger.info("No items to reserve")
            return
        
        # Build the reserve items with real IDs
        ordered_reserve_items = []
        consumption_reserve_items = []
        
        # Map product_id to its ordered items
        product_item_map = {}
        for item in created_items:
            product_id = item.ordered_product_id
            if product_id not in product_item_map:
                product_item_map[product_id] = []
            product_item_map[product_id].append({
                "id": item.id_ordered_item,
                "quantity": item.ordered_quantity,
                "product_id": product_id
            })
        
        # Map product_id to its consumptions
        consumption_map = {}
        for item in consumptions:
            product_id = item.consumed_product_id
            if product_id not in consumption_map:
                consumption_map[product_id] = []
            
            # Find the matching source in reservation_plan to get the correct quantity
            matching_source = None
            if product_id in reservation_plan:
                for source in reservation_plan[product_id].get("sources", []):
                    if (source.get("type") == "consumption" and 
                        source.get("id") == item.resource_req_ref):
                        matching_source = source
                        break
            
            consumption_map[product_id].append({
                "id": item.id_product_consumption,
                "quantity": matching_source.get("quantity") ,
                "product_id": product_id,
                # "resource_req_ref": item.resource_req_ref
            })
        
        # Build reserve items for each product in the reservation plan
        for product_id, plan in reservation_plan.items():
            # Get ordered items for this product
            ordered_items_for_product = product_item_map.get(product_id, [])
            consumptions_for_product = consumption_map.get(product_id, [])
            
            # Add ordered items
            for item in ordered_items_for_product:
                ordered_reserve_items.append({
                    "id": item["id"],
                    # "product_id": product_id,
                    "quantity": item["quantity"],
                    "item_type": "ordered_item"
                })
            
            # Add consumptions
            for consumption in consumptions_for_product:
                consumption_reserve_items.append({
                    "id": consumption["id"],
                    # "product_id": product_id,
                    "quantity": consumption["quantity"],
                    "item_type": "consumption",
                    # "resource_req_ref": consumption["resource_req_ref"]
                })
        
        # Reserve ordered items
        if ordered_reserve_items:
            try:
                response = await self.inventory_client.reserve_inventory(
                    items=ordered_reserve_items,
                    item_type='ordered_item'
                )
                logger.info(f"✅ Successfully reserved {len(ordered_reserve_items)} ordered items")
            except Exception as e:
                logger.error(f"Failed to reserve ordered items: {e}")
                raise
        
        # Reserve consumptions
        if consumption_reserve_items:
            try:
                response = await self.inventory_client.reserve_inventory(
                    items=consumption_reserve_items,
                    item_type='consumption'
                )
                logger.info(f"✅ Successfully reserved {len(consumption_reserve_items)} consumptions")
            except Exception as e:
                logger.error(f"Failed to reserve consumptions: {e}")
                # If consumption reservation fails, we should release the ordered items
                if ordered_reserve_items:
                    try:
                        await self.inventory_client.release_inventory(
                            items=ordered_reserve_items,
                            item_type='ordered_item'
                        )
                        logger.info("Released ordered items after consumption reservation failure")
                    except Exception as release_error:
                        logger.error(f"Failed to release ordered items: {release_error}")
                raise
        
        logger.info("✅ Inventory reservation completed successfully")

    async def _persist_cart(
        self,
        cart: Cart,
        total_price: float,
        person_obj: Optional[Any]
    ) -> Tuple[Cart, List[OrderedItem], List[OrderedService]]:
        """Persist cart, invoice, and related entities."""
        
        # Create invoice
        invoice = Invoice(
            invoice_total_amount=total_price,
            invoice_status='unpaid',
            invoice_issue_date=datetime.now().date(),
            invoice_due_date=datetime.now().date() + timedelta(days=30),
            invoice_type='invoice',
            invoice_tax_applied=19,
        )
        created_invoice = self.invoice_repo.create_invoice(invoice)
        logger.info(f"✅ Created invoice: {created_invoice.invoice_id}")
        
        # Set invoice on cart
        cart.cart_invoice = created_invoice.invoice_id
        
        # Save cart
        cart = self.cart_repo.create_cart(cart)
        logger.info(f"Cart created with ID: {cart.cart_id}")
        
        # Save ordered items with cart reference
        created_items = []
        for ordered_item in cart.ordered_item:
            ordered_item.ordered_item_cart_ref = cart.cart_id
            created_item = self.order_repo.create_order_item(ordered_item)
            created_items.append(created_item)
            logger.info(f"Created ordered item ID: {created_item.id_ordered_item}")
        
        # Save ordered services with cart reference
        created_services = []
        for ordered_service in cart.ordered_service:
            ordered_service.ordered_service_cart_id = cart.cart_id
            created_service = self.cart_repo.create_ordered_service(ordered_service)
            created_services.append(created_service)
            logger.info(f"Created ordered service ID: {created_service.ordered_service_id}")
        
        # Update cart with created items
        cart.ordered_item = created_items
        cart.ordered_service = created_services
        
        return cart, created_items, created_services

    # ==================== HELPER METHODS ====================

    async def _validate_entities(self, provider_id: int, seller_user_id: int, buyer_user_id: int) -> None:
        """Validate provider, seller, and buyer exist"""
        # Validate provider
        provider = self.supplier_repo.get_supplier_by_id(provider_id)
        if not provider:
            raise CartSupplierNotFoundException(provider_id=provider_id)
        
        # Validate seller
        selling_user = self.user_repo.get_by_id(seller_user_id)
        if not selling_user:
            raise CartSellerNotFoundException(seller_id=seller_user_id)
        
        # Validate buyer (optional)
        if buyer_user_id > 0:
            buyer_user = self.user_repo.get_by_id(buyer_user_id)
            if not buyer_user:
                raise CartBuyerNotFoundException(buyer_id=buyer_user_id)


    async def _load_products_and_services(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API]
    ) -> Tuple[Dict[int, Any], Dict[int, Any]]:
        """Load all products and services in bulk with eager loading"""
        
        # Extract IDs
        product_ids = [item.ordered_product_id for item in ordered_items]
        service_ids = [service.ordered_service_service_id for service in ordered_services]
        
        # Bulk load products
        products = {}
        if product_ids:
            product_list = self.product_repo.get_products_by_ids(product_ids)
            products = {p.id_product: p for p in product_list}
            
            # Validate all products exist
            if len(products) != len(set(product_ids)):
                missing = set(product_ids) - set(products.keys())
                raise CartProductNotFoundException(product_id=next(iter(missing)))
        
        # Bulk load services with resource requirements eagerly loaded
        services = {}
        if service_ids:
            # This should use eager loading to load service_resource_requirement
            service_list = self.service_repo.get_services_by_ids(service_ids)
            services = {s.provided_service_id: s for s in service_list}
            
            # Validate all services exist
            if len(services) != len(set(service_ids)):
                missing = set(service_ids) - set(services.keys())
                raise ServiceNotFoundException(service_id=next(iter(missing)))
        
        return products, services

    async def _build_reservation_plan(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
        products: Dict[int, Any],
        services: Dict[int, Any]
    ) -> Tuple[Dict[int, Dict], Dict[int, Dict]]:
        """
        Build a single reservation plan and item details in one pass.
        
        Returns:
            reservation_plan: {product_id: {"quantity": total, "sources": [...]}}
            item_details: {product_id: {"unit_price": ..., "product": ...}}
        """
        reservation_plan = {}
        item_details = {}
        
        # Process ordered items
        for item in ordered_items:
            product_id = item.ordered_product_id
            product = products.get(product_id)
            
            if not product:
                continue
            
            quantity = item.ordered_quantity
            
            if product_id not in reservation_plan:
                reservation_plan[product_id] = {
                    "quantity": 0,
                    "sources": []
                }
            reservation_plan[product_id]["quantity"] += quantity
            reservation_plan[product_id]["sources"].append({
                "type": "ordered_item",
                "id": item.id_ordered_item if hasattr(item, 'id_ordered_item') else 0,
                "quantity": quantity
            })
            
            if product_id not in item_details:
                item_details[product_id] = {
                    "unit_price": self._safe_float(product.product_price),
                    "product": product
                }
        
        # Process ordered services - Using the services dict with eager loaded relationships
        for service_api in ordered_services:
            service_id = service_api.ordered_service_service_id
            service = services.get(service_id)
            
            if not service:
                continue
            

            
            # Access resource_requirements directly from the loaded service
            resource_requirements = self.service_repo.get_service_resource_requirements(service_id)
            
            if resource_requirements:
                for requirement in resource_requirements:
                    if not requirement.service_resource_requirement_is_consumable:
                        continue

                    logger.info(f"Adding consumable resource {requirement.service_resource_requirement_id} to reservation plan")
                    
                    product_id = requirement.service_resource_requirement_product_ref
                    quantity_needed = (
                        self._safe_float(requirement.service_resource_requirement_quantity) * 
                        service_api.ordered_service_quantity
                    )
                    
                    if product_id not in reservation_plan:
                        reservation_plan[product_id] = {
                            "quantity": 0,
                            "sources": []
                        }
                    reservation_plan[product_id]["quantity"] += quantity_needed
                    reservation_plan[product_id]["sources"].append({
                        "type": "consumption",
                        "service_id": service_id,
                        "id": requirement.service_resource_requirement_id,
                        "quantity": quantity_needed
                    })
                    
                    if product_id not in item_details:
                        product = self.product_repo.get_product_by_id(product_id)
                        if product:
                            item_details[product_id] = {
                                "unit_price": self._safe_float(product.product_price),
                                "product": product
                            }
        
        return reservation_plan, item_details  

    async def _validate_inventory(self, reservation_plan: Dict[int, Dict]) -> None:
        """Validate inventory availability without reserving"""
        if not reservation_plan:
            return
        
        # Use a "check availability" endpoint instead of "reserve"
        # This assumes your inventory client has a check_availability method
        availability_response = await self.inventory_client.check_availability(
            items=[{
                "product_id": product_id,
                "quantity": plan["quantity"]
            } for product_id, plan in reservation_plan.items()]
        )
        
        # Check if all items are available
        for item in availability_response.get('items', []):
            if not item.get('available', False):
                raise InsufficientStockException(
                    product_id=item['product_id'],
                    requested=item['requested'],
                    available=item['available']
                )


    async def _reserve_inventory(self, reservation_plan: Dict[int, Dict]) -> Dict:
        """Reserve inventory with a single API call"""
        if not reservation_plan:
            return {"success": True, "reservation_id": None}
        
        # Build reserve items with required fields
        reserve_items = []
        for product_id, plan in reservation_plan.items():
            # Each item needs a unique ID - generate one if not available
            for source in plan["sources"]:
                item_id = source.get('id')
                if not item_id or item_id == 0:
                    # Generate a temporary ID for reservation
                    item_id = int(f"{product_id}{int(datetime.now().timestamp())}{random.randint(100, 999)}")
                
                reserve_items.append({
                    "id": item_id,  # REQUIRED field
                    "product_id": product_id,
                    "quantity": source["quantity"],
                    "item_type": source["type"]  # Must be 'ordered_item' or 'consumption'
                })
        
        # Only send unique items to avoid duplicates
        unique_items = []
        seen = set()
        for item in reserve_items:
            key = f"{item['product_id']}_{item['id']}"
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        if not unique_items:
            return {"success": True, "reservation_id": None}
        
        # The API expects 'item_type' at the root level as well
        response = await self.inventory_client.reserve_inventory(
            items=unique_items,
            item_type='ordered_item'  # Use 'ordered_item' or 'consumption'
        )
        
        if isinstance(response, dict) and not response.get('success', True):
            raise Exception(f"Inventory reservation failed: {response}")
        
        return {
            "success": True,
            "reservation_id": response.get('reservation_id'),
            "items": unique_items
        }






    async def _confirm_inventory_reservation(
        self,
        reservation_result: Dict,
        created_items: List[OrderedItem],
        created_services: List[OrderedService]
    ) -> None:
        """Confirm inventory reservation with actual IDs"""
        if not reservation_result.get('reservation_id'):
            return
        
        # Build confirmation items with actual IDs
        confirm_items = []
        
        # Add ordered items
        for item in created_items:
            confirm_items.append({
                "id": item.id_ordered_item,
                "quantity": item.ordered_quantity,
                "product_id": item.ordered_product_id,
                "item_type": "ordered_item"
            })
        
        # Add service resources
        # (You would need to map service resource requirements here)
        
        if confirm_items:
            await self.inventory_client.confirm_reservation(
                reservation_id=reservation_result['reservation_id'],
                items=confirm_items
            )


    async def _release_inventory(self, reservation_result: Dict) -> None:
        """Release inventory reservation (compensation action)"""
        if not reservation_result.get('reservation_id'):
            return
        
        try:
            await self.inventory_client.release_reservation(
                reservation_id=reservation_result['reservation_id'],
                reason="Cart creation failed"
            )
            logger.info(f"Released inventory reservation: {reservation_result['reservation_id']}")
        except Exception as e:
            logger.error(f"Failed to release inventory reservation: {e}")
            # Log failure but don't re-raise - this is a compensation action


    def _safe_float(self, value: Any) -> float:
        """Safely convert any value to float"""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0


    def _parse_inventory_response(self, response: Dict) -> Dict:
        """Parse inventory service response"""
        if isinstance(response, dict):
            return response.get('data', response)
        return {}    
    
    async def _rollback_cart_creation(self, cart: Optional[Cart], created_items: List[OrderedItem] = None):
        """Rollback cart creation in case of failure."""
        if not cart:
            return
        
        logger.info(f"🔄 Rolling back cart creation for cart {cart.cart_id}")
        
        try:
            # Release inventory
            items_to_release = []
            if cart.ordered_item:
                for item in cart.ordered_item:
                    items_to_release.append({
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id
                    })
            elif created_items:
                for item in created_items:
                    items_to_release.append({
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id
                    })
            
            if items_to_release:
                try:
                    await self.inventory_client.release_inventory(
                        items=items_to_release,
                        item_type='ordered_item'
                    )
                    logger.info("✅ Inventory released")
                except Exception as e:
                    logger.error(f"Failed to release inventory: {e}")
            
            # Delete cart
            self.cart_repo.delete_cart_sync(cart)
            logger.info("✅ Cart deleted during rollback")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")

    # ==================== Cart Update and Delete Methods ====================

    def update_cart_status(self, cart_id: int, new_status: str) -> Cart:
        """Update cart status."""
        logger.info(f"Updating cart {cart_id} status to '{new_status}'")
        cart = self.get_cart_by_id(cart_id)
        cart.cart_status = new_status
        cart.cart_updated_at = datetime.now()
        
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

    async def delete_cart(self, cart_id: int, force_delete: bool = False) -> bool:
        """Delete a cart and release inventory."""
        logger.info(f"Deleting cart {cart_id} (force={force_delete})")
        
        try:
            cart = self.get_cart_by_id(cart_id)
        except CartNotFoundException:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise
        
        try:
            # Get ordered items
            ordered_items = list(cart.ordered_item) if cart.ordered_item else []
            
            # Release inventory
            if ordered_items:
                release_items = [
                    {
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id
                    }
                    for item in ordered_items
                ]
                
                await self.inventory_client.release_inventory(
                    items=release_items,
                    item_type='ordered_item'
                )
                logger.info("✅ Inventory released")
            
            # Delete cart using ID (cleaner approach)
            result = self.cart_repo.delete_cart_by_id_sync(cart_id)
            logger.info(f"Cart {cart_id} deleted successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete cart {cart_id}: {e}")
            raise CartDeleteFailedException(cart_id=cart_id, error=str(e))

            
        except Exception as e:
            logger.error(f"Failed to delete cart {cart_id}: {e}")
            raise CartDeleteFailedException(cart_id=cart_id, error=str(e))