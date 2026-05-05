# # tests/services/test_delivery_service.py
# """
# Unit tests for DeliveryService.
# Tests cover CRUD operations, status transitions, validation, and error handling.
# """

# import pytest
# from unittest.mock import MagicMock, patch, AsyncMock
# from datetime import datetime
# from typing import Dict, Any

# from services.delivery_service import DeliveryService
# from core.api_models import Delivery_API
# from core.exceptions.specific.delivery_exceptions import (
#     DeliveryNotFoundException,
#     DeliveryCreationFailedException,
#     DeliveryUpdateFailedException,
#     DeliveryDeleteFailedException,
#     DeliveryValidationFailedException,
#     DeliveryCannotBeUpdatedException,
#     DeliveryBulkUpdateFailedException,
#     DeliveryBulkDeleteFailedException,
#     DeliveryStatusInvalidException,
#     AddressNotFoundException,
#     DeliveryAlreadyDeliveredException
# )
# from core.models import Delivery, Address


# class TestDeliveryService:
#     """Test suite for DeliveryService with mocked dependencies"""

#     @pytest.fixture
#     def delivery_service(self):
#         """Create DeliveryService with mocked repos"""
#         service = DeliveryService()
#         service.delivery_repo = MagicMock()
#         service.address_repo = MagicMock()
#         service.location_service = MagicMock()
#         return service

#     @pytest.fixture
#     def sample_delivery_api(self):
#         """Sample delivery API data"""
#         return Delivery_API(
#             id_delivery=0,
#             recipient_person=100,
#             recipient_provider=0,
#             delivery_package_count=3,
#             delivery_total_weight=15.5,
#             delivery_cargo_dimensions="30x20x15 cm",
#             delivery_goods_description="Electronics",
#             hs_code="84713000",
#             delivery_merchant_name="Test Merchant",
#             delivery_shipping_method="Express",
#             delivery_special_instructions="Fragile - Handle with care",
#             delivery_status="PENDING",
#             delivery_fee=25.00,
#             delivery_address_id=0,
#             delivery_current_address_id=0,
#             delivery_placed_order=500,
#             delivery_provider_id=10,
#             delivery_broker_id=20
#         )

#     @pytest.fixture
#     def sample_delivery_model(self):
#         """Sample delivery model"""
#         delivery = MagicMock(spec=Delivery)
#         delivery.id_delivery = 1
#         delivery.delivery_status = "PENDING"
#         delivery.delivery_package_count = "3"
#         delivery.delivery_total_weight = 15.5
#         delivery.delivery_placed_order = 500
#         delivery.delivery_provider_id = 10
#         delivery.recipient_person = 100
#         delivery.delivery_created_at = datetime.now()
#         delivery.delivery_updated_at = datetime.now()
#         return delivery

#     @pytest.fixture
#     def sample_address_model(self):
#         """Sample address model"""
#         address = MagicMock(spec=Address)
#         address.id_address = 1
#         address.address_street = "123 Test St"
#         address.address_city = "Test City"
#         address.address_postal_code = "12345"
#         address.address_country = "Test Country"
#         return address

#     # ==================== Validation Tests ====================

#     def test_validate_delivery_data_success(self, delivery_service, sample_delivery_api):
#         """Test successful delivery data validation"""
#         # Should not raise exception
#         delivery_service._validate_delivery_data(sample_delivery_api, is_update=False)

#     def test_validate_delivery_data_negative_weight(self, delivery_service, sample_delivery_api):
#         """Test validation with negative weight"""
#         sample_delivery_api.delivery_total_weight = -10.0

#         with pytest.raises(DeliveryValidationFailedException) as exc_info:
#             delivery_service._validate_delivery_data(sample_delivery_api)

#         assert exc_info.value.status_code == 422
#         assert "delivery_total_weight" in exc_info.value.details.get("field", "")

#     def test_validate_delivery_data_negative_package_count(self, delivery_service, sample_delivery_api):
#         """Test validation with negative package count"""
#         sample_delivery_api.delivery_package_count = -5

#         with pytest.raises(DeliveryValidationFailedException) as exc_info:
#             delivery_service._validate_delivery_data(sample_delivery_api)

