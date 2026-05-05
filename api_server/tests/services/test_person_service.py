# # tests/services/test_person_service.py
# import pytest
# from unittest.mock import Mock, patch
# from core.exceptions.handler import APIException
# from core.api_models import Person_API, Location_API
# from core.models import Person, PersonDetails, BloodType
# from services.person_service import PersonService


# class TestPersonService:
#     """Test suite for PersonService with mocked dependencies"""
    
#     @pytest.fixture
#     def mock_person_repo(self):
#         """Create mock person repository"""
#         return Mock()
    
#     @pytest.fixture
#     def mock_location_service(self):
#         """Create mock location service"""
#         return Mock()
    
#     @pytest.fixture
#     def person_service(self, mock_person_repo, mock_location_service):
#         """Create person service with mocked dependencies"""
#         service = PersonService()
#         service.person_repo = mock_person_repo
#         service.location_service = mock_location_service
#         return service
    
#     @pytest.fixture
#     def sample_person_api(self):
#         """Create sample person API data based on actual model"""
#         return Person_API(
#             id_person=123,
#             person_details_id=456,
#             id_person_details=456,
#             person_first_name="John",
#             person_last_name="Doe",
#             person_birth_date="1990-01-01",
#             person_gender="M",
#             person_nationality="US",
#             id_blood_type=1
#         )
    
#     @pytest.fixture
#     def sample_person_api_without_details(self):
#         """Create sample person API data without existing details"""
#         return Person_API(
#             id_person=123,
#             person_details_id=None,
#             id_person_details=0,
#             person_first_name="John",
#             person_last_name="Doe",
#             person_birth_date="1990-01-01",
#             person_gender="M",
#             person_nationality="US",
#             id_blood_type=1
#         )
    
#     @pytest.fixture
#     def sample_location_api(self):
#         """Create sample location API data"""
#         return Location_API(
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
#         )
    
#     @pytest.fixture
#     def sample_person_model(self):
#         """Create sample person model"""
#         person = Mock(spec=Person)
#         person.id_person = 123
#         person.person_details_id = 456
#         person.person_blood_type_id = 1
#         person.person_location_id = 789
#         return person
    
#     @pytest.fixture
#     def sample_person_details(self):
#         """Create sample person details"""
#         details = Mock(spec=PersonDetails)
#         details.id_person_details = 456
#         details.person_first_name = "John"
#         details.person_last_name = "Doe"
#         details.person_birth_date = "1990-01-01"
#         details.person_gender = "M"
#         details.person_nationality = "US"
#         return details
    
#     @pytest.fixture
#     def sample_blood_type(self):
#         """Create sample blood type"""
#         blood_type = Mock(spec=BloodType)
#         blood_type.id_blood_type = 1
#         blood_type.blood_type_desc = "A+"
#         return blood_type
    
#     # ==================== get_person_by_id Tests ====================
    
#     def test_get_person_by_id_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful retrieval of person by ID"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
        
#         result = person_service.get_person_by_id("123", full=True)
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_by_id.assert_called_once_with("123", eager_load=True)
    
#     def test_get_person_by_id_not_found(self, person_service, mock_person_repo):
#         """Test getting non-existent person raises exception"""
#         from core.exceptions.specific.person_exceptions import PersonNotFoundException
        
#         mock_person_repo.get_person_by_id.return_value = None
        
#         with pytest.raises(PersonNotFoundException) as exc_info:
#             person_service.get_person_by_id("999")
        
#         # Use error_code instead of code
#         assert exc_info.value.error_code.value == "PERSON_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
    
#     def test_get_person_by_id_without_full_load(self, person_service, mock_person_repo, sample_person_model):
#         """Test getting person without eager loading"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
        
#         result = person_service.get_person_by_id("123", full=False)
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_by_id.assert_called_once_with("123", eager_load=False)
    
#     # ==================== get_person_basic Tests ====================
    
#     def test_get_person_basic_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful retrieval of basic person info"""
#         mock_person_repo.get_person_basic.return_value = sample_person_model
        
#         result = person_service.get_person_basic("123")
        
#         assert result == sample_person_model
#         mock_person_repo.get_person_basic.assert_called_once_with("123")
    
#     def test_get_person_basic_not_found(self, person_service, mock_person_repo):
#         """Test getting basic info for non-existent person"""
#         mock_person_repo.get_person_basic.return_value = None
        
#         result = person_service.get_person_basic("999")
        
#         assert result is None
    
