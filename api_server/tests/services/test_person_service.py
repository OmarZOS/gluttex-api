# # tests/services/test_person_service.py
# """
# Unit tests for PersonService
# """

# import pytest
# from unittest.mock import Mock, patch, MagicMock
# from datetime import date
# from typing import Optional

# from api_server.core.persistent_models import Location
# from core.api_models import Person_API, Location_API, Gender, BloodType, CountryCode
# from core.models import Person, PersonDetails
# from core.exceptions.specific.person_exceptions import *
# from core.exceptions.handler import DatabaseException
# from services.person_service import PersonService


# # ==================== FIXTURES ====================

# @pytest.fixture
# def mock_person_repo():
#     """Create mock person repository"""
#     return Mock()


# @pytest.fixture
# def mock_location_service():
#     """Create mock location service"""
#     return Mock()


# @pytest.fixture
# def person_service(mock_person_repo, mock_location_service):
#     """Create person service with mocked dependencies"""
#     service = PersonService()
#     service.person_repo = mock_person_repo
#     service.location_service = mock_location_service
#     return service


# @pytest.fixture
# def sample_person_api():
#     """Create sample person API data"""
#     return Person_API(
#         id_person=123,
#         person_details_id=456,
#         id_person_details=456,
#         person_first_name="John",
#         person_last_name="Doe",
#         person_birth_date=date(1990, 1, 1),
#         person_gender=Gender.MALE,
#         person_nationality=CountryCode.US,
#         blood_type=BloodType.A_POSITIVE
#     )


# @pytest.fixture
# def sample_person_api_without_details():
#     """Create sample person API data without existing details"""
#     return Person_API(
#         id_person=0,
#         person_details_id=None,
#         id_person_details=0,
#         person_first_name="Jane",
#         person_last_name="Smith",
#         person_birth_date=date(1995, 5, 15),
#         person_gender=Gender.FEMALE,
#         person_nationality=CountryCode.CA,
#         blood_type=BloodType.O_NEGATIVE
#     )


# @pytest.fixture
# def sample_location_api():
#     """Create sample location API data"""
#     return Location_API(
#         id_location=789,
#         location_latitude=40.7128,
#         location_longitude=-74.0060,
#         location_name="Home",
#         location_address_id=101,
#         id_address=101,
#         address_street="123 Main St",
#         address_city="New York",
#         address_postal_code="10001",
#         address_country="USA"
#     )


# @pytest.fixture
# def sample_person_details():
#     """Create sample person details"""
#     details = Mock(spec=PersonDetails)
#     details.id_person_details = 456
#     details.person_first_name = "John"
#     details.person_last_name = "Doe"
#     details.person_birth_date = date(1990, 1, 1)
#     details.person_gender = "Male"
#     details.person_nationality = "US"
#     return details


# @pytest.fixture
# def sample_person_model(sample_person_details):
#     """Create sample person model"""
#     person = Mock(spec=Person)
#     person.id_person = 123
#     person.person_details_id = 456
#     person.person_blood_type = "A+"
#     person.person_location_id = 789
#     person.person_details = sample_person_details
#     return person


# @pytest.fixture
# def sample_location_model():
#     """Create sample location model"""
#     location = Mock(spec=Location)
#     location.id_location = 789
#     location.location_latitude = 40.7128
#     location.location_longitude = -74.0060
#     return location


# # ==================== get_person_by_id TESTS ====================

# class TestGetPersonById:
#     """Tests for get_person_by_id method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful retrieval of person by ID"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
        
#         result = person_service.get_person_by_id("123", full=True)
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_by_id.assert_called_once_with("123", eager_load=True)
    
#     def test_success_without_full_load(self, person_service, mock_person_repo, sample_person_model):
#         """Test getting person without eager loading"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
        
#         result = person_service.get_person_by_id("123", full=False)
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_by_id.assert_called_once_with("123", eager_load=False)
    
#     def test_not_found(self, person_service, mock_person_repo):
#         """Test getting non-existent person raises exception"""
#         mock_person_repo.get_person_by_id.return_value = None
        
#         with pytest.raises(PersonNotFoundException) as exc_info:
#             person_service.get_person_by_id("999")
        
#         assert exc_info.value.error_code.value == "PERSON_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
#         assert exc_info.value.details["search_type"] == "by_id"


# # ==================== get_person_basic TESTS ====================

