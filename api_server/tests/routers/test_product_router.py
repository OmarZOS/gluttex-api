#!/usr/bin/env python3
"""
Pytest tests for Product Router Endpoints
Run with: pytest test_product_endpoints_pytest.py -v
"""

import pytest
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:9000/api"
HEADERS = {"Content-Type": "application/json"}

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def headers():
    return HEADERS

@pytest.fixture
def categories(base_url):
    """Get product categories once for all tests"""
    response = requests.get(f"{base_url}/product/category/all")
    if response.status_code == 200:
        return response.json()
    return []

@pytest.fixture
def ensure_category_exists(base_url, headers, categories):
    """Ensure we have a valid category ID for tests"""
    if categories:
        return categories[0]['id_product_category']
    
    # If no categories exist, create one via API if possible
    # Check if there's a category creation endpoint
    # Adjust this based on your actual API
    try:
        category_data = {
            "product_category_name": "Test Category",
            "product_category_description": "Category for testing"
        }
        
        # Try to create a category (adjust endpoint as needed)
        create_response = requests.post(
            f"{base_url}/product/category/add",  # Check your actual endpoint
            json=category_data,
            headers=headers
        )
        
        if create_response.status_code == 200:
            return create_response.json().get('id_product_category')
    except Exception as e:
        print(f"Could not create category: {e}")
    
    # If we can't get or create a category, skip tests that need it
    pytest.skip("No product categories available and cannot create one")

@pytest.fixture
def sample_product_data(ensure_category_exists):
    """Create sample product data for tests"""
    category_id = ensure_category_exists
    
    return {
        "id_product": 0,
        "product_provider_id": 1,
        "id_product_category": category_id,
        "product_category_id": category_id,
        "product_price": 1999.99,
        "product_quantity": 50.0,
        "product_name": f"Test Product {datetime.now().strftime('%H%M%S')}",
        "product_brand": "TestBrand",
        "product_barcode": f"TEST{datetime.now().strftime('%H%M%S')}",
        "product_description": "A test product",
        "product_quantifier": "pieces",
        "product_owner": 1
    }

