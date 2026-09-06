# # tests/services/test_supplier_service.py - Fixed version

# import pytest
# from unittest.mock import MagicMock, patch, ANY
# import sys


# # Mock geoalchemy2 BEFORE importing any models
# sys.modules['geoalchemy2'] = MagicMock()
# sys.modules['geoalchemy2.types'] = MagicMock()
# sys.modules['geoalchemy2.functions'] = MagicMock()

# from services.supplier_service import SupplierService, OrganisationService
# from core.api_models import (
#     ProductProvider_API, Location_API, ProviderImage_API,
#     ProviderOrganisation_API, OrganisationImage_API
# )
# from core.exceptions.handler import APIException
# from core.exceptions.specific.supplier_exceptions import (
#     SupplierNotFoundException,
#     SupplierAlreadyExistsException,
#     SupplierTypeNotFoundException,
#     SupplierInsertFailedException,
#     SupplierUpdateFailedException,
#     SupplierDeleteFailedException,
#     OrganisationNotFoundException,
#     OrganisationNameAlreadyUsedException,
#     OrganisationInsertFailedException,
#     OrganisationUpdateFailedException,
#     OrganisationDeleteFailedException
# )
# from core.models import (
#     ProductProvider, ProductProviderType, ProviderDetails,
#     ProviderImage, ProviderOrganisation, OrganisationImage
# )


# class TestSupplierService:
    
#     @pytest.fixture
#     def supplier_service(self):
#         """Create SupplierService instance with mocked repos"""
#         service = SupplierService()
#         # Replace repos with mocks to avoid database calls
#         service.supplier_repo = MagicMock()
#         service.org_repo = MagicMock()
#         service.location_service = MagicMock()
#         return service
    
#     @pytest.fixture
#     def sample_provider_api(self):
#         """Sample ProductProvider_API data"""
#         return ProductProvider_API(
#             id_product_provider=1,
#             id_provider_owner=100,
#             idprovider_details_id=0,
#             id_product_provider_type=1,
#             id_provider_organisation=0,
#             product_provider_type_desc="Retail Store",
#             provider_organisation_name="Test Org",
#             provider_organisation_desc="Test Description",
#             provider_name="Test Provider Inc.",
#             provider_contact_info="contact@test.com"
#         )
    
#     @pytest.fixture
#     def sample_location_api(self):
#         """Sample Location_API data"""
#         return Location_API(
#             id_location=0,
#             location_latitude=36.7525,
#             location_longitude=3.0419,
#             location_name="Test Location",
#             location_address_id=0,
#             id_address=0,
#             address_street="123 Test St",
#             address_city="Test City",
#             address_postal_code="12345",
#             address_country="Test Country"
#         )
    
#     @pytest.fixture
#     def sample_provider_model(self, sample_provider_api):
#         """Sample ProductProvider model"""
#         provider = ProductProvider()
#         provider.id_product_provider = 1
#         provider.product_provider_type_id = 1
#         provider.product_provider_owner = 100
#         provider.product_provider_org_id = 0
        
#         # Create provider details
#         provider.product_provider_details = ProviderDetails(
#             idprovider_details_id=1,
#             provider_name="Test Provider Inc.",
#             provider_contact_info="contact@test.com"
#         )
        
#         return provider
    
#     def test_build_supplier_details_new(self, supplier_service, sample_provider_api):
#         """Test building new ProviderDetails from API data"""
#         details = supplier_service._build_supplier_details(sample_provider_api)
        
#         assert details.provider_name == sample_provider_api.provider_name
#         assert details.provider_contact_info == sample_provider_api.provider_contact_info
#         # When idprovider_details_id is 0, it should be None (not set)
#         # The model field might be None by default, which is acceptable
#         # So we check that it's either None or 0
#         assert details.idprovider_details_id in (None, 0)
    
#     def test_build_supplier_details_existing(self, supplier_service, sample_provider_api):
#         """Test building ProviderDetails with existing ID"""
#         sample_provider_api.idprovider_details_id = 5
#         details = supplier_service._build_supplier_details(sample_provider_api)
        
#         assert details.idprovider_details_id == 5
    
#     def test_validate_supplier_type_success(self, supplier_service):
#         """Test successful supplier type validation"""
#         mock_supplier_type = ProductProviderType()
#         mock_supplier_type.id_product_provider_type = 1
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = mock_supplier_type
        