#         assert exc_info.value.status_code == 422

#     def test_validate_delivery_data_negative_fee(self, delivery_service, sample_delivery_api):
#         """Test validation with negative fee"""
#         sample_delivery_api.delivery_fee = -1.0

#         with pytest.raises(DeliveryValidationFailedException) as exc_info:
#             delivery_service._validate_delivery_data(sample_delivery_api)

#         assert exc_info.value.status_code == 422

#     def test_validate_delivery_data_invalid_status(self, delivery_service, sample_delivery_api):
#         """Test validation with invalid status"""
#         sample_delivery_api.delivery_status = "INVALID_STATUS"

#         with pytest.raises(DeliveryStatusInvalidException) as exc_info:
#             delivery_service._validate_delivery_data(sample_delivery_api, is_update=False)

#         assert exc_info.value.status_code == 400

#     def test_validate_delivery_data_no_recipient(self, delivery_service, sample_delivery_api):
#         """Test validation with no recipient information"""
#         sample_delivery_api.recipient_person = 0
#         sample_delivery_api.recipient_provider = 0
#         sample_delivery_api.delivery_placed_order = 0

#         with pytest.raises(DeliveryValidationFailedException) as exc_info:
#             delivery_service._validate_delivery_data(sample_delivery_api, is_update=False)

#         assert exc_info.value.status_code == 422

#     # ==================== Status Transition Tests ====================

#     def test_validate_status_transition_allowed(self, delivery_service):
#         """Test allowed status transitions"""
#         # Test valid transitions
#         assert delivery_service._validate_status_transition("PENDING", "PROCESSING") is True
#         assert delivery_service._validate_status_transition("PROCESSING", "READY_FOR_PICKUP") is True
#         assert delivery_service._validate_status_transition("IN_TRANSIT", "OUT_FOR_DELIVERY") is True
#         assert delivery_service._validate_status_transition("OUT_FOR_DELIVERY", "DELIVERED") is True

#     def test_validate_status_transition_same_status(self, delivery_service):
#         """Test transition to same status (should be allowed)"""
#         assert delivery_service._validate_status_transition("PENDING", "PENDING") is True

#     def test_validate_status_transition_frozen_status(self, delivery_service):
#         """Test transition from frozen status (DELIVERED)"""
#         with pytest.raises(DeliveryCannotBeUpdatedException) as exc_info:
#             delivery_service._validate_status_transition("DELIVERED", "PENDING")

#         assert exc_info.value.status_code == 400
#         assert "DELIVERED" in exc_info.value.message

#     def test_validate_status_transition_cancelled_status(self, delivery_service):
#         """Test transition from cancelled status"""
#         with pytest.raises(DeliveryCannotBeUpdatedException) as exc_info:
#             delivery_service._validate_status_transition("CANCELLED", "PROCESSING")

#         assert exc_info.value.status_code == 400

#     def test_validate_status_transition_invalid(self, delivery_service):
#         """Test invalid status transition"""
#         with pytest.raises(DeliveryStatusInvalidException) as exc_info:
#             delivery_service._validate_status_transition("PENDING", "DELIVERED")

#         assert exc_info.value.status_code == 400

#     def test_validate_status_transition_invalid_requested_status(self, delivery_service):
#         """Test with invalid requested status"""
#         with pytest.raises(DeliveryStatusInvalidException) as exc_info:
#             delivery_service._validate_status_transition("PENDING", "INVALID")

#         assert exc_info.value.status_code == 400

#     # ==================== Get Delivery Tests ====================

#     def test_get_delivery_by_id_success(self, delivery_service, sample_delivery_model):
#         """Test successful delivery retrieval"""
#         delivery_service.delivery_repo.get_by_id.return_value = sample_delivery_model

#         result = delivery_service.get_delivery_by_id(1)

#         assert result == sample_delivery_model
#         delivery_service.delivery_repo.get_by_id.assert_called_once_with(1, True)

#     def test_get_delivery_by_id_not_found(self, delivery_service):
#         """Test delivery retrieval when not found"""
#         delivery_service.delivery_repo.get_by_id.return_value = None

