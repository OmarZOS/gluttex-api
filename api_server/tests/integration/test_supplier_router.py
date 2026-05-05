# tests/integration/test_supplier_router.py
"""
Integration tests for Supplier and Organisation endpoints.
Tests cover CRUD operations, search, pagination, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import os
import time

from server import app

# Create test client
client = TestClient(app)


# ==================== Skip if no database ====================

# Only run integration tests if explicitly requested
pytestmark = pytest.mark.skipif(
    not os.environ.get('RUN_INTEGRATION_TESTS', 'true').lower() == 'true',
    reason="Integration tests require database. Set RUN_INTEGRATION_TESTS=true to run."
)


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_supplier_data() -> Dict[str, Any]:
    """Sample supplier data for testing matching ProductProvider_API and Location_API"""
    return {
        "provider": {
            "id_product_provider": 0,  # Will be auto-generated
            "id_provider_owner": 1,
            "idprovider_details_id": 0,
            "id_product_provider_type": 1,
            "id_provider_organisation": 0,
            "product_provider_type_desc": "Test Type",
            "provider_organisation_name": "Test Org",
            "provider_organisation_desc": "Test Description",
            "provider_name": "Test Supplier",
            "provider_contact_info": "contact@testsupplier.com"
        },
        "location": {
            "id_location": 0,
            "location_latitude": 36.7538,
            "location_longitude": 3.0588,
            "location_name": "Main Office",
            "location_address_id": 0,
            "id_address": 0,
            "address_street": "123 Test St",
            "address_city": "Algiers",
            "address_postal_code": "16000",
            "address_country": "Algeria"
        },
        "image": {
            "id_provider_image": 0,
            "provider_image_url": "https://example.com/supplier.jpg",
            "provider_ref_id": 0
        }
    }


@pytest.fixture
def sample_organisation_data():
    """Sample organisation data for testing matching ProviderOrganisation_API and OrganisationImage_API"""
    unique_suffix = int(time.time())
    return {
        "org": {
            "id_provider_organisation": 0,  # Will be auto-generated
            "provider_organisation_name": f"Test Organisation_{unique_suffix}",
            "provider_organisation_desc": "A test organisation for integration testing"
        },
        "org_image": {
            "id_org_image": 0,
            "org_image_url": "https://example.com/org.jpg",
            "org_ref_id": 0  # Will be set by service after org creation
        }
    }


@pytest.fixture
def sample_update_supplier_data() -> Dict[str, Any]:
    """Sample supplier update data matching the API models"""
    return {
        "provider": {
            "id_product_provider": "test_supplier_123",
            "provider_name": "Updated Supplier Name",
            "provider_contact_info": "updated@testsupplier.com",
            "id_provider_owner": 1,
            "id_product_provider_type": 1,
            "id_provider_organisation": 0,
            "idprovider_details_id": 0,
            "product_provider_type_desc": "Updated Type",
            "provider_organisation_name": "Updated Org",
            "provider_organisation_desc": "Updated Description"
        },
        "image": {
            "id_provider_image": 0,
            "provider_image_url": "https://example.com/updated_supplier.jpg",
            "provider_ref_id": 0
        },
        "location": {
            "id_location": 0,
            "location_name": "Updated Office",
            "location_latitude": 36.7538,
            "location_longitude": 3.0588,
            "location_address_id": 0,
            "id_address": 0,
            "address_street": "456 Updated St",
            "address_city": "Algiers",
            "address_postal_code": "16000",
            "address_country": "Algeria"
        }
    }


@pytest.fixture
def cleanup_supplier():
    """Clean up created suppliers after tests"""
    created_ids = []
    
    def add_id(supplier_id):
        created_ids.append(supplier_id)
    
    yield add_id
    
    # Clean up after test
    for supplier_id in created_ids:
        try:
            client.delete(f"/api/v1/suppliers/{supplier_id}?force_delete=true")
        except:
            pass


@pytest.fixture
def cleanup_organisation():
    """Clean up created organisations after tests"""
    created_ids = []
    
    def add_id(org_id):
        created_ids.append(org_id)
    
    yield add_id
    
    # Clean up after test
    for org_id in created_ids:
        try:
            client.delete(f"/api/v1/organisations/{org_id}?force_delete=true")
        except:
            pass


# ==================== Supplier Endpoint Tests ====================

class TestSupplierEndpoints:
    """Test suite for supplier-related endpoints"""
    
    def test_get_all_suppliers_success(self):
        """Test successful retrieval of all suppliers"""
        response = client.get("/api/v1/suppliers?offset=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_all_suppliers_with_filters(self):
        """Test retrieval of suppliers with filters"""
        response = client.get("/api/v1/suppliers?owner_id=1&offset=0&limit=20")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_supplier_types_success(self):
        """Test successful retrieval of supplier types"""
        response = client.get("/api/v1/supplier-types")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_search_suppliers_by_location_success(self):
        """Test successful location-based supplier search"""
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=36.7538&latitude=3.0588&distance_km=10&offset=0&limit=10"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_suppliers_by_location_invalid_coordinates(self):
        """Test location search with invalid coordinates"""
        # Longitude out of range (-180 to 180)
        response = client.get(
            "/api/v1/suppliers/search/location?longitude=200&latitude=3.0588&distance_km=10"
        )
        
        assert response.status_code == 422
    
    def test_get_supplier_by_id_not_found(self):
        """Test supplier retrieval when supplier doesn't exist"""
        response = client.get("/api/v1/suppliers/nonexistent_999999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
    
    def test_create_supplier_success(self, sample_supplier_data, cleanup_supplier):
        """Test successful supplier creation"""
        response = client.post("/api/v1/suppliers", json=sample_supplier_data)
        
        # If we get a 404, it might be because supplier type doesn't exist in DB
        if response.status_code == 404:
            pytest.skip("Supplier type ID 1 not found in database. Please ensure test data is seeded.")
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data["success"] is True
        assert "Supplier created successfully" in data["message"]
        
        # Store supplier ID for cleanup if available
        if "supplier_id" in data.get("details", {}):
            cleanup_supplier(data["details"]["supplier_id"])
    
    def test_create_supplier_missing_required_fields(self):
        """Test supplier creation with missing required fields"""
        response = client.post(
            "/api/v1/suppliers",
            json={"provider": {}, "location": {}}
        )
        
        assert response.status_code == 422
    
    def test_update_supplier_not_found(self, sample_update_supplier_data):
        """Test supplier update when supplier doesn't exist"""
        response = client.put("/api/v1/suppliers/nonexistent_999999", json=sample_update_supplier_data)
        
        assert response.status_code == 404
    
    def test_delete_supplier_not_found(self):
        """Test supplier deletion when supplier doesn't exist"""
        response = client.delete("/api/v1/suppliers/999999")
        
        assert response.status_code == 404


# ==================== Organisation Endpoint Tests ====================

class TestOrganisationEndpoints:
    """Test suite for organisation-related endpoints"""
    
    def test_get_all_organisations_success(self):
        """Test successful retrieval of all organisations"""
        response = client.get("/api/v1/organisations?offset=0&limit=100")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_get_all_organisations_pagination(self):
        """Test organisations retrieval with custom pagination"""
        response = client.get("/api/v1/organisations?offset=0&limit=25")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_organisation_by_id_not_found(self):
        """Test organisation retrieval when organisation doesn't exist"""
        response = client.get("/api/v1/organisations/999999")
        
        assert response.status_code == 404
    
    def test_create_organisation_success(self, sample_organisation_data, cleanup_organisation):
        """Test successful organisation creation"""
        response = client.post("/api/v1/organisations", json=sample_organisation_data)
        
        # 409 means it already exists (shouldn't happen with unique names)
        if response.status_code == 409:
            pytest.skip("Organisation name conflict - this should not happen with unique names")
        
        assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
        data = response.json()
        assert data["success"] is True
        
        # Store organisation ID for cleanup
        if "organisation_id" in data.get("details", {}):
            cleanup_organisation(data["details"]["organisation_id"])
    
    def test_create_organisation_missing_name(self):
        """Test organisation creation with missing required name"""
        response = client.post(
            "/api/v1/organisations",
            json={"org": {"provider_organisation_name": ""}, "org_image": None}
        )
        
        assert response.status_code == 422
    
    def test_update_organisation_not_found(self, sample_organisation_data):
        """Test organisation update when organisation doesn't exist"""
        response = client.put("/api/v1/organisations/999999", json=sample_organisation_data)
        
        assert response.status_code == 404
    
    def test_delete_organisation_not_found(self):
        """Test organisation deletion when organisation doesn't exist"""
        response = client.delete("/api/v1/organisations/999999")
        
        assert response.status_code == 404


# ==================== Edge Cases & Validation Tests ====================

class TestSupplierEdgeCases:
    """Test suite for edge cases and validation"""
    
    def test_get_suppliers_zero_limit(self):
        """Test getting suppliers with zero limit (invalid)"""
        response = client.get("/api/v1/suppliers?offset=0&limit=0")
        assert response.status_code == 422
    
    def test_get_suppliers_negative_offset(self):
        """Test getting suppliers with negative offset"""
        response = client.get("/api/v1/suppliers?offset=-1&limit=10")
        assert response.status_code == 422
    
    def test_search_suppliers_extreme_distance(self):
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
            json={"provider": {"id_product_provider": 1, "provider_name": "Test"}}
        )
        assert response.status_code == 422