# class TestGetPersonBasic:
#     """Tests for get_person_basic method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful retrieval of basic person info"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
        
#         result = person_service.get_person_basic("123")
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_basic.assert_called_once_with("123")
    
#     def test_not_found(self, person_service, mock_person_repo):
#         """Test getting basic info for non-existent person"""
#         mock_person_repo.get_person_basic.return_value = None
        
#         result = person_service.get_person_basic("999")
        
#         assert result is None


# # ==================== create_person_details TESTS ====================

# class TestCreatePersonDetails:
#     """Tests for create_person_details method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test successful creation of person details"""
#         mock_person_repo.create_person_details.return_value = sample_person_details
        
#         result = person_service.create_person_details(sample_person_api)
        
#         assert result == sample_person_details
#         mock_person_repo.create_person_details.assert_called_once()
    
#     def test_failure(self, person_service, mock_person_repo, sample_person_api):
#         """Test person details creation failure"""
#         mock_person_repo.create_person_details.side_effect = Exception("Database error")
        
#         with pytest.raises(PersonDetailsCreationException) as exc_info:
#             person_service.create_person_details(sample_person_api)
        
#         assert exc_info.value.error_code.value == "PERSON_DETAIL_INSERT_FAILED"
#         assert exc_info.value.status_code == 417


# # ==================== generate_person_object TESTS ====================

# class TestGeneratePersonObject:
#     """Tests for generate_person_object method"""
    
#     def test_with_existing_details(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test generating person object with existing person details"""
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
        
#         result = person_service.generate_person_object(sample_person_api)
        
#         assert result.person_details_id == sample_person_details.id_person_details
#         mock_person_repo.get_person_details_by_id.assert_called_once_with(456)
    
#     def test_without_existing_details(self, person_service, mock_person_repo, sample_person_api):
#         """Test generating person object without existing person details"""
#         mock_person_repo.get_person_details_by_id.return_value = None
        
#         result = person_service.generate_person_object(sample_person_api)
        
#         assert result.person_details.person_first_name == sample_person_api.person_first_name
#         assert result.person_details.person_last_name == sample_person_api.person_last_name
#         assert result.person_details.person_birth_date == sample_person_api.person_birth_date
    
#     def test_with_location(self, person_service, mock_person_repo, sample_person_api, mock_location_service):
#         """Test generating person object with location"""
#         mock_person_repo.get_person_details_by_id.return_value = None
        
#         # Create a simple location object
#         mock_location = Mock()
#         mock_location.id_location = 789
        
#         # Mock the location service methods
#         mock_location_service.get_location_object.return_value = mock_location
        
#         result = person_service.generate_person_object(sample_person_api, Location_API(
#             id_location=789,
#             location_latitude=40.7128,
#             location_longitude=-74.0060,
#             location_name="Home",
#             location_address_id=101,
#             id_address=101,
#             address_street="123 Main St",
#             address_city="New York",
#             address_postal_code="10001",
#             address_country="USA"
#         ))
        
#         assert result.person_location_id == 789
#         mock_location_service.get_location_object.assert_called_once_with(789)


# # ==================== refresh_or_insert_person TESTS ====================

# class TestRefreshOrInsertPerson:
#     """Tests for refresh_or_insert_person method"""
    
#     def test_update_existing_person(self, person_service, mock_person_repo, sample_person_api, 
#                                     sample_person_model, sample_person_details, sample_location_api):
#         """Test updating an existing person"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.update_person.return_value = sample_person_model
        
#         # Mock location service
#         mock_location = Mock()
#         mock_location.id_location = 789
#         person_service.location_service.get_location_object.return_value = mock_location
#         person_service.location_service.update_location.return_value = mock_location
        
#         result = person_service.refresh_or_insert_person(
#             sample_person_api, 
#             sample_location_api
#         )
        
#         assert result == sample_person_model
#         mock_person_repo.update_person.assert_called_once_with(sample_person_model)
    
#     def test_create_new_person(self, person_service, mock_person_repo, sample_person_api_without_details, 
#                                sample_location_api, sample_person_details):
#         """Test creating a new person"""
#         mock_person_repo.get_person_basic.return_value = None
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.create_person_details.return_value = sample_person_details
#         mock_person_repo.create_person.return_value = Mock(spec=Person)
        
