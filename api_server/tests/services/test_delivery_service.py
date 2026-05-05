# tests/services/test_delivery_service.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Optional
from fastapi import BackgroundTasks
from core.api_models import Delivery_API
from core.exceptions.handler import APIException
from core.messages import *
from core.models import Delivery, Address
from services.delivery_service import DeliveryService


class TestDeliveryService:
    """Test suite for DeliveryService"""
    
    @pytest.fixture
    def mock_delivery_repo(self):
        """Create mock delivery repository"""
        repo = Mock()
        repo.get_by_id = Mock()
        repo.get_all = Mock()
        repo.get_by_status = Mock()
        repo.create = Mock()
        repo.update = Mock()
        repo.delete = Mock()
        repo.bulk_delete_by_criteria = Mock()
        repo.count_by_status = Mock()
        return repo
    
    @pytest.fixture
    def mock_address_repo(self):
        """Create mock address repository"""
        repo = Mock()
        repo.get_address_by_id = Mock()
        repo.create_address = Mock()
        repo.update_address = Mock()
        return repo
    
    @pytest.fixture
    def mock_location_service(self):
        """Create mock location service"""
        service = Mock()
        service.build_address_from_delivery = Mock()
        return service
    
    @pytest.fixture
    def delivery_service(self, mock_delivery_repo, mock_address_repo, mock_location_service):
        """Create delivery service with mocked dependencies"""
        service = DeliveryService()
        service.delivery_repo = mock_delivery_repo
        service.address_repo = mock_address_repo
        service.location_service = mock_location_service
        return service
    
    @pytest.fixture
    def sample_delivery_api(self):
        """Sample delivery API data"""
        return Delivery_API(
            id_delivery=1,
            recipient_person=100,
            recipient_provider=0,
            delivery_package_count=3,
            delivery_total_weight=15.5,
            delivery_cargo_dimensions="30x20x10 cm",
            delivery_goods_description="Electronics",
            hs_code="84713000",
            delivery_merchant_name="Best Buy",
            delivery_shipping_method="Express",
            delivery_special_instructions="Handle with care",
            delivery_status="PENDING",
            delivery_address_id=200,
            delivery_current_address_id=200,
            delivery_fee=25.50,
            delivery_placed_order=300,
            delivery_provider_id=400,
            delivery_broker_id=500,
            address_street="123 Main St",
            address_city="New York",
            address_postal_code="10001",
            address_country="USA"
        )
    
    @pytest.fixture
    def sample_delivery_model(self):
        """Sample delivery model"""
        delivery = Mock(spec=Delivery)
        delivery.id_delivery = 1
        delivery.delivery_status = "PENDING"
        delivery.delivery_package_count = "3"
        delivery.delivery_total_weight = 15.5
        delivery.delivery_cargo_dimensions = "30x20x10 cm"
        delivery.delivery_goods_description = "Electronics"
        delivery.delivery_merchant_name = "Best Buy"
        delivery.delivery_shipping_method = "Express"
        delivery.delivery_fee = 25.50
        delivery.delivery_placed_order = 300
        delivery.delivery_provider_id = 400
        delivery.delivery_broker_id = 500
        delivery.delivery_created_at = datetime.now()
        delivery.delivery_updated_at = datetime.now()
        return delivery
    
    @pytest.fixture
    def sample_address(self):
        """Sample address model"""
        address = Mock(spec=Address)
        address.id_address = 200
        address.address_street = "123 Main St"
        address.address_city = "New York"
        address.address_postal_code = "10001"
        address.address_country = "USA"
        return address
    
    # ==================== Validation Tests ====================
    
    def test_validate_delivery_data_invalid_weight(self, delivery_service, sample_delivery_api):
        """Test validation fails for negative weight"""
        sample_delivery_api.delivery_total_weight = -10
        
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_delivery_data(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
        assert exc_info.value.status == HTTP_400_BAD_REQUEST
        assert "Delivery weight cannot be negative" in str(exc_info.value.details)
    
    def test_validate_delivery_data_invalid_package_count(self, delivery_service, sample_delivery_api):
        """Test validation fails for negative package count"""
        sample_delivery_api.delivery_package_count = -5
        
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_delivery_data(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
        assert "Package count cannot be negative" in str(exc_info.value.details)
    
    def test_validate_delivery_data_invalid_fee(self, delivery_service, sample_delivery_api):
        """Test validation fails for negative fee"""
        sample_delivery_api.delivery_fee = -10
        
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_delivery_data(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
        assert "Delivery fee cannot be negative" in str(exc_info.value.details)
    
    def test_validate_delivery_data_invalid_status(self, delivery_service, sample_delivery_api):
        """Test validation fails for invalid status"""
        sample_delivery_api.delivery_status = "INVALID_STATUS"
        
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_delivery_data(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
        assert "Invalid delivery status" in str(exc_info.value.details)
    
    def test_validate_delivery_data_no_recipient(self, delivery_service, sample_delivery_api):
        """Test validation fails when no recipient information provided"""
        sample_delivery_api.recipient_person = 0
        sample_delivery_api.recipient_provider = 0
        sample_delivery_api.delivery_placed_order = 0
        
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_delivery_data(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
        assert "Either recipient person, provider, or order reference is required" in str(exc_info.value.details)
    
    def test_validate_delivery_data_success(self, delivery_service, sample_delivery_api):
        """Test validation passes with valid data"""
        # Should not raise an exception
        delivery_service._validate_delivery_data(sample_delivery_api)
    
    # ==================== Status Transition Tests ====================
    
    def test_validate_status_transition_same_status(self, delivery_service):
        """Test same status transition is allowed"""
        result = delivery_service._validate_status_transition("PENDING", "PENDING")
        assert result is True
    
    def test_validate_status_transition_frozen_status(self, delivery_service):
        """Test cannot change frozen status (DELIVERED)"""
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_status_transition("DELIVERED", "PROCESSING")
        
        assert exc_info.value.code == DELIVERY_UPDATE_FAILED
        assert "Cannot change status of a delivered delivery" in str(exc_info.value.details)
    
    def test_validate_status_transition_invalid_new_status(self, delivery_service):
        """Test invalid new status"""
        with pytest.raises(APIException) as exc_info:
            delivery_service._validate_status_transition("PENDING", "INVALID")
        
        assert exc_info.value.code == DELIVERY_UPDATE_FAILED
        assert "Invalid delivery status" in str(exc_info.value.details)
    
    def test_validate_status_transition_valid(self, delivery_service):
        """Test valid status transition"""
        result = delivery_service._validate_status_transition("PENDING", "PROCESSING")
        assert result is True
    
    # ==================== get_delivery_by_id Tests ====================
    
    def test_get_delivery_by_id_success(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test successful delivery retrieval"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        
        result = delivery_service.get_delivery_by_id(1)
        
        assert result == sample_delivery_model
        mock_delivery_repo.get_by_id.assert_called_once_with(1, eager_load=True)
    
    def test_get_delivery_by_id_not_found(self, delivery_service, mock_delivery_repo):
        """Test getting non-existent delivery"""
        mock_delivery_repo.get_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.get_delivery_by_id(999)
        
        assert exc_info.value.code == DELIVERY_NOT_EXISTS
        assert exc_info.value.status == HTTP_404_NOT_FOUND
    
    # ==================== get_all_deliveries Tests ====================
    
    def test_get_all_deliveries(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test getting all deliveries with filters"""
        mock_delivery_repo.get_all.return_value = [sample_delivery_model]
        
        result = delivery_service.get_all_deliveries(provider_id=400, order_id=300, offset=0, limit=50)
        
        assert len(result) == 1
        assert result[0] == sample_delivery_model
        mock_delivery_repo.get_all.assert_called_once_with(400, 300, 0, 0, 50)
    
    # ==================== get_deliveries_by_status Tests ====================
    
    def test_get_deliveries_by_status_success(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test getting deliveries by status"""
        mock_delivery_repo.get_by_status.return_value = [sample_delivery_model]
        
        result = delivery_service.get_deliveries_by_status("PENDING")
        
        assert len(result) == 1
        mock_delivery_repo.get_by_status.assert_called_once_with("PENDING")
    
    def test_get_deliveries_by_status_invalid(self, delivery_service):
        """Test getting deliveries with invalid status"""
        with pytest.raises(APIException) as exc_info:
            delivery_service.get_deliveries_by_status("INVALID")
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
    
    # ==================== create_delivery Tests ====================
    
    def test_create_delivery_success(self, delivery_service, mock_delivery_repo, sample_delivery_api, sample_delivery_model):
        """Test successful delivery creation"""
        mock_delivery_repo.create.return_value = sample_delivery_model
        
        result = delivery_service.create_delivery(sample_delivery_api)
        
        assert result == sample_delivery_model
        mock_delivery_repo.create.assert_called_once()
    
    def test_create_delivery_without_recipient(self, delivery_service, sample_delivery_api):
        """Test delivery creation fails without recipient"""
        sample_delivery_api.recipient_person = 0
        sample_delivery_api.recipient_provider = 0
        sample_delivery_api.delivery_placed_order = 0
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.create_delivery(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_VALIDATION_FAILED
    
    def test_create_delivery_db_error(self, delivery_service, mock_delivery_repo, sample_delivery_api):
        """Test delivery creation with database error"""
        mock_delivery_repo.create.side_effect = Exception("DB Error")
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.create_delivery(sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_INSERT_FAILED
        assert exc_info.value.status == HTTP_417_EXPECTATION_FAILED
    
    # ==================== update_delivery Tests ====================
    
    def test_update_delivery_success(self, delivery_service, mock_delivery_repo, sample_delivery_api, sample_delivery_model):
        """Test successful delivery update"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        result = delivery_service.update_delivery(1, sample_delivery_api)
        
        assert result == sample_delivery_model
        mock_delivery_repo.update.assert_called_once()
    
    def test_update_delivery_not_found(self, delivery_service, mock_delivery_repo, sample_delivery_api):
        """Test updating non-existent delivery"""
        mock_delivery_repo.get_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.update_delivery(999, sample_delivery_api)
        
        assert exc_info.value.code == DELIVERY_NOT_EXISTS
    
    def test_update_delivery_with_background_tasks(self, delivery_service, mock_delivery_repo, sample_delivery_api, sample_delivery_model):
        """Test delivery update with background tasks"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.update.return_value = sample_delivery_model
        background_tasks = Mock(spec=BackgroundTasks)
        
        result = delivery_service.update_delivery(1, sample_delivery_api, background_tasks)
        
        assert result == sample_delivery_model
        background_tasks.add_task.assert_called_once()
    
    # ==================== update_delivery_status Tests ====================
    
    def test_update_delivery_status_success(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test successful status update"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        result = delivery_service.update_delivery_status(1, "PROCESSING")
        
        assert result == sample_delivery_model
        # Verify status was updated
        assert sample_delivery_model.delivery_status == "PROCESSING"
    
    def test_update_delivery_status_frozen(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test updating status of delivered delivery"""
        sample_delivery_model.delivery_status = "DELIVERED"
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.update_delivery_status(1, "PROCESSING")
        
        assert exc_info.value.code == DELIVERY_UPDATE_FAILED
    
    # ==================== update_delivery_address Tests ====================
    
    def test_update_delivery_address_success(self, delivery_service, mock_delivery_repo, mock_address_repo, sample_delivery_model, sample_address):
        """Test successful address update"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_address_repo.get_address_by_id.return_value = sample_address
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        result = delivery_service.update_delivery_address(1, 200)
        
        assert result == sample_delivery_model
        mock_address_repo.get_address_by_id.assert_called_once_with(200)
    
    def test_update_delivery_address_not_found(self, delivery_service, mock_delivery_repo, mock_address_repo):
        """Test updating with non-existent address"""
        mock_delivery_repo.get_by_id.return_value = Mock()
        mock_address_repo.get_address_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.update_delivery_address(1, 999)
        
        assert exc_info.value.code == DELIVERY_UPDATE_FAILED
        assert "Address with ID 999 does not exist" in str(exc_info.value.details)
    
    # ==================== update_delivery_tracking Tests ====================
    
    def test_update_delivery_tracking_success(self, delivery_service, mock_delivery_repo, mock_address_repo, sample_delivery_model, sample_address):
        """Test successful tracking update"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_address_repo.get_address_by_id.return_value = sample_address
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        result = delivery_service.update_delivery_tracking(1, 200)
        
        assert result == sample_delivery_model
        mock_address_repo.get_address_by_id.assert_called_once_with(200)
    
    # ==================== delete_delivery Tests ====================
    
    def test_delete_delivery_success(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test successful delivery deletion"""
        sample_delivery_model.delivery_status = "PENDING"
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.delete.return_value = True
        
        result = delivery_service.delete_delivery(1)
        
        assert result["message"] == "Delivery deleted successfully"
        assert result["delivery_id"] == 1
        mock_delivery_repo.delete.assert_called_once()
    
    def test_delete_delivery_invalid_status(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test deleting delivery with invalid status"""
        sample_delivery_model.delivery_status = "IN_TRANSIT"
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.delete_delivery(1)
        
        assert exc_info.value.code == DELIVERY_DELETE_FAILED
        assert "Cannot delete delivery with status: IN_TRANSIT" in str(exc_info.value.details)
    
    def test_delete_delivery_not_found(self, delivery_service, mock_delivery_repo):
        """Test deleting non-existent delivery"""
        mock_delivery_repo.get_by_id.return_value = None
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.delete_delivery(999)
        
        assert exc_info.value.code == DELIVERY_NOT_EXISTS
    
    def test_delete_delivery_failure(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test delivery deletion failure"""
        sample_delivery_model.delivery_status = "PENDING"
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.delete.return_value = False
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.delete_delivery(1)
        
        assert exc_info.value.code == DELIVERY_DELETE_FAILED
        assert exc_info.value.status == HTTP_500_INTERNAL_SERVER_ERROR
    
    # ==================== bulk_delete_deliveries Tests ====================
    
    def test_bulk_delete_deliveries_success(self, delivery_service, mock_delivery_repo):
        """Test successful bulk deletion"""
        mock_delivery_repo.bulk_delete_by_criteria.return_value = 5
        
        result = delivery_service.bulk_delete_deliveries(provider_id=400, status="PENDING")
        
        assert result["message"] == "Deleted 5 deliveries"
        assert result["deleted_count"] == 5
        mock_delivery_repo.bulk_delete_by_criteria.assert_called_once_with(400, 0, "PENDING")
    
    def test_bulk_delete_deliveries_error(self, delivery_service, mock_delivery_repo):
        """Test bulk deletion error"""
        mock_delivery_repo.bulk_delete_by_criteria.side_effect = Exception("DB Error")
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.bulk_delete_deliveries()
        
        assert exc_info.value.code == DELIVERY_BULK_DELETE_FAILED
    
    # ==================== bulk_update_status Tests ====================
    
    def test_bulk_update_status_success(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test successful bulk status update"""
        mock_delivery_repo.get_by_id.return_value = sample_delivery_model
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        result = delivery_service.bulk_update_status([1, 2, 3], "PROCESSING")
        
        assert len(result) == 3
        assert mock_delivery_repo.update.call_count == 3
    
    def test_bulk_update_status_partial_failure(self, delivery_service, mock_delivery_repo, sample_delivery_model):
        """Test bulk update with partial failures"""
        mock_delivery_repo.get_by_id.side_effect = [sample_delivery_model, None, sample_delivery_model]
        mock_delivery_repo.update.return_value = sample_delivery_model
        
        with pytest.raises(APIException) as exc_info:
            delivery_service.bulk_update_status([1, 2, 3], "PROCESSING")
        
        assert exc_info.value.code == DELIVERY_BULK_UPDATE_FAILED
        assert exc_info.value.status == HTTP_207_MULTI_STATUS
        assert exc_info.value.details['successful'] == 2
        assert len(exc_info.value.details['failed']) == 1
    
    # ==================== get_delivery_stats Tests ====================
    
    def test_get_delivery_stats(self, delivery_service, mock_delivery_repo):
        """Test getting delivery statistics"""
        mock_delivery_repo.count_by_status.side_effect = [5, 3, 2, 1, 0, 4, 1, 0, 2]
        
        stats = delivery_service.get_delivery_stats()
        
        assert stats['pending'] == 5
        assert stats['processing'] == 3
        assert stats['delivered'] == 4
        assert mock_delivery_repo.count_by_status.call_count == 9
    
    # ==================== Helper method Tests ====================
    
    def test_delivery_to_dict(self, delivery_service, sample_delivery_model):
        """Test delivery to dictionary conversion"""
        sample_delivery_model.__dict__ = {
            'id_delivery': 1,
            'delivery_status': 'PENDING',
            'delivery_created_at': datetime(2024, 1, 1, 12, 0, 0),
            '_sa_instance_state': None
        }
        
        result = delivery_service._delivery_to_dict(sample_delivery_model)
        
        assert result['id_delivery'] == 1
        assert result['delivery_status'] == 'PENDING'
        assert 'delivery_created_at' in result
        assert '_sa_instance_state' not in result


# ==================== Integration Tests ====================

@pytest.mark.integration
class TestDeliveryServiceIntegration:
    """Integration tests for DeliveryService"""
    
    @pytest.fixture
    def delivery_service(self):
        """Create real delivery service"""
        return DeliveryService()
    
    def test_delivery_status_constants(self, delivery_service):
        """Test delivery status constants are defined"""
        assert len(delivery_service.VALID_STATUSES) > 0
        assert 'PENDING' in delivery_service.VALID_STATUSES
        assert 'DELIVERED' in delivery_service.VALID_STATUSES
        assert 'CANCELLED' in delivery_service.VALID_STATUSES
        assert len(delivery_service.FROZEN_STATUSES) > 0
        assert 'DELIVERED' in delivery_service.FROZEN_STATUSES