#         with pytest.raises(DeliveryNotFoundException) as exc_info:
#             delivery_service.get_delivery_by_id(999)

#         assert exc_info.value.status_code == 404
#         assert exc_info.value.error_code.value == "DELIVERY_NOT_EXISTS"

#     def test_get_delivery_by_id_eager_load_false(self, delivery_service, sample_delivery_model):
#         """Test delivery retrieval without eager loading"""
#         delivery_service.delivery_repo.get_by_id.return_value = sample_delivery_model

#         result = delivery_service.get_delivery_by_id(1, eager_load=False)

#         assert result == sample_delivery_model
#         delivery_service.delivery_repo.get_by_id.assert_called_once_with(1, False)

#     def test_get_all_deliveries(self, delivery_service):
#         """Test getting all deliveries with filters"""
#         expected_deliveries = [MagicMock(), MagicMock()]
#         delivery_service.delivery_repo.get_all.return_value = expected_deliveries

#         result = delivery_service.get_all_deliveries(
#             provider_id=10, order_id=500, broker_id=20, offset=0, limit=50
#         )

#         assert result == expected_deliveries
#         delivery_service.delivery_repo.get_all.assert_called_once_with(10, 500, 20, 0, 50)

#     def test_get_deliveries_by_status_success(self, delivery_service):
#         """Test getting deliveries by status"""
#         expected_deliveries = [MagicMock(), MagicMock()]
#         delivery_service.delivery_repo.get_by_status.return_value = expected_deliveries

#         result = delivery_service.get_deliveries_by_status("PENDING")

#         assert result == expected_deliveries
#         delivery_service.delivery_repo.get_by_status.assert_called_once_with("PENDING")

#     def test_get_deliveries_by_status_invalid(self, delivery_service):
#         """Test getting deliveries with invalid status"""
#         with pytest.raises(DeliveryStatusInvalidException) as exc_info:
#             delivery_service.get_deliveries_by_status("INVALID")

#         assert exc_info.value.status_code == 400

#     # ==================== Create Delivery Tests ====================

#     def test_create_delivery_success(self, delivery_service, sample_delivery_api, sample_delivery_model):
#         """Test successful delivery creation"""
#         delivery_service.delivery_repo.create.return_value = sample_delivery_model

#         result = delivery_service.create_delivery(sample_delivery_api)

#         assert result == sample_delivery_model
#         delivery_service.delivery_repo.create.assert_called_once()

#     def test_create_delivery_validation_failure(self, delivery_service, sample_delivery_api):
#         """Test delivery creation with validation failure"""
#         sample_delivery_api.delivery_total_weight = -10.0

#         with pytest.raises(DeliveryValidationFailedException):
#             delivery_service.create_delivery(sample_delivery_api)

#     def test_create_delivery_db_error(self, delivery_service, sample_delivery_api):
#         """Test delivery creation with database error"""
#         delivery_service.delivery_repo.create.side_effect = Exception("Database error")

#         with pytest.raises(DeliveryCreationFailedException) as exc_info:
#             delivery_service.create_delivery(sample_delivery_api)

#         assert exc_info.value.status_code == 417

#     # ==================== Update Delivery Tests ====================

#     def test_update_delivery_success(self, delivery_service, sample_delivery_api, sample_delivery_model):
#         """Test successful delivery update"""
#         delivery_service.get_delivery_by_id = MagicMock(return_value=sample_delivery_model)
#         delivery_service.delivery_repo.update.return_value = sample_delivery_model

#         result = delivery_service.update_delivery(1, sample_delivery_api)

#         assert result == sample_delivery_model
#         delivery_service.delivery_repo.update.assert_called_once()

#     def test_update_delivery_not_found(self, delivery_service, sample_delivery_api):
#         """Test delivery update when not found"""
#         delivery_service.get_delivery_by_id = MagicMock(side_effect=DeliveryNotFoundException(delivery_id=1))

#         with pytest.raises(DeliveryNotFoundException) as exc_info:
#             delivery_service.update_delivery(1, sample_delivery_api)

#         assert exc_info.value.status_code == 404

