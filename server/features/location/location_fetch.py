
from server.core.models import Address, AppUser, AppUserType, BloodType, Location, Person, PersonDetails
import server.storage.storage_broker as storage_broker
from server.features.person.person_fetch import fetch_person_blood_type_object, fetch_person_details_object

def fetch_location_object(location_id: str):
    record = storage_broker.get(Location,{Location.id_location:location_id},None,[])
    if record == []:
        return None
    
    location = Location(
                    id_location=record[0].id_location,
                    location_latitude = record[0].location_latitude,
                    location_longitude = record[0].location_longitude,
                    location_name = record[0].location_name,
                    location_address_id = record[0].location_address_id,)
    return location
def fetch_address_object(address_id: str):
    record = storage_broker.get(Address,{Address.id_address:address_id},None,[])
    if record == []:
        return None
    
    address = Address(
                    id_address=record[0].id_address,
                    address_street = record[0].address_street,
                    address_city = record[0].address_city,
                    address_postal_code = record[0].address_postal_code,
                    address_country = record[0].address_country,)
    return address



def fetch_location(location_id: str):
    return storage_broker.get(Location,{Location.id_location:location_id},None,[Location.location_address])
