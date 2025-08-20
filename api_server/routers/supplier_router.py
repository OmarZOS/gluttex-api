from fastapi import APIRouter,  status
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
    return insert_supplier(supplier, location)

@supplier_router.put("/org/add")
def insert_org_record(org: ProviderOrganisation_API):
    """
    Insert a new org.
    """
    return insert_org(org)

@supplier_router.get("/supplier/{supplier_id}")
def get_supplier_by_id(supplier_id: int):
    """
    Retrieve a supplier by ID.
    """
    return fetch_supplier_by_id(supplier_id)

@supplier_router.get("/org/{org_id}")
def get_org_by_id(org_id: int):
    """
    Retrieve a org by ID.
    """
    return fetch_org_by_id(org_id)

@supplier_router.get("/supplier/{owner_id}/{org_id}/{offset}/{limit}")
def get_all_suppliers(owner_id=0,org_id=0,offset=0,limit=10):
    """
    Retrieve all suppliers.
    """
    return fetch_suppliers(owner_id,org_id,offset,limit)
    

@supplier_router.get("/org/{offset}/{limit}")
def get_all_orgs(offset,limit):
    """
    Retrieve all orgs.
    """
    return fetch_orgs(offset,limit)


@supplier_router.get("/supplier/category/all")
def get_all_supplier_categories():
    """
    Retrieve all supplier categories.
    """
    return fetch_supplier_categories()

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
    return  update_supplier(supplier, image)

