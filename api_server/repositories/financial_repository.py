# repositories/financial_repository.py
from typing import Optional, List
from core.models.models import Invoice, Payment
import storage.storage_broker as storage_broker

class FinancialRepository:
    """Repository for financial document operations"""
    
    def create_invoice(self, invoice: Invoice) -> Invoice:
        """Create an invoice"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(invoice)
    
    def create_payment(self, payment: Payment) -> Payment:
        """Create a payment"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(payment)
    
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        records = storage_broker.get(Invoice, {Invoice.invoice_id: invoice_id}, [], [])
        return records[0] if records else None
    
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        records = storage_broker.get(Payment, {Payment.payment_id: payment_id}, [], [])
        return records[0] if records else None
    
    def update_invoice(self, invoice: Invoice) -> Invoice:
        """Update an invoice"""
        from features.insertion import update_record_in_api
        return update_record_in_api(invoice)
    
    def delete_invoice(self, invoice: Invoice) :
        """Delete an invoice"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(invoice)

    def update_payment(self, payment: Payment) -> Payment:
        """Update a payment"""
        from features.insertion import update_record_in_api
        return update_record_in_api(payment)