# repositories/invoice_repository.py
"""
Invoice repository for database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func

from core.models.models import (
    Invoice, Payment, Cart, PlacedOrder, Delivery, AdditionalFee
)
import storage.storage_broker as StorageBroker
from core.exceptions.handler import APIException
from core.messages import *


class InvoiceRepository:
    """Repository for invoice operations"""
    
    def __init__(self):
        self.storage = StorageBroker
    
    def _get_session(self) -> Session:
        """Get a database session."""
        return self.storage.get_session()
    
    # ==================== CREATE ====================
    
    def create(self, invoice: Invoice) -> Invoice:
        """Create a new invoice."""
        try:
            with self._get_session() as session:
                session.add(invoice)
                session.flush()
                session.refresh(invoice)
                return invoice
        except Exception as e:
            raise APIException(
                message=f"Failed to create invoice: {str(e)}",
                error_code="INVOICE_CREATION_FAILED",
                status_code=500
            )
    
    def link_to_cart(self, invoice_id: int, cart_id: int) -> None:
        """Link invoice to cart."""
        try:
            with self._get_session() as session:
                cart = session.query(Cart).filter(Cart.cart_id == cart_id).first()
                if cart:
                    cart.cart_invoice = invoice_id
                    session.flush()
        except Exception as e:
            raise APIException(
                message=f"Failed to link invoice to cart: {str(e)}",
                error_code="INVOICE_LINK_FAILED",
                status_code=500
            )
    
    def link_to_order(self, invoice_id: int, order_id: int) -> None:
        """Link invoice to order."""
        try:
            with self._get_session() as session:
                order = session.query(PlacedOrder).filter(
                    PlacedOrder.id_placed_order == order_id
                ).first()
                if order:
                    order.placed_order_invoice = invoice_id
                    session.flush()
        except Exception as e:
            raise APIException(
                message=f"Failed to link invoice to order: {str(e)}",
                error_code="INVOICE_LINK_FAILED",
                status_code=500
            )
    
    # ==================== READ ====================
    
    def get(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID."""
        try:
            with self._get_session() as session:
                return session.query(Invoice).filter(
                    Invoice.invoice_id == invoice_id
                ).first()
        except Exception as e:
            raise APIException(
                message=f"Failed to get invoice: {str(e)}",
                error_code="INVOICE_FETCH_FAILED",
                status_code=500
            )
    
    def get_with_relations(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice with all related data."""
        try:
            with self._get_session() as session:
                return session.query(Invoice).filter(
                    Invoice.invoice_id == invoice_id
                ).options(
                    joinedload(Invoice.payment),
                    joinedload(Invoice.placed_order),
                    joinedload(Invoice.cart),
                    joinedload(Invoice.delivery),
                    joinedload(Invoice.additional_fee)
                ).first()
        except Exception as e:
            raise APIException(
                message=f"Failed to get invoice with relations: {str(e)}",
                error_code="INVOICE_FETCH_FAILED",
                status_code=500
            )
    
    def get_with_filters(
        self,
        status: Optional[str] = None,
        type_: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        cart_id: Optional[int] = None,
        order_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """Get invoices with filters."""
        try:
            with self._get_session() as session:
                query = session.query(Invoice)
                
                # Apply filters
                if status:
                    query = query.filter(Invoice.invoice_status == status)
                if type_:
                    query = query.filter(Invoice.invoice_type == type_)
                if date_from:
                    query = query.filter(Invoice.invoice_issue_date >= date_from)
                if date_to:
                    query = query.filter(Invoice.invoice_issue_date <= date_to)
                if cart_id:
                    query = query.join(Cart).filter(Cart.cart_id == cart_id)
                if order_id:
                    query = query.join(PlacedOrder).filter(
                        PlacedOrder.id_placed_order == order_id
                    )
                
                # Order by creation date (newest first)
                query = query.order_by(desc(Invoice.invoice_created_at))
                query = query.offset(offset).limit(limit)
                
                return query.all()
        except Exception as e:
            raise APIException(
                message=f"Failed to get invoices: {str(e)}",
                error_code="INVOICE_FETCH_FAILED",
                status_code=500
            )
    
    def count_with_filters(
        self,
        status: Optional[str] = None,
        type_: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        cart_id: Optional[int] = None,
        order_id: Optional[int] = None
    ) -> int:
        """Count invoices with filters."""
        try:
            with self._get_session() as session:
                query = session.query(func.count(Invoice.invoice_id))
                
                if status:
                    query = query.filter(Invoice.invoice_status == status)
                if type_:
                    query = query.filter(Invoice.invoice_type == type_)
                if date_from:
                    query = query.filter(Invoice.invoice_issue_date >= date_from)
                if date_to:
                    query = query.filter(Invoice.invoice_issue_date <= date_to)
                if cart_id:
                    query = query.join(Cart).filter(Cart.cart_id == cart_id)
                if order_id:
                    query = query.join(PlacedOrder).filter(
                        PlacedOrder.id_placed_order == order_id
                    )
                
                return query.scalar() or 0
        except Exception as e:
            raise APIException(
                message=f"Failed to count invoices: {str(e)}",
                error_code="INVOICE_COUNT_FAILED",
                status_code=500
            )
    
    # ==================== UPDATE ====================
    
    def update(self, invoice_id: int, update_data: Dict[str, Any]) -> Invoice:
        """Update an invoice."""
        try:
            with self._get_session() as session:
                invoice = session.query(Invoice).filter(
                    Invoice.invoice_id == invoice_id
                ).first()
                
                if not invoice:
                    raise APIException(
                        message=f"Invoice {invoice_id} not found",
                        error_code="INVOICE_NOT_FOUND",
                        status_code=404
                    )
                
                for key, value in update_data.items():
                    if hasattr(invoice, key):
                        setattr(invoice, key, value)
                
                invoice.invoice_updated_at = datetime.now()
                session.flush()
                session.refresh(invoice)
                
                return invoice
        except APIException:
            raise
        except Exception as e:
            raise APIException(
                message=f"Failed to update invoice: {str(e)}",
                error_code="INVOICE_UPDATE_FAILED",
                status_code=500
            )
    
    # ==================== DELETE ====================
    
    def delete(self, invoice_id: int) -> None:
        """Delete an invoice."""
        try:
            with self._get_session() as session:
                invoice = session.query(Invoice).filter(
                    Invoice.invoice_id == invoice_id
                ).first()
                
                if invoice:
                    session.delete(invoice)
                    session.flush()
        except Exception as e:
            raise APIException(
                message=f"Failed to delete invoice: {str(e)}",
                error_code="INVOICE_DELETE_FAILED",
                status_code=500
            )
    
    def delete_relations(self, invoice_id: int) -> None:
        """Delete related records (payments, deliveries, fees)."""
        try:
            with self._get_session() as session:
                # Delete payments
                session.query(Payment).filter(
                    Payment.payment_invoice_id == invoice_id
                ).delete()
                
                # Delete deliveries
                session.query(Delivery).filter(
                    Delivery.delivery_invoice_ref == invoice_id
                ).delete()
                
                # Delete additional fees
                session.query(AdditionalFee).filter(
                    AdditionalFee.additional_fee_invoice == invoice_id
                ).delete()
                
                session.flush()
        except Exception as e:
            raise APIException(
                message=f"Failed to delete invoice relations: {str(e)}",
                error_code="INVOICE_RELATIONS_DELETE_FAILED",
                status_code=500
            )
    
    # ==================== RELATED DATA ====================
    
    def get_payments(self, invoice_id: int) -> List[Payment]:
        """Get payments for an invoice."""
        try:
            with self._get_session() as session:
                return session.query(Payment).filter(
                    Payment.payment_invoice_id == invoice_id
                ).order_by(desc(Payment.payment_created_at)).all()
        except Exception as e:
            raise APIException(
                message=f"Failed to get payments: {str(e)}",
                error_code="PAYMENT_FETCH_FAILED",
                status_code=500
            )
    
    def get_deliveries(self, invoice_id: int) -> List[Delivery]:
        """Get deliveries for an invoice."""
        try:
            with self._get_session() as session:
                return session.query(Delivery).filter(
                    Delivery.delivery_invoice_ref == invoice_id
                ).all()
        except Exception as e:
            raise APIException(
                message=f"Failed to get deliveries: {str(e)}",
                error_code="DELIVERY_FETCH_FAILED",
                status_code=500
            )
    
    def get_fees(self, invoice_id: int) -> List[AdditionalFee]:
        """Get additional fees for an invoice."""
        try:
            with self._get_session() as session:
                return session.query(AdditionalFee).filter(
                    AdditionalFee.additional_fee_invoice == invoice_id
                ).all()
        except Exception as e:
            raise APIException(
                message=f"Failed to get fees: {str(e)}",
                error_code="FEE_FETCH_FAILED",
                status_code=500
            )
    
    def get_cart(self, cart_id: int) -> Optional[Cart]:
        """Get cart with related data."""
        try:
            with self._get_session() as session:
                return session.query(Cart).filter(
                    Cart.cart_id == cart_id
                ).options(
                    joinedload(Cart.ordered_item),
                    joinedload(Cart.ordered_service)
                ).first()
        except Exception as e:
            raise APIException(
                message=f"Failed to get cart: {str(e)}",
                error_code="CART_FETCH_FAILED",
                status_code=500
            )