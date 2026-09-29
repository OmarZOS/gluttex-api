# services/order_workflow.py
"""
Order workflow — orchestration layer.

Owns every call that crosses a process boundary:
  - InventoryServiceClient (availability, reserve, confirm, release)
  - FinanceServiceClient    (create payment, confirm payment)

Owns the sequencing of the three phases:
  Phase 1  create_order
  Phase 2  process_payment
  Phase 3  confirm_inventory_for_order
  Finalize finalize_order  → Phase 2 + Phase 3

Owns remote failure handling: when a remote call fails after local
persistence, the workflow asks the service to roll back local entities and
asks the inventory client to release reservations.

OrderService (local) is injected. No remote clients live on the service.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from storage.wrappers.finance_client import FinanceServiceClient
from storage.wrappers.inventory_client import InventoryServiceClient
from core.models.api_models import Delivery_Info_API, OrderedItem_API, PlacedOrder_API
from core.models.models import PlacedOrder, OrderedItem, Invoice, Delivery
from core.exceptions.specific.product_exceptions import (
    ProductQuantityNotEnoughException,
)
from services.order_service import OrderService

logger = logging.getLogger(__name__)


class OrderWorkflow:
    """
    Orchestration around OrderService.

    The workflow never touches repositories directly, and the service never
    touches remote clients. Every cross-boundary call goes through this
    class.
    """

    def __init__(
        self,
        service: Optional[OrderService] = None,
        inventory_client: Optional[InventoryServiceClient] = None,
        finance_client: Optional[FinanceServiceClient] = None,
    ):
        self.service = service or OrderService()
        self.inventory_client = inventory_client or InventoryServiceClient()
        self.finance_client = finance_client or FinanceServiceClient()

    # ================================================================
    # PHASE 1 — CREATE ORDER
    # ================================================================

    async def create_order(
        self,
        items: List[OrderedItem_API],
        order_data: PlacedOrder_API,
        payment_method: str = 'card',
        user_id: Optional[int] = None,
        delivery_data: Optional[Delivery_Info_API] = None,
    ) -> Tuple[List[int], PlacedOrder, Dict[str, Any]]:
        """
        Phase 1 orchestration:
          1. local: resolve user (via service)
          2. remote: check inventory availability
          3. local: persist order entities (via service)
          4. remote: reserve inventory
          5. on remote failure after persist: rollback local + release remote
        """
        logger.info(
            f"Creating new order for user: {order_data.ordering_user_id}"
        )

        # Local: user resolution happens inside persist, but we resolve early
        ordering_user = self.service.user_repo.get_by_id(
            order_data.ordering_user_id
        )
        if not ordering_user:
            from core.exceptions.handler import UserNotFoundException
            raise UserNotFoundException(user_id=order_data.ordering_user_id)

        if not user_id:
            user_id = order_data.ordering_user_id

        created_order: Optional[PlacedOrder] = None
        created_invoice: Optional[Invoice] = None
        created_items: List[OrderedItem] = []
        created_deliveries: List[Delivery] = []
        inventory_reserved = False

        try:
            # Step 1 — remote read-only availability check
            logger.info("Step 1: Checking inventory availability...")
            await self._check_inventory_availability(items)

            # Step 2 — local persist
            logger.info("Step 2: Persisting order entities...")
            (
                created_order,
                created_items,
                created_invoice,
                created_deliveries,
            ) = self.service.persist_order_entities(
                items=items,
                order_data=order_data,
                user_id=user_id,
                delivery_data=delivery_data,
            )

            # Step 3 — remote reservation
            logger.info("Step 3: Reserving inventory...")
            await self._reserve_inventory(created_items)
            inventory_reserved = True
            logger.info("✅ Inventory reserved successfully")

            result = {
                'order_id': created_order.id_placed_order,
                'invoice_id': created_invoice.invoice_id,
                'payment_id': None,
                'payment_status': None,
                'inventory_reserved': True,
                'inventory_deducted': False,
            }
            logger.info(
                f"✅ Order {created_order.id_placed_order} created "
                f"(payment and inventory confirmation are pending)"
            )
            return (
                [p.ordered_quantity for p in created_items],
                created_order,
                result,
            )

        except Exception as e:
            logger.error(f"Order creation failed: {e}")

            # Remote: release reservation if it succeeded
            if inventory_reserved and created_items:
                await self._safe_release_inventory(created_items)

            # Local: delete entities
            self.service.rollback_entities(
                order=created_order,
                invoice=created_invoice,
                items=created_items,
                deliveries=created_deliveries,
            )
            raise

    # ================================================================
    # PHASE 2 — PROCESS PAYMENT
    # ================================================================

    async def process_payment(
        self,
        order_id: int,
        payment_method: str = 'card',
        transaction_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Phase 2 orchestration:
          1. local: load order + invoice, idempotency check
          2. remote: create payment
          3. remote: confirm payment
          4. local: mark invoice paid, advance order state
        """
        logger.info(f"Processing payment for order {order_id}...")

        # Step 1 — local reads + idempotency
        order = self.service.get_order_by_id(order_id, with_items=True)
        invoice = self.service.get_invoice_for_order(order)

        if invoice.invoice_status == 'paid':
            logger.info(f"Order {order_id} invoice already paid — skipping")
            return {
                'order_id': order_id,
                'invoice_id': invoice.invoice_id,
                'payment_id': None,
                'payment_status': 'paid',
            }

        # Step 2 — remote create payment
        payment_payload = self.service.build_payment_create_payload(
            order=order,
            invoice=invoice,
            payment_method=payment_method,
        )
        payment_response = await self.finance_client.create_payment(
            payment_payload
        )
        logger.info(f"✅ Payment created: {payment_response.id}")

        # Step 3 — remote confirm payment
        details = (
            transaction_details
            or self.service.build_payment_transaction_details(
                order=order,
                invoice=invoice,
                payment_method=payment_method,
            )
        )
        confirmed_payment = await self.finance_client.confirm_payment(
            payment_id=payment_response.id,
            transaction_details=details,
        )
        logger.info(
            f"✅ Payment {confirmed_payment.id} confirmed "
            f"(status={confirmed_payment.status})"
        )

        # Step 4 — local state updates
        self.service.mark_invoice_paid(invoice)
        self.service.advance_order_after_payment(order)

        return {
            'order_id': order.id_placed_order,
            'invoice_id': invoice.invoice_id,
            'payment_id': confirmed_payment.id,
            'payment_status': confirmed_payment.status,
        }

    # ================================================================
    # PHASE 3 — CONFIRM INVENTORY
    # ================================================================

    async def confirm_inventory_for_order(
        self, order_id: int
    ) -> Dict[str, Any]:
        """
        Phase 3 orchestration (by order id):
          1. local: load order items
          2. remote: confirm inventory
        Idempotent — the silo ignores already-confirmed items.
        """
        logger.info(f"Confirming inventory for order {order_id}...")

        order = self.service.get_order_by_id(order_id, with_items=True)
        items = list(order.ordered_item or [])
        if not items:
            logger.info(f"Order {order_id} has no items to confirm")
            return {
                'order_id': order_id,
                'items_confirmed': 0,
                'success': True,
            }

        return await self.confirm_inventory_for_items(
            items, order_id=order_id
        )

    async def confirm_inventory_for_items(
        self,
        ordered_items: List[Any],
        *,
        order_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Phase 3 orchestration (by items):
          1. local: normalize items
          2. remote: confirm inventory
        Accepts ORM objects or dicts. Used by the delivery flow when only a
        subset of items is being confirmed.
        """
        confirm_items = self.service.build_confirm_payload(ordered_items)

        if not confirm_items:
            label = f"order {order_id}" if order_id is not None else "items"
            logger.info(f"No items to confirm for {label}")
            return {
                'order_id': order_id,
                'items_confirmed': 0,
                'success': True,
            }

        confirm_response = await self.inventory_client.confirm_inventory(
            items=confirm_items,
            item_type='ordered_item',
        )

        if isinstance(confirm_response, dict):
            if not confirm_response.get('success', True):
                raise Exception(
                    f"Inventory confirmation failed: {confirm_response}"
                )

        label = f"order {order_id}" if order_id is not None else "items"
        logger.info(f"✅ Inventory confirmed for {label}")
        return {
            'order_id': order_id,
            'items_confirmed': len(confirm_items),
            'success': True,
        }

    # ================================================================
    # CONVENIENCE — FINALIZE (phases 2 + 3)
    # ================================================================

    async def finalize_order(
        self,
        order_id: int,
        payment_method: str = 'card',
        transaction_details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payment_result = await self.process_payment(
            order_id=order_id,
            payment_method=payment_method,
            transaction_details=transaction_details,
        )
        inventory_result = await self.confirm_inventory_for_order(order_id)
        return {
            **payment_result,
            **inventory_result,
            'inventory_deducted': True,
        }

    # ================================================================
    # REMOTE HELPERS (all HTTP calls live here)
    # ================================================================

    async def _check_inventory_availability(
        self, items: List[OrderedItem_API]
    ) -> None:
        """Remote: read-only bulk availability check."""
        product_ids = [item.ordered_product_id for item in items]

        availability_response = (
            await self.inventory_client.get_bulk_stock_status(
                product_ids=product_ids
            )
        )
        stock_by_product = self.service.parse_inventory_response(
            availability_response
        )
        logger.info(f"Stock data: {stock_by_product}")

        for item in items:
            product_id = item.ordered_product_id
            stock_status = stock_by_product.get(str(product_id), {})
            available_qty = stock_status.get('available_quantity', 0)

            logger.info(
                f"Product {product_id}: available={available_qty}, "
                f"requested={item.ordered_quantity}"
            )

            if available_qty < item.ordered_quantity:
                raise ProductQuantityNotEnoughException(
                    product_id=product_id,
                    requested=item.ordered_quantity,
                    available=available_qty,
                )

        logger.info("✅ Inventory availability check passed")

    async def _reserve_inventory(
        self, items: List[OrderedItem]
    ) -> None:
        """Remote: reserve inventory for persisted items."""
        reserve_items = self.service.build_reserve_payload(items)

        reserve_response = await self.inventory_client.reserve_inventory(
            items=reserve_items,
            item_type='ordered_item',
        )

        if isinstance(reserve_response, dict):
            if not reserve_response.get('success', True):
                raise Exception(
                    f"Inventory reservation failed: {reserve_response}"
                )
            success_count = reserve_response.get(
                'success_count', len(items)
            )
            if success_count == 0:
                raise Exception(
                    "Inventory reservation failed: no items reserved"
                )

    async def _safe_release_inventory(
        self, items: List[OrderedItem]
    ) -> None:
        """Remote: best-effort release during rollback. Never raises."""
        try:
            release_items = self.service.build_reserve_payload(items)
            await self.inventory_client.release_inventory(
                items=release_items,
                item_type='ordered_item',
            )
            logger.info("✅ Inventory released")
        except Exception as e:
            logger.error(f"Failed to release inventory: {e}")

    # ================================================================
    # DELETE ORDER (remote release + local delete)
    # ================================================================

    async def delete_order(self, order_id: int) -> bool:
        """
        Orchestrates: load items → release remote inventory → delete local.
        """
        logger.info(f"Deleting order with ID: {order_id}")
        order = self.service.get_order_by_id(order_id, with_items=True)

        release_items = self.service.build_reserve_payload(
            list(order.ordered_item or [])
        )
        if release_items:
            await self._safe_release_inventory(list(order.ordered_item or []))

        return self.service.delete_order(order_id)