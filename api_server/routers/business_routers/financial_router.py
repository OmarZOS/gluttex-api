# routers/financial_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.api_models import Payment_API, Deposit_API, AdditionalFee_API
from services.financial_service import FinancialService

financial_router = APIRouter()

def get_financial_service() -> FinancialService:
    return FinancialService()

@financial_router.post("/payment")
def create_payment(
    payment: Payment_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Create a payment"""
    return financial_service.create_payment(payment)

@financial_router.post("/deposit")
def create_deposit(
    deposit: Deposit_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Create a deposit"""
    return financial_service.create_deposit(deposit)

@financial_router.post("/fee")
def create_fee(
    fee: AdditionalFee_API,
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Create an additional fee"""
    return financial_service.create_fee(fee)

@financial_router.get("/payments")
def get_payments(
    invoice_id: Optional[int] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Get payments with filters"""
    return financial_service.get_payments(invoice_id, offset, limit)

@financial_router.get("/deposits")
def get_deposits(
    cart_id: Optional[int] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    financial_service: FinancialService = Depends(get_financial_service)
):
    """Get deposits with filters"""
    return financial_service.get_deposits(cart_id, offset, limit)