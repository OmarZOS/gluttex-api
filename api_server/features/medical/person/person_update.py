from core.exception_handler import APIException
from core.api_models import Location_API, Person_API
from core.messages import (
    HTTP_417_EXPECTATION_FAILED,
    PERSON_INSERT_FAILED,
    BLOOD_TYPE_NOT_EXISTS,
)
from core.models import Address, Location, Person, PersonDetails
from features.insertion import insert_or_complete_or_raise, update_record_in_api
from features.business.location.location_fetch import build_location, fetch_address_object, fetch_location_object
from features.medical.person.person_fetch import (
    fetch_person_blood_type_object,
    fetch_person_details_object,
)



def insert_person_details(person: Person_API) -> PersonDetails:
    """
    Insert or complete PersonDetails for a given Person_API.
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
            code=PERSON_INSERT_FAILED,
            details=f"Failed to insert person details: {str(e)}",
        )


def _build_address(location: Location_API) -> Address:
    """Helper to build an Address from Location_API."""
    return Address(
        address_street=location.address_street,
        address_city=location.address_city,
        address_postal_code=location.address_postal_code,
        address_country=location.address_country,
    )





def generate_person_object(person: Person_API, location: Location_API = None) -> Person:
    """
    Build a Person ORM object with nested PersonDetails and Location if needed.
    """
    mensch = Person()

    # Attach or build person details
    person_detail = fetch_person_details_object(person.id_person_details)
    if person_detail:
        mensch.person_details_id = person_detail.id_person_details
    else:
        mensch.person_details = PersonDetails(
            person_first_name=person.person_first_name,
            person_last_name=person.person_last_name,
            person_birth_date=person.person_birth_date,
            person_gender=person.person_gender,
            person_nationality=person.person_nationality,
        )

    # Attach or build location
    if location:
        location_object = fetch_location_object(location.id_location)
        if location_object:
            mensch.person_location_id = location_object.id_location
        else:
            new_location = build_location(location)

            address_object = fetch_address_object(location.location_address_id)
            if not address_object:
                new_location.location_address = _build_address(location)

            mensch.person_location = new_location

    return mensch


def update_person(
    person: Person_API, location_id: str, person_details_id: str, id_blood_type: str
) -> Person:
    """
    Update a Person record with existing foreign keys.
    """
    blood_type = fetch_person_blood_type_object(id_blood_type)
    if not blood_type:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=BLOOD_TYPE_NOT_EXISTS,
            details=f"Blood type {id_blood_type} not found",
        )

    person_detail = fetch_person_details_object(person_details_id)
    person_location = fetch_location_object(location_id)

    mensch = Person(
        id_person=person.id_person,
        person_blood_type_id=blood_type.id_blood_type,
    )

    if person_detail:
        mensch.person_details_id = person_detail.id_person_details
    if person_location:
        mensch.person_location_id = person_location.id_location

    try:
        return update_record_in_api(mensch)
    except Exception as e:
        raise APIException(
            status=HTTP_417_EXPECTATION_FAILED,
            code=PERSON_INSERT_FAILED,
            details=f"Failed to update person: {str(e)}",
        )
