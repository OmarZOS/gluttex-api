# policies/payment_policy.py
"""
PaymentPolicy — Payment status rules, built on TransitionEngine.

Payment uses lowercase states. Predicates enforce gateway/capture rules.
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

def gateway_charge_started(ctx: Mapping[str, Any]) -> bool:
    """pending → processing requires the gateway charge to be in flight."""
    return bool(ctx.get('charge_started', True))


def full_amount_captured(ctx: Mapping[str, Any]) -> bool:
    """processing/partial → completed requires the full amount captured."""
    return bool(ctx.get('amount_captured_fully', True))


def partial_amount_captured(ctx: Mapping[str, Any]) -> bool:
    """processing → partial requires some but not all captured."""
    return bool(ctx.get('amount_captured_partially', True))


def gateway_failed(ctx: Mapping[str, Any]) -> bool:
    """* → failed requires the gateway to have returned a failure."""
    return bool(ctx.get('gateway_failed', True))


def cancellable(ctx: Mapping[str, Any]) -> bool:
    """Any → cancelled requires no completed settlement."""
    return not bool(ctx.get('settled', False))


# ============================================================================
# POLICY
# ============================================================================

class PaymentPolicy(PolicyBase):
    """
    Payment status rules.
    States: pending, processing, completed, partial, failed, cancelled
    """

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'pending', 'processing', 'completed',
                'partial', 'failed', 'cancelled',
            },
            initial_state='pending',
            terminal_states={'completed', 'cancelled'},
            normalize=lambda s: (s or 'pending').lower(),
        )

        registry.add_many([
            Transition(
                source='pending',
                target='processing',
                predicate=gateway_charge_started,
                side_effects=('gateway_charge_started',),
                name='pending_to_processing',
            ),
            Transition(
                source='pending',
                target='failed',
                predicate=gateway_failed,
                side_effects=('notify_user',),
                name='pending_to_failed',
            ),
            Transition(
                source='pending',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_gateway_hold',),
                name='pending_to_cancelled',
            ),

            Transition(
                source='processing',
                target='completed',
                predicate=full_amount_captured,
                side_effects=('invoice_mark_paid', 'order_advance'),
                name='processing_to_completed',
            ),
            Transition(
                source='processing',
                target='partial',
                predicate=partial_amount_captured,
                side_effects=('invoice_mark_partially_paid',),
                name='processing_to_partial',
            ),
            Transition(
                source='processing',
                target='failed',
                predicate=gateway_failed,
                side_effects=('notify_user',),
                name='processing_to_failed',
            ),
            Transition(
                source='processing',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_gateway_hold',),
                name='processing_to_cancelled',
            ),

            Transition(
                source='partial',
                target='completed',
                predicate=full_amount_captured,
                side_effects=('invoice_mark_paid', 'order_advance'),
                name='partial_to_completed',
            ),
            Transition(
                source='partial',
                target='failed',
                predicate=gateway_failed,
                side_effects=('notify_user',),
                name='partial_to_failed',
            ),
            Transition(
                source='partial',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_gateway_hold',),
                name='partial_to_cancelled',
            ),

            Transition(
                source='failed',
                target='cancelled',
                predicate=lambda ctx: True,
                side_effects=(),
                name='failed_to_cancelled',
            ),
        ])

        return registry

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal payment transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid payment status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )