# services/document_service.py
from typing import Optional, Dict, Any
from fastapi.responses import HTMLResponse
from features.document.generator import get_renderer
from features.document.invoice_data import InvoiceGenerator
from services.cart_service import CartService

class DocumentService:
    """Service for document generation (invoices, receipts)"""
    
    def __init__(self):
        self.cart_service = CartService()
    
    def get_cart_for_document(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        person_id: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Get cart data for document generation"""
        
        # Use cart service to fetch the cart
        if cart_id > 0:
            cart = self.cart_service.get_cart_by_id(cart_id)
            return InvoiceGenerator.cart_to_json(cart)
        elif provider_id > 0:
            carts = self.cart_service.get_carts_by_provider(provider_id, offset=0, limit=1)
            if carts:
                return InvoiceGenerator.cart_to_json(carts[0])
        elif seller_id > 0:
            carts = self.cart_service.get_carts_by_seller(seller_id, offset=0, limit=1)
            if carts:
                return InvoiceGenerator.cart_to_json(carts[0])
        elif client_id > 0:
            carts = self.cart_service.get_carts_by_buyer(client_id, offset=0, limit=1)
            if carts:
                return InvoiceGenerator.cart_to_json(carts[0])
        
        return None
    
    def generate_invoice_html(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        person_id: int = 0
    ) -> HTMLResponse:
        """Generate invoice HTML for a cart"""
        
        cart_data = self.get_cart_for_document(provider_id, seller_id, cart_id, client_id, person_id)
        
        if not cart_data:
            return HTMLResponse(
                content="<h1>Error: Cart not found</h1>",
                status_code=404
            )
        
        invoice = InvoiceGenerator.from_json(cart_data)
        html_content = get_renderer().render_compact_invoice(invoice)
        
        return HTMLResponse(content=html_content, status_code=200)
    
    def generate_receipt_html(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        person_id: int = 0
    ) -> HTMLResponse:
        """Generate receipt HTML for a cart"""
        
        cart_data = self.get_cart_for_document(provider_id, seller_id, cart_id, client_id, person_id)
        
        if not cart_data:
            return HTMLResponse(
                content="<h1>Error: Cart not found</h1>",
                status_code=404
            )
        
        invoice = InvoiceGenerator.from_json(cart_data)
        html_content = get_renderer().render_compact_receipt(invoice)
        
        return HTMLResponse(content=html_content, status_code=200)
    
    def generate_invoice_pdf(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        person_id: int = 0
    ) -> bytes:
        """Generate invoice PDF for a cart"""
        
        cart_data = self.get_cart_for_document(provider_id, seller_id, cart_id, client_id, person_id)
        
        if not cart_data:
            raise ValueError("Cart not found")
        
        invoice = InvoiceGenerator.from_json(cart_data)
        return get_renderer().render_pdf_invoice(invoice)
    
    def generate_receipt_pdf(
        self,
        provider_id: int = 0,
        seller_id: int = 0,
        cart_id: int = 0,
        client_id: int = 0,
        person_id: int = 0
    ) -> bytes:
        """Generate receipt PDF for a cart"""
        
        cart_data = self.get_cart_for_document(provider_id, seller_id, cart_id, client_id, person_id)
        
        if not cart_data:
            raise ValueError("Cart not found")
        
        invoice = InvoiceGenerator.from_json(cart_data)
        return get_renderer().render_pdf_receipt(invoice)