#         # Mock location service
#         mock_location = Mock()
#         mock_location.id_location = 789
#         person_service.location_service.get_location_object.return_value = None
#         person_service.location_service.create_location.return_value = mock_location
        
#         result = person_service.refresh_or_insert_person(
#             sample_person_api_without_details,
#             sample_location_api
#         )
        
#         assert result is not None
#         mock_person_repo.create_person.assert_called_once()
    
#     def test_create_new_person_with_existing_details(self, person_service, mock_person_repo,
#                                                      sample_person_api_without_details, 
#                                                      sample_location_api, sample_person_details):
#         """Test creating a new person with existing person details"""
#         mock_person_repo.get_person_basic.return_value = None
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.create_person.return_value = Mock(spec=Person)
        
#         # Mock location service
#         mock_location = Mock()
#         mock_location.id_location = 789
#         person_service.location_service.get_location_object.return_value = None
#         person_service.location_service.create_location.return_value = mock_location
        
#         result = person_service.refresh_or_insert_person(
#             sample_person_api_without_details,
#             sample_location_api
#         )
        
#         assert result is not None
#         assert result.person_details_id == sample_person_details.id_person_details
#         mock_person_repo.create_person_details.assert_not_called()
    
#     def test_update_failure(self, person_service, mock_person_repo, sample_person_api, 
#                            sample_person_model, sample_person_details, sample_location_api):
#         """Test update failure"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.update_person.side_effect = Exception("Update failed")
        
#         # Mock location service
#         mock_location = Mock()
#         mock_location.id_location = 789
#         person_service.location_service.get_location_object.return_value = mock_location
#         person_service.location_service.update_location.return_value = mock_location
        
#         with pytest.raises(PersonUpdateFailedException) as exc_info:
#             person_service.refresh_or_insert_person(sample_person_api, sample_location_api)
        
#         assert exc_info.value.error_code.value == "PERSON_UPDATE_FAILED"
#         assert exc_info.value.status_code == 500


# # ==================== delete_person TESTS ====================

# class TestDeletePerson:
#     """Tests for delete_person method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful person deletion"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
#         mock_person_repo.delete_person.return_value = True
        
#         result = person_service.delete_person("123")
        
#         assert result["message"] == "Person deleted successfully"
#         assert result["person_id"] == "123"
#         mock_person_repo.delete_person.assert_called_once_with(sample_person_model)
    
#     def test_not_found(self, person_service, mock_person_repo):
#         """Test deleting non-existent person"""
#         mock_person_repo.get_person_by_id.return_value = None
        
#         with pytest.raises(PersonNotFoundException) as exc_info:
#             person_service.delete_person("999")
        
#         assert exc_info.value.error_code.value == "PERSON_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
    
#     def test_failure(self, person_service, mock_person_repo, sample_person_model):
#         """Test deletion failure"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
#         mock_person_repo.delete_person.return_value = False
        
#         with pytest.raises(PersonDeleteFailedException) as exc_info:
#             person_service.delete_person("123")
        
#         assert exc_info.value.error_code.value == "PERSON_DELETE_FAILED"
#         assert exc_info.value.status_code == 500


# # ==================== get_person_details_by_id TESTS ====================

# class TestGetPersonDetailsById:
#     """Tests for get_person_details_by_id method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_details):
#         """Test successful retrieval of person details by ID"""
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
        
#         result = person_service.get_person_details_by_id(456)
        
#         assert result == sample_person_details
#         mock_person_repo.get_person_details_by_id.assert_called_once_with(456)
    
#     def test_not_found(self, person_service, mock_person_repo):
#         """Test getting non-existent person details"""
#         mock_person_repo.get_person_details_by_id.return_value = None
        
#         result = person_service.get_person_details_by_id(999)
        
#         assert result is None
#         mock_person_repo.get_person_details_by_id.assert_called_once_with(999)


# # ==================== update_person_details TESTS ====================

# class TestUpdatePersonDetails:
#     """Tests for update_person_details method"""
    
#     def test_success(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test successful update of person details"""
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.update_person_details.return_value = sample_person_details
        
#         result = person_service.update_person_details(456, sample_person_api)
        
#         assert result == sample_person_details
#         mock_person_repo.update_person_details.assert_called_once()
    
#     def test_not_found(self, person_service, mock_person_repo, sample_person_api):
#         """Test updating non-existent person details"""
#         mock_person_repo.get_person_details_by_id.return_value = None
        
