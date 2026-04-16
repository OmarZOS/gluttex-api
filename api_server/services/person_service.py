# services/person_service.py
from typing import Optional, Dict, Any
from core.api_models import Person_API, Location_API
from core.exception_handler import APIException
from core.messages import *
from core.models import Person, PersonDetails, BloodType
from core.persistent_models import Location
from repositories.person_repository import PersonRepository
from services.location_service import LocationService

class PersonService:
    """Service for person-related operations"""
    
    def __init__(self):
        self.person_repo = PersonRepository()
        self.location_service = LocationService()
    
    # ==================== Person Operations ====================
    
    def get_person_by_id(self, person_id: str, full: bool = False) -> Optional[Person]:
        """Get person by ID"""
        person = self.person_repo.get_person_by_id(person_id, eager_load=full)
        if not person:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PERSON_NOT_EXISTS,
                details=f"Person {person_id} not found"
            )
        return person
    
    def get_person_basic(self, person_id: str) -> Optional[Person]:
        """Get person with basic info"""
        return self.person_repo.get_person_basic(person_id)
    
    def create_person_details(self, person_data: Person_API) -> PersonDetails:
        """Create person details"""
        person_detail = PersonDetails(
            person_first_name=person_data.person_first_name,
            person_last_name=person_data.person_last_name,
            person_birth_date=person_data.person_birth_date,
            person_gender=person_data.person_gender,
            person_nationality=person_data.person_nationality,
        )
        
        try:
            return self.person_repo.create_person_details(person_detail)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=PERSON_DETAIL_INSERT_FAILED,
                details=f"Failed to insert person details: {str(e)}"
            )
    
    def generate_person_object(
        self,
        person_data: Person_API,
        location_data: Optional[Location_API] = None
    ) -> Person:
        """Generate a Person ORM object without inserting to DB"""
        
        person = Person()
        
        # Handle blood type
        if person_data.id_blood_type:
            blood_type = self.person_repo.get_blood_type_object(person_data.id_blood_type)
            if blood_type:
                person.person_blood_type_id = blood_type.id_blood_type
        
        # Handle person details
        existing_details = self.person_repo.get_person_details_by_id(person_data.id_person_details)
        if existing_details:
            person.person_details_id = existing_details.id_person_details
        else:
            person.person_details = PersonDetails(
                person_first_name=person_data.person_first_name,
                person_last_name=person_data.person_last_name,
                person_birth_date=person_data.person_birth_date,
                person_gender=person_data.person_gender,
                person_nationality=person_data.person_nationality,
            )
        
        # Handle location
        if location_data:
            location = self.location_service.get_location_object(location_data.id_location)
            if location:
                person.person_location_id = location.id_location
            else:
                person.person_location = self.location_service.build_location_model(location_data)
        
        return person
    
    def refresh_or_insert_person(
        self,
        person_data: Person_API,
        location_data: Location_API
    ) -> Person:
        """Insert or update a person"""
        
        # Get existing person
        existing_person = self.person_repo.get_person_basic(person_data.id_person)
        
        # Validate blood type
        blood_type = None
        if person_data.id_blood_type:
            blood_type = self.person_repo.get_blood_type_object(person_data.id_blood_type)
            if not blood_type:
                raise APIException(
                    status=HTTP_417_EXPECTATION_FAILED,
                    code=BLOOD_TYPE_NOT_EXISTS,
                    message=f"{BLOOD_TYPE_NOT_EXISTS}: {person_data.id_blood_type}"
                )
        
        # Handle person details
        existing_details = self.person_repo.get_person_details_by_id(person_data.id_person_details)
        
        if existing_person:
            # Update existing person
            if existing_details:
                existing_details.person_gender = person_data.person_gender
                existing_details.person_first_name = person_data.person_first_name
                existing_details.person_last_name = person_data.person_last_name
                existing_details.person_nationality = person_data.person_nationality
                existing_person.person_details = existing_details
            else:
                existing_person.person_details_id = self.create_person_details(person_data).id_person_details
            
            if blood_type:
                existing_person.person_blood_type_id = blood_type.id_blood_type
            
            # Handle location
            location = self.location_service.get_location_object(location_data.id_location)
            if location:
                location = self.location_service.update_location(location_data.id_location, location_data)
                existing_person.person_location_id = location.id_location
            else:
                new_location = self.location_service.create_location(location_data)
                existing_person.person_location_id = new_location.id_location
            
            try:
                return self.person_repo.update_person(existing_person)
            except Exception as e:
                raise APIException(
                    status=HTTP_417_EXPECTATION_FAILED,
                    code=PERSON_INSERT_FAILED,
                    details=str(e)
                )
        else:
            # Create new person
            person = Person()
            
            if blood_type:
                person.person_blood_type_id = blood_type.id_blood_type
            
            if existing_details:
                person.person_details_id = existing_details.id_person_details
            else:
                person.person_details_id = self.create_person_details(person_data).id_person_details
            
            # Handle location
            location = self.location_service.get_location_object(location_data.id_location)
            if location:
                person.person_location_id = location.id_location
            else:
                person.person_location_id = self.location_service.create_location(location_data).id_location
            
            try:
                return self.person_repo.create_person(person)
            except Exception as e:
                raise APIException(
                    status=HTTP_417_EXPECTATION_FAILED,
                    code=PERSON_INSERT_FAILED,
                    details=str(e)
                )
    
    def delete_person(self, person_id: str) -> Dict[str, Any]:
        """Delete a person"""
        person = self.get_person_by_id(person_id)
        success = self.person_repo.delete_person(person)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=PERSON_DELETE_FAILED,
                details=f"Failed to delete person {person_id}"
            )
        
        return {
            "message": "Person deleted successfully",
            "person_id": person_id
        }
    
    # ==================== Blood Type Operations ====================
    
    def get_blood_type_by_id(self, blood_type_id: str) -> BloodType:
        """Get blood type by ID"""
        blood_type = self.person_repo.get_blood_type_by_id(blood_type_id)
        if not blood_type:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=BLOOD_TYPE_NOT_EXISTS,
                message=f"{BLOOD_TYPE_NOT_EXISTS}: {blood_type_id}"
            )
        return blood_type
    
    def get_all_blood_types(self) -> list:
        """Get all blood types"""
        return self.person_repo.get_all_blood_types()