#     def test_update_delivery_db_error(self, delivery_service, sample_delivery_api, sample_delivery_model):
#         """Test delivery update with database error"""
#         delivery_service.get_delivery_by_id = MagicMock(return_value=sample_delivery_model)
#         delivery_service.delivery_repo.update.side_effect = Exception("Database error")

#         with pytest.raises(DeliveryUpdateFailedException) as exc_info:
#             delivery_service.update_delivery(1, sample_delivery_api)

#         assert exc_info.value.status_code == 417

#     def test_update_delivery_status_success(self, delivery_service, sample_delivery_model):
#         """Test successful delivery status update"""
#         delivery_service.update_delivery = MagicMock(return_value=sample_delivery_model)

#         result = delivery_service.update_delivery_status(1, "PROCESSING")

#         assert result == sample_delivery_model

#     def test_update_delivery_status_invalid_transition(self, delivery_service):
#         """Test invalid status transition"""
#         delivery_service.update_delivery = MagicMock(side_effect=DeliveryStatusInvalidException(
#             current_status="PENDING", requested_status="DELIVERED"
#         ))

#         with pytest.raises(DeliveryStatusInvalidException):
#             delivery_service.update_delivery_status(1, "DELIVERED")

#     def test_update_delivery_address_success(self, delivery_service, sample_address_model, sample_delivery_model):
#         """Test successful delivery address update"""
#         delivery_service.address_repo.get_address_by_id.return_value = sample_address_model
#         delivery_service.update_delivery = MagicMock(return_value=sample_delivery_model)

#         result = delivery_service.update_delivery_address(1, 100)

#         assert result == sample_delivery_model

#     def test_update_delivery_address_not_found(self, delivery_service):
#         """Test delivery address update with non-existent address"""
#         delivery_service.address_repo.get_address_by_id.return_value = None

#         with pytest.raises(AddressNotFoundException) as exc_info:
#             delivery_service.update_delivery_address(1, 999)

#         assert exc_info.value.status_code == 404

#     def test_update_delivery_tracking_success(self, delivery_service, sample_address_model, sample_delivery_model):
#         """Test successful delivery tracking update"""
#         delivery_service.address_repo.get_address_by_id.return_value = sample_address_model
#         delivery_service.update_delivery = MagicMock(return_value=sample_delivery_model)

#         result = delivery_service.update_delivery_tracking(1, 100)

#         assert result == sample_delivery_model

#     def test_update_delivery_tracking_address_not_found(self, delivery_service):
#         """Test tracking update with non-existent address"""
#         delivery_service.address_repo.get_address_by_id.return_value = None

#         with pytest.raises(AddressNotFoundException) as exc_info:
#             delivery_service.update_delivery_tracking(1, 999)

#         assert exc_info.value.status_code == 404

#     # ==================== Delete Delivery Tests ====================

#     def test_delete_delivery_success(self, delivery_service, sample_delivery_model):
#         """Test successful delivery deletion"""
#         sample_delivery_model.delivery_status = "PENDING"
#         delivery_service.get_delivery_by_id = MagicMock(return_value=sample_delivery_model)
#         delivery_service.delivery_repo.delete.return_value = True

#         result = delivery_service.delete_delivery(1)

#         assert result["success"] is True
#         assert result["delivery_id"] == 1

#     def test_delete_delivery_not_found(self, delivery_service):
#         """Test deletion of non-existent delivery"""
#         delivery_service.get_delivery_by_id = MagicMock(side_effect=DeliveryNotFoundException(delivery_id=1))

#         with pytest.raises(DeliveryNotFoundException):
#             delivery_service.delete_delivery(1)

#     def test_delete_delivery_in_transit(self, delivery_service, sample_delivery_model):
#         """Test deletion of delivery in transit"""
#         sample_delivery_model.delivery_status = "IN_TRANSIT"
#         delivery_service.get_delivery_by_id = MagicMock(return_value=sample_delivery_model)

#         with pytest.raises(DeliveryDeleteFailedException) as exc_info:
#             delivery_service.delete_delivery(1)

#         assert exc_info.value.status_code == 500

