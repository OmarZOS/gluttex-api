# services/location_service.py
from typing import Optional, List, Dict, Any
from geoalchemy2.elements import WKTElement
from core.api_models import Location_API, Delivery_API
from core.models import Address
from core.persistent_models import Location
from core.exception_handler import APIException
from core.messages import *
from repositories.location_repository import LocationRepository
from repositories.address_repository import AddressRepository

class LocationService:
    """Service for location-related business logic"""
    
    def __init__(self):
        self.location_repo = LocationRepository()
        self.address_repo = AddressRepository()
    
    def build_address_from_location(self, location: Location_API) -> Address:
        """Build an Address from Location_API"""
        return Address(
            address_street=location.address_street,
            address_city=location.address_city,
            address_postal_code=location.address_postal_code,
            address_country=location.address_country,
        )
    
    def build_address_from_delivery(self, delivery: Delivery_API) -> Address:
        """Build an Address from Delivery_API"""
        address = Address()
        
        if delivery.delivery_address_id:
            address.id_address = delivery.delivery_address_id
        if delivery.address_street:
            address.address_street = delivery.address_street
        if delivery.address_city:
            address.address_city = delivery.address_city
        if delivery.address_postal_code:
            address.address_postal_code = delivery.address_postal_code
        if delivery.address_country:
            address.address_country = delivery.address_country
        
        return address
    
    def build_location_model(self, location: Location_API) -> Location:
        """Build a Location ORM object from Location_API"""
        if not location.location_latitude or not location.location_longitude:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=LOCATION_INSERT_FAILED,
                details="Latitude and longitude must be provided"
            )
        
        # Create address if provided
        address = None
        if any([location.address_street, location.address_city, 
                location.address_postal_code, location.address_country]):
            address = Address(
                address_street=location.address_street,
                address_city=location.address_city,
                address_postal_code=location.address_postal_code,
                address_country=location.address_country,
            )
        
        # Create location
        loc = Location(
            location_position=WKTElement(
                f"POINT({location.location_longitude} {location.location_latitude})",
                srid=4326
            ),
            location_name=location.location_name,
        )
        
        if address:
            loc.location_address = address
        
        return loc
    
    def get_location_by_id(self, location_id: str, with_address: bool = True) -> Optional[Location]:
        """Get location by ID"""
        location = self.location_repo.get_location_by_id(location_id, with_address)
        if not location:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=LOCATION_NOT_FOUND,
                details=f"Location {location_id} not found"
            )
        return location
    
    def get_location_object(self, location_id: str) -> Optional[Location]:
        """Get location object by ID (alias for get_location_by_id)"""
        return self.get_location_by_id(location_id, with_address=False)
    
    def get_address_by_id(self, address_id: str) -> Optional[Address]:
        """Get address by ID"""
        address = self.address_repo.get_address_by_id(address_id)
        if not address:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=ADDRESS_NOT_FOUND,
                details=f"Address {address_id} not found"
            )
        return address
    
    def create_location(self, location_data: Location_API) -> Location:
        """Create a new location"""
        try:
            location = self.build_location_model(location_data)
            created_location = self.location_repo.create_location(location)
            return created_location
        except APIException:
            raise
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=LOCATION_INSERT_FAILED,
                details=f"Failed to insert location: {str(e)}"
            )
    
    def update_location(self, location_id: str, location_data: Location_API) -> Location:
        """Update an existing location"""
        # Get existing location
        existing_location = self.location_repo.get_location_by_id(location_id, with_address=True)
        if not existing_location:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=LOCATION_NOT_FOUND,
                details=f"Location {location_id} not found"
            )
        
        # Update address if it exists
        if existing_location.location_address:
            if location_data.address_street is not None:
                existing_location.location_address.address_street = location_data.address_street
            if location_data.address_city is not None:
                existing_location.location_address.address_city = location_data.address_city
            if location_data.address_postal_code is not None:
                existing_location.location_address.address_postal_code = location_data.address_postal_code
            if location_data.address_country is not None:
                existing_location.location_address.address_country = location_data.address_country
        elif any([location_data.address_street, location_data.address_city,
                  location_data.address_postal_code, location_data.address_country]):
            # Create new address if none exists but data provided
            existing_location.location_address = Address(
                address_street=location_data.address_street,
                address_city=location_data.address_city,
                address_postal_code=location_data.address_postal_code,
                address_country=location_data.address_country,
            )
        
        # Update location fields
        if location_data.location_name is not None:
            existing_location.location_name = location_data.location_name
        
        if location_data.location_latitude and location_data.location_longitude:
            existing_location.location_position = WKTElement(
                f"POINT({location_data.location_longitude} {location_data.location_latitude})",
                srid=4326
            )
        
        # Save changes
        try:
            updated_location = self.location_repo.update_location(existing_location)
            return updated_location
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=LOCATION_UPDATE_FAILED,
                details=f"Failed to update Location {location_id}: {str(e)}"
            )
    
    def delete_location(self, location_id: str) -> bool:
        """Delete a location"""
        return self.location_repo.delete_location(location_id)
    
    def get_nearby_locations(self, latitude: float, longitude: float, radius_km: float = 10) -> List[Location]:
        """Get locations within a radius (requires PostGIS)"""
        # This would use ST_DWithin for spatial queries
        # Implementation depends on your specific spatial query needs
        pass
    
    def create_address_from_location(self, location_data: Location_API) -> Address:
        """Create an address from location data"""
        address = self.build_address_from_location(location_data)
        return self.address_repo.create_address(address)
    
    def update_address(self, address_id: str, address_data: Dict[str, Any]) -> Address:
        """Update an existing address"""
        address = self.get_address_by_id(address_id)
        
        if address_data.get('address_street'):
            address.address_street = address_data['address_street']
        if address_data.get('address_city'):
            address.address_city = address_data['address_city']
        if address_data.get('address_postal_code'):
            address.address_postal_code = address_data['address_postal_code']
        if address_data.get('address_country'):
            address.address_country = address_data['address_country']
        
        return self.address_repo.update_address(address)
    
    def get_location_with_address(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get location with its associated address as a dictionary"""
        location = self.get_location_by_id(location_id, with_address=True)
        
        result = {
            "id_location": location.id_location,
            "location_name": location.location_name,
            "location_position": location.location_position,
        }
        
        if location.location_address:
            result["address"] = {
                "id_address": location.location_address.id_address,
                "street": location.location_address.address_street,
                "city": location.location_address.address_city,
                "postal_code": location.location_address.address_postal_code,
                "country": location.location_address.address_country,
            }
        
        return result