#         with pytest.raises(PersonDetailsNotFoundException) as exc_info:
#             person_service.update_person_details(999, sample_person_api)
        
#         assert exc_info.value.error_code.value == "PERSON_DETAILS_NOT_FOUND"
#         assert exc_info.value.status_code == 404
    
#     def test_database_error(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test database error during update"""
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.update_person_details.side_effect = Exception("Database error")
        
#         with pytest.raises(DatabaseException) as exc_info:
#             person_service.update_person_details(456, sample_person_api)
        
#         assert "Failed to update person details" in str(exc_info.value)


# # ==================== Utility Methods TESTS ====================

# class TestUtilityMethods:
#     """Tests for utility methods"""
    
#     def test_person_exists_true(self, person_service, mock_person_repo, sample_person_model):
#         """Test person_exists returns True when person exists"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
        
#         result = person_service.person_exists("123")
        
#         assert result is True
#         mock_person_repo.get_person_basic.assert_called_once_with("123")
    
#     def test_person_exists_false(self, person_service, mock_person_repo):
#         """Test person_exists returns False when person doesn't exist"""
#         mock_person_repo.get_person_basic.return_value = None
        
#         result = person_service.person_exists("999")
        
#         assert result is False
    
#     def test_get_person_full_name_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test getting person full name successfully"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
        
#         result = person_service.get_person_full_name("123")
        
#         assert result == "John Doe"
#         mock_person_repo.get_person_basic.assert_called_once_with("123")
    
#     def test_get_person_full_name_no_details(self, person_service, mock_person_repo):
#         """Test getting full name when person has no details"""
#         person = Mock(spec=Person)
#         person.person_details = None
#         mock_person_repo.get_person_basic.return_value = person
        
#         result = person_service.get_person_full_name("123")
        
#         assert result is None
    
#     def test_get_person_full_name_not_found(self, person_service, mock_person_repo):
#         """Test getting full name for non-existent person"""
#         mock_person_repo.get_person_basic.return_value = None
        
#         result = person_service.get_person_full_name("999")
        
#         assert result is None


# # ==================== search_persons TESTS ====================

# class TestSearchPersons:
#     """Tests for search_persons method"""
    
#     def test_search_by_first_name(self, person_service, mock_person_repo, sample_person_model):
#         """Test searching persons by first name"""
#         mock_person_repo.get_persons_by_conditions.return_value = [sample_person_model]
        
#         results = person_service.search_persons(first_name="John", limit=10)
        
#         assert len(results) == 1
#         assert results[0] == sample_person_model
#         mock_person_repo.get_persons_by_conditions.assert_called_once_with(
#             {"person_first_name": "John"}, limit=10, offset=0
#         )
    
#     def test_search_by_last_name(self, person_service, mock_person_repo, sample_person_model):
#         """Test searching persons by last name"""
#         mock_person_repo.get_persons_by_conditions.return_value = [sample_person_model]
        
#         results = person_service.search_persons(last_name="Doe")
        
#         assert len(results) == 1
#         mock_person_repo.get_persons_by_conditions.assert_called_once_with(
#             {"person_last_name": "Doe"}, limit=20, offset=0
#         )
    
#     def test_search_with_pagination(self, person_service, mock_person_repo, sample_person_model):
#         """Test searching persons with pagination"""
#         mock_person_repo.get_persons_by_conditions.return_value = [sample_person_model]
        
#         results = person_service.search_persons(
#             first_name="John", 
#             last_name="Doe", 
#             limit=5, 
#             offset=10
#         )
        
#         assert len(results) == 1
#         mock_person_repo.get_persons_by_conditions.assert_called_once_with(
#             {"person_first_name": "John", "person_last_name": "Doe"}, 
#             limit=5, 
#             offset=10
#         )
    
#     def test_search_with_no_conditions(self, person_service, mock_person_repo):
#         """Test search with no conditions returns empty list"""
#         results = person_service.search_persons()
        
#         assert results == []
#         mock_person_repo.get_persons_by_conditions.assert_not_called()
    
#     def test_search_handles_exception(self, person_service, mock_person_repo):
#         """Test search handles exceptions gracefully"""
#         mock_person_repo.get_persons_by_conditions.side_effect = Exception("Database error")
        
#         results = person_service.search_persons(first_name="John")
        
#         assert results == []


# # ==================== RUN TESTS ====================

# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])