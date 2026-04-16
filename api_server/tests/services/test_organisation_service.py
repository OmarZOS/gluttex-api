# tests/test_organisation_service.py
import pytest
from unittest.mock import MagicMock


from services.supplier_service import OrganisationService
from core.api_models import ProviderOrganisation_API, OrganisationImage_API
from core.exception_handler import APIException
from core.models import ProviderOrganisation, OrganisationImage


class TestOrganisationService:
    

    @pytest.fixture
    def mock_org_repo(self):
        """Create mock organisation repository"""
        repo = Mock()
        repo.get_org_by_id = Mock()
        repo.get_org_by_name = Mock()
        repo.get_all_orgs = Mock()
        repo.create_org = Mock()
        repo.update_org = Mock()
        repo.delete_org = Mock()
        repo.get_org_images = Mock()
        repo.delete_org_image = Mock()
        repo.create_org_image = Mock()
        repo.update_org_image = Mock()
        repo.get_org_image_by_id = Mock()
        return repo
    
    @pytest.fixture
    def org_service(self, mock_org_repo):
        """Create organisation service with mocked repository"""
        service = OrganisationService()
        service.org_repo = mock_org_repo
        return service
    @pytest.fixture
    def org_service(self):
        """Create OrganisationService instance with mocked repo"""
        service = OrganisationService()
        service.org_repo = MagicMock()
        return service
    
    @pytest.fixture
    def sample_org_api(self):
        """Sample ProviderOrganisation_API data"""
        return ProviderOrganisation_API(
            id_provider_organisation=0,
            provider_organisation_name="Test Organisation",
            provider_organisation_desc="This is a test organisation"
        )
    
    @pytest.fixture
    def sample_org_model(self):
        """Sample ProviderOrganisation model"""
        org = ProviderOrganisation()
        org.id_provider_organisation = 1
        org.provider_organisation_name = "Test Organisation"
        org.provider_organisation_desc = "This is a test organisation"
        return org
    
    def test_get_org_by_id_found(self, org_service, sample_org_model):
        """Test getting organisation by ID when found"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        
        result = org_service.get_org_by_id("1")
        
        assert result == sample_org_model
        org_service.org_repo.get_org_by_id.assert_called_once_with("1")
    
    def test_get_org_by_id_not_found(self, org_service):
        """Test getting organisation by ID when not found"""
        org_service.org_repo.get_org_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            org_service.get_org_by_id("999")
        
        assert exc_info.value.status == 404
    
    def test_get_org_by_name_found(self, org_service, sample_org_model):
        """Test getting organisation by name when found"""
        org_service.org_repo.get_org_by_name.return_value = sample_org_model
        
        result = org_service.get_org_by_name("Test Organisation")
        
        assert result == sample_org_model
        org_service.org_repo.get_org_by_name.assert_called_once_with("Test Organisation")
    
    def test_get_org_by_name_not_found(self, org_service):
        """Test getting organisation by name when not found"""
        org_service.org_repo.get_org_by_name.return_value = None
        
        result = org_service.get_org_by_name("Non Existent")
        
        assert result is None
    
    def test_get_all_orgs(self, org_service):
        """Test getting all organisations"""
        expected_orgs = [MagicMock(), MagicMock(), MagicMock()]
        org_service.org_repo.get_all_orgs.return_value = expected_orgs
        
        result = org_service.get_all_orgs(offset=10, limit=50)
        
        assert result == expected_orgs
        org_service.org_repo.get_all_orgs.assert_called_once_with(10, 50)
    
    def test_get_all_orgs_default_params(self, org_service):
        """Test getting all organisations with default parameters"""
        expected_orgs = []
        org_service.org_repo.get_all_orgs.return_value = expected_orgs
        
        result = org_service.get_all_orgs()
        
        assert result == expected_orgs
        org_service.org_repo.get_all_orgs.assert_called_once_with(0, 100)
    
    def test_create_organisation_success(self, org_service, sample_org_api):
        """Test creating a new organisation successfully"""
        # Mock no existing organisation with same name
        org_service.org_repo.get_org_by_name.return_value = None
        
        # Mock create
        expected_result = MagicMock()
        org_service.org_repo.create_org.return_value = expected_result
        
        result = org_service.create_organisation(sample_org_api)
        
        assert result == expected_result
        
        # Verify organisation was built correctly
        call_args = org_service.org_repo.create_org.call_args[0][0]
        assert call_args.provider_organisation_name == sample_org_api.provider_organisation_name
        assert call_args.provider_organisation_desc == sample_org_api.provider_organisation_desc
    
    def test_create_organisation_with_image(self, org_service, sample_org_api):
        """Test creating a new organisation with an image"""
        org_service.org_repo.get_org_by_name.return_value = None
        
        sample_image = OrganisationImage_API(
            id_org_image=0,
            org_image_url="http://example.com/org-logo.jpg",
            org_ref_id=0
        )
        
        expected_result = MagicMock()
        org_service.org_repo.create_org.return_value = expected_result
        
        result = org_service.create_organisation(sample_org_api, sample_image)
        
        assert result == expected_result
        
        # Verify image was added
        call_args = org_service.org_repo.create_org.call_args[0][0]
        assert len(call_args.organisation_image) == 1
        assert call_args.organisation_image[0].org_image_url == "http://example.com/org-logo.jpg"
    
    def test_create_organisation_duplicate_name(self, org_service, sample_org_api):
        """Test creating an organisation with a name that already exists"""
        org_service.org_repo.get_org_by_name.return_value = MagicMock()
        
        with pytest.raises(APIException) as exc_info:
            org_service.create_organisation(sample_org_api)
        
        assert exc_info.value.status == 409
        org_service.org_repo.create_org.assert_not_called()
    
    def test_create_organisation_db_error(self, org_service, sample_org_api):
        """Test creating an organisation when database error occurs"""
        org_service.org_repo.get_org_by_name.return_value = None
        org_service.org_repo.create_org.side_effect = Exception("Database error")
        
        with pytest.raises(APIException) as exc_info:
            org_service.create_organisation(sample_org_api)
        
        assert exc_info.value.status == 417
    
    def test_update_organisation_success(self, org_service, sample_org_api, sample_org_model):
        """Test updating an existing organisation successfully"""
        # Mock get existing organisation
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        
        # Mock no name conflict (name unchanged)
        org_service.org_repo.get_org_by_name.return_value = None
        
        # Mock update
        org_service.org_repo.update_org.return_value = sample_org_model
        
        result = org_service.update_organisation(sample_org_api)
        
        assert result == sample_org_model
        assert sample_org_model.provider_organisation_name == sample_org_api.provider_organisation_name
        assert sample_org_model.provider_organisation_desc == sample_org_api.provider_organisation_desc
        org_service.org_repo.update_org.assert_called_once_with(sample_org_model)
    
    def test_update_organisation_with_name_change_no_conflict(self, org_service, sample_org_api, sample_org_model):
        """Test updating organisation name when new name is available"""
        sample_org_api.provider_organisation_name = "New Name"
        sample_org_model.provider_organisation_name = "Old Name"
        
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        org_service.org_repo.get_org_by_name.return_value = None
        org_service.org_repo.update_org.return_value = sample_org_model
        
        result = org_service.update_organisation(sample_org_api)
        
        assert result.provider_organisation_name == "New Name"
        org_service.org_repo.get_org_by_name.assert_called_once_with("New Name")
    
    def test_update_organisation_with_name_conflict(self, org_service, sample_org_api, sample_org_model):
        """Test updating organisation with a name that's already taken"""
        sample_org_api.provider_organisation_name = "Taken Name"
        sample_org_model.provider_organisation_name = "Old Name"
        
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        
        # Mock existing organisation with same name
        conflicting_org = MagicMock()
        conflicting_org.id_provider_organisation = 99
        org_service.org_repo.get_org_by_name.return_value = conflicting_org
        
        with pytest.raises(APIException) as exc_info:
            org_service.update_organisation(sample_org_api)
        
        assert exc_info.value.status == 409
        org_service.org_repo.update_org.assert_not_called()
    
    def test_update_organisation_with_image_new(self, org_service, sample_org_api, sample_org_model):
        """Test updating organisation with a new image"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        org_service.org_repo.get_org_by_name.return_value = None
        org_service.org_repo.update_org.return_value = sample_org_model
        
        sample_image = OrganisationImage_API(
            id_org_image=0,
            org_image_url="http://example.com/new-logo.jpg",
            org_ref_id=0
        )
        
        result = org_service.update_organisation(sample_org_api, sample_image)
        
        assert result == sample_org_model
        org_service.org_repo.create_org_image.assert_called_once()
    
    def test_update_organisation_with_image_update(self, org_service, sample_org_api, sample_org_model):
        """Test updating organisation with an existing image"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        org_service.org_repo.get_org_by_name.return_value = None
        org_service.org_repo.update_org.return_value = sample_org_model
        
        sample_image = OrganisationImage_API(
            id_org_image=10,
            org_image_url="http://example.com/updated-logo.jpg",
            org_ref_id=1
        )
        
        mock_existing_image = MagicMock()
        mock_existing_image.org_image_url = "old.jpg"
        org_service.org_repo.get_org_image_by_id.return_value = mock_existing_image
        
        result = org_service.update_organisation(sample_org_api, sample_image)
        
        assert result == sample_org_model
        assert mock_existing_image.org_image_url == "http://example.com/updated-logo.jpg"
        org_service.org_repo.update_org_image.assert_called_once_with(mock_existing_image)
    
    def test_delete_organisation_success(self, org_service, sample_org_model):
        """Test deleting an organisation successfully"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        
        mock_images = [MagicMock(), MagicMock()]
        org_service.org_repo.get_org_images.return_value = mock_images
        org_service.org_repo.delete_org.return_value = True
        
        result = org_service.delete_organisation("1")
        
        assert result["message"] == "Organisation deleted successfully"
        assert result["organisation_id"] == "1"
        
        # Verify images were deleted
        assert org_service.org_repo.delete_org_image.call_count == 2
        org_service.org_repo.delete_org.assert_called_once_with(sample_org_model)
    
    def test_delete_organisation_no_images(self, org_service, sample_org_model):
        """Test deleting an organisation with no images"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        org_service.org_repo.get_org_images.return_value = []
        org_service.org_repo.delete_org.return_value = True
        
        result = org_service.delete_organisation("1")
        
        assert result["message"] == "Organisation deleted successfully"
        org_service.org_repo.delete_org_image.assert_not_called()
        org_service.org_repo.delete_org.assert_called_once()
    
    def test_delete_organisation_failure(self, org_service, sample_org_model):
        """Test deleting an organisation when deletion fails"""
        org_service.org_repo.get_org_by_id.return_value = sample_org_model
        org_service.org_repo.get_org_images.return_value = []
        org_service.org_repo.delete_org.return_value = False
        
        with pytest.raises(APIException) as exc_info:
            org_service.delete_organisation("1")
        
        assert exc_info.value.status == 500
    
    def test_handle_org_image_new(self, org_service, sample_org_model):
        """Test handling new organisation image creation"""
        sample_image = OrganisationImage_API(
            id_org_image=0,
            org_image_url="http://example.com/new-org-image.jpg",
            org_ref_id=0
        )
        
        org_service._handle_org_image(sample_org_model, sample_image)
        
        assert org_service.org_repo.create_org_image.called
        call_arg = org_service.org_repo.create_org_image.call_args[0][0]
        assert call_arg.org_image_url == "http://example.com/new-org-image.jpg"
        assert call_arg.org_ref_id == sample_org_model.id_provider_organisation
    
    def test_handle_org_image_new(self, org_service, mock_org_repo, sample_org_model):
        """Test handling new organisation image"""
        sample_image_api = OrganisationImage_API(
            id_org_image=0,
            org_image_url="https://example.com/new-org.jpg",
            org_ref_id=None
        )
        
        # Call the private method directly
        org_service._handle_org_image(sample_org_model, sample_image_api)
        
        # Verify create_org_image was called with correct parameters
        mock_org_repo.create_org_image.assert_called_once()
        call_args = mock_org_repo.create_org_image.call_args[0][0]
        assert call_args.org_image_url == sample_image_api.org_image_url
        assert call_args.org_ref_id == sample_org_model.idprovider_organisation

    def test_handle_org_image_update(self, org_service, sample_org_model):
        """Test handling existing organisation image update"""
        sample_image = OrganisationImage_API(
            id_org_image=20,
            org_image_url="http://example.com/updated-org-image.jpg",
            org_ref_id=1
        )
        
        mock_existing_image = MagicMock()
        mock_existing_image.org_image_url = "old-image.jpg"
        org_service.org_repo.get_org_image_by_id.return_value = mock_existing_image
        
        org_service._handle_org_image(sample_org_model, sample_image)
        
        assert mock_existing_image.org_image_url == "http://example.com/updated-org-image.jpg"
        org_service.org_repo.update_org_image.assert_called_once_with(mock_existing_image)
    
    def test_handle_org_image_create_failure(self, org_service, sample_org_model):
        """Test handling organisation image creation when database fails"""
        sample_image = OrganisationImage_API(
            id_org_image=0,
            org_image_url="http://example.com/new-image.jpg",
            org_ref_id=0
        )
        
        org_service.org_repo.create_org_image.side_effect = Exception("Database error")
        
        with pytest.raises(APIException) as exc_info:
            org_service._handle_org_image(sample_org_model, sample_image)
        
        assert exc_info.value.status == 417