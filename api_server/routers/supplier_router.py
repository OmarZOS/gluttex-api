from fastapi import APIRouter, HTTPException, status
from features.supplier.supplier_update import update_supplier
from core.api_models import Location_API, ProductProvider_API, ProviderImage_API, ProviderOrganisation_API
from features.supplier.supplier_fetch import (
    fetch_org_by_id, fetch_orgs, fetch_supplier_by_id, fetch_supplier_categories, fetch_suppliers
)
from features.supplier.supplier_insert import insert_org, insert_supplier

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

@supplier_router.put("/org/add")
def insert_org_record(org: ProviderOrganisation_API):
    """
    Insert a new org.
    """
    try:
        return insert_org(org)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert org: {str(e)}"
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

@supplier_router.get("/org/{org_id}")
def get_org_by_id(org_id: int):
    """
    Retrieve a org by ID.
    """
    try:
        return fetch_org_by_id(org_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't get org: {str(e)}"
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
    

@supplier_router.get("/org/{offset}/{limit}")
def get_all_orgs(offset,limit):
    """
    Retrieve all orgs.
    """
    try:
        return fetch_orgs(offset,limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch orgs: {str(e)}"
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

@supplier_router.post("/supplier/{supplier_id}")
def update_supplier_details(
    supplier_id: int, 
    supplier: ProductProvider_API, 
    image: ProviderImage_API, 
    # background_tasks: BackgroundTasks
):
    """
    Update supplier details.
    """
    try:
        res = update_supplier(supplier, image)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}"
        )

