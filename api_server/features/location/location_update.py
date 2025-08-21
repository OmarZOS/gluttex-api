from core.exception_handler import APIException
from core.messages import *
from core.api_models import Location_API
from core.models import Address, Location
from features.insertion import insert_or_complete_or_raise
from geoalchemy2.elements import WKTElement
from storage import storage_broker


def update_location(location_id: str, location: Location_API):
    """
    Update an existing Location and its related Address.
    """

    # Fetch the existing location
    existing_location = storage_broker.get(Location, {Location.id_location: location_id}, None, [Location.location_address])
    if not existing_location:
        raise APIException(status=HTTP_404_NOT_FOUND, code=LOCATION_NOT_FOUND, details=f"Location {location_id} not found")
    
    loc = existing_location[0]

    # Update the address if it exists, else create new
    if loc.location_address:
        loc.location_address.address_street = location.address_street
        loc.location_address.address_city = location.address_city
        loc.location_address.address_postal_code = location.address_postal_code
        loc.location_address.address_country = location.address_country
    else:
        loc.location_address = Address(
            address_street=location.address_street,
            address_city=location.address_city,
            address_postal_code=location.address_postal_code,
            address_country=location.address_country,
        )

    # Update location fields
    loc.location_name = location.location_name
    loc.location_position = WKTElement(
        f"POINT({location.location_longitude} {location.location_latitude})", srid=4326
    )

    # Try saving
    try:
        updated_location = insert_or_complete_or_raise(loc)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=LOCATION_UPDATE_FAILED,
            details=f"Failed to update Location {location_id}: {str(e)}"
        )

    return updated_location