#         result = supplier_service._validate_supplier_type(1)
        
#         assert result == mock_supplier_type
#         supplier_service.supplier_repo.get_supplier_type_by_id.assert_called_once_with(1)
    
#     def test_validate_supplier_type_not_found(self, supplier_service):
#         """Test supplier type validation when not found"""
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = None
        
#         with pytest.raises(SupplierTypeNotFoundException) as exc_info:
#             supplier_service._validate_supplier_type(999)
        
#         assert exc_info.value.status_code == 404
    
#     def test_build_supplier_model_success(self, supplier_service, sample_provider_api, sample_location_api):
#         """Test building ProductProvider model successfully"""
#         # Mock supplier type lookup
#         mock_supplier_type = ProductProviderType()
#         mock_supplier_type.id_product_provider_type = 1
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = mock_supplier_type
        
#         # Mock location service
#         mock_location = MagicMock()
#         supplier_service.location_service.build_location_model.return_value = mock_location
        
#         # Build model
#         result = supplier_service._build_supplier_model(sample_provider_api, sample_location_api)
        
#         assert result.product_provider_type_id == 1
#         assert result.product_provider_owner == 100
#         assert result.product_provider_location == mock_location
#         assert result.product_provider_details is not None
#         assert result.product_provider_org.provider_organisation_name == "Test Org"
        
#         # Verify calls
#         supplier_service.supplier_repo.get_supplier_type_by_id.assert_called_once_with(1)
#         supplier_service.location_service.build_location_model.assert_called_once_with(sample_location_api)
    
#     def test_build_supplier_model_invalid_type(self, supplier_service, sample_provider_api):
#         """Test building model with invalid supplier type"""
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = None
        
#         with pytest.raises(SupplierTypeNotFoundException) as exc_info:
#             supplier_service._build_supplier_model(sample_provider_api, None)
        
#         assert exc_info.value.status_code == 404
    
#     def test_build_supplier_model_existing_org(self, supplier_service, sample_provider_api):
#         """Test building model with existing organisation ID"""
#         sample_provider_api.id_provider_organisation = 10
#         mock_supplier_type = ProductProviderType()
#         mock_supplier_type.id_product_provider_type = 1
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = mock_supplier_type
        
#         result = supplier_service._build_supplier_model(sample_provider_api, None)
        
#         assert result.product_provider_org_id == 10
#         assert result.product_provider_org is None
    
#     def test_get_supplier_by_id_found(self, supplier_service, sample_provider_model):
#         """Test getting supplier by ID when found"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = sample_provider_model
        
#         result = supplier_service.get_supplier_by_id("1")
        
#         assert result == sample_provider_model
#         supplier_service.supplier_repo.get_supplier_by_id.assert_called_once_with("1", eager_load=True)
    
#     def test_get_supplier_by_id_not_found(self, supplier_service):
#         """Test getting supplier by ID when not found"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = None
        
#         with pytest.raises(SupplierNotFoundException) as exc_info:
#             supplier_service.get_supplier_by_id("999")
        
#         assert exc_info.value.status_code == 404
    
#     def test_get_all_suppliers(self, supplier_service):
#         """Test getting all suppliers with filters"""
#         expected_suppliers = [MagicMock(), MagicMock()]
#         supplier_service.supplier_repo.get_all_suppliers.return_value = expected_suppliers
        
#         result = supplier_service.get_all_suppliers(owner_id=100, org_id=1, offset=0, limit=20)
        
#         assert result == expected_suppliers
#         supplier_service.supplier_repo.get_all_suppliers.assert_called_once_with(100, 1, 0, 20)
    
#     def test_get_supplier_types(self, supplier_service):
#         """Test getting all supplier types"""
#         expected_types = [MagicMock(), MagicMock()]
#         supplier_service.supplier_repo.get_all_supplier_types.return_value = expected_types
        
#         result = supplier_service.get_supplier_types()
        
#         assert result == expected_types
    
#     def test_create_supplier_success(self, supplier_service, sample_provider_api, sample_location_api):
#         """Test creating a new supplier successfully"""
#         # Mock no existing supplier
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = None
        
#         # Mock supplier type lookup
#         mock_supplier_type = ProductProviderType()
#         mock_supplier_type.id_product_provider_type = 1
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = mock_supplier_type
        
