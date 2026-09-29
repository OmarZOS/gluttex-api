# policies/delivery_policy.py
"""
DeliveryPolicy — Delivery status rules, built on TransitionEngine.

States (from the `delivery_status` enum on the `Delivery` model):
    pending, processing, confirmed, shipped, in_transit,
    out_for_delivery, delivered, failed, cancelled, returned, refunded

Transitions (from the state diagram):

    pending          → processing
    processing       → confirmed
    confirmed        → shipped
    shipped          → in_transit
    in_transit       → out_for_delivery
    out_for_delivery → delivered
    delivered        → returned
    delivered        → refunded

    pending          → cancelled
    processing       → cancelled
    confirmed        → cancelled
    shipped          → cancelled

    processing       → failed
    in_transit       → failed
    out_for_delivery → failed
    failed           → returned

Predicates take a `Delivery` instance directly. Extra values a rule needs
(reroute confirmation, return confirmation, etc.) come in as keyword
arguments on `decide(...)` and flow through to the predicate.

Note: `delivery_status` on the DB is lowercase, but the diagram uses
UPPERCASE labels. The policy normalizes to lowercase on input and keeps
that case throughout.
"""

from typing import Any, Optional

from core.models.models import Delivery

from policies.transitions import (
    Decision,
    PolicyBase,
    Transition,
    TransitionRegistry,
)


# ============================================================================
# PREDICATES
# ============================================================================

def has_destination(delivery: Delivery) -> bool:
    """pending → processing: a destination must be set before dispatch prep."""
    return bool(
        delivery.delivery_address_id
        or delivery.delivery_current_address_id
        or delivery.recipient_person
        or delivery.recipient_provider
    )


def has_packages(delivery: Delivery) -> bool:
    """processing → confirmed: at least one package must be declared."""
    count = delivery.delivery_package_count or 0
    return int(count) > 0


def has_provider(delivery: Delivery) -> bool:
    """confirmed → shipped: a provider must be attached to hand off."""
    return bool(delivery.delivery_provider_id)


def has_broker_or_provider(delivery: Delivery) -> bool:
    """shipped → in_transit: either a broker or the provider moves it."""
    return bool(delivery.delivery_broker_id or delivery.delivery_provider_id)


def in_transit_acknowledged(
    delivery: Delivery, *, in_transit_acknowledged: bool = True
) -> bool:
    """in_transit → out_for_delivery: the courier acknowledges the last leg."""
    return in_transit_acknowledged


def delivery_proof_captured(
    delivery: Delivery, *, proof_captured: bool = True
) -> bool:
    """out_for_delivery → delivered: recipient signature / proof of delivery."""
    return proof_captured


def failure_reported(
    delivery: Delivery, *, failure_reported: bool = True
) -> bool:
    """processing/in_transit/out_for_delivery → failed: an incident was filed."""
    return failure_reported


def return_confirmed(
    delivery: Delivery, *, return_confirmed: bool = True
) -> bool:
    """delivered/failed → returned: goods came back to origin."""
    return return_confirmed


def refund_settled(
    delivery: Delivery, *, refund_completed: bool = True
) -> bool:
    """delivered → refunded: the finance side has issued the refund."""
    return refund_completed


def cancellable(delivery: Delivery) -> bool:
    """
    * → cancelled: cancellable only before the goods leave the warehouse.
    Once `shipped`, the delivery is in motion — cancel via `failed` or
    `returned`, not `cancelled`.
    """
    status = (delivery.delivery_status or '').lower()
    return status in {'pending', 'processing', 'confirmed'}


# ============================================================================
# POLICY
# ============================================================================

