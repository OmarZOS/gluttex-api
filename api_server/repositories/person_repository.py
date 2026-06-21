# repositories/person_repository.py
from typing import Optional, List
from core.persistent_models import Location
from core.models import Person, PersonDetails
import storage.storage_broker as storage_broker

class PersonRepository:
    """Repository for Person-related database operations"""
    
    # ==================== Person Operations ====================
    
    def get_person_by_id(self, person_id: str, eager_load: bool = False) -> Optional[Person]:
        """Get person by ID with optional eager loading"""
        if eager_load:
            records = storage_broker.get(
                Person,
                {Person.id_person: person_id},
                None,
                [Person.person_blood_type, {Person.person_location:[Location.position_wkt,Location.location_name,Location.id_location]}, Person.person_details]
            )
        else:
            records = storage_broker.get(
                Person,
                {Person.id_person: person_id},
                None,
                []
            )
        return records[0] if records else None
    
    def get_person_basic(self, person_id: str) -> Optional[Person]:
        """Get person with only basic info"""
        records = storage_broker.get(Person, {Person.id_person: person_id}, None, [])
        return records[0] if records else None
    
    def create_person(self, person: Person) -> Person:
        """Create a new person"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(person)
    
    def update_person(self, person: Person) -> Person:
        """Update an existing person"""
        from features.insertion import update_record_in_api
        return update_record_in_api(person)
    
    def delete_person(self, person: Person) -> bool:
        """Delete a person"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(person)
    
    # ==================== PersonDetails Operations ====================
    
    def get_person_details_by_id(self, details_id: str) -> Optional[PersonDetails]:
        """Get person details by ID"""
        records = storage_broker.get(PersonDetails, {PersonDetails.id_person_details: details_id}, None, [])
        return records[0] if records else None
    
    def get_person_details_object(self, details_id: str) -> Optional[PersonDetails]:
        """Get person details as object with all fields"""
        record = storage_broker.get(PersonDetails, {PersonDetails.id_person_details: details_id}, None, [])
        if not record:
            return None
        
        return PersonDetails(
            id_person_details=record[0].id_person_details,
            person_first_name=record[0].person_first_name,
            person_last_name=record[0].person_last_name,
            person_birth_date=record[0].person_birth_date,
            person_gender=record[0].person_gender,
            person_nationality=record[0].person_nationality,
        )
    
    def create_person_details(self, details: PersonDetails) -> PersonDetails:
        """Create person details"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(details)
    
    def update_person_details(self, details: PersonDetails) -> PersonDetails:
        """Update person details"""
        from features.insertion import update_record_in_api
        return update_record_in_api(details)
    