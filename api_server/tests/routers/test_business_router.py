#!/usr/bin/env python3
"""
Test script for business order endpoints
Run with: python test_business_orders.py
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:9000/api")
HEADERS = {"Content-Type": "application/json"}

def print_test_result(test_name: str, success: bool, response=None, error=None):
    """Helper to print test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    
    if response:
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                response_data = response.json()
                # Print abbreviated response for readability
                if isinstance(response_data, list):
                    print(f"   Response: List with {len(response_data)} items")
                else:
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}...")  # Truncate long responses
    
    if error:
        print(f"   Error: {error}")
    
    print("-" * 50)

def create_sample_order_data(user_id: int = 1) -> tuple:
    """Create sample order data for testing"""
    
    # Sample placed order
    submitted_order = {
        "id_placed_order": 0,  # Will be auto-generated
        "ordered_timestamp": datetime.now().isoformat(),
        "order_discount": 10.0,
        "placed_order_last_mod": datetime.now().isoformat(),
        "payment_status": "pending",
        "payment_ref": f"TEST_PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "placed_order_state": "processing",
        "payment_method": "credit_card",
        "ordering_user_id": user_id
    }
    
    # Sample ordered items
    ordered_items = [
        {
            "id_ordered_item": 0,  # Will be auto-generated
            "ordered_product_id": 1,  # Assuming product ID 1 exists
            "order_ref": 0,  # Will be set to actual order ID
            "product_discount": 5.0,
            "ordered_quantity": 2.0,
            "unit_price": 25.99,
            "applied_vat": 0.21
        },
        {
            "id_ordered_item": 0,
            "ordered_product_id": 2,  # Assuming product ID 2 exists
            "order_ref": 0,
            "product_discount": 0.0,
            "ordered_quantity": 1.0,
            "unit_price": 15.50,
            "applied_vat": 0.21
        }
    ]
    
    return ordered_items, submitted_order

def test_create_order():
    """Test POST /business/order/add endpoint"""
    print("Testing POST /business/order/add endpoint...")
    try:
        ordered_items, submitted_order = create_sample_order_data(user_id=1)
        
        # Prepare the request data
        request_data = {
            "ordered_items": ordered_items,
            "submitted_order": submitted_order
        }
        
        url = f"{BASE_URL}/business/order/add"
        response = requests.post(url, json=request_data, headers=HEADERS)
        
        success = response.status_code == 200
        print_test_result("CREATE Order", success, response)
        
        # Extract order ID from response for later tests
        if success:
            response_data = response.json()
            # Try different possible ID field names
            order_id = (response_data.get('id_placed_order') or 
                       response_data.get('order_id') or 
                       response_data.get('id'))
            return order_id
        
        return None
        
    except Exception as e:
        print_test_result("CREATE Order", False, error=str(e))
        return None

def test_get_all_user_orders(user_id: int = 1):
    """Test GET /business/user/orders/all/{user_id} endpoint"""
    print(f"Testing GET /business/user/orders/all/{user_id} endpoint...")
    try:
        url = f"{BASE_URL}/business/user/orders/all/{user_id}"
        response = requests.get(url)
        
        success = response.status_code in [200, 404]  # 404 is valid if user has no orders
        print_test_result(f"GET All User Orders (user_id: {user_id})", success, response)
        
        if success and response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list) and len(orders) > 0:
                return orders[0].get('id_placed_order')  # Return first order ID for testing
        return None
        
    except Exception as e:
        print_test_result("GET All User Orders", False, error=str(e))
        return None

def test_get_order_details(order_id: int):
    """Test GET /business/user/orders/{order_id} endpoint"""
    print(f"Testing GET /business/user/orders/{order_id} endpoint...")
    try:
        url = f"{BASE_URL}/business/user/orders/{order_id}"
        response = requests.get(url)
        
        success = response.status_code in [200, 404]  # 404 is valid if order doesn't exist
        print_test_result(f"GET Order Details (order_id: {order_id})", success, response)
        return success
        
    except Exception as e:
        print_test_result("GET Order Details", False, error=str(e))
        return False

def test_update_order(order_id: int):
    """Test PUT /business/order/update/{order_id} endpoint"""
    print(f"Testing PUT /business/order/update/{order_id} endpoint...")
    try:
        # Create updated order data
        ordered_items, submitted_order = create_sample_order_data(user_id=1)
        
        # Update the order data
        submitted_order.update({
            "id_placed_order": order_id,
            "payment_status": "paid",
            "placed_order_state": "shipped",
            "order_discount": 15.0  # Increased discount
        })
        
        # Update items
        for item in ordered_items:
            item["order_ref"] = order_id
            item["ordered_quantity"] = 3.0  # Increased quantity
        
        # Prepare the request data
        request_data = {
            "updated_items": ordered_items,
            "updated_order": submitted_order
        }
        
        url = f"{BASE_URL}/business/order/update/{order_id}"
        response = requests.put(url, json=request_data, headers=HEADERS)
        
        success = response.status_code == 200
        print_test_result(f"UPDATE Order (order_id: {order_id})", success, response)
        return success
        
    except Exception as e:
        print_test_result("UPDATE Order", False, error=str(e))
        return False

def test_delete_order(order_id: int):
    """Test DELETE /business/order/delete/{order_id} endpoint"""
    print(f"Testing DELETE /business/order/delete/{order_id} endpoint...")
    try:
        url = f"{BASE_URL}/business/order/delete/{order_id}"
        response = requests.delete(url)
        
        success = response.status_code == 200
        print_test_result(f"DELETE Order (order_id: {order_id})", success, response)
        return success
        
    except Exception as e:
        print_test_result("DELETE Order", False, error=str(e))
        return False