class DeliveryPolicy(PolicyBase):
    """Delivery status rules."""

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'pending',
                'processing',
                'confirmed',
                'shipped',
                'in_transit',
                'out_for_delivery',
                'delivered',
                'failed',
                'cancelled',
                'returned',
                'refunded',
            },
            initial_state='pending',
            terminal_states={'cancelled', 'returned', 'refunded'},
            normalize=lambda s: (s or 'pending').lower(),
        )

        registry.add_many([
            # ── pending ─────────────────────────────────────────────
            Transition(
                source='pending',
                target='processing',
                predicate=has_destination,
                side_effects=('prepare_dispatch',),
                name='pending_to_processing',
            ),
            Transition(
                source='pending',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_delivery_slot',),
                name='pending_to_cancelled',
            ),

            # ── processing ──────────────────────────────────────────
            Transition(
                source='processing',
                target='confirmed',
                predicate=has_packages,
                side_effects=('assign_provider',),
                name='processing_to_confirmed',
            ),
            Transition(
                source='processing',
                target='failed',
                predicate=failure_reported,
                side_effects=('report_incident', 'notify_user'),
                name='processing_to_failed',
            ),
            Transition(
                source='processing',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_delivery_slot',),
                name='processing_to_cancelled',
            ),

            # ── confirmed ───────────────────────────────────────────
            Transition(
                source='confirmed',
                target='shipped',
                predicate=has_provider,
                side_effects=('hand_off_to_provider',),
                name='confirmed_to_shipped',
            ),
            Transition(
                source='confirmed',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_delivery_slot',),
                name='confirmed_to_cancelled',
            ),

            # ── shipped ─────────────────────────────────────────────
            Transition(
                source='shipped',
                target='in_transit',
                predicate=has_broker_or_provider,
                side_effects=('broadcast_in_transit',),
                name='shipped_to_in_transit',
            ),
            Transition(
                source='shipped',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_delivery_slot',),
                name='shipped_to_cancelled',
            ),

            # ── in_transit ──────────────────────────────────────────
            Transition(
                source='in_transit',
                target='out_for_delivery',
                predicate=in_transit_acknowledged,
                side_effects=('notify_recipient',),
                name='in_transit_to_out_for_delivery',
            ),
            Transition(
                source='in_transit',
                target='failed',
                predicate=failure_reported,
                side_effects=('report_incident', 'notify_user'),
                name='in_transit_to_failed',
            ),

            # ── out_for_delivery ────────────────────────────────────
            Transition(
                source='out_for_delivery',
                target='delivered',
                predicate=delivery_proof_captured,
                side_effects=('capture_proof', 'notify_recipient'),
                name='out_for_delivery_to_delivered',
            ),
            Transition(
                source='out_for_delivery',
                target='failed',
                predicate=failure_reported,
                side_effects=('report_incident', 'notify_user'),
                name='out_for_delivery_to_failed',
            ),

            # ── delivered ───────────────────────────────────────────
            Transition(
                source='delivered',
                target='returned',
                predicate=return_confirmed,
                side_effects=('restock_delivery', 'refund_if_paid'),
                name='delivered_to_returned',
            ),
            Transition(
                source='delivered',
                target='refunded',
                predicate=refund_settled,
                side_effects=('refund_delivery_fee',),
                name='delivered_to_refunded',
            ),

            # ── failed ──────────────────────────────────────────────
            Transition(
                source='failed',
                target='returned',
                predicate=return_confirmed,
                side_effects=('restock_delivery',),
                name='failed_to_returned',
            ),
        ])

        return registry

    # ── Convenience ──────────────────────────────────────────────────

    def decide_for_delivery(
        self,
        delivery: Delivery,
        target: str,
        **extras: Any,
    ) -> Decision:
        """Decide using the delivery's own status as the current state."""
        current = delivery.delivery_status or self.initial_state
        return self.decide(current, target, delivery, **extras)

    def is_final(self, state: str) -> bool:
        """Delivered is the success terminal; others are terminal too."""
        return self.normalize(state) in {
            'delivered', 'cancelled', 'returned', 'refunded',
        }

    def is_in_flight(self, state: str) -> bool:
        """Physical goods are moving — cancellation is off the table."""
        return self.normalize(state) in {
            'shipped', 'in_transit', 'out_for_delivery',
        }

    def is_cancellable(self, delivery: Delivery) -> bool:
        return cancellable(delivery)

    # ── Error mapping ────────────────────────────────────────────────

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal delivery transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid delivery status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )