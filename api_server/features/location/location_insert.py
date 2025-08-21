# schema translations for Location

from core.exception_handler import APIException
from core.messages import HTTP_417_EXPECTATION_FAILED, LOCATION_INSERT_FAILED
from core.api_models import Location_API
from core.models import Address, Location
from features.insertion import insert_or_complete_or_raise
from geoalchemy2.elements import WKTElement


def build_location(location: Location_API) -> Location:
    """
    Build a Location ORM object (with nested Address) from a Location_API schema.
    """
    if not location.location_latitude or not location.location_longitude:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=LOCATION_INSERT_FAILED,
            details="Latitude and longitude must be provided"
        )

    address = Address(
        address_street=location.address_street,
        address_city=location.address_city,
        address_postal_code=location.address_postal_code,
        address_country=location.address_country,
    )

    loc = Location(
        location_position=WKTElement(
            f"POINT({location.location_longitude} {location.location_latitude})",
            srid=4326
        ),
        location_name=location.location_name,
        location_address=address,
    )

    return loc


def insert_location(location: Location_API) -> Location:
    """
    Insert a new Location into the database or raise a controlled API exception.
    """
    try:
        loc = build_location(location)
        loc = insert_or_complete_or_raise(loc)
    except APIException:  # already wrapped
        raise
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=LOCATION_INSERT_FAILED,
            details=f"Failed to insert location: {str(e)}"
        )

    return loc