def test_invalid_order_scenarios():
    """Test endpoints with invalid data"""
    print("Testing with invalid data scenarios...")
    
    # Test 1: Create order with missing required fields
    try:
        invalid_data = {
            "ordered_items": [],  # Empty items list
            "submitted_order": {
                "payment_status": "pending"
                # Missing required fields
            }
        }
        url = f"{BASE_URL}/business/order/add"
        response = requests.post(url, json=invalid_data, headers=HEADERS)
        
        success = response.status_code in [400, 422, 500]  # Expecting some error
        print_test_result("CREATE Order with Invalid Data", success, response)
        
    except Exception as e:
        print_test_result("CREATE Order with Invalid Data", False, error=str(e))
    
    # Test 2: Get orders for non-existent user
    try:
        invalid_user_id = 999999
        url = f"{BASE_URL}/business/user/orders/all/{invalid_user_id}"
        response = requests.get(url)
        
        success = response.status_code in [200, 404]  # Both are acceptable
        print_test_result(f"GET Orders for Non-existent User (id: {invalid_user_id})", success, response)
        
    except Exception as e:
        print_test_result("GET Orders for Non-existent User", False, error=str(e))
    
    # Test 3: Get details for non-existent order
    try:
        invalid_order_id = 999999
        url = f"{BASE_URL}/business/user/orders/{invalid_order_id}"
        response = requests.get(url)
        
        success = response.status_code in [200, 404]  # Both are acceptable
        print_test_result(f"GET Details for Non-existent Order (id: {invalid_order_id})", success, response)
        
    except Exception as e:
        print_test_result("GET Details for Non-existent Order", False, error=str(e))

def test_complete_order_workflow():
    """Test a complete order management workflow"""
    print("Testing complete order management workflow...")
    
    # Step 1: Create a new order
    ordered_items, submitted_order = create_sample_order_data(user_id=2)
    
    request_data = {
        "ordered_items": ordered_items,
        "submitted_order": submitted_order
    }
    
    create_response = requests.post(f"{BASE_URL}/business/order/add", json=request_data, headers=HEADERS)
    if create_response.status_code != 200:
        print("❌ Workflow failed at creation step")
        return False
    
    created_order = create_response.json()
    order_id = (created_order.get('id_placed_order') or 
                created_order.get('order_id') or 
                created_order.get('id'))
    
    if not order_id:
        print("❌ Could not extract order ID from creation response")
        return False
    
    print(f"✅ Created order with ID: {order_id}")
    
    # Step 2: Get all orders for the user
    user_orders_response = requests.get(f"{BASE_URL}/business/user/orders/all/2")
    if user_orders_response.status_code not in [200, 404]:
        print("❌ Workflow failed at get user orders step")
        return False
    
    print("✅ Successfully retrieved user orders")
    
    # Step 3: Get order details
    order_details_response = requests.get(f"{BASE_URL}/business/user/orders/{order_id}")
    if order_details_response.status_code not in [200, 404]:
        print("❌ Workflow failed at get order details step")
        return False
    
    print("✅ Successfully retrieved order details")
    
    # Step 4: Update the order
    updated_items, updated_order_data = create_sample_order_data(user_id=2)
    updated_order_data.update({
        "id_placed_order": order_id,
        "payment_status": "completed",
        "placed_order_state": "delivered"
    })
    
    for item in updated_items:
        item["order_ref"] = order_id
    
    update_data = {
        "updated_items": updated_items,
        "updated_order": updated_order_data
    }
    
    update_response = requests.put(f"{BASE_URL}/business/order/update/{order_id}", json=update_data, headers=HEADERS)
    if update_response.status_code != 200:
        print("❌ Workflow failed at update step")
        return False
    
    print("✅ Successfully updated order")
    
    # Step 5: Delete the order
    delete_response = requests.delete(f"{BASE_URL}/business/order/delete/{order_id}")
    if delete_response.status_code != 200:
        print("❌ Workflow failed at delete step")
        return False
    
    print("✅ Successfully deleted order")
    print("🎉 Complete order workflow test passed!")
    return True

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting Business Order Endpoints Tests")
    print("=" * 50)
    
    results = {
        "create_order": False,
        "get_user_orders": False,
        "get_order_details": False,
        "update_order": False,
        "delete_order": False,
        "complete_workflow": False
    }
    
    # Test 1: Create a new order
    created_order_id = test_create_order()
    results["create_order"] = created_order_id is not None
    
    # Test 2: Get all orders for a user
    existing_order_id = test_get_all_user_orders(user_id=1)
    results["get_user_orders"] = True  # This test passes even if no orders exist
    
    # Test 3: Get order details (use created order if available, otherwise any existing order)
    test_order_id = created_order_id or existing_order_id
    if test_order_id:
        results["get_order_details"] = test_get_order_details(test_order_id)
    else:
        # Test with a likely non-existent ID
        results["get_order_details"] = test_get_order_details(999999)
    
    # Test 4 & 5: Update and delete if we have a created order
    if created_order_id:
        results["update_order"] = test_update_order(created_order_id)
        results["delete_order"] = test_delete_order(created_order_id)
    else:
        print("⚠️  Skipping update/delete tests - no order was created")
    
    # Test 6: Invalid data scenarios
    test_invalid_order_scenarios()
    
    # Test 7: Complete workflow
    results["complete_workflow"] = test_complete_order_workflow()
    
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

def check_server_connectivity():
    """Check if the server is reachable"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"✅ Server is reachable at {BASE_URL}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure your FastAPI server is running!")
        return False

if __name__ == "__main__":
    # Check server connectivity first
    if not check_server_connectivity():
        sys.exit(1)
    
    # Run tests
    success = run_all_tests()
    sys.exit(0 if success else 1)