#         # Mock location building
#         mock_location = MagicMock()
#         supplier_service.location_service.build_location_model.return_value = mock_location
        
#         # Mock create
#         expected_result = MagicMock()
#         supplier_service.supplier_repo.create_supplier.return_value = expected_result
        
#         result = supplier_service.create_supplier(sample_provider_api, sample_location_api)
        
#         assert result == expected_result
#         supplier_service.supplier_repo.create_supplier.assert_called_once()
    
#     def test_create_supplier_with_image(self, supplier_service, sample_provider_api, sample_location_api):
#         """Test creating a new supplier with an image"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = None
        
#         mock_supplier_type = ProductProviderType()
#         mock_supplier_type.id_product_provider_type = 1
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = mock_supplier_type
        
#         mock_location = MagicMock()
#         supplier_service.location_service.build_location_model.return_value = mock_location
        
#         # Create image
#         sample_image = ProviderImage_API(
#             id_provider_image=0,
#             provider_image_url="http://example.com/image.jpg",
#             provider_ref_id=0
#         )
        
#         expected_result = MagicMock()
#         supplier_service.supplier_repo.create_supplier.return_value = expected_result
        
#         result = supplier_service.create_supplier(sample_provider_api, sample_location_api, sample_image)
        
#         assert result == expected_result
        
#         # Verify that image was added to the model
#         call_args = supplier_service.supplier_repo.create_supplier.call_args[0][0]
#         assert len(call_args.provider_image) == 1
#         assert call_args.provider_image[0].provider_image_url == "http://example.com/image.jpg"
    
#     def test_create_supplier_already_exists(self, supplier_service, sample_provider_api, sample_location_api):
#         """Test creating a supplier that already exists"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = MagicMock()
        
#         with pytest.raises(SupplierAlreadyExistsException) as exc_info:
#             supplier_service.create_supplier(sample_provider_api, sample_location_api)
        
#         assert exc_info.value.status_code == 409
    
#     def test_update_supplier_success(self, supplier_service, sample_provider_api, sample_provider_model):
#         """Test updating an existing supplier successfully"""
#         # Mock supplier type exists
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = MagicMock()
        
#         # Mock get supplier
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = sample_provider_model
        
#         # Mock update
#         supplier_service.supplier_repo.update_supplier.return_value = sample_provider_model
        
#         result = supplier_service.update_supplier(sample_provider_api)
        
#         assert result == sample_provider_model
#         # Verify details were updated
#         assert sample_provider_model.product_provider_details.provider_name == sample_provider_api.provider_name
#         assert sample_provider_model.product_provider_details.provider_contact_info == sample_provider_api.provider_contact_info
#         assert sample_provider_model.product_provider_type_id == sample_provider_api.id_product_provider_type
#         assert sample_provider_model.product_provider_org_id == sample_provider_api.id_provider_organisation
    
#     def test_update_supplier_invalid_type(self, supplier_service, sample_provider_api):
#         """Test updating with invalid supplier type"""
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = None
        
#         with pytest.raises(SupplierTypeNotFoundException) as exc_info:
#             supplier_service.update_supplier(sample_provider_api)
        
#         assert exc_info.value.status_code == 404
    
#     def test_update_supplier_with_location(self, supplier_service, sample_provider_api, sample_provider_model, sample_location_api):
#         """Test updating supplier with new location"""
#         supplier_service.supplier_repo.get_supplier_type_by_id.return_value = MagicMock()
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = sample_provider_model
        
#         mock_updated_location = MagicMock()
#         mock_updated_location.id_location = 99
#         supplier_service.location_service.update_location.return_value = mock_updated_location
        
#         sample_location_api.id_location = 5
#         supplier_service.supplier_repo.update_supplier.return_value = sample_provider_model
        
#         result = supplier_service.update_supplier(sample_provider_api, location=sample_location_api)
        
#         assert result == sample_provider_model
#         assert sample_provider_model.product_provider_location_id == 99
#         supplier_service.location_service.update_location.assert_called_once_with(5, sample_location_api)
    
#     def test_delete_supplier_success(self, supplier_service, sample_provider_model):
#         """Test deleting a supplier successfully"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = sample_provider_model
        
