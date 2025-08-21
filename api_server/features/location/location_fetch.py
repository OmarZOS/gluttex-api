from typing import Optional
from core.api_models import Location_API
from core.models import Address, AppUser, AppUserType, BloodType, Location, Person, PersonDetails
import storage.storage_broker as storage_broker
from features.person.person_fetch import fetch_person_blood_type_object, fetch_person_details_object
from geoalchemy2.elements import WKTElement

def build_location(location: Location_API) -> Location:
    """Helper to build a Location from Location_API."""
    return Location(
        location_position=WKTElement(
            f"POINT({location.location_longitude} {location.location_latitude})",
            srid=4326,
        ),
        location_name=location.location_name,
        location_address_id=location.location_address_id,
    )


def fetch_location_object(location_id: str) -> Optional[Location]:
    """Fetch a Location object by its ID."""
    records = storage_broker.get(Location, {Location.id_location: location_id}, None, [])
    return records[0] if records else None


def fetch_address_object(address_id: str) -> Optional[Address]:
    """Fetch an Address object by its ID."""
    records = storage_broker.get(Address, {Address.id_address: address_id}, None, [])
    return records[0] if records else None


def fetch_location(location_id: str) -> Optional[Location]:
    """Fetch a Location with its related Address."""
    records = storage_broker.get(
        Location,
        {Location.id_location: location_id},
        None,
        [Location.location_address],
    )
    return records[0] if records else None