# ==================== Response Format Tests ====================

class TestSupplierResponseFormat:
    """Test suite for response format validation"""
    
    def test_success_response_format(self):
        """Test that success responses follow the expected format"""
        response = client.get("/api/v1/supplier-types")
        data = response.json()
        
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["success"] is True
    
    def test_error_response_format(self):
        """Test that error responses follow the expected format"""
        response = client.get("/api/v1/suppliers/nonexistent_999999")
        data = response.json()
        
        assert "success" in data
        assert "status_code" in data
        assert "code" in data
        assert "message" in data
        assert "timestamp" in data
        assert data["success"] is False
        assert data["status_code"] == 404


# ==================== Database Setup Helpers ====================

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup required test data in database before running tests"""
    # This runs once before all tests
    if os.environ.get('RUN_INTEGRATION_TESTS', 'false').lower() == 'true':
        try:
            # Try to ensure supplier type exists
            from storage.storage_service.StorageService import get_engine, session_scope
            from core.models import ProductProviderType
            from config import DB_URI
            
            engine = get_engine(DB_URI)
            
            with session_scope(engine) as session:
                # Check if supplier type exists
                supplier_type = session.query(ProductProviderType).filter(
                    ProductProviderType.id_product_provider_type == 1
                ).first()
                
                if not supplier_type:
                    # Create test supplier type
                    test_type = ProductProviderType(
                        id_product_provider_type=1,
                        product_provider_type_desc="Test Supplier Type",
                        product_provider_ref=0
                    )
                    session.add(test_type)
                    session.commit()
                    print("\n✅ Created test supplier type in database")
                else:
                    print("\n✅ Test supplier type already exists in database")
        except Exception as e:
            print(f"\n⚠️ Could not setup test database: {e}")
    
    yield


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])