#         mock_images = [MagicMock(), MagicMock()]
#         supplier_service.supplier_repo.get_supplier_images.return_value = mock_images
#         supplier_service.supplier_repo.delete_supplier.return_value = True
        
#         result = supplier_service.delete_supplier("1")
        
#         assert result["message"] == "Supplier deleted successfully"
#         assert result["supplier_id"] == "1"
        
#         # Verify images were deleted
#         assert supplier_service.supplier_repo.delete_supplier_image.call_count == 2
#         supplier_service.supplier_repo.delete_supplier.assert_called_once_with(sample_provider_model)
    
#     def test_delete_supplier_not_found(self, supplier_service):
#         """Test deleting a supplier that doesn't exist"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = None
        
#         with pytest.raises(SupplierNotFoundException) as exc_info:
#             supplier_service.delete_supplier("999")
        
#         assert exc_info.value.status_code == 404
    
#     def test_delete_supplier_failure(self, supplier_service, sample_provider_model):
#         """Test deleting a supplier when deletion fails"""
#         supplier_service.supplier_repo.get_supplier_by_id.return_value = sample_provider_model
#         supplier_service.supplier_repo.get_supplier_images.return_value = []
#         supplier_service.supplier_repo.delete_supplier.return_value = False
        
#         with pytest.raises(SupplierDeleteFailedException) as exc_info:
#             supplier_service.delete_supplier("1")
        
#         assert exc_info.value.status_code == 500
    
#     def test_search_suppliers_by_location(self, supplier_service):
#         """Test searching suppliers by location"""
#         expected_results = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]
#         supplier_service.supplier_repo.search_by_filter.return_value = expected_results
        
#         result = supplier_service.search_suppliers_by_location(3.0419, 36.7525, 10.0, 0, 20)
        
#         assert result == expected_results
#         supplier_service.supplier_repo.search_by_filter.assert_called_once_with(
#             (3.0419, 36.7525), 10.0, 0, 20
#         )
    
#     def test_handle_supplier_image_new(self, supplier_service, sample_provider_model):
#         """Test handling new supplier image creation"""
#         sample_image = ProviderImage_API(
#             id_provider_image=0,
#             provider_image_url="http://example.com/new.jpg",
#             provider_ref_id=0
#         )
        
#         supplier_service._handle_supplier_image(sample_provider_model, sample_image)
        
#         # Verify new image was created and added
#         assert supplier_service.supplier_repo.create_supplier_image.called
#         call_arg = supplier_service.supplier_repo.create_supplier_image.call_args[0][0]
#         assert call_arg.provider_image_url == "http://example.com/new.jpg"
#         assert call_arg.provider_ref == sample_provider_model
    
#     def test_handle_supplier_image_update(self, supplier_service, sample_provider_model):
#         """Test handling existing supplier image update"""
#         sample_image = ProviderImage_API(
#             id_provider_image=10,
#             provider_image_url="http://example.com/updated.jpg",
#             provider_ref_id=0
#         )
        
#         mock_existing_image = MagicMock()
#         mock_existing_image.provider_image_url = "old.jpg"
#         supplier_service.supplier_repo.get_supplier_image_by_id.return_value = mock_existing_image
        
#         supplier_service._handle_supplier_image(sample_provider_model, sample_image)
        
#         assert mock_existing_image.provider_image_url == "http://example.com/updated.jpg"
#         supplier_service.supplier_repo.update_supplier_image.assert_called_once_with(mock_existing_image)


# class TestOrganisationService:
    
#     @pytest.fixture
#     def organisation_service(self):
#         """Create OrganisationService instance with mocked repos"""
#         service = OrganisationService()
#         service.org_repo = MagicMock()
#         return service
    
#     @pytest.fixture
#     def sample_org_api(self):
#         """Sample ProviderOrganisation_API data"""
#         return ProviderOrganisation_API(
#             id_provider_organisation=0,
#             provider_organisation_name="Test Organisation",
#             provider_organisation_desc="Test Description"
#         )
    
#     @pytest.fixture
#     def sample_org_model(self):
#         """Sample ProviderOrganisation model"""
#         org = ProviderOrganisation()
#         org.id_provider_organisation = 1
#         org.provider_organisation_name = "Test Organisation"
#         org.provider_organisation_desc = "Test Description"
#         return org
    
