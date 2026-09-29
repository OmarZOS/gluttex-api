# policies/__init__.py
"""
Entity policies built on the generic TransitionEngine.

Every policy exposes:
    normalize(state)                      — case handling
    is_valid(state)                       — membership
    is_terminal(state)                    — no outgoing edges
    allowed_targets(current)              — possible next states
    can_transition(current, target, ctx?) — silent boolean
    decide(current, target, ctx?)         — full Decision object
    assert_transition(current, target, ctx?) — raises on denial
    assert_valid(state)                   — raises on unknown state

The context dict is free-form. Every predicate is a callable
    (context) -> bool
that receives at least {"current": ..., "target": ...}. Callers add
whatever else the predicate needs — amounts, flags, sibling entity states,
user roles.
"""

from policies.transitions import (
    Decision,
    PolicyBase,
    Predicate,
    Transition,
    TransitionEngine,
    TransitionRegistry,
    always,
)
from policies.order_policy import OrderPolicy
from policies.payment_policy import PaymentPolicy
from policies.invoice_policy import InvoicePolicy
from policies.ordered_item_policy import OrderedItemPolicy

__all__ = [
    # Engine primitives
    'Transition',
    'TransitionRegistry',
    'TransitionEngine',
    'PolicyBase',
    'Predicate',
    'Decision',
    'always',

    # Concrete policies
    'OrderPolicy',
    'PaymentPolicy',
    'InvoicePolicy',
    'OrderedItemPolicy',
]