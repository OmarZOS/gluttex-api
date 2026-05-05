# tests/integration/test_supplier_router.py
"""
Integration tests for Supplier and Organisation endpoints.
Tests cover CRUD operations, search, pagination, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

# Import the actual router module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import app
from core.api_models import (
    Location_API, ProductProvider_API, ProviderImage_API,
    ProviderOrganisation_API, OrganisationImage_API
)
from core.models import ProductProvider, ProviderOrganisation

# Create test client
client = TestClient(app)


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_supplier_data() -> Dict[str, Any]:
    """Sample supplier data for testing"""
    return {
        "provider": {
            "id_product_provider": "test_supplier_123",
            "provider_name": "Test Supplier",
            "provider_contact_info": "contact@testsupplier.com",
            "id_provider_owner": 1,
            "id_product_provider_type": 1,
            "id_provider_organisation": 0,
            "provider_organisation_name": "Test Org",
            "provider_organisation_desc": "Test Description"
        },
        "location": {
            "id_location": 0,
            "location_name": "Main Office",
            "location_latitude": 36.7538,
            "location_longitude": 3.0588,
            "address_street": "123 Test St",
            "address_city": "Algiers",
            "address_postal_code": "16000",
            "address_country": "Algeria"
        },
        "image": {
            "id_provider_image": 0,
            "provider_image_url": "https://example.com/supplier.jpg"
        }
    }


@pytest.fixture
def sample_organisation_data() -> Dict[str, Any]:
    """Sample organisation data for testing"""
    return {
        "org": {
            "id_provider_organisation": 0,
            "provider_organisation_name": "Test Organisation",
            "provider_organisation_desc": "A test organisation for integration testing"
        },
        "org_image": {
            "id_org_image": 0,
            "org_image_url": "https://example.com/org.jpg"
        }
    }


# ==================== Corrected Mock Fixtures ====================

@pytest.fixture
def mock_supplier_service():
    """Mock SupplierService for testing - using correct import path"""
    # The router is likely in routers.business_routers.supplier_router
    # Adjust the path based on your actual structure
    with patch('routers.business_routers.supplier_router.get_supplier_service') as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_organisation_service():
    """Mock OrganisationService for testing - using correct import path"""
    with patch('routers.business_routers.supplier_router.get_organisation_service') as mock:
        service_instance = Mock()
        mock.return_value = service_instance
        yield service_instance


# Alternative: Patch the actual service classes directly
@pytest.fixture
def mock_supplier_service_direct():
    """Mock SupplierService directly"""
    with patch('services.supplier_service.SupplierService') as MockSupplierService:
        service_instance = Mock()
        MockSupplierService.return_value = service_instance
        yield service_instance


@pytest.fixture
def mock_organisation_service_direct():
    """Mock OrganisationService directly"""
    with patch('services.supplier_service.OrganisationService') as MockOrgService:
        service_instance = Mock()
        MockOrgService.return_value = service_instance
        yield service_instance


# ==================== Supplier Endpoint Tests ====================

class TestSupplierEndpoints:
    """Test suite for supplier-related endpoints"""
    
    def test_get_all_suppliers_success(self, mock_supplier_service_direct):
        """Test successful retrieval of all suppliers"""
        # Arrange
        expected_suppliers = [
            Mock(id_product_provider="sup1", provider_name="Supplier 1"),
            Mock(id_product_provider="sup2", provider_name="Supplier 2")
        ]
        mock_supplier_service_direct.get_all_suppliers.return_value = expected_suppliers
        
        # Act
        response = client.get("/api/v1/suppliers?offset=0&limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_get_all_suppliers_with_filters(self, mock_supplier_service_direct):
        """Test retrieval of suppliers with filters"""
        # Arrange
        mock_supplier_service_direct.get_all_suppliers.return_value = []
        
        # Act
        response = client.get("/api/v1/suppliers?owner_id=5&org_id=10&offset=0&limit=20")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_all_suppliers_pagination_validation(self, mock_supplier_service_direct):
        """Test pagination parameter validation"""
        # Act - Test invalid limit (too high)
        response = client.get("/api/v1/suppliers?offset=0&limit=200")
        
        # Assert - Router passes through, service handles validation
        assert response.status_code == 200
    
    def test_get_supplier_types_success(self, mock_supplier_service_direct):
        """Test successful retrieval of supplier types"""
        # Arrange
        expected_types = [
            Mock(id_product_provider_type=1, product_provider_type_desc="Type A"),
            Mock(id_product_provider_type=2, product_provider_type_desc="Type B")
        ]
        mock_supplier_service_direct.get_supplier_types.return_value = expected_types
        
        # Act
        response = client.get("/api/v1/supplier-types")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_suppliers_by_location_success(self, mock_supplier_service_direct):
        """Test successful location-based supplier search"""
        # Arrange
        expected_results = [
            Mock(id_product_provider="sup1", distance=5.2),
            Mock(id_product_provider="sup2", distance=8.7)
        ]
        mock_supplier_service_direct.search_suppliers_by_location.return_value = expected_results
        
        # Act
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=36.7538&latitude=3.0588&distance_km=10&offset=0&limit=10"
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_suppliers_by_location_invalid_coordinates(self, mock_supplier_service_direct):
        """Test location search with invalid coordinates"""
        # Act - Longitude out of range
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=200&latitude=3.0588&distance_km=10"
        )
        
        # Assert - FastAPI validation should catch this
        assert response.status_code == 422  # Validation error
    
    def test_get_supplier_by_id_success(self, mock_supplier_service_direct):
        """Test successful retrieval of supplier by ID"""
        # Arrange
        expected_supplier = Mock(id_product_provider="test123")
        mock_supplier_service_direct.get_supplier_by_id.return_value = expected_supplier
        
        # Act
        response = client.get("/api/v1/suppliers/test123?full=true")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_supplier_by_id_not_found(self, mock_supplier_service_direct):
        """Test supplier retrieval when supplier doesn't exist"""
        # Arrange
        from core.exceptions import SupplierNotFoundException
        mock_supplier_service_direct.get_supplier_by_id.side_effect = SupplierNotFoundException(
            supplier_id="nonexistent"
        )
        
        # Act
        response = client.get("/api/v1/suppliers/nonexistent")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_create_supplier_success(self, mock_supplier_service_direct, sample_supplier_data):
        """Test successful supplier creation"""
        # Arrange
        created_supplier = Mock(id_product_provider="new_supplier_123")
        mock_supplier_service_direct.create_supplier.return_value = created_supplier
        
        # Act
        response = client.post(
            "/api/v1/suppliers",
            json=sample_supplier_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "Supplier created successfully" in data["message"]
    
    def test_create_supplier_missing_required_fields(self, mock_supplier_service_direct):
        """Test supplier creation with missing required fields"""
        # Act
        response = client.post(
            "/api/v1/suppliers",
            json={"provider": {}, "location": {}}  # Missing required fields
        )
        
        # Assert - Should be validation error
        assert response.status_code == 422
    
    def test_update_supplier_success(self, mock_supplier_service_direct, sample_supplier_data):
        """Test successful supplier update"""
        # Arrange
        updated_supplier = Mock(id_product_provider="test123")
        mock_supplier_service_direct.update_supplier.return_value = updated_supplier
        
        # Act
        response = client.put(
            "/api/v1/suppliers/test123",
            json=sample_supplier_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_supplier_not_found(self, mock_supplier_service_direct, sample_supplier_data):
        """Test supplier update when supplier doesn't exist"""
        # Arrange
        from core.exceptions import SupplierNotFoundException
        mock_supplier_service_direct.update_supplier.side_effect = SupplierNotFoundException(
            supplier_id="nonexistent"
        )
        
        # Act
        response = client.put(
            "/api/v1/suppliers/nonexistent",
            json=sample_supplier_data
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_supplier_success(self, mock_supplier_service_direct):
        """Test successful supplier deletion"""
        # Arrange
        mock_supplier_service_direct.delete_supplier.return_value = {"message": "Supplier deleted successfully"}
        
        # Act
        response = client.delete("/api/v1/suppliers/test123?force_delete=false")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_supplier_force_delete(self, mock_supplier_service_direct):
        """Test supplier deletion with force delete option"""
        # Arrange
        mock_supplier_service_direct.delete_supplier.return_value = {"message": "Supplier deleted successfully"}
        
        # Act
        response = client.delete("/api/v1/suppliers/test123?force_delete=true")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["details"]["force_deleted"] is True
    
    def test_delete_supplier_not_found(self, mock_supplier_service_direct):
        """Test supplier deletion when supplier doesn't exist"""
        # Arrange
        from core.exceptions import SupplierNotFoundException
        mock_supplier_service_direct.delete_supplier.side_effect = SupplierNotFoundException(
            supplier_id="nonexistent"
        )
        
        # Act
        response = client.delete("/api/v1/suppliers/nonexistent")
        
        # Assert
        assert response.status_code == 404


# ==================== Organisation Endpoint Tests ====================

class TestOrganisationEndpoints:
    """Test suite for organisation-related endpoints"""
    
    def test_get_all_organisations_success(self, mock_organisation_service_direct):
        """Test successful retrieval of all organisations"""
        # Arrange
        expected_orgs = [
            Mock(id_provider_organisation=1, provider_organisation_name="Org 1"),
            Mock(id_provider_organisation=2, provider_organisation_name="Org 2")
        ]
        mock_organisation_service_direct.get_all_orgs.return_value = expected_orgs
        
        # Act
        response = client.get("/api/v1/organisations?offset=0&limit=100")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_all_organisations_pagination(self, mock_organisation_service_direct):
        """Test organisations retrieval with custom pagination"""
        # Arrange
        mock_organisation_service_direct.get_all_orgs.return_value = []
        
        # Act
        response = client.get("/api/v1/organisations?offset=50&limit=25")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_organisation_by_id_success(self, mock_organisation_service_direct):
        """Test successful retrieval of organisation by ID"""
        # Arrange
        expected_org = Mock(id_provider_organisation="org123", provider_organisation_name="Test Org")
        mock_organisation_service_direct.get_org_by_id.return_value = expected_org
        
        # Act
        response = client.get("/api/v1/organisations/org123")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_organisation_by_id_not_found(self, mock_organisation_service_direct):
        """Test organisation retrieval when organisation doesn't exist"""
        # Arrange
        from core.exceptions import OrganisationNotFoundException
        mock_organisation_service_direct.get_org_by_id.side_effect = OrganisationNotFoundException(
            org_id="nonexistent"
        )
        
        # Act
        response = client.get("/api/v1/organisations/nonexistent")
        
        # Assert
        assert response.status_code == 404
    
    def test_create_organisation_success(self, mock_organisation_service_direct, sample_organisation_data):
        """Test successful organisation creation"""
        # Arrange
        created_org = Mock(id_provider_organisation="new_org_123")
        mock_organisation_service_direct.create_organisation.return_value = created_org
        
        # Act
        response = client.post(
            "/api/v1/organisations",
            json=sample_organisation_data
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
    
    def test_create_organisation_missing_name(self, mock_organisation_service_direct):
        """Test organisation creation with missing required name"""
        # Act
        response = client.post(
            "/api/v1/organisations",
            json={"org": {"provider_organisation_name": ""}, "org_image": None}
        )
        
        # Assert
        assert response.status_code == 422
    
    def test_create_organisation_duplicate(self, mock_organisation_service_direct, sample_organisation_data):
        """Test organisation creation with duplicate name"""
        # Arrange
        from core.exceptions import OrganisationAlreadyExistsException
        mock_organisation_service_direct.create_organisation.side_effect = OrganisationAlreadyExistsException(
            org_name="Test Organisation"
        )
        
        # Act
        response = client.post(
            "/api/v1/organisations",
            json=sample_organisation_data
        )
        
        # Assert
        assert response.status_code == 409
    
    def test_update_organisation_success(self, mock_organisation_service_direct, sample_organisation_data):
        """Test successful organisation update"""
        # Arrange
        updated_org = Mock(id_provider_organisation="org123")
        mock_organisation_service_direct.update_organisation.return_value = updated_org
        
        # Act
        response = client.put(
            "/api/v1/organisations/org123",
            json=sample_organisation_data
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_organisation_not_found(self, mock_organisation_service_direct, sample_organisation_data):
        """Test organisation update when organisation doesn't exist"""
        # Arrange
        from core.exceptions import OrganisationNotFoundException
        mock_organisation_service_direct.update_organisation.side_effect = OrganisationNotFoundException(
            org_id="nonexistent"
        )
        
        # Act
        response = client.put(
            "/api/v1/organisations/nonexistent",
            json=sample_organisation_data
        )
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_organisation_success(self, mock_organisation_service_direct):
        """Test successful organisation deletion"""
        # Arrange
        mock_organisation_service_direct.delete_organisation.return_value = {"message": "Organisation deleted successfully"}
        
        # Act
        response = client.delete("/api/v1/organisations/org123?force_delete=false")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_organisation_force_delete(self, mock_organisation_service_direct):
        """Test organisation deletion with force delete option"""
        # Arrange
        mock_organisation_service_direct.delete_organisation.return_value = {"message": "Organisation deleted successfully"}
        
        # Act
        response = client.delete("/api/v1/organisations/org123?force_delete=true")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["details"]["force_deleted"] is True
    
    def test_delete_organisation_not_found(self, mock_organisation_service_direct):
        """Test organisation deletion when organisation doesn't exist"""
        # Arrange
        from core.exceptions import OrganisationNotFoundException
        mock_organisation_service_direct.delete_organisation.side_effect = OrganisationNotFoundException(
            org_id="nonexistent"
        )
        
        # Act
        response = client.delete("/api/v1/organisations/nonexistent")
        
        # Assert
        assert response.status_code == 404


# ==================== Edge Cases & Validation Tests ====================

class TestSupplierEdgeCases:
    """Test suite for edge cases and validation"""
    
    def test_get_suppliers_zero_limit(self, mock_supplier_service_direct):
        """Test getting suppliers with zero limit (invalid)"""
        # Act - FastAPI should reject limit < 1
        response = client.get("/api/v1/suppliers?offset=0&limit=0")
        assert response.status_code == 422
    
    def test_get_suppliers_negative_offset(self, mock_supplier_service_direct):
        """Test getting suppliers with negative offset"""
        response = client.get("/api/v1/suppliers?offset=-1&limit=10")
        assert response.status_code == 422
    
    def test_search_suppliers_extreme_distance(self, mock_supplier_service_direct):
        """Test location search with extreme distance values"""
        # Test with distance_km at maximum (500)
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=36.7538&latitude=3.0588&distance_km=500"
        )
        assert response.status_code == 200
        
        # Test with distance_km above maximum (should fail validation)
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=36.7538&latitude=3.0588&distance_km=1000"
        )
        assert response.status_code == 422
    
    def test_create_supplier_without_location(self):
        """Test creating supplier without location data"""
        response = client.post(
            "/api/v1/suppliers",
            json={
                "provider": {
                    "id_product_provider": "test",
                    "provider_name": "Test Supplier"
                }
                # Missing location
            }
        )
        assert response.status_code == 422
    
    def test_update_supplier_non_existent_id(self, mock_supplier_service_direct):
        """Test updating supplier with non-existent ID"""
        from core.exceptions import SupplierNotFoundException
        mock_supplier_service_direct.update_supplier.side_effect = SupplierNotFoundException(
            supplier_id="fake_id"
        )
        
        response = client.put(
            "/api/v1/suppliers/fake_id",
            json={
                "provider": {"id_product_provider": "fake_id", "provider_name": "Updated"},
                "image": None,
                "location": None
            }
        )
        
        assert response.status_code == 404


# ==================== Response Format Tests ====================

class TestSupplierResponseFormat:
    """Test suite for response format validation"""
    
    def test_success_response_format(self, mock_supplier_service_direct):
        """Test that success responses follow the expected format"""
        mock_supplier_service_direct.get_supplier_types.return_value = []
        
        response = client.get("/api/v1/supplier-types")
        data = response.json()
        
        # Check required fields
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["success"] is True
    
    def test_error_response_format(self, mock_supplier_service_direct):
        """Test that error responses follow the expected format"""
        from core.exceptions import SupplierNotFoundException
        mock_supplier_service_direct.get_supplier_by_id.side_effect = SupplierNotFoundException(
            supplier_id="nonexistent"
        )
        
        response = client.get("/api/v1/suppliers/nonexistent")
        data = response.json()
        
        # Check required fields in error response
        assert "success" in data
        assert "status_code" in data
        assert "code" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["success"] is False
        assert data["status_code"] == 404


# ==================== Performance Tests ====================

class TestSupplierPerformance:
    """Basic performance tests for supplier endpoints"""
    
    def test_get_all_suppliers_response_time(self, mock_supplier_service_direct):
        """Test response time for getting all suppliers"""
        import time
        mock_supplier_service_direct.get_all_suppliers.return_value = []
        
        start_time = time.time()
        response = client.get("/api/v1/suppliers?limit=100")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Allow 2 seconds
    
    def test_search_suppliers_response_time(self, mock_supplier_service_direct):
        """Test response time for location search"""
        import time
        mock_supplier_service_direct.search_suppliers_by_location.return_value = []
        
        start_time = time.time()
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=36.7538&latitude=3.0588&distance_km=10"
        )
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Allow 2 seconds


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])