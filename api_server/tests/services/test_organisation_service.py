# # tests/services/test_organisation_service.py
# import pytest
# from unittest.mock import MagicMock, patch
# from core.exceptions.specific.supplier_exceptions import (
#     OrganisationNotFoundException,
#     OrganisationNameAlreadyUsedException,
#     OrganisationInsertFailedException,
#     OrganisationUpdateFailedException,
#     OrganisationDeleteFailedException,
#     ImageInsertFailedException,
#     ImageUpdateFailedException,
# )
# from services.supplier_service import OrganisationService
# from core.api_models import ProviderOrganisation_API, OrganisationImage_API


# class TestOrganisationService:
#     """Test suite for OrganisationService"""

#     @pytest.fixture
#     def organisation_service(self):
#         """Create OrganisationService with mocked repo"""
#         service = OrganisationService()
#         service.org_repo = MagicMock()
#         return service

#     @pytest.fixture
#     def sample_org_api(self):
#         """Sample organisation API data"""
#         return ProviderOrganisation_API(
#             id_provider_organisation=0,
#             provider_organisation_name="Test Organisation",
#             provider_organisation_desc="Test Description"
#         )

#     @pytest.fixture
#     def sample_org_model(self):
#         """Sample organisation model"""
#         org = MagicMock()
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

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 404

#     def test_get_org_by_name_found(self, organisation_service, sample_org_model):
#         """Test getting organisation by name when found"""
#         organisation_service.org_repo.get_org_by_name.return_value = sample_org_model

#         result = organisation_service.get_org_by_name("Test Organisation")

#         assert result == sample_org_model
#         organisation_service.org_repo.get_org_by_name.assert_called_once_with("Test Organisation")

#     def test_get_org_by_name_not_found(self, organisation_service):
#         """Test getting organisation by name when not found"""
#         organisation_service.org_repo.get_org_by_name.return_value = None

#         result = organisation_service.get_org_by_name("Non Existent")

#         assert result is None

#     def test_get_all_orgs(self, organisation_service):
#         """Test getting all organisations"""
#         expected_orgs = [MagicMock(), MagicMock()]
#         organisation_service.org_repo.get_all_orgs.return_value = expected_orgs

#         result = organisation_service.get_all_orgs(offset=10, limit=50)

#         assert result == expected_orgs
#         organisation_service.org_repo.get_all_orgs.assert_called_once_with(10, 50)

#     def test_get_all_orgs_default_params(self, organisation_service):
#         """Test getting all organisations with default parameters"""
#         organisation_service.org_repo.get_all_orgs.return_value = []

#         result = organisation_service.get_all_orgs()

#         assert result == []
#         organisation_service.org_repo.get_all_orgs.assert_called_once_with(0, 100)

#     def test_create_organisation_success(self, organisation_service, sample_org_api):
#         """Test successful organisation creation"""
#         # Mock no existing organisation with same name
#         organisation_service.get_org_by_name = MagicMock(return_value=None)

#         expected_result = MagicMock()
#         expected_result.id_provider_organisation = 1
#         organisation_service.org_repo.create_org.return_value = expected_result

#         result = organisation_service.create_organisation(sample_org_api)

#         assert result == expected_result
#         organisation_service.org_repo.create_org.assert_called_once()

#     def test_create_organisation_with_image(self, organisation_service, sample_org_api):
#         """Test creating organisation with image"""
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
#         organisation_service.org_repo.create_org.assert_called_once()

#     def test_create_organisation_duplicate_name(self, organisation_service, sample_org_api):
#         """Test creating organisation with duplicate name"""
#         # Mock existing organisation with same name
#         existing_org = MagicMock()
#         organisation_service.get_org_by_name = MagicMock(return_value=existing_org)

#         with pytest.raises(OrganisationNameAlreadyUsedException) as exc_info:
#             organisation_service.create_organisation(sample_org_api)

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 409

#     def test_create_organisation_db_error(self, organisation_service, sample_org_api):
#         """Test organisation creation with database error"""
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
#         organisation_service.org_repo.create_org.side_effect = Exception("Database error")

#         with pytest.raises(OrganisationInsertFailedException) as exc_info:
#             organisation_service.create_organisation(sample_org_api)

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 417

#     def test_update_organisation_success(self, organisation_service, sample_org_api, sample_org_model):
#         """Test successful organisation update"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
#         organisation_service.org_repo.update_org.return_value = sample_org_model

#         sample_org_api.id_provider_organisation = 1
#         result = organisation_service.update_organisation(sample_org_api)

#         assert result == sample_org_model
#         organisation_service.org_repo.update_org.assert_called_once_with(sample_org_model)

#     def test_update_organisation_with_name_change_no_conflict(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating organisation name without conflict"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         # No other organisation with the new name
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
#         organisation_service.org_repo.update_org.return_value = sample_org_model

