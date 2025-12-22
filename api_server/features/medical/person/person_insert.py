from features.business.location.location_insert import insert_location
from core.exception_handler import APIException
from core.api_models import Location_API, Person_API
from core.messages import *
from core.models import Address, BloodType, Location, Person, PersonDetails
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.location.location_fetch import build_location, fetch_address_object, fetch_location_object
from features.medical.person.person_fetch import fetch_only_person_by_id, fetch_person_blood_type_object, fetch_person_details, fetch_person_details_object
from geoalchemy2.elements import WKTElement


def insert_person_details(person: Person_API):
    """
    Insert a new PersonDetails record.
    """
    person_detail = PersonDetails(
        person_first_name=person.person_first_name,
        person_last_name=person.person_last_name,
        person_birth_date=person.person_birth_date,
        person_gender=person.person_gender,
        person_nationality=person.person_nationality,
    )

    try:
        return insert_or_complete_or_raise(person_detail)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=PERSON_DETAIL_INSERT_FAILED,
            details=f"{str(e)}"
        )


def generate_person_object(person: Person_API, location: Location_API = None) -> Person:
    """
    Build a Person object with its details and location.
    Does not insert into DB — only constructs the ORM object.
    """
    mensch = Person()

    # Attach PersonDetails
    person_detail_object = fetch_person_details_object(person.id_person_details)
    if person_detail_object:
        mensch.person_details_id = person.id_person_details
    else:
        mensch.person_details = PersonDetails(
            person_first_name=person.person_first_name,
            person_last_name=person.person_last_name,
            # person_birth_date=person.person_birth_date,
            person_gender=person.person_gender,
            person_nationality=person.person_nationality,
        )
        if person.person_birth_date != None and person.person_birth_date!='':
            mensch.person_details.person_birth_date =person.person_birth_date

    # Attach Location
    if location:
        location_object = fetch_location_object(location.id_location)
        if location_object:
            mensch.person_location_id = location.id_location
        else:
            new_location = build_location(location)
            

            address = fetch_address_object(new_location.location_address_id)
            if not address:
                new_location.location_address = Address(
                    address_street=location.address_street,
                    address_city=location.address_city,
                    address_postal_code=location.address_postal_code,
                    address_country=location.address_country,
                )
            mensch.person_location = new_location

    return mensch


def refresh_or_insert_person(person: Person_API, location: Location_API) -> Person:
    """
    Insert a new person if not exists, or refresh (update) if already exists.
    """

    mensch = fetch_only_person_by_id(person.id_person)
    blood_type = fetch_person_blood_type_object(person.id_blood_type)
    person_detail = fetch_person_details(person.id_person_details)
    person_location = fetch_location_object(location.id_location)

    if(mensch==None):
        mensch = Person(
            person_blood_type_id=blood_type.id_blood_type if blood_type else None,
        )

    
    if person_detail !=[]:
        person_detail[0].person_gender = person.person_gender
        person_detail[0].person_first_name = person.person_first_name
        person_detail[0].person_last_name = person.person_last_name
        person_detail[0].person_nationality = person.person_nationality
        mensch.person_details = person_detail[0]
    else:
        mensch.person_details_id = insert_person_details(person).id_person_details
    if person_location:
        
        person_location.location_name = location.location_name
        person_location.location_position = WKTElement(
            f"POINT({location.location_longitude} {location.location_latitude})",
            srid=4326
        ),
        person_location.location_address.address_city = location.address_city
        person_location.location_address.address_country = location.address_country
        person_location.location_address.address_postal_code = location.address_postal_code
        person_location.location_address.address_street = location.address_street
        # loc = update_record_in_api(person_location)
        mensch.person_location = person_location
    else:
        mensch.person_location_id = insert_location(location).id_location
    try:
        return insert_or_complete_or_raise(mensch)
        # Else → insert new
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=PERSON_INSERT_FAILED,
            details=f"{str(e)}"
        )
