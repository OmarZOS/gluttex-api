#!/usr/bin/env python3
"""
Test script for Product Router Endpoints
Run with: python test_product_endpoints.py
"""

import requests
import json
import sys
import asyncio
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:9000/api"  # Change to your server URL
HEADERS = {"Content-Type": "application/json"}

def print_test_result(test_name, success, response=None, error=None):
    """Helper to print test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    
    if response:
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                response_data = response.json()
                if isinstance(response_data, list) and len(response_data) > 3:
                    print(f"   Response: List with {len(response_data)} items")
                else:
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
            except:
                print(f"   Response: {response.text}")
    
    if error:
        print(f"   Error: {error}")
    
    print("-" * 50)

def test_get_product_categories():
    """Test GET /product/category/all endpoint"""
    print("Testing GET /product/category/all...")
    try:
        url = f"{BASE_URL}/product/category/all"
        response = requests.get(url)
        
        success = response.status_code == 200
        print_test_result("Get Product Categories", success, response)
        return success
        
    except Exception as e:
        print_test_result("Get Product Categories", False, error=str(e))
        return False

def test_get_all_products():
    """Test GET /product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}"""
    print("Testing GET /product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}...")
    try:
        # Test with various parameters
        test_cases = [
            (1, 1, 0, 0, 10),   # user_id=1, provider_id=1, category_id=0 (all), offset=0, limit=10
            (1, 1, 1, 0, 5),    # Specific category
            (1, 1, 0, 10, 10),  # With offset
        ]
        
        for user_id, provider_id, category_id, offset, limit in test_cases:
            url = f"{BASE_URL}/product/{user_id}/{provider_id}/{category_id}/{offset}/{limit}"
            response = requests.get(url)
            
            success = response.status_code in [200, 404]  # 404 if no products
            test_name = f"Get Products (user={user_id}, provider={provider_id}, category={category_id})"
            print_test_result(test_name, success, response)
            
            if success and response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    return products[0].get('id_product')  # Return first product ID
        
        return None
        
    except Exception as e:
        print_test_result("Get All Products", False, error=str(e))
        return None

def test_get_products_by_category():
    """Test GET /product/category/{category_id}/{offset}/{limit}"""
    print("Testing GET /product/category/{category_id}/{offset}/{limit}...")
    try:
        url = f"{BASE_URL}/product/category/1/0/10"  # category_id=1, offset=0, limit=10
        response = requests.get(url)
        
        success = response.status_code in [200, 404]
        print_test_result("Get Products by Category", success, response)
        return success
        
    except Exception as e:
        print_test_result("Get Products by Category", False, error=str(e))
        return False

def test_get_product_by_id(product_id):
    """Test GET /product/{product_id}"""
    print(f"Testing GET /product/{product_id}...")
    try:
        url = f"{BASE_URL}/product/{product_id}"
        response = requests.get(url)
        
        success = response.status_code in [200, 404]
        print_test_result("Get Product by ID", success, response)
        return success
        
    except Exception as e:
        print_test_result("Get Product by ID", False, error=str(e))
        return False

def test_get_product_image():
    """Test GET /image/product/{image_id}"""
    print("Testing GET /image/product/{image_id}...")
    try:
        url = f"{BASE_URL}/image/product/1"  # Test with image ID 1
        response = requests.get(url)
        
        success = response.status_code in [200, 404]
        print_test_result("Get Product Image", success, response)
        return success
        
    except Exception as e:
        print_test_result("Get Product Image", False, error=str(e))
        return False

# def test_barcode_search():
#     """Test GET /product/barcode/{barcode}"""
#     print("Testing GET /product/barcode/{barcode}...")
#     try:
#         # Test with some common barcodes
#         test_barcodes = [
#             "1234567890123",  # Generic test barcode
#             "978020137962",   # ISBN-like
#             "4006381333931",  # Real product barcode format
#         ]
        
#         for barcode in test_barcodes:
#             url = f"{BASE_URL}/product/barcode/{barcode}"
#             response = requests.get(url)
            
#             success = response.status_code in [200, 404]
#             source = "unknown"
#             if success and response.status_code == 200:
#                 data = response.json()
#                 source = data.get('source', 'unknown')
            
#             test_name = f"Barcode Search: {barcode} (source: {source})"
#             print_test_result(test_name, success, response)
            
#             # If we found a product in DB, return its ID
#             if success and source == "database":
#                 product_data = data.get('data', {})
#                 if isinstance(product_data, list) and len(product_data) > 0:
#                     return product_data[0].get('id_product')
#                 elif isinstance(product_data, dict):
#                     return product_data.get('id_product')
        
#         return None
        
#     except Exception as e:
#         print_test_result("Barcode Search", False, error=str(e))
#         return None

def test_create_product():
    """Test POST /product/add"""
    print("Testing POST /product/add...")
    try:
        # Get categories first
        categories_response = requests.get(f"{BASE_URL}/product/category/all")
        categories = categories_response.json() if categories_response.status_code == 200 else []
        
        # Create product data
        product_data = {
            "id_product": 0,  # Auto-generated
            "product_provider_id": 1,
            "id_product_category": categories[0]['id_product_category'] if categories else 1,
            "product_category_id": categories[0]['id_product_category'] if categories else 1,
            "product_price": 1999.99,
            "product_quantity": 50.0,
            "product_name": f"Test Product {datetime.now().strftime('%H%M%S')}",
            "product_brand": "TestBrand",
            "product_barcode": f"TEST{datetime.now().strftime('%H%M%S')}",
            "product_description": "A test product created via API",
            "product_quantifier": "pieces",
            "product_owner": 1
        }
        
        # Create image data
        image_data = {
            "id_product_image": 0,
            "product_image_url": "https://example.com/test-product.jpg",
            "product_ref_id": 0
        }
        
        # Create iproduct data (AI-generated product info)
        iproduct_data = {
            "id_iproduct": 0,
            "iproduct_name": product_data["product_name"],
            "iproduct_barcode": product_data["product_barcode"],
            "iproduct_brand": product_data["product_brand"],
            "iproduct_estimated_price": product_data["product_price"],
            "iproduct_price_currency": "DZD",
            "iproduct_gluten_status": "gluten_free",
            "iproduct_info_source": "test",
            "iproduct_info_confidence": 0.95,
            "iproduct_last_price_update": datetime.now().isoformat(),
            "iproduct_created_at": datetime.now().isoformat(),
            "iproduct_last_update": datetime.now().isoformat(),
            "iproduct_model_name": "test_model",
            "iproduct_image_url": image_data["product_image_url"]
        }
        
        payload = {
            "product": product_data,
            "image": image_data,
            "iproduct": iproduct_data
        }
        
        url = f"{BASE_URL}/product/add"
        response = requests.post(url, json=payload, headers=HEADERS)
        
        success = response.status_code == 200
        print_test_result("Create Product", success, response)
        
        # Return created product ID
        if success and response.json():
            response_data = response.json()
            product_id = response_data.get('id_product') or response_data.get('id')
            return product_id
        
        return None
        
    except Exception as e:
        print_test_result("Create Product", False, error=str(e))
        return None

def test_update_product(product_id):
    """Test PUT /product/{product_id}"""
    print(f"Testing PUT /product/{product_id}...")
    try:
        # Get current product first
        current_response = requests.get(f"{BASE_URL}/product/{product_id}")
        if current_response.status_code != 200:
            print("   Could not fetch current product for update")
            return False
        
        current_product = current_response.json()
        
        # Update product data
        product_data = {
            "id_product": product_id,
            "product_provider_id": current_product.get('product_provider_id', 1),
            "id_product_category": current_product.get('id_product_category', 1),
            "product_category_id": current_product.get('product_category_id', 1),
            "product_price": 2499.99,  # Updated price
            "product_quantity": 25.0,  # Updated quantity
            "product_name": f"Updated {current_product.get('product_name', 'Test Product')}",
            "product_brand": current_product.get('product_brand', 'TestBrand'),
            "product_barcode": current_product.get('product_barcode', ''),
            "product_description": f"Updated description - {datetime.now().isoformat()}",
            "product_quantifier": current_product.get('product_quantifier', 'pieces'),
            "product_owner": current_product.get('product_owner', 1)
        }
        
        # Update image data
        image_data = {
            "id_product_image": current_product.get('image', {}).get('id_product_image', 0),
            "product_image_url": "https://example.com/updated-product.jpg",
            "product_ref_id": product_id
        }
        
        payload = {
            "product": product_data,
            "image": image_data
        }
        
        url = f"{BASE_URL}/product/{product_id}"
        response = requests.put(url, json=payload, headers=HEADERS)
        
        success = response.status_code == 200
        print_test_result("Update Product", success, response)
        return success
        
    except Exception as e:
        print_test_result("Update Product", False, error=str(e))
        return False

def test_delete_product(product_id):
    """Test DELETE /product/delete/{product_id}"""
    print(f"Testing DELETE /product/delete/{product_id}...")
    try:
        url = f"{BASE_URL}/product/delete/{product_id}"
        response = requests.delete(url)
        
        success = response.status_code == 200
        print_test_result("Delete Product", success, response)
        return success
        
    except Exception as e:
        print_test_result("Delete Product", False, error=str(e))
        return False

def test_image_search():
    """Test POST /product/search/image"""
    print("Testing POST /product/search/image...")
    try:
        # Note: This is a simplified test since we can't easily upload real images
        # In a real scenario, you'd need to create a test image file
        
        # For now, we'll test the endpoint with a dummy file upload
        # This might fail, but we're testing the endpoint availability
        
        url = f"{BASE_URL}/product/search/image"
        
        # Create a simple text file as a dummy (this will likely fail but tests the endpoint)
        files = {'file': ('test.jpg', b'fake image content', 'image/jpeg')}
        
        try:
            response = requests.post(url, files=files)
            success = response.status_code in [200, 400, 422]  # Various possible responses
            print_test_result("Image Search", success, response)
            return success
        except Exception as upload_error:
            # Endpoint might not handle the fake image well
            print_test_result("Image Search", False, error=f"Upload failed: {upload_error}")
            return False
        
    except Exception as e:
        print_test_result("Image Search", False, error=str(e))
        return False

def test_sse_endpoint():
    """Test GET /products/observer/{product_id} (SSE endpoint)"""
    print("Testing GET /products/observer/{product_id} (SSE)...")
    try:
        # This is a simplified test for SSE endpoints
        # In practice, you'd need proper async handling for SSE
        
        url = f"{BASE_URL}/products/observer/1"  # Test with product ID 1
        
        # Make a quick request to check if endpoint exists
        # Note: SSE endpoints typically don't return immediately
        response = requests.get(url, timeout=2)  # Short timeout
        
        # SSE endpoints might return 200 with streaming response
        success = response.status_code in [200, 404]
        print_test_result("SSE Product Updates", success, response)
        return success
        
    except requests.exceptions.Timeout:
        # Timeout is expected for SSE endpoints
        print_test_result("SSE Product Updates", True, error="Timeout expected for SSE")
        return True
    except Exception as e:
        print_test_result("SSE Product Updates", False, error=str(e))
        return False

def test_invalid_scenarios():
    """Test endpoints with invalid data"""
    print("Testing invalid scenarios...")
    
    # Test 1: Get product with invalid ID
    try:
        url = f"{BASE_URL}/product/999999"
        response = requests.get(url)
        success = response.status_code in [200, 404]
        print_test_result("Get Non-existent Product", success, response)
    except Exception as e:
        print_test_result("Get Non-existent Product", False, error=str(e))
    
    # Test 2: Create product with missing required fields
    try:
        invalid_product = {
            "product_name": "Incomplete Product"
            # Missing required fields
        }
        url = f"{BASE_URL}/product/add"
        response = requests.post(url, json={"product": invalid_product}, headers=HEADERS)
        success = response.status_code in [400, 422]
        print_test_result("Create Product with Invalid Data", success, response)
    except Exception as e:
        print_test_result("Create Product with Invalid Data", False, error=str(e))
    
    # Test 3: Barcode search with invalid format
    try:
        url = f"{BASE_URL}/product/barcode/invalid-barcode"
        response = requests.get(url)
        success = response.status_code in [200, 404, 400]
        print_test_result("Barcode Search with Invalid Format", success, response)
    except Exception as e:
        print_test_result("Barcode Search with Invalid Format", False, error=str(e))

def test_complete_workflow():
    """Test complete product management workflow"""
    print("Testing complete product management workflow...")
    
    # Step 1: Get categories
    categories_response = requests.get(f"{BASE_URL}/product/category/all")
    if categories_response.status_code != 200:
        print("❌ Need product categories to test workflow")
        return False
    
    categories = categories_response.json()
    
    # Step 2: Create a new product
    product_data = {
        "id_product": 0,
        "product_provider_id": 1,
        "id_product_category": categories[0]['id_product_category'],
        "product_category_id": categories[0]['id_product_category'],
        "product_price": 2999.99,
        "product_quantity": 100.0,
        "product_name": f"Workflow Test Product {datetime.now().strftime('%H%M%S')}",
        "product_brand": "WorkflowBrand",
        "product_barcode": f"WORKFLOW{datetime.now().strftime('%H%M%S')}",
        "product_description": "Product created for workflow testing",
        "product_quantifier": "units",
        "product_owner": 1
    }
    
    image_data = {
        "id_product_image": 0,
        "product_image_url": "https://example.com/workflow-product.jpg",
        "product_ref_id": 0
    }
    
    iproduct_data = {
        "id_iproduct": 0,
        "iproduct_name": product_data["product_name"],
        "iproduct_barcode": product_data["product_barcode"],
        "iproduct_brand": product_data["product_brand"],
        "iproduct_estimated_price": product_data["product_price"],
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "unknown",
        "iproduct_info_source": "workflow_test",
        "iproduct_info_confidence": 0.90,
        "iproduct_last_price_update": datetime.now().isoformat(),
        "iproduct_created_at": datetime.now().isoformat(),
        "iproduct_last_update": datetime.now().isoformat(),
        "iproduct_model_name": "workflow_model",
        "iproduct_image_url": image_data["product_image_url"]
    }
    
    create_response = requests.post(
        f"{BASE_URL}/product/add",
        json={
            "product": product_data,
            "image": image_data,
            "iproduct": iproduct_data
        },
        headers=HEADERS
    )
    
    if create_response.status_code != 200:
        print("❌ Workflow failed at creation step")
        return False
    
    created_product = create_response.json()
    product_id = created_product.get('id_product') or created_product.get('id')
    
    if not product_id:
        print("❌ Could not extract product ID from creation response")
        return False
    
    print(f"✅ Created product with ID: {product_id}")
    
    # Step 3: Verify product was created
    get_response = requests.get(f"{BASE_URL}/product/{product_id}")
    if get_response.status_code != 200:
        print("❌ Workflow failed at get product step")
        return False
    
    print("✅ Successfully retrieved created product")
    
    # Step 4: Search by barcode (should find our product)
    barcode_response = requests.get(f"{BASE_URL}/product/barcode/{product_data['product_barcode']}")
    if barcode_response.status_code == 200:
        barcode_data = barcode_response.json()
        if barcode_data.get('source') == 'database':
            print("✅ Product found in database via barcode search")
        else:
            print("⚠️  Product not found in database via barcode (might be expected)")
    
    # Step 5: Update the product
    product_data['id_product'] = product_id
    product_data['product_price'] = 3499.99  # Updated price
    product_data['product_name'] = f"Updated Workflow Product {datetime.now().strftime('%H%M%S')}"
    image_data['product_ref_id'] = product_id
    
    update_response = requests.put(
        f"{BASE_URL}/product/{product_id}",
        json={"product": product_data, "image": image_data},
        headers=HEADERS
    )
    
    if update_response.status_code != 200:
        print("❌ Workflow failed at update step")
        return False
    
    print("✅ Successfully updated product")
    
    # Step 6: Delete the product
    delete_response = requests.delete(f"{BASE_URL}/product/delete/{product_id}")
    if delete_response.status_code != 200:
        print("❌ Workflow failed at delete step")
        return False
    
    print("✅ Successfully deleted product")
    print("🎉 Complete product workflow test passed!")
    return True

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting Product Endpoints Tests")
    print("=" * 50)
    
    results = {
        "get_categories": False,
        "get_all_products": False,
        "get_products_by_category": False,
        "get_product_by_id": False,
        "get_product_image": False,
        "barcode_search": False,
        "image_search": False,
        "sse_endpoint": False,
        "create_product": False,
        "update_product": False,
        "delete_product": False,
        "complete_workflow": False
    }
    
    # Test 1: Get product categories
    results["get_categories"] = test_get_product_categories()
    
    # Test 2: Get all products
    existing_product_id = test_get_all_products()
    results["get_all_products"] = existing_product_id is not None
    
    # Test 3: Get products by category
    results["get_products_by_category"] = test_get_products_by_category()
    
    # Test 4: Get specific product by ID
    if existing_product_id:
        results["get_product_by_id"] = test_get_product_by_id(existing_product_id)
    
    # Test 5: Get product image
    results["get_product_image"] = test_get_product_image()
    
    # Test 6: Barcode search
    barcode_product_id = test_barcode_search()
    results["barcode_search"] = barcode_product_id is not None
    
    # Test 7: Image search
    results["image_search"] = test_image_search()
    
    # Test 8: SSE endpoint
    results["sse_endpoint"] = test_sse_endpoint()
    
    # Test 9: Create product
    created_product_id = test_create_product()
    results["create_product"] = created_product_id is not None
    
    # Test 10: Update product
    if created_product_id:
        results["update_product"] = test_update_product(created_product_id)
    
    # Test 11: Delete product
    if created_product_id:
        results["delete_product"] = test_delete_product(created_product_id)
    
    # Test 12: Invalid scenarios
    test_invalid_scenarios()
    
    # Test 13: Complete workflow
    results["complete_workflow"] = test_complete_workflow()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    # Check if server is reachable
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Server is reachable at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure your FastAPI server is running!")
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)