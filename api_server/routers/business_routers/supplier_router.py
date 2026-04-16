# routers/supplier_router.py (corrected)
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.models import ProductProvider, ProviderOrganisation
from services.supplier_service import SupplierService
from services.supplier_service import OrganisationService

supplier_router = APIRouter()

def get_supplier_service() -> SupplierService:
    return SupplierService()

def get_organisation_service() -> OrganisationService:
    return OrganisationService()

# ==================== Supplier Endpoints ====================

@supplier_router.get("/")
def get_all_suppliers(
    owner_id: int = Query(0, description="Filter by owner ID"),
    org_id: int = Query(0, description="Filter by organisation ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Get all suppliers with pagination and filters"""
    return supplier_service.get_all_suppliers(owner_id, org_id, offset, limit)

@supplier_router.get("/types")
def get_supplier_types(
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Get all supplier types"""
    return supplier_service.get_supplier_types()

@supplier_router.get("/search/location")
def search_suppliers_by_location(
    longitude: float = Query(..., description="Longitude"),
    latitude: float = Query(..., description="Latitude"),
    distance_km: float = Query(10, description="Search radius in kilometers"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Search suppliers by geographic location"""
    return supplier_service.search_suppliers_by_location(
        longitude, latitude, distance_km, offset, limit
    )

@supplier_router.get("/{provider_id}")
def get_supplier(
    provider_id: str,
    full: bool = Query(True, description="Include all related data"),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Get supplier by ID"""
    return supplier_service.get_supplier_by_id(provider_id, full)

@supplier_router.post("/")
def create_supplier(
    provider: ProductProvider_API,
    location: Location_API,
    image: Optional[ProviderImage_API] = None,
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Create a new supplier"""
    return supplier_service.create_supplier(provider, location, image)

@supplier_router.put("/{provider_id}")
def update_supplier(
    provider_id: str,
    provider: ProductProvider_API,
    image: Optional[ProviderImage_API] = None,
    location: Optional[Location_API] = None,
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Update an existing supplier"""
    # Ensure the ID in path matches the ID in body
    provider.id_product_provider = provider_id
    return supplier_service.update_supplier(provider, image, location)

@supplier_router.delete("/{provider_id}")
def delete_supplier(
    provider_id: str,
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """Delete a supplier"""
    return supplier_service.delete_supplier(provider_id)

# ==================== Organisation Endpoints ====================

@supplier_router.get("/organisations/all")
def get_all_organisations(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """Get all organisations with pagination"""
    return organisation_service.get_all_orgs(offset, limit)

@supplier_router.get("/organisations/{org_id}")
def get_organisation(
    org_id: str,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """Get organisation by ID"""
    return organisation_service.get_org_by_id(org_id)

@supplier_router.post("/organisations")
def create_organisation(
    org: ProviderOrganisation_API,
    org_image: Optional[OrganisationImage_API] = None,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """Create a new organisation"""
    return organisation_service.create_organisation(org, org_image)

@supplier_router.put("/organisations/{org_id}")
def update_organisation(
    org_id: str,
    org: ProviderOrganisation_API,  # Fixed: Use API model, not database model
    org_image: Optional[OrganisationImage_API] = None,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """Update an existing organisation"""
    org.id_provider_organisation = org_id
    return organisation_service.update_organisation(org, org_image)

@supplier_router.delete("/organisations/{org_id}")
def delete_organisation(
    org_id: str,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """Delete an organisation"""
    return organisation_service.delete_organisation(org_id)