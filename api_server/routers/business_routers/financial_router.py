# routers/financial_router.py
"""
Financial router for managing payments, deposits, and fees.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.api_models import Payment_API, Deposit_API, AdditionalFee_API
from core.response_models import (
    SuccessResponseModel,
    PaginatedResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)
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

financial_router = APIRouter(
    # tags=["financial"],
    # prefix="/api/financial"
)


def get_financial_service() -> FinancialService:
    """Dependency to get FinancialService instance"""
    return FinancialService()


# ==================== Payment Endpoints ====================

@financial_router.post(
    "/payments",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create payment",
    description="Create a payment",
    responses={
        201: {
            "description": "Payment created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid payment data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Invoice not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_payment(
    payment: Payment_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create a payment.
    
    - **payment**: Payment details (request body)
    """
    logger.info(f"Creating payment for invoice: {payment.payment_invoice_id}")
    
    result = financial_service.create_payment(payment)
    
    payment_id = getattr(result, 'payment_id', None)
    
    return SuccessResponseModel(
        success=True,
        message="Payment created successfully",
        data=result,
        details={
            "payment_id": payment_id,
            "amount": payment.payment_amount,
            "status": payment.payment_status,
            "invoice_id": payment.payment_invoice_id
        }
    )


@financial_router.post(
    "/deposits",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create deposit",
    description="Create a deposit",
    responses={
        201: {
            "description": "Deposit created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid deposit data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Cart not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_deposit(
    deposit: Deposit_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create a deposit.
    
    - **deposit**: Deposit details (request body)
    """
    logger.info(f"Creating deposit for cart: {deposit.deposit_cart_id}")
    
    result = financial_service.create_deposit(deposit)
    
    deposit_id = getattr(result, 'deposit_id', None)
    
    return SuccessResponseModel(
        success=True,
        message="Deposit created successfully",
        data=result,
        details={
            "deposit_id": deposit_id,
            "amount": deposit.deposit_amount,
            "cart_id": deposit.deposit_cart_id
        }
    )


@financial_router.post(
    "/fees",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create fee",
    description="Create an additional fee",
    responses={
        201: {
            "description": "Fee created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid fee data",
            "model": ErrorResponseModel
        },
        404: {
            "description": "Not Found - Provider not found",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True, include_409=True)
    }
)
def create_fee(
    fee: AdditionalFee_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Create an additional fee.
    
    - **fee**: Fee details (request body)
    """
    logger.info(f"Creating fee for provider: {fee.additional_fee_on_provider_id}")
    
    result = financial_service.create_fee(fee)
    
    fee_id = getattr(result, 'additional_fee_id', None)
    
    return SuccessResponseModel(
        success=True,
        message="Fee created successfully",
        data=result,
        details={
            "fee_id": fee_id,
            "name": fee.additional_fee_name,
            "amount": fee.additional_fee_amount,
            "provider_id": fee.additional_fee_on_provider_id
        }
    )


# ==================== Payment Query Endpoints ====================

@financial_router.get(
    "/payments",
    response_model=SuccessResponseModel,
    summary="Get payments",
    description="Get payments with filters",
    responses={
        200: {
            "description": "Payments retrieved successfully",
            "model": SuccessResponseModel
        },
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
    
    - **invoice_id**: Filter by invoice ID (query parameter)
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter)
    """
    logger.info(f"Fetching payments - invoice_id:{invoice_id}, offset:{offset}, limit:{limit}")
    
    result = financial_service.get_payments(invoice_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} payments",
        details={
            "filters": {
                "invoice_id": invoice_id
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result) if isinstance(result, list) else 0
            }
        }
    )


@financial_router.get(
    "/payments/{payment_id}",
    response_model=SuccessResponseModel,
    summary="Get payment by ID",
    description="Get a specific payment by its ID",
    responses={
        200: {
            "description": "Payment retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_payment_by_id(
    payment_id: int,  # Path parameter - NO Query()
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get payment by ID.
    
    - **payment_id**: Payment ID to fetch (path parameter)
    """
    logger.info(f"Fetching payment with ID: {payment_id}")
    
    result = financial_service.get_payment_by_id(payment_id)
    
    if not result:
        raise PaymentNotFoundException(payment_id=payment_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Payment {payment_id} retrieved successfully"
    )


# ==================== Deposit Query Endpoints ====================

@financial_router.get(
    "/deposits",
    response_model=SuccessResponseModel,
    summary="Get deposits",
    description="Get deposits with filters",
    responses={
        200: {
            "description": "Deposits retrieved successfully",
            "model": SuccessResponseModel
        },
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
    
    - **cart_id**: Filter by cart ID (query parameter)
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter)
    """
    logger.info(f"Fetching deposits - cart_id:{cart_id}, offset:{offset}, limit:{limit}")
    
    result = financial_service.get_deposits(cart_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} deposits",
        details={
            "filters": {
                "cart_id": cart_id
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result) if isinstance(result, list) else 0
            }
        }
    )


@financial_router.get(
    "/deposits/{deposit_id}",
    response_model=SuccessResponseModel,
    summary="Get deposit by ID",
    description="Get a specific deposit by its ID",
    responses={
        200: {
            "description": "Deposit retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_deposit_by_id(
    deposit_id: int,  # Path parameter - NO Query()
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get deposit by ID.
    
    - **deposit_id**: Deposit ID to fetch (path parameter)
    """
    logger.info(f"Fetching deposit with ID: {deposit_id}")
    
    result = financial_service.get_deposit_by_id(deposit_id)
    
    if not result:
        raise DepositNotFoundException(deposit_id=deposit_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Deposit {deposit_id} retrieved successfully"
    )


# ==================== Fee Query Endpoints ====================

@financial_router.get(
    "/fees",
    response_model=SuccessResponseModel,
    summary="Get fees",
    description="Get additional fees with filters",
    responses={
        200: {
            "description": "Fees retrieved successfully",
            "model": SuccessResponseModel
        },
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
    
    - **provider_id**: Filter by provider ID (query parameter)
    - **user_id**: Filter by user ID (query parameter)
    - **offset**: Pagination offset (query parameter)
    - **limit**: Number of records to return (query parameter)
    """
    logger.info(f"Fetching fees - provider_id:{provider_id}, user_id:{user_id}, offset:{offset}, limit:{limit}")
    
    result = financial_service.get_fees(provider_id, user_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 0} fees",
        details={
            "filters": {
                "provider_id": provider_id,
                "user_id": user_id
            },
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": len(result) if isinstance(result, list) else 0
            }
        }
    )


@financial_router.get(
    "/fees/{fee_id}",
    response_model=SuccessResponseModel,
    summary="Get fee by ID",
    description="Get a specific additional fee by its ID",
    responses={
        200: {
            "description": "Fee retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_fee_by_id(
    fee_id: int,  # Path parameter - NO Query()
    financial_service: FinancialService = Depends(get_financial_service)
):
    """
    Get fee by ID.
    
    - **fee_id**: Fee ID to fetch (path parameter)
    """
    logger.info(f"Fetching fee with ID: {fee_id}")
    
    result = financial_service.get_fee_by_id(fee_id)
    
    if not result:
        raise FeeNotFoundException(fee_id=fee_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Fee {fee_id} retrieved successfully"
    )