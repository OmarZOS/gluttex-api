from fastapi import APIRouter,  status
from features.supplier.supplier_delete import delete_supplier
from features.supplier.supplier_update import update_organisation, update_supplier
from core.api_models import Location_API, OrganisationImage_API, ProductProvider_API, ProviderImage_API, ProviderOrganisation_API
from features.supplier.supplier_fetch import (
    fetch_org_by_id, fetch_orgs, fetch_supplier_by_id, fetch_supplier_categories, fetch_suppliers
)
from features.supplier.supplier_insert import insert_org, insert_supplier

supplier_router = APIRouter()

# ----------------- Supplier Endpoints -----------------

@supplier_router.post("/supplier/add")
def insert_supplier_record(supplier: ProductProvider_API, location: Location_API, image: ProviderImage_API):
    """
    Insert a new supplier.
    """
    return insert_supplier(supplier, location,image)

@supplier_router.post("/org/add")
def insert_org_record(org: ProviderOrganisation_API,org_image: OrganisationImage_API):
    """
    Insert a new org.
    """
    return insert_org(org,org_image)

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

@supplier_router.put("/supplier/{supplier_id}")
def update_supplier_details(
    supplier_id: int, 
    supplier: ProductProvider_API, 
    image: ProviderImage_API,
    location: Location_API, 
    # background_tasks: BackgroundTasks
):
    """
    Update supplier details.
    """
    return  update_supplier(supplier, image,location)



@supplier_router.put("/org/{org_id}")
def update_org_details(
    org_id: int, 
    org: ProviderOrganisation_API, 
    image: OrganisationImage_API, 
    # background_tasks: BackgroundTasks
):
    """
    Update org details.
    """
    return  update_organisation(org, image)

@supplier_router.delete("/supplier/delete/{supplier_id}")
def delete_supplier_by_id(supplier_id: int):
    """
    Delete a supplier by ID.
    """
    return delete_supplier(supplier_id)