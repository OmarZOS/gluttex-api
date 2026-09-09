# services/financial_service.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from repositories.financial_repository import FinancialRepository
from core.models.api_models import InvoiceStatus, Payment_API, Deposit_API, AdditionalFee_API
from core.exceptions.handler import APIException
from core.messages import *
from core.models.models import Payment, AdditionalFee

class FinancialService:
    """Service for financial operations"""
    
    def __init__(self):
        self.financial_repo = FinancialRepository()
    
    def create_payment(self, payment_data: Payment_API) -> Payment:
        """Create a payment"""
        payment = Payment(
            payment_amount=payment_data.payment_amount,
            payment_method=payment_data.payment_method,
            payment_status=payment_data.payment_status,
            payment_reference=payment_data.payment_reference,
            payment_notes=payment_data.payment_notes
        )
        
        if payment_data.payment_invoice_id:
            payment.payment_invoice_id = payment_data.payment_invoice_id

        invoice = self.financial_repo.get_invoice_by_id(payment_data.payment_invoice_id)
        if invoice:
            old_invoice = invoice
            total_paid = sum(p.payment_amount for p in invoice.payment) + payment_data.payment_amount
            if total_paid >= invoice.invoice_total_amount:
                invoice.invoice_status = InvoiceStatus.PAID
            elif total_paid > 0:
                invoice.invoice_status = InvoiceStatus.PARTIALLY_PAID
            self.financial_repo.update_invoice(invoice)
        try:
            payment = self.financial_repo.create_payment(payment)
        except Exception as e:          
            self.financial_repo.update_invoice(old_invoice)
            raise e

        return payment
    
    
    def create_fee(self, fee_data: AdditionalFee_API) -> AdditionalFee:
        """Create an additional fee"""
        fee = AdditionalFee(
            fee_name=fee_data.fee_name,
            fee_amount=fee_data.fee_amount,
            fee_type=fee_data.fee_type,
            fee_description=fee_data.fee_description
        )
        
        return self.financial_repo.create_fee(fee)
    
    def create_financial_item(
        self,
        payment: Optional[Payment_API] = None,
        deposit: Optional[Deposit_API] = None,
        fee: Optional[AdditionalFee_API] = None
    ) -> Dict[str, Any]:
        """Create a financial item (generic method)"""
        result = {}
        
        if payment:
            result['payment'] = self.create_payment(payment)
        if deposit:
            result['deposit'] = self.create_deposit(deposit)
        if fee:
            result['fee'] = self.create_fee(fee)
        
        return result
    
    def get_payments(self, invoice_id: Optional[int] = None, offset: int = 0, limit: int = 100) -> List[Payment]:
        """Get payments with filters"""
        # Implementation depends on your repository
        pass
    
    def get_deposits(self, cart_id: Optional[int] = None, offset: int = 0, limit: int = 100) :
        """Get deposits with filters"""
        # Implementation depends on your repository
        pass
    
    def get_financial_items(
        self,
        supplier_id: int = 0,
        person_id: int = 0,
        client_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        order_id: int = 0,
        deposit_id: int = 0,
        invoice_id: int = 0,
        offset: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get financial items with filters"""
        # Implementation depends on your repository
        return {
            "payments": [],
            "deposits": [],
            "invoices": [],
            "receipts": []
        }