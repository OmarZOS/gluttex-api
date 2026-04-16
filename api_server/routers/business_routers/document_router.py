# routers/document_router.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, Response
from typing import Optional
from services.document_service import DocumentService

document_router = APIRouter()

def get_document_service() -> DocumentService:
    return DocumentService()

@document_router.get("/cart/invoice/{provider_id}/{seller_id}/{cart_id}/{client_id}/{person_id}")
def fetch_cart_invoice(
    provider_id: int = 0,
    seller_id: int = 0,
    cart_id: int = 0,
    client_id: int = 0,
    person_id: int = 0,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Generate invoice HTML for a cart.
    
    Args:
        provider_id: Filter by provider ID
        seller_id: Filter by seller ID
        cart_id: Filter by cart ID
        client_id: Filter by client ID
        person_id: Filter by person ID
    
    Returns:
        HTMLResponse: Invoice HTML document
    """
    return document_service.generate_invoice_html(
        provider_id, seller_id, cart_id, client_id, person_id
    )

@document_router.get("/cart/receipt/{provider_id}/{seller_id}/{cart_id}/{client_id}/{person_id}")
def fetch_cart_receipt(
    provider_id: int = 0,
    seller_id: int = 0,
    cart_id: int = 0,
    client_id: int = 0,
    person_id: int = 0,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Generate receipt HTML for a cart.
    
    Args:
        provider_id: Filter by provider ID
        seller_id: Filter by seller ID
        cart_id: Filter by cart ID
        client_id: Filter by client ID
        person_id: Filter by person ID
    
    Returns:
        HTMLResponse: Receipt HTML document
    """
    return document_service.generate_receipt_html(
        provider_id, seller_id, cart_id, client_id, person_id
    )

@document_router.get("/cart/invoice/pdf")
def fetch_cart_invoice_pdf(
    provider_id: int = Query(0),
    seller_id: int = Query(0),
    cart_id: int = Query(0),
    client_id: int = Query(0),
    person_id: int = Query(0),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Generate invoice PDF for a cart.
    
    Returns:
        Response: PDF file download
    """
    try:
        pdf_content = document_service.generate_invoice_pdf(
            provider_id, seller_id, cart_id, client_id, person_id
        )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoice_cart_{cart_id or provider_id or seller_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@document_router.get("/cart/receipt/pdf")
def fetch_cart_receipt_pdf(
    provider_id: int = Query(0),
    seller_id: int = Query(0),
    cart_id: int = Query(0),
    client_id: int = Query(0),
    person_id: int = Query(0),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Generate receipt PDF for a cart.
    
    Returns:
        Response: PDF file download
    """
    try:
        pdf_content = document_service.generate_receipt_pdf(
            provider_id, seller_id, cart_id, client_id, person_id
        )
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=receipt_cart_{cart_id or provider_id or seller_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Optional: Add endpoint to get cart data as JSON for debugging/integration
@document_router.get("/cart/data")
def get_cart_data(
    provider_id: int = Query(0),
    seller_id: int = Query(0),
    cart_id: int = Query(0),
    client_id: int = Query(0),
    person_id: int = Query(0),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Get cart data as JSON for debugging or API integration.
    
    Returns:
        dict: Cart data in JSON format
    """
    cart_data = document_service.get_cart_for_document(
        provider_id, seller_id, cart_id, client_id, person_id
    )
    
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return cart_data