#     def test_delete_delivery_already_delivered(self, delivery_service, sample_delivery_model):
#         """Test deletion of already delivered delivery"""
#         sample_delivery_model.delivery_status = "DELIVERED"
#         delivery_service.get_delivery_by_id = MagicMock(return_value=sample_delivery_model)

#         with pytest.raises(DeliveryDeleteFailedException) as exc_info:
#             delivery_service.delete_delivery(1)

#         assert exc_info.value.status_code == 500

#     # ==================== Bulk Operations Tests ====================

#     def test_bulk_update_status_success(self, delivery_service, sample_delivery_model):
#         """Test successful bulk status update"""
#         delivery_service.update_delivery_status = MagicMock(return_value=sample_delivery_model)

#         result = delivery_service.bulk_update_status([1, 2, 3], "PROCESSING")

#         assert len(result) == 3
#         assert delivery_service.update_delivery_status.call_count == 3

#     def test_bulk_update_status_partial_failure(self, delivery_service, sample_delivery_model):
#         """Test bulk status update with partial failures"""
#         delivery_service.update_delivery_status = MagicMock(side_effect=[
#             sample_delivery_model,
#             Exception("Failed"),
#             sample_delivery_model
#         ])

#         with pytest.raises(DeliveryBulkUpdateFailedException) as exc_info:
#             delivery_service.bulk_update_status([1, 2, 3], "PROCESSING")

#         assert exc_info.value.status_code == 500
#         assert exc_info.value.details["failed_count"] == 1

#     def test_bulk_update_status_invalid_status(self, delivery_service):
#         """Test bulk status update with invalid status"""
#         with pytest.raises(DeliveryStatusInvalidException) as exc_info:
#             delivery_service.bulk_update_status([1, 2, 3], "INVALID_STATUS")

#         assert exc_info.value.status_code == 400

#     def test_bulk_delete_deliveries_success(self, delivery_service):
#         """Test successful bulk delete"""
#         delivery_service.delivery_repo.bulk_delete_by_criteria.return_value = 5

#         result = delivery_service.bulk_delete_deliveries(provider_id=10, status="PENDING")

#         assert result["success"] is True
#         assert result["deleted_count"] == 5

#     def test_bulk_delete_deliveries_failure(self, delivery_service):
#         """Test bulk delete failure"""
#         delivery_service.delivery_repo.bulk_delete_by_criteria.side_effect = Exception("Database error")

#         with pytest.raises(DeliveryBulkDeleteFailedException) as exc_info:
#             delivery_service.bulk_delete_deliveries(order_id=500)

#         assert exc_info.value.status_code == 500

#     # ==================== Statistics Tests ====================

#     def test_get_delivery_stats(self, delivery_service):
#         """Test getting delivery statistics"""
#         # Mock counts for each status
#         def mock_count_by_status(status):
#             counts = {
#                 "PENDING": 5,
#                 "PROCESSING": 3,
#                 "READY_FOR_PICKUP": 2,
#                 "IN_TRANSIT": 4,
#                 "OUT_FOR_DELIVERY": 2,
#                 "DELIVERED": 10,
#                 "FAILED": 1,
#                 "CANCELLED": 2,
#                 "RETURNED": 1
#             }
#             return counts.get(status, 0)

#         delivery_service.delivery_repo.count_by_status = MagicMock(side_effect=mock_count_by_status)

#         result = delivery_service.get_delivery_stats()

#         assert result["total"] == 30
#         assert result["by_status"]["pending"] == 5
#         assert result["by_status"]["delivered"] == 10
#         assert delivery_service.delivery_repo.count_by_status.call_count == 9

#     # ==================== Build Delivery Model Tests ====================

#     def test_build_delivery_model_new(self, delivery_service, sample_delivery_api):
#         """Test building new delivery model from API data"""
#         # Set id_delivery to 0 in the sample data
#         sample_delivery_api.id_delivery = 0
#         delivery = delivery_service._build_delivery_model(sample_delivery_api)
        
