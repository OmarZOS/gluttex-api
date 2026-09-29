# policies/invoice_policy.py
"""
InvoicePolicy — Invoice status rules, built on TransitionEngine.
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

def has_partial_payment(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('has_partial_payment', True))


def full_payment_received(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('full_payment_received', True))


def is_overdue(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('is_overdue', True))


def no_payment_received(ctx: Mapping[str, Any]) -> bool:
    """unpaid → canceled only if no partial payment exists."""
    return not bool(ctx.get('has_partial_payment', False))


def refund_completed(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('refund_completed', True))


def partial_refund_completed(ctx: Mapping[str, Any]) -> bool:
    return bool(ctx.get('partial_refund_completed', True))


# ============================================================================
# POLICY
# ============================================================================

class InvoicePolicy(PolicyBase):
    """
    Invoice status rules.
    States: unpaid, partially_paid, paid, overdue, canceled, refunded
    """

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'unpaid', 'partially_paid', 'paid',
                'overdue', 'canceled', 'refunded',
            },
            initial_state='unpaid',
            terminal_states={'canceled', 'refunded'},
            normalize=lambda s: (s or 'unpaid').lower(),
        )

        registry.add_many([
            # ── unpaid ──────────────────────────────────────────────
            Transition(
                source='unpaid',
                target='partially_paid',
                predicate=has_partial_payment,
                side_effects=('record_partial_payment',),
                name='unpaid_to_partially_paid',
            ),
            Transition(
                source='unpaid',
                target='paid',
                predicate=full_payment_received,
                side_effects=('order_advance', 'delivery_may_start'),
                name='unpaid_to_paid',
            ),
            Transition(
                source='unpaid',
                target='overdue',
                predicate=is_overdue,
                side_effects=('notify_user', 'apply_late_fee_policy'),
                name='unpaid_to_overdue',
            ),
            Transition(
                source='unpaid',
                target='canceled',
                predicate=no_payment_received,
                side_effects=('release_inventory',),
                name='unpaid_to_canceled',
            ),

            # ── partially_paid ──────────────────────────────────────
            Transition(
                source='partially_paid',
                target='paid',
                predicate=full_payment_received,
                side_effects=('order_advance', 'delivery_may_start'),
                name='partial_to_paid',
            ),
            Transition(
                source='partially_paid',
                target='overdue',
                predicate=is_overdue,
                side_effects=('notify_user',),
                name='partial_to_overdue',
            ),
            Transition(
                source='partially_paid',
                target='canceled',
                predicate=partial_refund_completed,
                side_effects=('refund_partial_payment',),
                name='partial_to_canceled',
            ),

            # ── overdue ─────────────────────────────────────────────
            Transition(
                source='overdue',
                target='paid',
                predicate=full_payment_received,
                side_effects=('order_advance',),
                name='overdue_to_paid',
            ),
            Transition(
                source='overdue',
                target='canceled',
                predicate=lambda ctx: True,
                side_effects=('write_off',),
                name='overdue_to_canceled',
            ),

            # ── paid ────────────────────────────────────────────────
            Transition(
                source='paid',
                target='refunded',
                predicate=refund_completed,
                side_effects=('order_refund', 'delivery_refund'),
                name='paid_to_refunded',
            ),
        ])

        return registry

    # ── Domain queries ───────────────────────────────────────────────

    def is_settled(self, state: str) -> bool:
        return self.normalize(state) in {'paid', 'refunded'}

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal invoice transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid invoice status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )