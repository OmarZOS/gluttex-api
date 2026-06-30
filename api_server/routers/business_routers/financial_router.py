# routers/financial_router.py
"""
Financial router for managing payments, deposits, and fees.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.models.api_models import Payment_API, Deposit_API, AdditionalFee_API
from core.response_models import ErrorResponseModel, get_crud_error_responses
from core.exceptions.specific.finance_exceptions import (
    PaymentNotFoundException,
    PaymentCreationFailedException,
    DepositNotFoundException,
    DepositCreationFailedException,
    FeeCreationFailedException,
    InvoiceNotFoundException,
    FeeNotFoundException
)
from services.financial_service import FinancialService

logger = logging.getLogger(__name__)

financial_router = APIRouter()


def get_financial_service() -> FinancialService:
    """Dependency to get FinancialService instance"""
    return FinancialService()


# ==================== Payment Endpoints ====================

@financial_router.post(
    "/payments",
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description="Create a payment",
    responses={
        201: {"description": "Payment created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_payment(
    payment: Payment_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create a payment.
    """
    logger.info(f"Creating payment for invoice: {payment.payment_invoice_id}")
    return financial_service.create_payment(payment)


@financial_router.post(
    "/deposits",
    status_code=status.HTTP_201_CREATED,
    # response_model=Deposit_API,
    summary="Create deposit",
    description="Create a deposit",
    responses={
        201: {"description": "Deposit created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_deposit(
    deposit: Deposit_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create a deposit.
    """
    logger.info(f"Creating deposit for cart: {deposit.deposit_cart_id}")
    return financial_service.create_deposit(deposit)


@financial_router.post(
    "/fees",
    status_code=status.HTTP_201_CREATED,
    # response_model=AdditionalFee_API,
    summary="Create fee",
    description="Create an additional fee",
    responses={
        201: {"description": "Fee created successfully"},
        400: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_fee(
    fee: AdditionalFee_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create an additional fee.
    """
    logger.info(f"Creating fee for provider: {fee.additional_fee_on_provider_id}")
    return financial_service.create_fee(fee)


# ==================== Payment Query Endpoints ====================

@financial_router.get(
    "/payments",
    # response_model=List[Payment_API],
    summary="Get payments",
    description="Get payments with filters",
    responses={
        200: {"description": "Payments retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_payments(
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return (max 1000)"),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get payments with filters.
    """
    logger.info(f"Fetching payments - invoice_id:{invoice_id}, offset:{offset}, limit:{limit}")
    return financial_service.get_payments(invoice_id, offset, limit)


@financial_router.get(
    "/payments/{payment_id}",
    # response_model=Payment_API,
    summary="Get payment by ID",
    description="Get a specific payment by its ID",
    responses={
        200: {"description": "Payment retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_payment_by_id(
    payment_id: int,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get payment by ID.
    """
    logger.info(f"Fetching payment with ID: {payment_id}")
    
    result = financial_service.get_payment_by_id(payment_id)
    if not result:
        raise PaymentNotFoundException(payment_id=payment_id)
    
    return result


# ==================== Deposit Query Endpoints ====================

@financial_router.get(
    "/deposits",
    # response_model=List[Deposit_API],
    summary="Get deposits",
    description="Get deposits with filters",
    responses={
        200: {"description": "Deposits retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_deposits(
    cart_id: Optional[int] = Query(None, description="Filter by cart ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return (max 1000)"),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get deposits with filters.
    """
    logger.info(f"Fetching deposits - cart_id:{cart_id}, offset:{offset}, limit:{limit}")
    return financial_service.get_deposits(cart_id, offset, limit)


@financial_router.get(
    "/deposits/{deposit_id}",
    # response_model=Deposit_API,
    summary="Get deposit by ID",
    description="Get a specific deposit by its ID",
    responses={
        200: {"description": "Deposit retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_deposit_by_id(
    deposit_id: int,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get deposit by ID.
    """
    logger.info(f"Fetching deposit with ID: {deposit_id}")
    
    result = financial_service.get_deposit_by_id(deposit_id)
    if not result:
        raise DepositNotFoundException(deposit_id=deposit_id)
    
    return result


# ==================== Fee Query Endpoints ====================

@financial_router.get(
    "/fees",
    # response_model=List[AdditionalFee_API],
    summary="Get fees",
    description="Get additional fees with filters",
    responses={
        200: {"description": "Fees retrieved successfully"},
        **get_crud_error_responses(include_404=False)
    }
)
def get_fees(
    provider_id: Optional[int] = Query(None, description="Filter by provider ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return (max 1000)"),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get additional fees with filters.
    """
    logger.info(f"Fetching fees - provider_id:{provider_id}, user_id:{user_id}, offset:{offset}, limit:{limit}")
    return financial_service.get_fees(provider_id, user_id, offset, limit)


@financial_router.get(
    "/fees/{fee_id}",
    # response_model=AdditionalFee_API,
    summary="Get fee by ID",
    description="Get a specific additional fee by its ID",
    responses={
        200: {"description": "Fee retrieved successfully"},
        **get_crud_error_responses(include_404=True)
    }
)
def get_fee_by_id(
    fee_id: int,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get fee by ID.
    """
    logger.info(f"Fetching fee with ID: {fee_id}")
    
    result = financial_service.get_fee_by_id(fee_id)
    if not result:
        raise FeeNotFoundException(fee_id=fee_id)
    
    return result