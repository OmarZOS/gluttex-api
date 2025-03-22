from fastapi import APIRouter, HTTPException, status
from core.api_models import Location_API, ProductProvider_API
from features.supplier.supplier_fetch import (
    fetch_supplier_by_id, fetch_supplier_categories, fetch_suppliers
)
from features.supplier.supplier_insert import insert_supplier

supplier_router = APIRouter()

# ----------------- Supplier Endpoints -----------------

@supplier_router.put("/supplier/add")
def insert_supplier_record(supplier: ProductProvider_API, location: Location_API):
    """
    Insert a new supplier.
    """
    try:
        return insert_supplier(supplier, location)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert supplier: {str(e)}"
        )

@supplier_router.get("/supplier/{supplier_id}")
def get_supplier_by_id(supplier_id: int):
    """
    Retrieve a supplier by ID.
    """
    try:
        return fetch_supplier_by_id(supplier_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't get supplier: {str(e)}"
        )

@supplier_router.get("/supplier/all/{offset}/{limit}")
def get_all_suppliers(offset,limit):
    """
    Retrieve all suppliers.
    """
    try:
        return fetch_suppliers(offset,limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch suppliers: {str(e)}"
        )

@supplier_router.get("/supplier/category/all")
def get_all_supplier_categories():
    """
    Retrieve all supplier categories.
    """
    try:
        return fetch_supplier_categories()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch supplier categories: {str(e)}"
        )
