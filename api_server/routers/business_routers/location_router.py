# routers/location_router.py
"""
Location router for managing locations and addresses.
"""

from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List, Dict, Any
import logging

from core.api_models import Location_API, Delivery_API
from core.response_models import (
    SuccessResponseModel,
    ErrorResponseModel,
    get_crud_error_responses
)
from core.exceptions import (
    LocationNotFoundException,
    LocationInsertFailedException,
    LocationUpdateFailedException,
    LocationDeleteFailedException,
    AddressNotFoundException,
    AddressInsertFailedException,
    AddressUpdateFailedException
)
from services.location_service import LocationService

logger = logging.getLogger(__name__)

location_router = APIRouter(
    # tags=["locations"],
    # prefix="/api/locations"
)


def get_location_service() -> LocationService:
    """Dependency to get LocationService instance"""
    return LocationService()


# ==================== Location Endpoints ====================

@location_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create location",
    description="Create a new location",
    responses={
        201: {
            "description": "Location created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False, include_409=True)
    }
)
def create_location(
    location: Location_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Create a new location.
    
    - **location**: Location data (request body)
    """
    logger.info(f"Creating new location with name: {location.location_name}")
    
    result = location_service.create_location(location)
    
    location_id = getattr(result, 'id_location', None)
    
    return SuccessResponseModel(
        success=True,
        message="Location created successfully",
        data=result,
        details={
            "location_id": location_id,
            "location_name": location.location_name
        }
    )


@location_router.get(
    "/{location_id}",
    response_model=SuccessResponseModel,
    summary="Get location",
    description="Get location by ID",
    responses={
        200: {
            "description": "Location retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_location(
    location_id: str,  # Path parameter - NO Query()
    with_address: bool = Query(True, description="Include address details"),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Get location by ID.
    
    - **location_id**: Location ID to fetch (path parameter)
    - **with_address**: Include address details (query parameter)
    """
    logger.info(f"Fetching location with ID: {location_id} (with_address={with_address})")
    
    if with_address:
        result = location_service.get_location_with_address(location_id)
    else:
        result = location_service.get_location_by_id(location_id, with_address=False)
    
    if not result:
        raise LocationNotFoundException(location_id=location_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Location {location_id} retrieved successfully",
        details={"with_address": with_address}
    )


@location_router.put(
    "/{location_id}",
    response_model=SuccessResponseModel,
    summary="Update location",
    description="Update an existing location",
    responses={
        200: {
            "description": "Location updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_location(
    location_id: str,  # Path parameter - NO Query()
    location: Location_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Update an existing location.
    
    - **location_id**: Location ID to update (path parameter)
    - **location**: Updated location data (request body)
    """
    logger.info(f"Updating location with ID: {location_id}")
    
    result = location_service.update_location(location_id, location)
    
    return SuccessResponseModel(
        success=True,
        message=f"Location {location_id} updated successfully",
        data=result,
        details={
            "location_id": location_id,
            "location_name": location.location_name
        }
    )


@location_router.delete(
    "/{location_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponseModel,
    summary="Delete location",
    description="Delete a location",
    responses={
        200: {
            "description": "Location deleted successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Cannot delete location with dependencies",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def delete_location(
    location_id: str,  # Path parameter - NO Query()
    force_delete: bool = Query(False, description="Force delete even if location has references"),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Delete a location.
    
    - **location_id**: Location ID to delete (path parameter)
    - **force_delete**: Force delete even if location has references (query parameter)
    """
    logger.info(f"Deleting location with ID: {location_id} (force={force_delete})")
    
    success = location_service.delete_location(location_id, force_delete)
    
    if not success:
        raise LocationDeleteFailedException(
            location_id=location_id,
            error="Location not found or cannot be deleted"
        )
    
    return SuccessResponseModel(
        success=True,
        message=f"Location {location_id} deleted successfully",
        data={"location_id": location_id, "force_deleted": force_delete}
    )


# ==================== Address Endpoints ====================

@location_router.post(
    "/address/from-delivery",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseModel,
    summary="Create address from delivery",
    description="Create an address from delivery information",
    responses={
        201: {
            "description": "Address created successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid delivery data",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=False)
    }
)
def create_address_from_delivery(
    delivery: Delivery_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Create an address from delivery information.
    
    - **delivery**: Delivery information (request body)
    """
    logger.info("Creating address from delivery information")
    
    address = location_service.build_address_from_delivery(delivery)
    result = location_service.address_repo.create_address(address)
    
    address_id = getattr(result, 'id_address', None)
    
    return SuccessResponseModel(
        success=True,
        message="Address created successfully from delivery",
        data=result,
        details={
            "address_id": address_id,
            "street": address.address_street,
            "city": address.address_city,
            "country": address.address_country
        }
    )


@location_router.get(
    "/address/{address_id}",
    response_model=SuccessResponseModel,
    summary="Get address",
    description="Get address by ID",
    responses={
        200: {
            "description": "Address retrieved successfully",
            "model": SuccessResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def get_address(
    address_id: str,  # Path parameter - NO Query()
    location_service: LocationService = Depends(get_location_service)
):
    """
    Get address by ID.
    
    - **address_id**: Address ID to fetch (path parameter)
    """
    logger.info(f"Fetching address with ID: {address_id}")
    
    result = location_service.get_address_by_id(address_id)
    
    if not result:
        raise AddressNotFoundException(address_id=address_id)
    
    return SuccessResponseModel(
        success=True,
        data=result,
        message=f"Address {address_id} retrieved successfully"
    )


@location_router.put(
    "/address/{address_id}",
    response_model=SuccessResponseModel,
    summary="Update address",
    description="Update an address",
    responses={
        200: {
            "description": "Address updated successfully",
            "model": SuccessResponseModel
        },
        400: {
            "description": "Bad Request - Invalid data",
            "model": ErrorResponseModel
        },
        **get_crud_error_responses(include_404=True)
    }
)
def update_address(
    address_id: str,  # Path parameter - NO Query()
    address_data: Dict[str, Any],
    location_service: LocationService = Depends(get_location_service)
):
    """
    Update an address.
    
    - **address_id**: Address ID to update (path parameter)
    - **address_data**: Updated address data (request body)
    """
    logger.info(f"Updating address with ID: {address_id}")
    
    result = location_service.update_address(address_id, address_data)
    
    return SuccessResponseModel(
        success=True,
        message=f"Address {address_id} updated successfully",
        data=result,
        details={
            "address_id": address_id,
            "updated_fields": list(address_data.keys())
        }
    )