# routers/location_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from core.api_models import Location_API, Delivery_API
from core.exception_handler import APIException
from core.messages import *
from services.location_service import LocationService

location_router = APIRouter()

def get_location_service() -> LocationService:
    return LocationService()

@location_router.post("/")
def create_location(
    location: Location_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Create a new location.
    """
    return location_service.create_location(location)

@location_router.get("/{location_id}")
def get_location(
    location_id: str,
    with_address: bool = Query(True, description="Include address details"),
    location_service: LocationService = Depends(get_location_service)
):
    """
    Get location by ID.
    """
    if with_address:
        return location_service.get_location_with_address(location_id)
    return location_service.get_location_by_id(location_id, with_address=False)

@location_router.put("/{location_id}")
def update_location(
    location_id: str,
    location: Location_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Update an existing location.
    """
    return location_service.update_location(location_id, location)

@location_router.delete("/{location_id}")
def delete_location(
    location_id: str,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Delete a location.
    """
    success = location_service.delete_location(location_id)
    if not success:
        raise APIException(
            status=HTTP_404_NOT_FOUND,
            code=LOCATION_NOT_FOUND,
            details=f"Location {location_id} not found"
        )
    return {"message": f"Location {location_id} deleted successfully"}

@location_router.post("/address/from-delivery")
def create_address_from_delivery(
    delivery: Delivery_API,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Create an address from delivery information.
    """
    address = location_service.build_address_from_delivery(delivery)
    return location_service.address_repo.create_address(address)

@location_router.get("/address/{address_id}")
def get_address(
    address_id: str,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Get address by ID.
    """
    return location_service.get_address_by_id(address_id)

@location_router.put("/address/{address_id}")
def update_address(
    address_id: str,
    address_data: dict,
    location_service: LocationService = Depends(get_location_service)
):
    """
    Update an address.
    """
    return location_service.update_address(address_id, address_data)