
# here, we make schema translations

from core.api_models import Location_API
from core.models import Address, Location
from features.insertion import insert_or_complete_or_raise

def build_location(location: Location_API):
    address = Address(
                        address_street=location.address_street,
                        address_city=location.address_city,
                        address_postal_code=location.address_postal_code,
                        address_country=location.address_country,)

    loc = Location(
        location_latitude=location.location_latitude,
        location_longitude=location.location_longitude,
        location_name=location.location_name,
        location_address=address)
    
    return loc

def insert_location(location: Location_API):
    
    _location = build_location(location)
    
    code,_location,msg = insert_or_complete_or_raise(_location)
    if (code == 1): return msg
    return _location