#         sample_org_api.id_provider_organisation = 1
#         sample_org_api.provider_organisation_name = "New Name"
#         result = organisation_service.update_organisation(sample_org_api)

#         assert result == sample_org_model
#         assert sample_org_model.provider_organisation_name == "New Name"

#     def test_update_organisation_with_name_conflict(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating organisation with conflicting name"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         # Another organisation with the same name
#         conflicting_org = MagicMock()
#         conflicting_org.id_provider_organisation = 2
#         organisation_service.get_org_by_name = MagicMock(return_value=conflicting_org)

#         sample_org_api.id_provider_organisation = 1
#         sample_org_api.provider_organisation_name = "Taken Name"

#         with pytest.raises(OrganisationNameAlreadyUsedException) as exc_info:
#             organisation_service.update_organisation(sample_org_api)

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 409

#     def test_update_organisation_with_image_new(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating organisation with new image"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
#         organisation_service.org_repo.update_org.return_value = sample_org_model

#         sample_image = OrganisationImage_API(
#             id_org_image=0,
#             org_image_url="http://example.com/new.jpg",
#             org_ref_id=0
#         )

#         sample_org_api.id_provider_organisation = 1
#         result = organisation_service.update_organisation(sample_org_api, sample_image)

#         assert result == sample_org_model
#         organisation_service.org_repo.create_org_image.assert_called_once()

#     def test_update_organisation_with_image_update(self, organisation_service, sample_org_api, sample_org_model):
#         """Test updating organisation with existing image update"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.get_org_by_name = MagicMock(return_value=None)
#         organisation_service.org_repo.update_org.return_value = sample_org_model

#         existing_image = MagicMock()
#         existing_image.id_org_image = 10
#         organisation_service.org_repo.get_org_image_by_id.return_value = existing_image

#         sample_image = OrganisationImage_API(
#             id_org_image=10,
#             org_image_url="http://example.com/updated.jpg",
#             org_ref_id=0
#         )

#         sample_org_api.id_provider_organisation = 1
#         result = organisation_service.update_organisation(sample_org_api, sample_image)

#         assert result == sample_org_model
#         organisation_service.org_repo.update_org_image.assert_called_once_with(existing_image)

#     def test_delete_organisation_success(self, organisation_service, sample_org_model):
#         """Test successful organisation deletion"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.org_repo.get_org_images = MagicMock(return_value=[])
#         organisation_service.org_repo.delete_org = MagicMock(return_value=True)

#         result = organisation_service.delete_organisation("1")

#         assert result["message"] == "Organisation deleted successfully"
#         assert result["organisation_id"] == "1"
#         organisation_service.org_repo.delete_org.assert_called_once_with(sample_org_model)

#     def test_delete_organisation_no_images(self, organisation_service, sample_org_model):
#         """Test deleting organisation without images"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.org_repo.get_org_images = MagicMock(return_value=[])
#         organisation_service.org_repo.delete_org = MagicMock(return_value=True)

#         result = organisation_service.delete_organisation("1")

#         assert result["message"] == "Organisation deleted successfully"
#         organisation_service.org_repo.delete_org_image.assert_not_called()

#     def test_delete_organisation_failure(self, organisation_service, sample_org_model):
#         """Test organisation deletion failure"""
#         organisation_service.get_org_by_id = MagicMock(return_value=sample_org_model)
#         organisation_service.org_repo.get_org_images = MagicMock(return_value=[])
#         organisation_service.org_repo.delete_org = MagicMock(return_value=False)

#         with pytest.raises(OrganisationDeleteFailedException) as exc_info:
#             organisation_service.delete_organisation("1")

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 500

#     def test_handle_org_image_update(self, organisation_service, sample_org_model):
#         """Test handling organisation image update"""
#         existing_image = MagicMock()
#         existing_image.org_image_url = "old.jpg"
#         organisation_service.org_repo.get_org_image_by_id.return_value = existing_image

#         sample_image = OrganisationImage_API(
#             id_org_image=10,
#             org_image_url="http://example.com/updated.jpg",
#             org_ref_id=0
#         )

#         organisation_service._handle_org_image(sample_org_model, sample_image)

#         assert existing_image.org_image_url == "http://example.com/updated.jpg"
#         organisation_service.org_repo.update_org_image.assert_called_once_with(existing_image)

#     def test_handle_org_image_create_failure(self, organisation_service, sample_org_model):
#         """Test handling organisation image creation failure"""
#         organisation_service.org_repo.create_org_image.side_effect = Exception("Database error")

#         sample_image = OrganisationImage_API(
#             id_org_image=0,
#             org_image_url="http://example.com/new.jpg",
#             org_ref_id=0
#         )

#         with pytest.raises(ImageInsertFailedException) as exc_info:
#             organisation_service._handle_org_image(sample_org_model, sample_image)

#         # Use status_code instead of status
#         assert exc_info.value.status_code == 417