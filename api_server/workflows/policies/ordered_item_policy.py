# policies/ordered_item_policy.py
"""
OrderedItemPolicy — OrderedItem status rules, built on TransitionEngine.
"""

from typing import Any, Mapping

from policies.transitions import (
    Decision,
    PolicyBase,
    Transition,
    TransitionRegistry,
)


# ============================================================================
# PREDICATES
# ============================================================================

def inventory_reserved(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('inventory_reserved', True))


def delivery_assigned(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('delivery_assigned', True))


def delivery_confirmed(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('delivery_confirmed', True))


def delivery_delivered(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('delivery_delivered', True))


def split_confirmed(ctx: Mapping[str, Any]) -> bool:
    """pending/processing/shipped → partial requires explicit split."""
    return bool(ctx.get('split_confirmed', True))


def partial_fully_delivered(ctx: Mapping[str, Any]) -> bool:
    """partial → delivered requires the remainder to have shipped."""
    return bool(ctx.get('partial_fully_delivered', True))


def return_received(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('return_received', True))


def cancellable(ctx: Mapping[str, Any]) -> bool:
    return not bool(ctx.get('already_delivered', False))


# ============================================================================
# POLICY
# ============================================================================

class OrderedItemPolicy(PolicyBase):
    """
    OrderedItem status rules.
    States: pending, processing, shipped, delivered, cancelled, returned, partial
    """

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'pending', 'processing', 'shipped', 'delivered',
                'cancelled', 'returned', 'partial',
            },
            initial_state='pending',
            terminal_states={'cancelled', 'returned'},
            normalize=lambda s: (s or 'pending').lower(),
        )

        registry.add_many([
            # ── pending ─────────────────────────────────────────────
            Transition(
                source='pending',
                target='processing',
                predicate=inventory_reserved,
                side_effects=('assign_picker',),
                name='pending_to_processing',
            ),
            Transition(
                source='pending',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_item_inventory',),
                name='pending_to_cancelled',
            ),
            Transition(
                source='pending',
                target='partial',
                predicate=split_confirmed,
                side_effects=('split_item',),
                name='pending_to_partial',
            ),

            # ── processing ──────────────────────────────────────────
            Transition(
                source='processing',
                target='shipped',
                predicate=delivery_assigned,
                side_effects=('hand_off_to_delivery',),
                name='processing_to_shipped',
            ),
            Transition(
                source='processing',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_item_inventory',),
                name='processing_to_cancelled',
            ),
            Transition(
                source='processing',
                target='partial',
                predicate=split_confirmed,
                side_effects=('split_item',),
                name='processing_to_partial',
            ),

            # ── shipped ─────────────────────────────────────────────
            Transition(
                source='shipped',
                target='delivered',
                predicate=delivery_delivered,
                side_effects=('confirm_item_inventory',),
                name='shipped_to_delivered',
            ),
            Transition(
                source='shipped',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_item_inventory',),
                name='shipped_to_cancelled',
            ),
            Transition(
                source='shipped',
                target='partial',
                predicate=split_confirmed,
                side_effects=('split_item',),
                name='shipped_to_partial',
            ),

            # ── partial ─────────────────────────────────────────────
            Transition(
                source='partial',
                target='delivered',
                predicate=partial_fully_delivered,
                side_effects=('confirm_remaining_inventory',),
                name='partial_to_delivered',
            ),
            Transition(
                source='partial',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_remaining_inventory',),
                name='partial_to_cancelled',
            ),

            # ── delivered ───────────────────────────────────────────
            Transition(
                source='delivered',
                target='returned',
                predicate=return_received,
                side_effects=('restock_item', 'refund_item_if_paid'),
                name='delivered_to_returned',
            ),
        ])

        return registry

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal ordered-item transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid ordered-item status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )