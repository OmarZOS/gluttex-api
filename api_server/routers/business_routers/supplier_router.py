# routers/supplier_router.py
"""
Supplier and Organisation router for managing suppliers, organisations, and their relationships.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
import logging

from core.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.response_models import (
    SuccessResponseModel,
    PaginatedResponseModel,
    ErrorResponseModel,
    IdResponseModel,
    EmptyResponseModel,
    get_crud_error_responses
)
from core.models import ProductProvider, ProviderOrganisation
from services.supplier_service import SupplierService
from services.supplier_service import OrganisationService

logger = logging.getLogger(__name__)

supplier_router = APIRouter(
    # tags=["suppliers"],
    # prefix="/api"
)


def get_supplier_service() -> SupplierService:
    return SupplierService()


def get_organisation_service() -> OrganisationService:
    return OrganisationService()


# ==================== Supplier Endpoints ====================

@supplier_router.get(
    "/suppliers",
    response_model=SuccessResponseModel,
    summary="Get all suppliers",
    description="Retrieve all suppliers with pagination and filters",
    responses={
        200: {
            "description": "Suppliers retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_all_suppliers(
    owner_id: int = Query(0, description="Filter by owner ID"),
    org_id: int = Query(0, description="Filter by organisation ID"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return (max 100)"),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Get all suppliers with pagination and filters.
    
    - **owner_id**: Filter by owner ID
    - **org_id**: Filter by organisation ID
    - **offset**: Pagination offset
    - **limit**: Maximum number of records (max 100)
    """
    logger.info(f"Fetching suppliers with filters - owner_id:{owner_id}, org_id:{org_id}, offset:{offset}, limit:{limit}")
    
    result = supplier_service.get_all_suppliers(owner_id, org_id, offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'suppliers'}",
        details={
            "filters": {
                "owner_id": owner_id if owner_id > 0 else None,
                "org_id": org_id if org_id > 0 else None
            },
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@supplier_router.get(
    "/supplier-types",
    response_model=SuccessResponseModel,
    summary="Get supplier types",
    description="Get all supplier types",
    responses={
        200: {
            "description": "Supplier types retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_supplier_types(
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Get all supplier types.
    """
    logger.info("Fetching supplier types")
    
    result = supplier_service.get_supplier_types()
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else result} supplier types"
    )


@supplier_router.get(
    "/suppliers/search/location",
    response_model=SuccessResponseModel,
    summary="Search suppliers by location",
    description="Search suppliers by geographic location within a radius",
    responses={
        200: {
            "description": "Suppliers found successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid coordinates",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def search_suppliers_by_location(
    longitude: float = Query(..., description="Longitude coordinate", ge=-180, le=180),
    latitude: float = Query(..., description="Latitude coordinate", ge=-90, le=90),
    distance_km: float = Query(10, description="Search radius in kilometers", ge=1, le=500),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return (max 100)"),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Search suppliers by geographic location.
    
    - **longitude**: Longitude coordinate (-180 to 180)
    - **latitude**: Latitude coordinate (-90 to 90)
    - **distance_km**: Search radius in kilometers (1-500)
    - **offset**: Pagination offset
    - **limit**: Maximum number of records (max 100)
    """
    logger.info(f"Searching suppliers near ({longitude}, {latitude}) within {distance_km}km")
    
    result = supplier_service.search_suppliers_by_location(
        longitude, latitude, distance_km, offset, limit
    )
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'suppliers'} near location",
        details={
            "location": {
                "longitude": longitude,
                "latitude": latitude,
                "radius_km": distance_km
            },
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@supplier_router.get(
    "/suppliers/{provider_id}",
    response_model=SuccessResponseModel,
    summary="Get supplier by ID",
    description="Retrieve a specific supplier by its ID",
    responses={
        200: {
            "description": "Supplier retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_supplier(
    provider_id: str,
    full: bool = Query(True, description="Include all related data (products, images, etc.)"),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Get supplier by ID.
    
    - **provider_id**: Supplier ID to fetch
    - **full**: Include all related data
    """
    logger.info(f"Fetching supplier with ID: {provider_id} (full={full})")
    
    result = supplier_service.get_supplier_by_id(provider_id, full)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Supplier {provider_id} retrieved successfully",
        details={"full_data": full}
    )


@supplier_router.post(
    "/suppliers",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create a new supplier",
    description="Create a new supplier with location and optional image",
    responses={
        201: {
            "description": "Supplier created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Supplier already exists",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False, include_409=True)
    }
)
def create_supplier(
    provider: ProductProvider_API,
    location: Location_API,
    image: Optional[ProviderImage_API] = None,
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Create a new supplier.
    
    - **provider**: Supplier details
    - **location**: Location information
    - **image**: Optional supplier image
    """
    logger.info(f"Creating new supplier: {provider.provider_name}")
    
    result = supplier_service.create_supplier(provider, location, image)
    
    # Extract the created supplier ID
    supplier_id = getattr(result, 'id_product_provider', None) or getattr(result, 'get', lambda x: None)('id')
    
    return SuccessResponseModel(
        success=True,
        message="Supplier created successfully",
        data=result,
        details={
            "supplier_id": supplier_id,
            "supplier_name": provider.provider_name,
            "has_image": image is not None
        }
    )


@supplier_router.put(
    "/suppliers/{provider_id}",
    response_model=SuccessResponseModel,
    summary="Update a supplier",
    description="Update an existing supplier's details",
    responses={
        200: {
            "description": "Supplier updated successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_supplier(
    provider_id: str,
    provider: ProductProvider_API,
    image: Optional[ProviderImage_API] = None,
    location: Optional[Location_API] = None,
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Update an existing supplier.
    
    - **provider_id**: Supplier ID to update
    - **provider**: Updated supplier details
    - **image**: Optional updated image
    - **location**: Optional updated location
    """
    logger.info(f"Updating supplier with ID: {provider_id}")
    
    # Ensure the ID in path matches the ID in body
    provider.id_product_provider = provider_id
    
    result = supplier_service.update_supplier(provider, image, location)
    
    return SuccessResponseModel(
        success=True,
        message=f"Supplier {provider_id} updated successfully",
        data=result,
        details={
            "updated_fields": {
                "name_updated": True,
                "location_updated": location is not None,
                "image_updated": image is not None
            }
        }
    )


@supplier_router.delete(
    "/suppliers/{provider_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete a supplier",
    description="Delete a supplier by ID",
    responses={
        200: {
            "description": "Supplier deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete supplier with dependencies",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_supplier(
    provider_id: str,
    force_delete: bool = Query(False, description="Force delete even if supplier has products"),
    supplier_service: SupplierService = Depends(get_supplier_service)
):
    """
    Delete a supplier.
    
    - **provider_id**: Supplier ID to delete
    - **force_delete**: Force delete even if supplier has products
    """
    logger.info(f"Deleting supplier with ID: {provider_id} (force={force_delete})")
    
    result = supplier_service.delete_supplier(provider_id)
    
    return SuccessResponseModel(
        success=True,
        message=f"Supplier {provider_id} deleted successfully",
        data=result,
        details={"force_deleted": force_delete}
    )


# ==================== Organisation Endpoints ====================

@supplier_router.get(
    "/organisations",
    response_model=SuccessResponseModel,
    summary="Get all organisations",
    description="Get all organisations with pagination",
    responses={
        200: {
            "description": "Organisations retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def get_all_organisations(
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return (max 500)"),
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """
    Get all organisations with pagination.
    
    - **offset**: Pagination offset
    - **limit**: Maximum number of records (max 500)
    """
    logger.info(f"Fetching all organisations (offset={offset}, limit={limit})")
    
    result = organisation_service.get_all_orgs(offset, limit)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Found {len(result) if isinstance(result, list) else 'organisations'}",
        details={
            "pagination": {
                "offset": offset,
                "limit": limit
            }
        }
    )


@supplier_router.get(
    "/organisations/{org_id}",
    response_model=SuccessResponseModel,
    summary="Get organisation by ID",
    description="Retrieve a specific organisation by its ID",
    responses={
        200: {
            "description": "Organisation retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_organisation(
    org_id: str,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """
    Get organisation by ID.
    
    - **org_id**: Organisation ID to fetch
    """
    logger.info(f"Fetching organisation with ID: {org_id}")
    
    result = organisation_service.get_org_by_id(org_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Organisation {org_id} retrieved successfully"
    )


@supplier_router.post(
    "/organisations",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create a new organisation",
    description="Create a new organisation with optional image",
    responses={
        201: {
            "description": "Organisation created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        409: {
            "description": "Conflict - Organisation already exists",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False, include_409=True)
    }
)
def create_organisation(
    org: ProviderOrganisation_API,
    org_image: Optional[OrganisationImage_API] = None,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """
    Create a new organisation.
    
    - **org**: Organisation details
    - **org_image**: Optional organisation image
    """
    logger.info(f"Creating new organisation: {org.provider_organisation_name}")
    
    result = organisation_service.create_organisation(org, org_image)
    
    # Extract the created organisation ID
    org_id = getattr(result, 'id_provider_organisation', None) or getattr(result, 'get', lambda x: None)('id')
    
    return SuccessResponseModel(
        success=True,
        message="Organisation created successfully",
        data=result,
        details={
            "organisation_id": org_id,
            "organisation_name": org.provider_organisation_name,
            "has_image": org_image is not None
        }
    )


@supplier_router.put(
    "/organisations/{org_id}",
    response_model=SuccessResponseModel,
    summary="Update an organisation",
    description="Update an existing organisation's details",
    responses={
        200: {
            "description": "Organisation updated successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_organisation(
    org_id: str,
    org: ProviderOrganisation_API,
    org_image: Optional[OrganisationImage_API] = None,
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """
    Update an existing organisation.
    
    - **org_id**: Organisation ID to update
    - **org**: Updated organisation details
    - **org_image**: Optional updated image
    """
    logger.info(f"Updating organisation with ID: {org_id}")
    
    org.id_provider_organisation = org_id
    result = organisation_service.update_organisation(org, org_image)
    
    return SuccessResponseModel(
        success=True,
        message=f"Organisation {org_id} updated successfully",
        data=result,
        details={
            "updated_fields": {
                "name_updated": True,
                "image_updated": org_image is not None
            }
        }
    )


@supplier_router.delete(
    "/organisations/{org_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete an organisation",
    description="Delete an organisation by ID",
    responses={
        200: {
            "description": "Organisation deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete organisation with dependencies",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_organisation(
    org_id: str,
    force_delete: bool = Query(False, description="Force delete even if organisation has suppliers"),
    organisation_service: OrganisationService = Depends(get_organisation_service)
):
    """
    Delete an organisation.
    
    - **org_id**: Organisation ID to delete
    - **force_delete**: Force delete even if organisation has suppliers
    """
    logger.info(f"Deleting organisation with ID: {org_id} (force={force_delete})")
    
    result = organisation_service.delete_organisation(org_id)
    
    return SuccessResponseModel(
        success=True,
        message=f"Organisation {org_id} deleted successfully",
        data=result,
        details={"force_deleted": force_delete}
    )