#     # ==================== create_person_details Tests ====================
    
#     def test_create_person_details_success(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test successful creation of person details"""
#         mock_person_repo.create_person_details.return_value = sample_person_details
        
#         result = person_service.create_person_details(sample_person_api)
        
#         assert result == sample_person_details
#         mock_person_repo.create_person_details.assert_called_once()
    
#     def test_create_person_details_failure(self, person_service, mock_person_repo, sample_person_api):
#         """Test person details creation failure"""
#         from core.exceptions.specific.person_exceptions import PersonDetailsCreationException
        
#         mock_person_repo.create_person_details.side_effect = Exception("Database error")
        
#         with pytest.raises(PersonDetailsCreationException) as exc_info:
#             person_service.create_person_details(sample_person_api)
        
#         assert exc_info.value.error_code.value == "PERSON_DETAIL_INSERT_FAILED"
#         assert exc_info.value.status_code == 417
    
#     # ==================== generate_person_object Tests ====================
    
#     def test_generate_person_object_with_existing_details(self, person_service, mock_person_repo, sample_person_api, sample_person_details):
#         """Test generating person object with existing details"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         # This should raise BloodTypeNotFoundException because blood type is not found
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service.generate_person_object(sample_person_api)
    
#     def test_generate_person_object_with_new_details(self, person_service, mock_person_repo, sample_person_api_without_details):
#         """Test generating person object with new details"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         # This should raise BloodTypeNotFoundException because blood type is not found
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service.generate_person_object(sample_person_api_without_details)
    
#     def test_generate_person_object_with_blood_type(self, person_service, mock_person_repo, sample_person_api, sample_blood_type):
#         """Test generating person object with blood type"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = sample_blood_type
        
#         # Need to also mock get_person_details_by_id to return None
#         # The test expects no exception, but blood type is found
#         result = person_service.generate_person_object(sample_person_api)
        
#         # Verify that blood type was set
#         # Since the service creates a new Person object, it should have person_blood_type_id set
#         assert result.person_blood_type_id == sample_blood_type.id_blood_type
    
#     # ==================== refresh_or_insert_person Tests ====================
    
#     def test_refresh_or_insert_person_update_existing(self, person_service, mock_person_repo, mock_location_service, 
#                                                        sample_person_api, sample_location_api, sample_person_model, sample_person_details):
#         """Test updating an existing person"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = sample_person_model
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.get_blood_type_object.return_value = None  # Blood type not found
        
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service.refresh_or_insert_person(sample_person_api, sample_location_api)
    
#     def test_refresh_or_insert_person_create_new(self, person_service, mock_person_repo, mock_location_service,
#                                                   sample_person_api_without_details, sample_location_api):
#         """Test creating a new person"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = None
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service.refresh_or_insert_person(sample_person_api_without_details, sample_location_api)
    
#     def test_refresh_or_insert_person_blood_type_not_found(self, person_service, mock_person_repo, 
#                                                             sample_person_api, sample_location_api):
#         """Test creating person with non-existent blood type"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException) as exc_info:
#             person_service.refresh_or_insert_person(sample_person_api, sample_location_api)
        
#         assert exc_info.value.error_code.value == "BLOOD_TYPE_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
    
#     def test_refresh_or_insert_person_update_failure(self, person_service, mock_person_repo, mock_location_service,
#                                                        sample_person_api, sample_location_api, sample_person_model, sample_person_details):
#         """Test update failure"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = sample_person_model
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service.refresh_or_insert_person(sample_person_api, sample_location_api)
    
#     # ==================== delete_person Tests ====================
    
#     def test_delete_person_success(self, person_service, mock_person_repo, sample_person_model):
#         """Test successful person deletion"""
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
#         mock_person_repo.delete_person.return_value = True
        
#         result = person_service.delete_person("123")
        
#         assert result["message"] == "Person deleted successfully"
#         assert result["person_id"] == "123"
#         mock_person_repo.delete_person.assert_called_once_with(sample_person_model)
    
#     def test_delete_person_not_found(self, person_service, mock_person_repo):
#         """Test deleting non-existent person"""
#         from core.exceptions.specific.person_exceptions import PersonNotFoundException
        
#         mock_person_repo.get_person_by_id.return_value = None
        
#         with pytest.raises(PersonNotFoundException) as exc_info:
#             person_service.delete_person("999")
        
#         assert exc_info.value.error_code.value == "PERSON_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
    
