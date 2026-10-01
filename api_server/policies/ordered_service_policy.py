# policies/ordered_service_policy.py
"""
OrderedServicePolicy — OrderedService status rules, built on TransitionEngine.

States (from `ordered_service_delivery_status` enum):
    pending, processing, scheduled, in_progress, completed, cancelled, no_show

Transitions (from the state diagram):

    pending      → processing
    processing   → scheduled
    scheduled    → in_progress
    in_progress  → completed

    pending      → cancelled
    processing   → cancelled
    scheduled    → cancelled

    scheduled    → no_show
    in_progress  → no_show

Predicates take an `OrderedService` instance directly. External signals
(staff assigned, appointment confirmed, attendance marked, etc.) come in
as keyword arguments on `decide(...)`.

The service carries a `scheduled_at` timestamp and a quantity. Predicates
read them off the instance. Any rule that depends on the parent cart or
on the referenced `ProvidedService` is expressed by the caller as a
keyword argument — the policy does not traverse relationships.
"""

from typing import Any
from datetime import datetime

from core.models.models import OrderedService

from policies.transitions import (
    Decision,
    PolicyBase,
    Transition,
    TransitionRegistry,
)


# ============================================================================
# PREDICATES
# ============================================================================

def has_positive_quantity(service: OrderedService) -> bool:
    """Any forward transition needs at least one unit booked."""
    return (service.ordered_service_quantity or 0) > 0


def staff_assigned(
    service: OrderedService, *, staff_assigned: bool = False
) -> bool:
    """pending → processing: a provider resource is attached."""
    return staff_assigned


def has_scheduled_at(
    service: OrderedService, *, scheduled_at: Any = None
) -> bool:
    """
    processing → scheduled: the service carries a scheduled time.

    Prefers the `scheduled_at` keyword argument (allows a caller to set it
    as part of the transition), falls back to the column value on the
    instance.
    """
    if scheduled_at is not None:
        return True
    return service.ordered_service_scheduled_at is not None


def scheduled_in_past(
    service: OrderedService, *, now: Any = None
) -> bool:
    """
    scheduled → in_progress: the scheduled time has arrived. Comparison
    uses `now` when supplied, otherwise the wall clock.
    """
    scheduled = service.ordered_service_scheduled_at
    if scheduled is None:
        return False
    reference = now or datetime.utcnow()
    return scheduled <= reference


def attendance_confirmed(
    service: OrderedService, *, attendance_confirmed: bool = False
) -> bool:
    """
    in_progress → completed: the service was actually delivered to the
    customer. Confirmed by the provider on-site.
    """
    return attendance_confirmed


def cancellable(service: OrderedService) -> bool:
    """
    * → cancelled: only before the appointment begins. Once
    `in_progress`, the customer is on-site — a no-show from that point
    doesn't exist; they're already there.
    """
    status = (service.ordered_service_delivery_status or '').lower()
    return status in {'pending', 'processing', 'scheduled'}


def no_show_reported(
    service: OrderedService, *, no_show_reported: bool = False
) -> bool:
    """
    scheduled/in_progress → no_show: the customer did not attend the
    appointment. Only meaningful after the scheduled time has passed.
    """
    if not no_show_reported:
        return False
    scheduled = service.ordered_service_scheduled_at
    if scheduled is None:
        return False
    return scheduled <= datetime.utcnow()


# ============================================================================
# POLICY
# ============================================================================

class OrderedServicePolicy(PolicyBase):
    """OrderedService status rules."""

    def _build_registry(self) -> TransitionRegistry:
        registry = TransitionRegistry(
            valid_states={
                'pending',
                'processing',
                'scheduled',
                'in_progress',
                'completed',
                'cancelled',
                'no_show',
            },
            initial_state='pending',
            terminal_states={'completed', 'cancelled', 'no_show'},
            normalize=lambda s: (s or 'pending').lower(),
        )

        registry.add_many([
            # ── pending ─────────────────────────────────────────────
            Transition(
                source='pending',
                target='processing',
                predicate=lambda s, **kw: (
                    has_positive_quantity(s) and staff_assigned(s, **kw)
                ),
                side_effects=('reserve_resource',),
                name='pending_to_processing',
            ),
            Transition(
                source='pending',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_resource',),
                name='pending_to_cancelled',
            ),

            # ── processing ──────────────────────────────────────────
            Transition(
                source='processing',
                target='scheduled',
                predicate=has_scheduled_at,
                side_effects=('notify_customer', 'book_calendar'),
                name='processing_to_scheduled',
            ),
            Transition(
                source='processing',
                target='cancelled',
                predicate=cancellable,
                side_effects=('release_resource',),
                name='processing_to_cancelled',
            ),

            # ── scheduled ───────────────────────────────────────────
            Transition(
                source='scheduled',
                target='in_progress',
                predicate=scheduled_in_past,
                side_effects=('start_service',),
                name='scheduled_to_in_progress',
            ),
            Transition(
                source='scheduled',
                target='cancelled',
                predicate=cancellable,
                side_effects=(
                    'release_resource',
                    'notify_customer',
                ),
                name='scheduled_to_cancelled',
            ),
            Transition(
                source='scheduled',
                target='no_show',
                predicate=no_show_reported,
                side_effects=('notify_customer', 'apply_no_show_policy'),
                name='scheduled_to_no_show',
            ),

            # ── in_progress ─────────────────────────────────────────
            Transition(
                source='in_progress',
                target='completed',
                predicate=attendance_confirmed,
                side_effects=(
                    'consume_resources',
                    'close_service',
                ),
                name='in_progress_to_completed',
            ),
            Transition(
                source='in_progress',
                target='no_show',
                predicate=no_show_reported,
                side_effects=('notify_customer', 'apply_no_show_policy'),
                name='in_progress_to_no_show',
            ),
        ])

        return registry

    # ── Convenience ──────────────────────────────────────────────────

    def decide_for_service(
        self,
        service: OrderedService,
        target: str,
        **extras: Any,
    ) -> Decision:
        """Decide using the service's own status as the current state."""
        current = service.ordered_service_delivery_status or self.initial_state
        return self.decide(current, target, service, **extras)

    def is_final(self, state: str) -> bool:
        """Completed, cancelled, or no-show — the appointment is resolved."""
        return self.normalize(state) in {
            'completed', 'cancelled', 'no_show',
        }

    def is_active(self, state: str) -> bool:
        """Not yet resolved: pending, processing, scheduled, or in progress."""
        return self.normalize(state) in {
            'pending', 'processing', 'scheduled', 'in_progress',
        }

    def is_cancellable(self, service: OrderedService) -> bool:
        return cancellable(service)

    def is_appointment_reached(self, service: OrderedService) -> bool:
        """Scheduled time has passed and the appointment is still open."""
        scheduled = service.ordered_service_scheduled_at
        if scheduled is None:
            return False
        status = (service.ordered_service_delivery_status or '').lower()
        return status in {'scheduled', 'in_progress'} and scheduled <= datetime.utcnow()

    # ── Error mapping ────────────────────────────────────────────────

    def transition_error(self, decision: Decision) -> Exception:
        return ValueError(
            f"Illegal ordered-service transition '{decision.current}' → "
            f"'{decision.target}': {decision.reason}"
        )

    def invalid_state_error(self, state: str) -> Exception:
        return ValueError(
            f"Invalid ordered-service status '{state}'. "
            f"Valid: {sorted(self.valid_states)}"
        )