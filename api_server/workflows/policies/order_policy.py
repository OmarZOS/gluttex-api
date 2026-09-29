# policies/order_policy.py
"""
OrderPolicy — PlacedOrder status rules, built on TransitionEngine.

Every edge carries its own predicate. Predicates receive a context dict:

    {
        "current":           "PENDING",
        "target":            "PROCESSING",
        # plus whatever the caller passes:
        "payment_paid":      True,
        "inventory_reserved": True,
        "user_role":         "admin",
        ...
    }
"""

from typing import Any, Mapping

from policies.transitions import (
    Decision,
    PolicyBase,
    Transition,
    TransitionRegistry,
)


# ============================================================================
# PREDICATES — one function per rule, named after the rule.
# ============================================================================

def payment_confirmed(ctx: Mapping[str, Any]) -> bool:
    """PENDING → PROCESSING requires the invoice to be paid."""
    return bool(ctx.get('payment_paid'))


def inventory_released(ctx: Mapping[str, Any]) -> bool:
    """Any → CANCELLED requires released reservations."""
    return bool(ctx.get('inventory_released', True))


def delivery_confirmed(ctx: Mapping[str, Any]) -> bool:
    """PROCESSING → SHIPPED requires a confirmed delivery."""
    return bool(ctx.get('delivery_confirmed', True))


def delivery_delivered(ctx: Mapping[str, Any]) -> bool:
    """SHIPPED → DELIVERED requires the delivery to be DELIVERED."""
    return bool(ctx.get('delivery_delivered', True))


def refund_settled(ctx: Mapping[str, Any]) -> bool:
    """Any → REFUNDED requires a completed refund."""
    return bool(ctx.get('refund_completed', True))


# ============================================================================
# POLICY
# ============================================================================

class OrderPolicy(PolicyBase):
    """
    PlacedOrder status rules.

    States: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED, REFUNDED
    """

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'PENDING', 'PROCESSING', 'SHIPPED',
                'DELIVERED', 'CANCELLED', 'REFUNDED',
            },
            initial_state='PENDING',
            terminal_states={'CANCELLED', 'REFUNDED'},
            normalize=lambda s: (s or 'PENDING').upper(),
        )

        registry.add_many([
            # ── PENDING ─────────────────────────────────────────────
            Transition(
                source='PENDING',
                target='PROCESSING',
                predicate=payment_confirmed,
                side_effects=('payment_confirmed', 'delivery_may_start'),
                name='pending_to_processing',
            ),
            Transition(
                source='PENDING',
                target='CANCELLED',
                predicate=inventory_released,
                side_effects=(
                    'release_inventory', 'cancel_invoice',
                    'refund_if_paid',
                ),
                name='pending_to_cancelled',
            ),

            # ── PROCESSING ──────────────────────────────────────────
            Transition(
                source='PROCESSING',
                target='SHIPPED',
                predicate=delivery_confirmed,
                side_effects=('delivery_in_transit',),
                name='processing_to_shipped',
            ),
            Transition(
                source='PROCESSING',
                target='CANCELLED',
                predicate=inventory_released,
                side_effects=(
                    'release_inventory', 'cancel_invoice',
                    'refund_if_paid',
                ),
                name='processing_to_cancelled',
            ),

            # ── SHIPPED ─────────────────────────────────────────────
            Transition(
                source='SHIPPED',
                target='DELIVERED',
                predicate=delivery_delivered,
                side_effects=('delivery_delivered', 'confirm_inventory'),
                name='shipped_to_delivered',
            ),
            Transition(
                source='SHIPPED',
                target='CANCELLED',
                predicate=inventory_released,
                side_effects=(
                    'release_inventory', 'cancel_invoice',
                    'refund_if_paid',
                ),
                name='shipped_to_cancelled',
            ),
            Transition(
                source='SHIPPED',
                target='REFUNDED',
                predicate=refund_settled,
                side_effects=('refund_payment', 'return_inventory'),
                name='shipped_to_refunded',
            ),

            # ── DELIVERED ───────────────────────────────────────────
            Transition(
                source='DELIVERED',
                target='REFUNDED',
                predicate=refund_settled,
                side_effects=('refund_payment', 'return_inventory'),
                name='delivered_to_refunded',
            ),
        ])

        return registry

    # ── Domain error mapping ─────────────────────────────────────────

    def transition_error(self, decision: Decision) -> Exception:
        from core.exceptions.specific.order_exceptions import (
            InvalidOrderStatusException,
            OrderStatusTransitionException,
        )
        if not self.is_valid(decision.target):
            return InvalidOrderStatusException(
                status=decision.target,
                valid_statuses=sorted(self.valid_states),
            )
        return OrderStatusTransitionException(
            current_status=decision.current,
            new_status=decision.target,
            allowed_transitions=sorted(
                self.allowed_targets(decision.current)
            ),
        )

    def invalid_state_error(self, state: str) -> Exception:
        from core.exceptions.specific.order_exceptions import (
            InvalidOrderStatusException,
        )
        return InvalidOrderStatusException(
            status=state,
            valid_statuses=sorted(self.valid_states),
        )