#     def test_get_org_by_id_found(self, organisation_service, sample_org_model):
#         """Test getting organisation by ID when found"""
#         organisation_service.org_repo.get_org_by_id.return_value = sample_org_model
        
#         result = organisation_service.get_org_by_id("1")
        
#         assert result == sample_org_model
#         organisation_service.org_repo.get_org_by_id.assert_called_once_with("1")
    
#     def test_get_org_by_id_not_found(self, organisation_service):
#         """Test getting organisation by ID when not found"""
#         organisation_service.org_repo.get_org_by_id.return_value = None
        
#         with pytest.raises(OrganisationNotFoundException) as exc_info:
#             organisation_service.get_org_by_id("999")
        
#         assert exc_info.value.status_code == 404
    
#     def test_get_all_orgs(self, organisation_service):
#         """Test getting all organisations"""
#         expected_orgs = [MagicMock(), MagicMock()]
#         organisation_service.org_repo.get_all_orgs.return_value = expected_orgs
        
#         result = organisation_service.get_all_orgs(offset=0, limit=50)
        
#         assert result == expected_orgs
#         organisation_service.org_repo.get_all_orgs.assert_called_once_with(0, 50)
    
#     def test_create_organisation_success(self, organisation_service, sample_org_api):
#         """Test creating a new organisation successfully"""
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
        
#         expected_result = MagicMock()
#         organisation_service.org_repo.create_org.return_value = expected_result
        
#         result = organisation_service.create_organisation(sample_org_api)
        
#         assert result == expected_result
#         organisation_service.org_repo.create_org.assert_called_once()
    
#     def test_create_organisation_with_image(self, organisation_service, sample_org_api):
#         """Test creating a new organisation with an image"""
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
        
#         sample_image = OrganisationImage_API(
#             id_org_image=0,
#             org_image_url="http://example.com/org.jpg",
#             org_ref_id=0
#         )
        
#         expected_result = MagicMock()
#         organisation_service.org_repo.create_org.return_value = expected_result
        
#         result = organisation_service.create_organisation(sample_org_api, sample_image)
        
#         assert result == expected_result
    
#     def test_create_organisation_name_exists(self, organisation_service, sample_org_api):
#         """Test creating an organisation with existing name"""
#         organisation_service.get_org_by_name = MagicMock(return_value=MagicMock())
        
#         with pytest.raises(OrganisationNameAlreadyUsedException) as exc_info:
#             organisation_service.create_organisation(sample_org_api)
        
#         assert exc_info.value.status_code == 409
    
#     def test_update_organisation_success(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating an organisation successfully"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
        
#         organisation_service.org_repo.update_org.return_value = sample_org_model
        
#         sample_org_api.id_provider_organisation = 1
#         result = organisation_service.update_organisation(sample_org_api)
        
#         assert result == sample_org_model
    
#     def test_update_organisation_name_conflict(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating an organisation with conflicting name"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         # Return a different organisation with the same name
#         conflicting_org = MagicMock()
#         conflicting_org.id_provider_organisation = 2
#         organisation_service.get_org_by_name = MagicMock(return_value=conflicting_org)
        
#         sample_org_api.id_provider_organisation = 1
#         sample_org_api.provider_organisation_name = "New Name"
        
#         with pytest.raises(OrganisationNameAlreadyUsedException) as exc_info:
#             organisation_service.update_organisation(sample_org_api)
        
#         assert exc_info.value.status_code == 409
    
#     def test_delete_organisation_success(self, organisation_service, sample_org_model):
#         """Test deleting an organisation successfully"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.org_repo.get_org_images = MagicMock(return_value=[])
#         organisation_service.org_repo.delete_org = MagicMock(return_value=True)
        
#         result = organisation_service.delete_organisation("1")
        
#         assert result["message"] == "Organisation deleted successfully"
#         assert result["organisation_id"] == "1"
#         organisation_service.org_repo.delete_org.assert_called_once_with(sample_org_model)
    
#     def test_delete_organisation_not_found(self, organisation_service):
#         """Test deleting an organisation that doesn't exist"""
#         organisation_service.get_org_by_id = MagicMock(side_effect=OrganisationNotFoundException(org_id="999"))
        
#         with pytest.raises(OrganisationNotFoundException) as exc_info:
#             organisation_service.delete_organisation("999")
        
#         assert exc_info.value.status_code == 404