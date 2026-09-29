# policies/cart_policy.py
"""
CartPolicy — Cart status rules, built on TransitionEngine.

States (from `cart_status` enum, stored lowercase):
    open, pending, completed, canceled, partial, checkout, abandoned

Transitions (from the state diagram):

    open       → pending
    open       → abandoned
    open       → canceled

    pending    → checkout
    pending    → partial
    pending    → canceled

    checkout   → completed
    checkout   → partial

    partial    → completed
    partial    → canceled

    abandoned  → open

Predicates take a `Cart` instance directly. External signals
(invoice issued, delivery created, item fulfilled, etc.) come in as
keyword arguments on `decide(...)`.

Note on `checkout`: it is a *transient* state — the invoice has been
issued and the delivery has been created, but the money and the goods
haven't moved yet. From `checkout` the cart either resolves to
`completed` (paid and fulfilled) or falls back to `partial` (only some
of the contents were fulfilled). It cannot go straight to `canceled`:
once an invoice exists, cancellation must go through the invoice, which
then brings the cart back via `pending → canceled` or by failing to
checkout and being reset to `pending`. See `cancelable` below.
"""

from typing import Any

from core.models.models import Cart

from policies.transitions import (
    Decision,
    PolicyBase,
    Transition,
    TransitionRegistry,
)


# ============================================================================
# PREDICATES
# ============================================================================

def has_items(cart: Cart) -> bool:
    """
    open → pending: a cart with no line items (items or services) cannot
    move to pending. Reads both relationships so a services-only cart
    still qualifies.
    """
    items = getattr(cart, 'ordered_item', None) or []
    services = getattr(cart, 'ordered_service', None) or []
    return (len(items) + len(services)) > 0


def has_provider(cart: Cart) -> bool:
    """open → pending: a cart must be scoped to a provider."""
    return bool(cart.cart_product_provider_id)


def cart_stale(
    cart: Cart, *, stale: bool = False
) -> bool:
    """
    open/pending → abandoned: only stale carts are auto-abandoned.
    Defaults to False — the caller must assert the staleness.
    """
    return stale


def checkout_ready(
    cart: Cart, *, invoice_issued: bool = False, delivery_created: bool = False
) -> bool:
    """
    pending → checkout: an invoice exists and a delivery has been
    created. Both must be true for the cart to enter checkout.
    """
    return invoice_issued and delivery_created


def partial_fulfilment(
    cart: Cart, *, partially_fulfilled: bool = False
) -> bool:
    """
    pending/checkout → partial: only some of the cart's contents were
    fulfilled (some items delivered, some refunded, etc.).
    """
    return partially_fulfilled


def fully_fulfilled(
    cart: Cart, *, fully_fulfilled: bool = False
) -> bool:
    """
    checkout/partial → completed: every line item has been delivered
    (or the remaining items explicitly cancelled with the invoice
    settled).
    """
    return fully_fulfilled


def cancellable(cart: Cart) -> bool:
    """
    * → canceled: only before checkout. Once an invoice exists
    (status == 'checkout'), cancellation flows through the invoice, not
    the cart.
    """
    status = (cart.cart_status or '').lower()
    return status in {'open', 'pending', 'partial'}


# ============================================================================
# POLICY
# ============================================================================

class CartPolicy(PolicyBase):
    """Cart status rules."""

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'open',
                'pending',
                'checkout',
                'completed',
                'partial',
                'canceled',
                'abandoned',
            },
            initial_state='open',
            terminal_states={'completed', 'canceled'},
            normalize=lambda s: (s or 'open').lower(),
        )

        registry.add_many([
            # ── open ────────────────────────────────────────────────
            Transition(
                source='open',
                target='pending',
                predicate=lambda cart, **_: (
                    has_items(cart) and has_provider(cart)
                ),
                side_effects=('lock_prices',),
                name='open_to_pending',
            ),
            Transition(
                source='open',
                target='abandoned',
                predicate=cart_stale,
                side_effects=('archive_cart',),
                name='open_to_abandoned',
            ),
            Transition(
                source='open',
                target='canceled',
                predicate=cancellable,
                side_effects=('release_slot',),
                name='open_to_canceled',
            ),

            # ── pending ─────────────────────────────────────────────
            Transition(
                source='pending',
                target='checkout',
                predicate=checkout_ready,
                side_effects=('invoice_issued', 'delivery_created'),
                name='pending_to_checkout',
            ),
            Transition(
                source='pending',
                target='partial',
                predicate=partial_fulfilment,
                side_effects=('split_fulfilment',),
                name='pending_to_partial',
            ),
            Transition(
                source='pending',
                target='canceled',
                predicate=cancellable,
                side_effects=(
                    'cancel_invoice_if_any',
                    'release_inventory',
                ),
                name='pending_to_canceled',
            ),

            # ── checkout ────────────────────────────────────────────
            Transition(
                source='checkout',
                target='completed',
                predicate=fully_fulfilled,
                side_effects=(
                    'close_invoice',
                    'confirm_inventory',
                ),
                name='checkout_to_completed',
            ),
            Transition(
                source='checkout',
                target='partial',
                predicate=partial_fulfilment,
                side_effects=('split_fulfilment',),
                name='checkout_to_partial',
            ),

            # ── partial ─────────────────────────────────────────────
            Transition(
                source='partial',
                target='completed',
                predicate=fully_fulfilled,
                side_effects=(
                    'close_invoice',
                    'confirm_remaining_inventory',
                ),
                name='partial_to_completed',
            ),
            Transition(
                source='partial',
                target='canceled',
                predicate=cancellable,
                side_effects=(
                    'cancel_remaining_invoice',
                    'release_remaining_inventory',
                    'refund_completed_portion',
                ),
                name='partial_to_canceled',
            ),

            # ── abandoned ───────────────────────────────────────────
            Transition(
                source='abandoned',
                target='open',
                predicate=lambda cart, **_: True,
                side_effects=('reopen_cart',),
                name='abandoned_to_open',
            ),
        ])

        return registry

    # ── Convenience ──────────────────────────────────────────────────

    def decide_for_cart(
        self,
        cart: Cart,
        target: str,
        **extras: Any,
    ) -> Decision:
        """Decide using the cart's own status as the current state."""
        current = cart.cart_status or self.initial_state
        return self.decide(current, target, cart, **extras)

    def is_final(self, state: str) -> bool:
        """Completed or canceled — no more line-item changes."""
        return self.normalize(state) in {'completed', 'canceled'}

    def is_active(self, state: str) -> bool:
        """A cart that's still being built or waiting on something."""
        return self.normalize(state) in {'open', 'pending', 'checkout', 'partial'}

    def is_cancellable(self, cart: Cart) -> bool:
        return cancellable(cart)

    def is_checkout_pending(self, cart: Cart) -> bool:
        """Invoice issued, fulfilment not yet resolved."""
        return self.normalize(cart.cart_status or '') == 'checkout'

    def is_fulfillable(self, cart: Cart) -> bool:
        """Checkout or partial — fulfilment is in progress."""
        return self.normalize(cart.cart_status or '') in {'checkout', 'partial'}

    # ── Error mapping ────────────────────────────────────────────────

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal cart transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid cart status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )