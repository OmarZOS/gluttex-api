from core.api_models import Location_API, Person_API
from core.messages import BLOOD_TYPE_NOT_EXISTS
from core.models import Address, BloodType, Location, Person, PersonDetails
from features.insertion import insert_or_complete_or_raise
from features.location.location_fetch import fetch_address_object, fetch_location, fetch_location_object
from features.person.person_fetch import fetch_person_blood_type_object, fetch_person_details_object
from geoalchemy2.elements import WKTElement


def insert_person_details(person: Person_API):
    person_detail = PersonDetails(
        id_person_details=person.id_person_details,
        person_first_name=person.person_first_name,
        person_last_name=person.person_last_name,
        person_birth_date=person.person_birth_date,
        person_gender=person.person_gender,
        person_nationality=person.person_nationality,
    )
    code,person_detail,msg = insert_or_complete_or_raise(person_detail)
    if (code == 1): 
        raise Exception(msg)
    return person_detail

def generate_person_object(person: Person_API,location: Location_API=None):

    blood_type = fetch_person_blood_type_object(person.id_blood_type)
    
    if blood_type is None:
        raise Exception(BLOOD_TYPE_NOT_EXISTS)
    mensch = Person(
                    # person_details_id=person.person_details_id, 
                    person_blood_type_id=blood_type.id_blood_type, 
                    # person_location_id=location.id_location
                    )

    person_detail_object = fetch_person_details_object(person.id_person_details)

    if person_detail_object:
        mensch.person_details_id = person.person_details_id
    else:
        person_detail = PersonDetails(
            
            person_first_name=person.person_first_name,
            person_last_name=person.person_last_name,
            person_birth_date=person.person_birth_date,
            person_gender=person.person_gender,
            person_nationality=person.person_nationality,
        )
        mensch.person_details = person_detail

    location_object = fetch_location_object(location.id_location)

    if location_object:
        mensch.person_location_id = location.id_location
    else:
        mensch.person_location = Location(

                    location_position= WKTElement(f"POINT({location.location_longitude} {location.location_latitude})", srid=4326),
                    location_name = location.location_name,
                    location_address_id = location.location_address_id,)
        
        _location = fetch_address_object(mensch.person_location.location_address_id)

        if not _location:  
            mensch.person_location.location_address = Address(
                    address_street = location.address_street,
                    address_city = location.address_city,
                    address_postal_code = location.address_postal_code,
                    address_country = location.address_country,)

    return mensch


def insert_person(person: Person_API, location_id:str,person_details_id: str,id_blood_type:str):
    try:
        blood_type = fetch_person_blood_type_object(id_blood_type)
        person_detail = fetch_person_details_object(person_details_id)
        person_location = fetch_location_object(location_id)
    except Exception as e:
        raise e
    mensch = Person(
            id_person= person.id_person,
            person_details_id=person_detail.id_person_details,
            person_blood_type_id=blood_type.id_blood_type,
            person_location_id=person_location.id_location,
        )
    
    code,mensch,msg = insert_or_complete_or_raise(mensch)
    if (code == 1): raise Exception(msg)
    return mensch