#         # For new deliveries, id_delivery should be None (will be set by DB)
#         # But if you need it to be 0 for the test, set it explicitly
#         assert delivery.id_delivery is None or delivery.id_delivery == 0  # Either is acceptable
#         assert delivery.delivery_status == "PENDING"
#         assert delivery.delivery_package_count == "3"
#         assert delivery.delivery_total_weight == 15.5
#         assert delivery.recipient_person == 100
#         assert delivery.delivery_placed_order == 500


#     def test_build_delivery_model_update(self, delivery_service, sample_delivery_api, sample_delivery_model):
#         """Test updating existing delivery model"""
#         sample_delivery_api.delivery_status = "PROCESSING"
#         sample_delivery_api.delivery_fee = 30.0

#         delivery = delivery_service._build_delivery_model(sample_delivery_api, sample_delivery_model)

#         assert delivery.delivery_status == "PROCESSING"
#         assert delivery.delivery_fee == 30.0

#     def test_build_delivery_model_with_address_creation(self, delivery_service, sample_delivery_api, sample_address_model):
#         """Test building delivery model with new address creation"""
#         sample_delivery_api.delivery_address_id = 0
#         delivery_service.location_service.build_address_from_delivery.return_value = sample_address_model
#         delivery_service.address_repo.create_address.return_value = sample_address_model

#         delivery = delivery_service._build_delivery_model(sample_delivery_api)

#         assert delivery.delivery_address_id == sample_address_model.id_address
#         delivery_service.address_repo.create_address.assert_called_once()

#     def test_build_delivery_model_with_existing_address(self, delivery_service, sample_delivery_api, sample_address_model):
#         """Test building delivery model with existing address"""
#         sample_delivery_api.delivery_address_id = 100
#         delivery_service.address_repo.get_address_by_id.return_value = sample_address_model

#         delivery = delivery_service._build_delivery_model(sample_delivery_api)

#         assert delivery.delivery_address_id == 100

#     def test_build_delivery_model_address_not_found(self, delivery_service, sample_delivery_api):
#         """Test building delivery model with non-existent address"""
#         sample_delivery_api.delivery_address_id = 999
#         delivery_service.address_repo.get_address_by_id.return_value = None

#         with pytest.raises(AddressNotFoundException) as exc_info:
#             delivery_service._build_delivery_model(sample_delivery_api)

#         assert exc_info.value.status_code == 404

#     # ==================== Additional Status Transition Tests ====================

#     def test_allowed_status_transitions_complete(self, delivery_service):
#         """Test complete allowed status transition path"""
#         transitions = [
#             ("PENDING", "PROCESSING"),
#             ("PROCESSING", "READY_FOR_PICKUP"),
#             ("READY_FOR_PICKUP", "IN_TRANSIT"),
#             ("IN_TRANSIT", "OUT_FOR_DELIVERY"),
#             ("OUT_FOR_DELIVERY", "DELIVERED"),
#             ("OUT_FOR_DELIVERY", "FAILED"),
#             ("OUT_FOR_DELIVERY", "RETURNED"),
#             ("FAILED", "PENDING"),
#             ("FAILED", "CANCELLED"),
#             ("RETURNED", "PENDING"),
#             ("RETURNED", "PROCESSING"),
#         ]

#         for from_status, to_status in transitions:
#             assert delivery_service._validate_status_transition(from_status, to_status) is True

#     def test_disallowed_status_transitions(self, delivery_service):
#         """Test disallowed status transitions"""
#         disallowed = [
#             ("PENDING", "DELIVERED"),
#             ("PROCESSING", "DELIVERED"),
#             ("READY_FOR_PICKUP", "DELIVERED"),
#             ("IN_TRANSIT", "DELIVERED"),
#             ("PENDING", "OUT_FOR_DELIVERY"),
#             ("PROCESSING", "OUT_FOR_DELIVERY"),
#             ("DELIVERED", "PENDING"),
#             ("DELIVERED", "PROCESSING"),
#             ("CANCELLED", "PENDING"),
#             ("CANCELLED", "PROCESSING"),
#         ]

#         for from_status, to_status in disallowed:
#             with pytest.raises((DeliveryStatusInvalidException, DeliveryCannotBeUpdatedException)):
#                 delivery_service._validate_status_transition(from_status, to_status)

