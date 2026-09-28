# services/cart_service.py

"""
Service for cart-related business logic including cart creation,
financial document management, and stock handling using Inventory microservice.
"""

import logging
import random
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

from services.financial_service import FinancialService
from repositories.service_repository import ServiceRepository
from repositories.order_repository import OrderRepository
from repositories.financial_repository import FinancialRepository
from repositories.cart_repository import CartRepository
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
from core.models.models import (
    Cart, Delivery, OrderedItem, OrderedService, Product,
    Invoice, Payment, ProductConsumption, ProvidedService,
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
from core.exceptions.handler import (
    ProductNotFoundException,
    InsufficientStockException,
    ServiceNotFoundException,
)
from core.exceptions.specific.product_exceptions import ProductQuantityNotEnoughException

logger = logging.getLogger(__name__)


# ==================== Payment intent enum ====================

class PaymentIntent(str, Enum):
    """
    What kind of payment the client is expressing at cart creation time.

    NONE      → no payment field was sent; invoice stays unpaid
    FULL      → cart_payment == True; settle the whole total
    DEPOSIT   → cart_deposit == True; settle a partial amount
    DUE_DATE  → installment scheduled; invoice gets the due date, no payment yet
    """
    NONE = "none"
    FULL = "full"
    DEPOSIT = "deposit"
    DUE_DATE = "due_date"


# Payment statuses as stored in the DB (must match the backend enum)
_PAYMENT_STATUS_COMPLETED = "completed"
_PAYMENT_STATUS_PENDING = "pending"

# Payment methods that settle instantly
_INSTANT_METHODS = {"cash"}


class CartService:
    """Service for cart-related business logic with microservice integration"""

    def __init__(self):
        self.cart_repo = CartRepository()
        self.financial_repo = FinancialRepository()
        self.financial_service = FinancialService()
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

        self.inventory_client = InventoryServiceClient()
        self.finance_client = FinanceServiceClient()

    # ==================== Helpers ====================

    def _safe_float(self, value: Any) -> float:
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
        if hasattr(value, "__float__"):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def _parse_inventory_response(self, response: Dict) -> Dict:
        """Parse inventory response to extract stock status by product ID."""
        if not response:
            return {}

        result = {}

        # Format 1: {"1": {"available_quantity": ...}}
        if all(isinstance(v, dict) for v in response.values()):
            return response

        # Format 2: {"items": [...]}
        if "items" in response and isinstance(response["items"], list):
            for item in response["items"]:
                pid = item.get("product_id")
                if pid:
                    result[str(pid)] = item
            return result

        # Format 3: {"data": [...]}
        if "data" in response and isinstance(response["data"], list):
            for item in response["data"]:
                pid = item.get("product_id")
                if pid:
                    result[str(pid)] = item
            return result

        # Format 4: flat mapping
        for key, value in response.items():
            try:
                int(key)
                result[str(key)] = value
            except (ValueError, TypeError):
                pass

        return result

    def _detect_payment_intent(self, cart_data: Cart_API) -> PaymentIntent:
        """
        Classify what the client intended based on the fields they sent.

        Priority:
          1. deposit flag → DEPOSIT
          2. payment flag → FULL
          3. due date set without payment → DUE_DATE
          4. otherwise → NONE
        """
        if getattr(cart_data, "cart_deposit", False):
            return PaymentIntent.DEPOSIT
        if getattr(cart_data, "cart_payment", False):
            return PaymentIntent.FULL
        if getattr(cart_data, "cart_due_date", None):
            return PaymentIntent.DUE_DATE
        return PaymentIntent.NONE

    def _resolve_initial_payment_status(self, method: str) -> str:
        """
        Cash settles instantly; everything else awaits gateway confirmation.
        """
        return (
            _PAYMENT_STATUS_COMPLETED
            if (method or "").lower() in _INSTANT_METHODS
            else _PAYMENT_STATUS_PENDING
        )

    def _compute_new_invoice_status(
        self,
        invoice_total: float,
        current_completed_total: float,
        new_payment_amount: float,
        new_payment_status: str,
    ) -> str:
        """
        Derive the invoice status after a payment lands.

        Only `completed` payments contribute to the paid total.
        A pending payment leaves the invoice untouched.
        """
        if new_payment_status != _PAYMENT_STATUS_COMPLETED:
            return "unpaid"

        total_paid = current_completed_total + new_payment_amount
        if invoice_total <= 0:
            return "unpaid"
        if total_paid >= invoice_total:
            return "paid"
        if total_paid > 0:
            return "partially_paid"
        return "unpaid"

    # ==================== Cart Retrieval ====================

    def get_cart_by_id(self, cart_id: int, eager_load: bool = True) -> Cart:
        cart = self.cart_repo.get_cart_by_id(cart_id, eager_load=eager_load)
        if not cart:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise CartNotFoundException(cart_id=cart_id)

        try:
            if hasattr(cart, "ordered_item") and cart.ordered_item:
                for item in cart.ordered_item:
                    _ = item.id_ordered_item
                    _ = item.ordered_product_id
            if hasattr(cart, "ordered_service") and cart.ordered_service:
                for service in cart.ordered_service:
                    _ = service.ordered_service_id
        except Exception as e:
            logger.warning(f"Error loading cart relationships: {e}")
            cart = self.cart_repo.get_cart_by_id(cart_id, eager_load=True)
            if not cart:
                raise CartNotFoundException(cart_id=cart_id)

        return cart

    def get_carts_by_provider(self, provider_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        return self.cart_repo.get_carts_by_provider(provider_id, offset, limit)

    def get_carts_by_seller(self, seller_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        return self.cart_repo.get_carts_by_seller(seller_id, offset, limit)

    def get_carts_by_buyer(self, buyer_id: int, offset: int = 0, limit: int = 100) -> List[Cart]:
        return self.cart_repo.get_carts_by_buyer(buyer_id, offset, limit)

    def list_carts(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        buyer_id: int = 0,
        status: str = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Cart]:
        return self.cart_repo.list_carts(provider_id, seller_id, buyer_id, status, offset, limit)

    def get_cart_summary(self, cart_id: int) -> Dict[str, Any]:
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        subtotal = 0.0
        item_count = 0
        service_count = 0

        if cart.ordered_item:
            for item in cart.ordered_item:
                subtotal += self._safe_float(item.ordered_quantity) * self._safe_float(item.unit_price)
                item_count += 1

        if cart.ordered_service:
            for service in cart.ordered_service:
                subtotal += self._safe_float(service.ordered_service_total_price)
                service_count += 1

        return {
            "cart_id": cart_id,
            "subtotal": round(subtotal, 2),
            "total": round(self._safe_float(cart.cart_total_amount or subtotal), 2),
            "item_count": item_count,
            "service_count": service_count,
            "status": cart.cart_status,
            "created_at": cart.cart_created_at,
        }

    def get_cart_items(self, cart_id: int) -> List[Dict[str, Any]]:
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        items = []
        if cart.ordered_item:
            for item in cart.ordered_item:
                product = self.product_repo.get_product_by_id(item.ordered_product_id)
                items.append({
                    "id": item.id_ordered_item,
                    "product_id": item.ordered_product_id,
                    "product_name": product.product_name if product else "Unknown",
                    "quantity": self._safe_float(item.ordered_quantity),
                    "unit_price": self._safe_float(item.unit_price),
                    "total_price": self._safe_float(item.ordered_quantity) * self._safe_float(item.unit_price),
                    "applied_vat": self._safe_float(item.applied_vat),
                    "product_discount": self._safe_float(item.product_discount or 0),
                })
        return items

    def get_cart_services(self, cart_id: int) -> List[Dict[str, Any]]:
        cart = self.get_cart_by_id(cart_id, eager_load=True)
        services = []
        if cart.ordered_service:
            for service in cart.ordered_service:
                service_obj = self.service_repo.get_service_by_id(service.ordered_service_service_id)
                services.append({
                    "id": service.ordered_service_id,
                    "service_id": service.ordered_service_service_id,
                    "service_name": service_obj.provided_service_name if service_obj else "Unknown",
                    "quantity": self._safe_float(service.ordered_service_quantity),
                    "unit_price": self._safe_float(service.ordered_service_unit_price),
                    "total_price": self._safe_float(service.ordered_service_total_price),
                    "scheduled_at": service.ordered_service_scheduled_at,
                    "notes": service.ordered_service_notes,
                })
        return services

    # ==================== Cart Creation ====================

    async def create_cart(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
        cart_data: Cart_API,
        delivery: Optional[Delivery_API] = None,
        payment: Optional[Payment_API] = None,
        client: Optional[Person_API] = None,
        provider_id: int = 0,
        seller_user_id: int = 0,
        buyer_user_id: int = 0,
    ) -> Tuple[Dict[str, Any], Cart]:
        """
        Create a new cart with optional payment capture.

        Payment is created as part of the same workflow when the client
        declares an intent via `cart_data.cart_payment` or `cart_data.cart_deposit`.
        """
        logger.info(f"Creating cart for provider {provider_id}, seller {seller_user_id}")

        if not ordered_items and not ordered_services:
            raise CartCreationFailedException(
                error="Cart must have at least one item or service",
                provider_id=provider_id,
                seller_id=seller_user_id,
            )

        intent = self._detect_payment_intent(cart_data)
        logger.info(f"Detected payment intent: {intent.value}")

        # Step 1: validate entities
        logger.info("Step 1: Validating entities...")
        await self._validate_entities(provider_id, seller_user_id, buyer_user_id)

        # Step 2: load catalog data
        logger.info("Step 2: Loading products and services...")
        products, services = await self._load_products_and_services(ordered_items, ordered_services)

        # Step 3: plan reservations
        logger.info("Step 3: Building reservation plan...")
        reservation_plan, item_details = await self._build_reservation_plan(
            ordered_items, ordered_services, products, services
        )

        # Step 4: check stock
        logger.info("Step 4: Validating inventory availability...")
        await self._validate_inventory_availability(reservation_plan)

        # Step 5: build cart in memory
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
            client=client,
        )

        # Step 6: persist cart + invoice
        logger.info("Step 6: Persisting cart...")
        cart, created_items, created_services, invoice = await self._persist_cart(
            cart, total_price, person_obj
        )

        # Step 7: reserve inventory
        logger.info("Step 7: Reserving inventory...")
        await self._reserve_inventory_with_real_ids(
            reservation_plan,
            created_items,
            [c for svc in created_services for c in svc.product_consumption],
        )

        # Step 8: create the payment if the client declared an intent
        logger.info("Step 8: Handling payment...")
        financial_docs = await self._handle_payment(
            intent=intent,
            cart=cart,
            invoice=invoice,
            total_price=total_price,
            cart_data=cart_data,
        )

        # Step 9: confirm the payment if the client declared an intent
        logger.info("Step 9: Confirming reservations...")

        ordered_payload = [
            {
                "id": item.id_ordered_item,
                "quantity": item.ordered_quantity,
            }
            for item in created_items
        ]

        consumption_payload = [
            {
                "id": consumption.id_product_consumption,
                "quantity": consumption.product_reserved_quantity,
            }
            for service in created_services
            for consumption in service.product_consumption
        ]

        await self.inventory_client.bulk_confirm(
            ordered_payload,
            consumption_payload,
        )


        # Attach invoice so the router can expose it
        financial_docs["invoice"] = invoice

        logger.info(f"Cart {cart.cart_id} creation completed")
        return financial_docs, cart

    # ==================== Payment workflow ====================

    async def _handle_payment(
        self,
        intent: PaymentIntent,
        cart: Cart,
        invoice: Invoice,
        total_price: float,
        cart_data: Cart_API,
    ) -> Dict[str, Any]:
        """
        Create a payment record if the client asked for one.

        Returns a dict of financial documents created.
        """
        financial_docs: Dict[str, Any] = {}

        if intent in (PaymentIntent.NONE, PaymentIntent.DUE_DATE):
            # Nothing to charge now — invoice stays unpaid.
            logger.info(f"No payment requested (intent={intent.value}); skipping.")
            return financial_docs

        # Amount to charge
        paid_money = self._safe_float(getattr(cart_data, "cart_paid_money", 0))
        if paid_money <= 0:
            logger.info("Payment intent declared but cart_paid_money is 0; skipping.")
            return financial_docs

        # Cap at invoice total
        if paid_money > total_price:
            logger.warning(
                f"cart_paid_money ({paid_money}) exceeds total ({total_price}); capping."
            )
            paid_money = total_price

        method = getattr(cart_data, "cart_payment_method", None) or "cash"
        status = self._resolve_initial_payment_status(method)

        try:
            payment = self._create_payment(
                invoice_id=invoice.invoice_id,
                amount=paid_money,
                method=method,
                status=status,
                notes=cart_data.cart_notes or "",
            )
            financial_docs["payment"] = payment

            # Recompute invoice status
            new_status = self._compute_new_invoice_status(
                invoice_total=total_price,
                current_completed_total=0.0,
                new_payment_amount=paid_money,
                new_payment_status=status,
            )
            self._apply_invoice_status(invoice, new_status)
            financial_docs["invoice"] = invoice

            logger.info(
                f"Payment {payment.payment_id} created "
                f"(method={method}, status={status}, amount={paid_money}); "
                f"invoice {invoice.invoice_id} → {new_status}"
            )
        except CartPaymentCreationException:
            raise
        except Exception as e:
            logger.error(f"Payment creation failed: {e}")
            raise CartPaymentCreationException(
                cart_id=cart.cart_id,
                invoice_id=invoice.invoice_id,
                error=str(e),
            )

        return financial_docs

    def _create_payment(
        self,
        invoice_id: int,
        amount: float,
        method: str,
        status: str,
        notes: str = "",
    ) -> Payment:
        """Persist a Payment row via the financial repository."""
        payment = Payment(
            payment_invoice_id=invoice_id,
            payment_amount=amount,
            payment_method=method,
            payment_status=status,
            payment_reference=f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            payment_notes=notes,
            payment_type="payment",
        )
        return self.financial_service.create_payment(payment)

    def _apply_invoice_status(self, invoice: Invoice, new_status: str) -> None:
        """Update the invoice row in the DB."""
        invoice.invoice_status = new_status
        invoice.invoice_updated_at = datetime.now()
        try:
            self.invoice_repo.update_invoice(invoice)
        except Exception as e:
            logger.error(f"Failed to update invoice {invoice.invoice_id} status: {e}")
            raise CartInvoiceCreationException(
                error=f"Invoice status update failed: {e}"
            )

    # ==================== Cart building ====================

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
        client: Optional[Person_API],
    ) -> Tuple[Cart, float, Optional[Any]]:
        total_price = 0.0
        ordered_item_models = []

        for item in ordered_items:
            product_id = item.ordered_product_id
            product = products.get(product_id)
            if not product:
                continue

            unit_price = self._safe_float(product.product_price)
            item_total = item.ordered_quantity * unit_price
            if item.applied_vat:
                item_total *= 1 + self._safe_float(item.applied_vat)
            total_price += item_total

            ordered_item = OrderedItem(
                ordered_product_id=product_id,
                ordered_quantity=item.ordered_quantity,
                applied_vat=self._safe_float(item.applied_vat),
                unit_price=unit_price,
                reserved_quantity=item.ordered_quantity,
            )
            if item.order_ref and item.order_ref > 0:
                ordered_item.order_ref = item.order_ref
            ordered_item_models.append(ordered_item)

        ordered_service_models = []
        for service_api in ordered_services:
            service_id = service_api.ordered_service_service_id
            service = services.get(service_id)
            if not service:
                continue

            unit_price = (
                self._safe_float(service.provided_service_final_price)
                or self._safe_float(service.provided_service_base_price)
                or 0.0
            )
            service_total = service_api.ordered_service_quantity * unit_price
            total_price += service_total

            ordered_service = OrderedService(
                ordered_service_service_id=service_id,
                ordered_service_quantity=service_api.ordered_service_quantity,
                ordered_service_unit_price=unit_price,
                ordered_service_total_price=service_total,
                ordered_service_notes=service_api.ordered_service_notes,
                ordered_service_delivery_status="pending",
            )

            reqs = self.service_repo.get_service_resource_requirements(service_id)
            ordered_service.product_consumption = [
                ProductConsumption(
                    consumed_product_id=req.service_resource_requirement_product_ref,
                    resource_req_ref=req.service_resource_requirement_id,
                    product_reserved_quantity=0,
                )
                for req in reqs
                if req.service_resource_requirement_is_consumable
            ]

            if service_api.ordered_service_scheduled_at:
                ordered_service.ordered_service_scheduled_at = service_api.ordered_service_scheduled_at

            ordered_service_models.append(ordered_service)

        person_obj = None
        if client:
            if client.id_person == 0:
                person_obj = self.person_service.refresh_or_insert_person(client)
            else:
                person_obj = self.person_service.get_person_by_id(client.id_person)

        now = datetime.now()
        final_total = round(self._safe_float(cart_data.cart_total_amount or total_price), 2)

        cart = Cart(
            cart_product_provider_id=provider_id,
            cart_selling_user=seller_user_id,
            cart_person_ref=person_obj.id_person if person_obj else None,
            cart_status=cart_data.cart_status or "open",
            cart_total_amount=final_total,
            cart_notes=cart_data.cart_notes or "",
            cart_created_at=now,
            cart_updated_at=now,
        )

        if buyer_user_id:
            cart.cart_client_user = buyer_user_id
        if cart_data.cart_due_date:
            cart.cart_due_date = cart_data.cart_due_date

        cart.ordered_item = ordered_item_models
        cart.ordered_service = ordered_service_models

        return cart, final_total, person_obj

    # ==================== Inventory ====================

    async def _validate_inventory_availability(self, reservation_plan: Dict[int, Dict]) -> None:
        if not reservation_plan:
            return

        product_ids = list(reservation_plan.keys())
        availability_response = await self.inventory_client.get_bulk_stock_status(
            product_ids=product_ids
        )
        stock_by_product = availability_response

        for product_id, plan in reservation_plan.items():
            stock_data = stock_by_product.get(str(product_id), {})
            available_qty = stock_data.get("available_quantity", 0)
            requested_qty = plan["quantity"]
            if available_qty < requested_qty:
                raise InsufficientStockException(
                    product_id=product_id,
                    requested=requested_qty,
                    available=available_qty,
                )

        logger.info("✅ Inventory availability check passed")

    async def _reserve_inventory_with_real_ids(
        self,
        reservation_plan: Dict[int, Dict],
        created_items: List[OrderedItem],
        consumptions: List[ProductConsumption],
    ) -> None:
        if not reservation_plan:
            logger.info("No items to reserve")
            return

        ordered_reserve_items = []
        consumption_reserve_items = []

        product_item_map: Dict[int, List[Dict]] = {}
        for item in created_items:
            pid = item.ordered_product_id
            product_item_map.setdefault(pid, []).append({
                "id": item.id_ordered_item,
                "quantity": item.ordered_quantity,
            })

        consumption_map: Dict[int, List[Dict]] = {}
        for item in consumptions:
            pid = item.consumed_product_id
            matching_source = None
            if pid in reservation_plan:
                for source in reservation_plan[pid].get("sources", []):
                    if source.get("type") == "consumption" and source.get("id") == item.resource_req_ref:
                        matching_source = source
                        break
            consumption_map.setdefault(pid, []).append({
                "id": item.id_product_consumption,
                "quantity": matching_source.get("quantity") if matching_source else 0,
            })

        for product_id, _plan in reservation_plan.items():
            for item in product_item_map.get(product_id, []):
                ordered_reserve_items.append({
                    "id": item["id"],
                    "quantity": item["quantity"],
                    "item_type": "ordered_item",
                })
            for consumption in consumption_map.get(product_id, []):
                consumption_reserve_items.append({
                    "id": consumption["id"],
                    "quantity": consumption["quantity"],
                    "item_type": "consumption",
                })

        if ordered_reserve_items:
            await self.inventory_client.reserve_inventory(
                items=ordered_reserve_items,
                item_type="ordered_item",
            )
            logger.info(f"✅ Successfully reserved {len(ordered_reserve_items)} ordered items")

        if consumption_reserve_items:
            try:
                await self.inventory_client.reserve_inventory(
                    items=consumption_reserve_items,
                    item_type="consumption",
                )
                logger.info(f"✅ Successfully reserved {len(consumption_reserve_items)} consumptions")
            except Exception:
                if ordered_reserve_items:
                    try:
                        await self.inventory_client.release_inventory(
                            items=ordered_reserve_items,
                            item_type="ordered_item",
                        )
                    except Exception as release_error:
                        logger.error(f"Failed to release ordered items: {release_error}")
                raise

        logger.info("✅ Inventory reservation completed successfully")

    # ==================== Persist cart ====================

    async def _persist_cart(
        self,
        cart: Cart,
        total_price: float,
        person_obj: Optional[Any],
    ) -> Tuple[Cart, List[OrderedItem], List[OrderedService], Invoice]:
        invoice = Invoice(
            invoice_total_amount=total_price,
            invoice_status="unpaid",
            invoice_issue_date=datetime.now().date(),
            invoice_due_date=datetime.now().date() + timedelta(days=30),
            invoice_type="invoice",
            invoice_tax_applied=19,
        )
        created_invoice = self.invoice_repo.create_invoice(invoice)
        logger.info(f"✅ Created invoice: {created_invoice.invoice_id}")

        cart.cart_invoice = created_invoice.invoice_id
        cart = self.cart_repo.create_cart(cart)
        logger.info(f"Cart created with ID: {cart.cart_id}")

        created_items = []
        for ordered_item in cart.ordered_item:
            ordered_item.ordered_item_cart_ref = cart.cart_id
            created_item = self.order_repo.create_order_item(ordered_item)
            created_items.append(created_item)
            logger.info(f"Created ordered item ID: {created_item.id_ordered_item}")

        created_services = []
        for ordered_service in cart.ordered_service:
            ordered_service.ordered_service_cart_id = cart.cart_id
            created_service = self.cart_repo.create_ordered_service(ordered_service)
            created_services.append(created_service)
            logger.info(f"Created ordered service ID: {created_service.ordered_service_id}")

        cart.ordered_item = created_items
        cart.ordered_service = created_services

        return cart, created_items, created_services, created_invoice

    # ==================== Entities / loading ====================

    async def _validate_entities(self, provider_id: int, seller_user_id: int, buyer_user_id: int) -> None:
        provider = self.supplier_repo.get_supplier_by_id(provider_id)
        if not provider:
            raise CartSupplierNotFoundException(provider_id=provider_id)

        selling_user = self.user_repo.get_by_id(seller_user_id)
        if not selling_user:
            raise CartSellerNotFoundException(seller_id=seller_user_id)

        if buyer_user_id > 0:
            buyer_user = self.user_repo.get_by_id(buyer_user_id)
            if not buyer_user:
                raise CartBuyerNotFoundException(buyer_id=buyer_user_id)

    async def _load_products_and_services(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
    ) -> Tuple[Dict[int, Any], Dict[int, Any]]:
        product_ids = [item.ordered_product_id for item in ordered_items]
        service_ids = [service.ordered_service_service_id for service in ordered_services]

        products: Dict[int, Any] = {}
        if product_ids:
            product_list = self.product_repo.get_products_by_ids(product_ids)
            products = {p.id_product: p for p in product_list}
            if len(products) != len(set(product_ids)):
                missing = set(product_ids) - set(products.keys())
                raise CartProductNotFoundException(product_id=next(iter(missing)))

        services: Dict[int, Any] = {}
        if service_ids:
            service_list = self.service_repo.get_services_by_ids(service_ids)
            services = {s.provided_service_id: s for s in service_list}
            if len(services) != len(set(service_ids)):
                missing = set(service_ids) - set(services.keys())
                raise ServiceNotFoundException(service_id=next(iter(missing)))

        return products, services

    async def _build_reservation_plan(
        self,
        ordered_items: List[OrderedItem_API],
        ordered_services: List[OrderedService_API],
        products: Dict[int, Any],
        services: Dict[int, Any],
    ) -> Tuple[Dict[int, Dict], Dict[int, Dict]]:
        reservation_plan: Dict[int, Dict] = {}
        item_details: Dict[int, Dict] = {}

        for item in ordered_items:
            product_id = item.ordered_product_id
            product = products.get(product_id)
            if not product:
                continue

            quantity = item.ordered_quantity
            reservation_plan.setdefault(product_id, {"quantity": 0, "sources": []})
            reservation_plan[product_id]["quantity"] += quantity
            reservation_plan[product_id]["sources"].append({
                "type": "ordered_item",
                "id": getattr(item, "id_ordered_item", 0),
                "quantity": quantity,
            })

            item_details.setdefault(product_id, {
                "unit_price": self._safe_float(product.product_price),
                "product": product,
            })

        for service_api in ordered_services:
            service_id = service_api.ordered_service_service_id
            if service_id not in services:
                continue

            resource_requirements = self.service_repo.get_service_resource_requirements(service_id)
            for requirement in resource_requirements or []:
                if not requirement.service_resource_requirement_is_consumable:
                    continue

                product_id = requirement.service_resource_requirement_product_ref
                quantity_needed = (
                    self._safe_float(requirement.service_resource_requirement_quantity)
                    * service_api.ordered_service_quantity
                )

                reservation_plan.setdefault(product_id, {"quantity": 0, "sources": []})
                reservation_plan[product_id]["quantity"] += quantity_needed
                reservation_plan[product_id]["sources"].append({
                    "type": "consumption",
                    "service_id": service_id,
                    "id": requirement.service_resource_requirement_id,
                    "quantity": quantity_needed,
                })

                if product_id not in item_details:
                    product = self.product_repo.get_product_by_id(product_id)
                    if product:
                        item_details[product_id] = {
                            "unit_price": self._safe_float(product.product_price),
                            "product": product,
                        }

        return reservation_plan, item_details

    # ==================== Rollback / update / delete ====================

    async def _rollback_cart_creation(
        self,
        cart: Optional[Cart],
        created_items: List[OrderedItem] = None,
    ) -> None:
        if not cart:
            return

        logger.info(f"🔄 Rolling back cart creation for cart {cart.cart_id}")

        try:
            items_to_release = []
            if cart.ordered_item:
                for item in cart.ordered_item:
                    items_to_release.append({
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id,
                    })
            elif created_items:
                for item in created_items:
                    items_to_release.append({
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id,
                    })

            if items_to_release:
                try:
                    await self.inventory_client.release_inventory(
                        items=items_to_release,
                        item_type="ordered_item",
                    )
                    logger.info("✅ Inventory released")
                except Exception as e:
                    logger.error(f"Failed to release inventory: {e}")

            self.cart_repo.delete_cart_sync(cart)
            logger.info("✅ Cart deleted during rollback")

        except Exception as e:
            logger.error(f"Rollback failed: {e}")

    def update_cart_status(self, cart_id: int, new_status: str) -> Cart:
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
                fields_attempted=["cart_status"],
            )

    async def delete_cart(self, cart_id: int, force_delete: bool = False) -> bool:
        logger.info(f"Deleting cart {cart_id} (force={force_delete})")

        try:
            cart = self.get_cart_by_id(cart_id)
        except CartNotFoundException:
            logger.warning(f"Cart with ID {cart_id} not found")
            raise

        try:
            ordered_items = list(cart.ordered_item) if cart.ordered_item else []

            if ordered_items:
                release_items = [
                    {
                        "id": item.id_ordered_item,
                        "quantity": item.ordered_quantity,
                        "product_id": item.ordered_product_id,
                    }
                    for item in ordered_items
                ]
                await self.inventory_client.release_inventory(
                    items=release_items,
                    item_type="ordered_item",
                )
                logger.info("✅ Inventory released")

            result = self.cart_repo.delete_cart_by_id_sync(cart_id)
            logger.info(f"Cart {cart_id} deleted successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to delete cart {cart_id}: {e}")
            raise CartDeleteFailedException(cart_id=cart_id, error=str(e))