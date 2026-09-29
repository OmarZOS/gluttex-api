# routers/business_routers/delivery_router.py
"""
Delivery router — business operations only.

Each action optionally accepts a Delivery_API body. Its real fields are
applied as a patch before the transition; its signal fields
(delivery_confirmed, proof_captured, ...) are forwarded to the policy.
Signals never persist — they're `exclude=True` on the model, and
apply_patch filters them out.
"""

from fastapi import APIRouter, Depends, Query, Body, status, HTTPException
from typing import Optional, List, Any, Dict
import logging

from core.models.api_models import Delivery_API
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.delivery_exceptions import (
    DeliveryNotFoundException,
    DeliveryUpdateFailedException,
    DeliveryStatusInvalidException,
)
from services.delivery_service import DeliveryService
from workflows.delivery_workflow import DeliveryWorkflow

logger = logging.getLogger(__name__)

delivery_router = APIRouter()


# ============================================================================
# Dependency providers
# ============================================================================

def get_delivery_service() -> DeliveryService:
    return DeliveryService()


def get_delivery_workflow() -> DeliveryWorkflow:
    try:
        from services.order_workflow import OrderWorkflow
        order_wf = OrderWorkflow()
    except Exception:
        order_wf = None
    return DeliveryWorkflow(order_workflow=order_wf)


TARGET_STATUSES = {
    "processing", "confirmed", "shipped", "in_transit",
    "out_for_delivery", "delivered",
    "failed", "cancelled", "returned", "refunded",
}

# Signal fields on Delivery_API the policy consumes. Single source of
# truth for the router's signal extractor.
SIGNAL_FIELDS = (
    "delivery_confirmed",
    "in_transit_acknowledged",
    "proof_captured",
    "failure_reported",
    "return_confirmed",
    "refund_completed",
)


# ============================================================================
# Shared plumbing
# ============================================================================

def _extract_signals(body: Optional[Delivery_API]) -> Dict[str, Any]:
    """
    Pull only the non-None signal fields off the body. Absent fields
    are simply not forwarded, so predicates keep their own defaults.
    """
    if body is None:
        return {}
    signals: Dict[str, Any] = {}
    for name in SIGNAL_FIELDS:
        value = getattr(body, name, None)
        if value is not None:
            signals[name] = value
    return signals


def _run_transition(
    delivery_id: int,
    action_label: str,
    workflow: DeliveryWorkflow,
    target: str,
    body: Optional[Delivery_API] = None,
) -> dict:
    """
    Apply an optional Delivery_API patch, then run the policy-gated
    transition. Signals embedded in the body flow into the policy.
    """
    if body is not None:
        workflow.apply_patch(delivery_id, body)

    signals = _extract_signals(body)

    try:
        return workflow.transition_status(delivery_id, target, **signals)
    except DeliveryNotFoundException:
        raise
    except DeliveryUpdateFailedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "transition_not_allowed",
                "action": action_label,
                "reason": str(e),
            },
        )


# ============================================================================
# READ
# ============================================================================

@delivery_router.get(
    "",
    summary="List deliveries",
    description=(
        "List deliveries filtered by provider, source, or status. "
        "At least one filter is required."
    ),
    responses={
        200: {"description": "Deliveries retrieved successfully"},
        **get_crud_error_responses(include_404=False),
    },
)
def list_deliveries(
    provider_id: int = Query(0, description="Filter by provider"),
    source_type: Optional[str] = Query(
        None, description="'placed_order' or 'cart'"
    ),
    source_id: int = Query(0, description="Filter by source ID"),
    delivery_status: Optional[str] = Query(
        None, alias="status", description="Filter by lifecycle status"
    ),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: DeliveryService = Depends(get_delivery_service),
):
    if not any([provider_id, source_id, delivery_status]):
        raise DeliveryStatusInvalidException(
            requested_status="<none>",
            allowed_statuses=sorted(TARGET_STATUSES),
        )

    if delivery_status:
        normalized = delivery_status.lower()
        if normalized not in TARGET_STATUSES:
            raise DeliveryStatusInvalidException(
                requested_status=delivery_status,
                allowed_statuses=sorted(TARGET_STATUSES),
            )
    else:
        normalized = None

    logger.info(
        f"List deliveries provider={provider_id} "
        f"source={source_type}:{source_id} status={normalized}"
    )
    return service.get_all_deliveries(
        provider_id=provider_id,
        order_id=source_id if source_type == "placed_order" else 0,
        broker_id=0,
        offset=offset,
        limit=limit,
    )