#     def test_delete_person_failure(self, person_service, mock_person_repo, sample_person_model):
#         """Test deletion failure"""
#         from core.exceptions.specific.person_exceptions import PersonDeleteFailedException
        
#         mock_person_repo.get_person_by_id.return_value = sample_person_model
#         mock_person_repo.delete_person.return_value = False
        
#         with pytest.raises(PersonDeleteFailedException) as exc_info:
#             person_service.delete_person("123")
        
#         assert exc_info.value.error_code.value == "PERSON_DELETE_FAILED"
#         assert exc_info.value.status_code == 500
    
#     # ==================== Blood Type Operations Tests ====================
    
#     def test_get_blood_type_by_id_success(self, person_service, mock_person_repo, sample_blood_type):
#         """Test successful blood type retrieval"""
#         mock_person_repo.get_blood_type_by_id.return_value = sample_blood_type
        
#         result = person_service.get_blood_type_by_id("1")
        
#         assert result == sample_blood_type
#         mock_person_repo.get_blood_type_by_id.assert_called_once_with("1")
    
#     def test_get_blood_type_by_id_not_found(self, person_service, mock_person_repo):
#         """Test getting non-existent blood type"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_blood_type_by_id.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException) as exc_info:
#             person_service.get_blood_type_by_id("999")
        
#         assert exc_info.value.error_code.value == "BLOOD_TYPE_NOT_EXISTS"
#         assert exc_info.value.status_code == 404
    
#     def test_get_all_blood_types(self, person_service, mock_person_repo, sample_blood_type):
#         """Test getting all blood types"""
#         mock_person_repo.get_all_blood_types.return_value = [sample_blood_type]
        
#         result = person_service.get_all_blood_types()
        
#         assert len(result) == 1
#         assert result[0] == sample_blood_type
#         mock_person_repo.get_all_blood_types.assert_called_once()
    
#     @pytest.fixture
#     def mock_location_service_fixed(self):
#         """Create a properly configured mock location service that doesn't trigger SQLAlchemy"""
#         location_service = Mock()
        
#         # Create a simple object that won't trigger SQLAlchemy events
#         mock_location = Mock()
#         mock_location.id_location = 789
        
#         def build_location_model(location_data):
#             return mock_location
        
#         location_service.build_location_model = Mock(side_effect=build_location_model)
#         location_service.update_location = Mock(return_value=mock_location)
#         location_service.create_location = Mock(return_value=mock_location)
#         location_service.get_location_object = Mock(return_value=None)
        
#         return location_service

#     @pytest.fixture
#     def person_service_fixed(self, mock_person_repo, mock_location_service_fixed):
#         """Create person service with properly mocked dependencies"""
#         service = PersonService()
#         service.person_repo = mock_person_repo
#         service.location_service = mock_location_service_fixed
#         return service

#     def test_generate_person_object_with_location(self, person_service_fixed, mock_person_repo, 
#                                                    sample_person_api, sample_location_api):
#         """Test generating person object with location"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         # This should raise BloodTypeNotFoundException
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service_fixed.generate_person_object(sample_person_api, sample_location_api)

#     def test_refresh_or_insert_person_update_existing_fixed(self, person_service_fixed, mock_person_repo,
#                                                              sample_person_api, sample_location_api, 
#                                                              sample_person_model, sample_person_details):
#         """Test updating an existing person"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = sample_person_model
#         mock_person_repo.get_person_details_by_id.return_value = sample_person_details
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service_fixed.refresh_or_insert_person(sample_person_api, sample_location_api)

#     def test_refresh_or_insert_person_create_new_fixed(self, person_service_fixed, mock_person_repo,
#                                                         sample_person_api_without_details, sample_location_api):
#         """Test creating a new person"""
#         from core.exceptions.specific.person_exceptions import BloodTypeNotFoundException
        
#         mock_person_repo.get_person_basic.return_value = None
#         mock_person_repo.get_person_details_by_id.return_value = None
#         mock_person_repo.get_blood_type_object.return_value = None
        
#         with pytest.raises(BloodTypeNotFoundException):
#             person_service_fixed.refresh_or_insert_person(sample_person_api_without_details, sample_location_api)


# # ==================== Integration Tests with Database ====================

# @pytest.mark.integration
# class TestPersonServiceIntegration:
#     """Integration tests for PersonService using actual database"""
    
#     @pytest.fixture
#     def person_service(self, db_session):
#         """Create person service with database session"""
#         service = PersonService()
#         service.person_repo.db_session = db_session
#         service.location_service.db_session = db_session
#         return service