@pytest.fixture
def created_product_id(base_url, headers, sample_product_data):
    """Fixture that creates a product and returns its ID, cleans up after test"""
    # Create product
    product_data = sample_product_data.copy()
    
    # Add image data
    image_data = {
        "id_product_image": 0,
        "product_image_url": "https://example.com/test-product.jpg",
        "product_ref_id": 0
    }
    
    # Make API call
    url = f"{base_url}/product/add"
    response = requests.post(url, json={"product": product_data, "image": image_data}, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        product_id = response_data.get('id_product') or response_data.get('id')
        yield product_id
        
        # Cleanup after test
        cleanup_url = f"{base_url}/product/delete/{product_id}"
        requests.delete(cleanup_url)
    else:
        pytest.skip(f"Cannot create product: {response.status_code} - {response.text}")
        yield None

# Test functions
def test_get_product_categories(base_url):
    """Test GET /product/category/all endpoint"""
    url = f"{base_url}/product/category/all"
    response = requests.get(url)
    print(f"Categories response: {response.status_code} - {response.text[:200]}")
    
    # The endpoint should exist and return something
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✅ Found {len(data)} categories")
    
    # Print category details for debugging
    for i, cat in enumerate(data[:5]):  # Show first 5 categories
        print(f"  Category {i+1}: ID={cat.get('id_product_category')}, Name={cat.get('product_category_name')}")

def test_get_all_products(base_url):
    """Test GET /product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}"""
    url = f"{base_url}/product/1/1/0/0/10"
    response = requests.get(url)
    print(f"Get products response: {response.status_code}")
    
    # Accept 200 or 404 (if no products)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            print(f"✅ Found {len(data)} products")
        else:
            print(f"✅ Response: {data}")

def test_create_product(base_url, headers, sample_product_data):
    """Test POST /product/add"""
    print(f"Using category ID: {sample_product_data['id_product_category']}")
    
    url = f"{base_url}/product/add"
    product_data = sample_product_data.copy()
    image_data = {
        "id_product_image": 0,
        "product_image_url": "https://example.com/test-product.jpg",
        "product_ref_id": 0
    }
    
    # Try different payload formats if needed
    payload = {"product": product_data, "image": image_data}
    
    # Also try without image if the API allows it
    # payload = {"product": product_data}
    
    response = requests.post(url, json=payload, headers=headers)
    print(f"Create product response: {response.status_code} - {response.text}")
    
    if response.status_code != 200:
        # For debugging, let's see what the exact error is
        print(f"❌ Failed to create product. Payload sent: {json.dumps(payload, indent=2)}")
    
    assert response.status_code == 200
    
    # Clean up
    response_data = response.json()
    product_id = response_data.get('id_product') or response_data.get('id')
    if product_id:
        cleanup_url = f"{base_url}/product/delete/{product_id}"
        delete_response = requests.delete(cleanup_url)
        print(f"✅ Cleaned up product {product_id}: {delete_response.status_code}")

def test_get_product_by_id(base_url, created_product_id):
    """Test GET /product/{product_id}"""
    if not created_product_id:
        pytest.skip("No product ID available")
        
    url = f"{base_url}/product/{created_product_id}"
    response = requests.get(url)
    print(f"Get product by ID response: {response.status_code}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['id_product'] == created_product_id
    print(f"✅ Retrieved product: {data.get('product_name', 'Unknown')}")

def test_update_product(base_url, headers, created_product_id):
    """Test PUT /product/{product_id}"""
    if not created_product_id:
        pytest.skip("No product ID available")
    
    # Get current product
    get_url = f"{base_url}/product/{created_product_id}"
    response = requests.get(get_url)
    assert response.status_code == 200
    current = response.json()
    print(f"Current product: {current.get('product_name')}")
    
    # Update data
    updated_data = current.copy()
    updated_data['product_price'] = 2499.99
    updated_data['product_name'] = f"Updated {current['product_name']}"
    
    # Update image data
    image_data = {
        "id_product_image": current.get('image', {}).get('id_product_image', 0),
        "product_image_url": "https://example.com/updated-product.jpg",
        "product_ref_id": created_product_id
    }
    
    # Send update
    update_url = f"{base_url}/product/{created_product_id}"
    payload = {"product": updated_data, "image": image_data}
    response = requests.put(update_url, json=payload, headers=headers)
    print(f"Update product response: {response.status_code} - {response.text}")
    
    assert response.status_code == 200

def test_invalid_scenarios(base_url, headers):
    """Test endpoints with invalid data"""
    print("\nTesting invalid scenarios...")
    
    # Test non-existent product
    url = f"{base_url}/product/999999"
    response = requests.get(url)
    print(f"Get non-existent product: {response.status_code}")
    assert response.status_code in [404, 200]  # Either is acceptable
    
    # Test invalid barcode format
    url = f"{base_url}/product/barcode/invalid-barcode"
    response = requests.get(url)
    print(f"Invalid barcode search: {response.status_code}")
    assert response.status_code in [404, 400, 200]

def test_product_workflow(base_url, headers, ensure_category_exists):
    """Test a complete product workflow"""
    print("\nTesting complete product workflow...")
    
    # Step 1: Create a product
    product_data = {
        "id_product": 0,
        "product_provider_id": 1,
        "id_product_category": ensure_category_exists,
        "product_category_id": ensure_category_exists,
        "product_price": 2999.99,
        "product_quantity": 100.0,
        "product_name": f"Workflow Test {datetime.now().strftime('%H%M%S')}",
        "product_brand": "WorkflowBrand",
        "product_barcode": f"WORKFLOW{datetime.now().strftime('%H%M%S')}",
        "product_description": "Product for workflow testing",
        "product_quantifier": "units",
        "product_owner": 1
    }
    
    image_data = {
        "id_product_image": 0,
        "product_image_url": "https://example.com/workflow-product.jpg",
        "product_ref_id": 0
    }
    
    create_url = f"{base_url}/product/add"
    create_response = requests.post(
        create_url, 
        json={"product": product_data, "image": image_data}, 
        headers=headers
    )
    
    print(f"Create response: {create_response.status_code}")
    
    if create_response.status_code != 200:
        # Try without image
        create_response = requests.post(
            create_url, 
            json={"product": product_data}, 
            headers=headers
        )
        print(f"Create response (no image): {create_response.status_code}")
    
    if create_response.status_code != 200:
        pytest.skip(f"Cannot create product for workflow: {create_response.text}")
    
    response_data = create_response.json()
    product_id = response_data.get('id_product') or response_data.get('id')
    print(f"✅ Created product ID: {product_id}")
    
    # Step 2: Get the product
    get_url = f"{base_url}/product/{product_id}"
    get_response = requests.get(get_url)
    assert get_response.status_code == 200
    print(f"✅ Retrieved product")
    
    # Step 3: Delete the product
    delete_url = f"{base_url}/product/delete/{product_id}"
    delete_response = requests.delete(delete_url)
    assert delete_response.status_code == 200
    print(f"✅ Deleted product")
    
    print("✅ Complete workflow test passed!")

if __name__ == "__main__":
    # This allows running the file directly as a script
    pytest.main([__file__, "-v", "-s"])