@delivery_router.get(
    "/{delivery_id}",
    summary="Get a delivery",
    responses={
        200: {"description": "Delivery retrieved successfully"},
        **get_crud_error_responses(include_404=True),
    },
)
def get_delivery(
    delivery_id: int,
    service: DeliveryService = Depends(get_delivery_service),
):
    return service.get_delivery_by_id(delivery_id, eager_load=True)


@delivery_router.get(
    "/{delivery_id}/next-states",
    summary="Which states can this delivery move to?",
    description=(
        "Return the set of legal next states according to "
        "DeliveryPolicy. The client uses this to render available "
        "actions; the server still enforces the policy on the actual "
        "transition request."
    ),
    responses={
        200: {"description": "Next states returned"},
        **get_crud_error_responses(include_404=True),
    },
)
def get_delivery_next_states(
    delivery_id: int,
    service: DeliveryService = Depends(get_delivery_service),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    delivery = service.get_delivery_by_id(delivery_id, eager_load=False)
    current = (delivery.delivery_status or "").lower()
    allowed = workflow.policy.allowed_targets(current)
    return {
        "delivery_id": delivery_id,
        "current_status": current,
        "next_states": sorted(allowed),
    }


# ============================================================================
# OPS — lifecycle transitions
# ============================================================================
#
# Uniform shape: POST /delivery/{id}/<action> with an optional
# Delivery_API body. Body fields patch the delivery; signal fields
# flow into the policy.
# ============================================================================


@delivery_router.post(
    "/{delivery_id}/accept",
    summary="Accept a delivery for handling",
    description=(
        "pending → processing. Optional body may carry a patch "
        "(e.g. delivery_package_count, delivery_total_weight)."
    ),
    responses={
        200: {"description": "Delivery accepted"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def accept_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "accept", workflow,
        target="processing",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/confirm",
    summary="Confirm the delivery is packed and ready",
    description=(
        "processing → confirmed. The typical use of the body here is "
        "to declare package count, weight, and dimensions at "
        "confirmation time."
    ),
    responses={
        200: {"description": "Delivery confirmed"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def confirm_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "confirm", workflow,
        target="confirmed",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/ship",
    summary="Ship the delivery",
    description=(
        "confirmed → shipped. Set `delivery_confirmed=true` on the "
        "body to assert the carrier accepted the handoff. Optional "
        "patch fields (merchant name, cargo dimensions) apply first."
    ),
    responses={
        200: {"description": "Delivery shipped"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def ship_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "ship", workflow,
        target="shipped",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/in-transit",
    summary="Mark the delivery in transit",
    description=(
        "shipped → in_transit. Set `in_transit_acknowledged=true` to "
        "assert the carrier ack'd the last leg."
    ),
    responses={
        200: {"description": "Delivery in transit"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def mark_in_transit(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "in_transit", workflow,
        target="in_transit",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/out-for-delivery",
    summary="Mark the delivery out for delivery",
    description="in_transit → out_for_delivery.",
    responses={
        200: {"description": "Delivery out for delivery"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def mark_out_for_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "out_for_delivery", workflow,
        target="out_for_delivery",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/deliver",
    summary="Mark the delivery delivered",
    description=(
        "out_for_delivery → delivered. Set `proof_captured=true` to "
        "assert proof of delivery was collected. Triggers inventory "
        "confirmation and order advancement when applicable."
    ),
    responses={
        200: {"description": "Delivery delivered"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def deliver_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "deliver", workflow,
        target="delivered",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/cancel",
    summary="Cancel the delivery",
    description=(
        "Move to `cancelled` from any pre-shipment state. Releases "
        "reserved inventory."
    ),
    responses={
        200: {"description": "Delivery cancelled"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def cancel_delivery(
    delivery_id: int,
    reason: Optional[str] = Query(None, description="Free-text reason"),
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    result = _run_transition(
        delivery_id, "cancel", workflow,
        target="cancelled",
        body=body,
    )
    if reason:
        result["reason"] = reason
    return result


@delivery_router.post(
    "/{delivery_id}/fail",
    summary="Report the delivery as failed",
    description=(
        "processing / in_transit / out_for_delivery → failed. Set "
        "`failure_reported=true` to assert an incident was filed."
    ),
    responses={
        200: {"description": "Delivery failed"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def fail_delivery(
    delivery_id: int,
    reason: Optional[str] = Query(None, description="Failure reason"),
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    result = _run_transition(
        delivery_id, "fail", workflow,
        target="failed",
        body=body,
    )
    if reason:
        result["reason"] = reason
    return result


@delivery_router.post(
    "/{delivery_id}/return",
    summary="Mark the delivery returned",
    description=(
        "delivered or failed → returned. Set `return_confirmed=true` "
        "to assert the goods came back."
    ),
    responses={
        200: {"description": "Delivery returned"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def return_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "return", workflow,
        target="returned",
        body=body,
    )


@delivery_router.post(
    "/{delivery_id}/refund",
    summary="Refund the delivery",
    description=(
        "delivered → refunded. Set `refund_completed=true` to assert "
        "the finance-side refund was issued."
    ),
    responses={
        200: {"description": "Delivery refunded"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def refund_delivery(
    delivery_id: int,
    body: Optional[Delivery_API] = Body(None),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return _run_transition(
        delivery_id, "refund", workflow,
        target="refunded",
        body=body,
    )


# ============================================================================
# OPS — non-state attributes
# ============================================================================


@delivery_router.post(
    "/{delivery_id}/tracking-pings",
    summary="Record a tracking ping",
    description="Append a tracking position to the delivery.",
    responses={
        200: {"description": "Tracking recorded"},
        404: {"model": ErrorResponseModel},
    },
)
def record_tracking_ping(
    delivery_id: int,
    current_address_id: int = Query(...),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return workflow.update_tracking(delivery_id, current_address_id)


@delivery_router.post(
    "/{delivery_id}/reroute",
    summary="Re-route the delivery",
    description=(
        "Change the destination address. Only legal before the "
        "delivery is out for delivery; later calls return 409."
    ),
    responses={
        200: {"description": "Delivery re-routed"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def reroute_delivery(
    delivery_id: int,
    address_id: int = Query(...),
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
):
    return workflow.update_address(delivery_id, address_id)


@delivery_router.post(
    "/{delivery_id}/archive",
    summary="Archive a delivery",
    description=(
        "Soft-remove a delivery from the active queue. Only legal "
        "from a terminal state."
    ),
    responses={
        200: {"description": "Delivery archived"},
        404: {"model": ErrorResponseModel},
        409: {"model": ErrorResponseModel},
    },
)
def archive_delivery(
    delivery_id: int,
    workflow: DeliveryWorkflow = Depends(get_delivery_workflow),
    service: DeliveryService = Depends(get_delivery_service),
):
    delivery = service.get_delivery_by_id(delivery_id, eager_load=False)
    current = (delivery.delivery_status or "").lower()

    terminal = {"delivered", "cancelled", "returned", "refunded"}
    if current not in terminal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "not_terminal",
                "current_status": current,
                "message": (
                    "Only terminal deliveries can be archived. "
                    "Finish or cancel the delivery first."
                ),
            },
        )
    return workflow.delete_delivery(delivery_id, force_delete=False)