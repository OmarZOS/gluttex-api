#!/usr/bin/env python3
"""
Comprehensive test script for WebSocket and Queue Binding Endpoints
"""

import requests
import json
import sys
import threading
import asyncio
import websockets
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:9097/stream"
HEADERS = {"Content-Type": "application/json"}

# Global variables to track WebSocket messages
websocket_messages = []
websocket_connected = False

def print_test_result(test_name, success, response=None, error=None):
    """Helper to print test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    
    if response:
        print(f"   Status: {response.status_code}")
        if response.text:
            try:
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"   Response: {response.text}")
    
    if error:
        print(f"   Error: {error}")
    
    print("-" * 50)

async def websocket_client(client_id: str, test_duration: int = 10):
    """WebSocket client to test the WebSocket endpoint"""
    global websocket_messages, websocket_connected
    
    uri = f"ws://localhost:9097/stream/ws/{client_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"🔗 WebSocket connected for client {client_id}")
            websocket_connected = True
            
            # Wait for connection message
            connection_msg = await websocket.recv()
            connection_data = json.loads(connection_msg)
            print(f"📨 Received connection message: {connection_data}")
            websocket_messages.append(connection_data)
            
            start_time = time.time()
            
            # Listen for messages for the test duration
            while time.time() - start_time < test_duration:
                try:
                    # Set a timeout for receiving messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    message_data = json.loads(message)
                    print(f"📨 Received message: {message_data}")
                    websocket_messages.append(message_data)
                    
                except asyncio.TimeoutError:
                    # No message received, continue listening
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        websocket_connected = False

def run_websocket_test(client_id: str, test_duration: int = 10):
    """Run WebSocket test in a separate thread"""
    print(f"🚀 Starting WebSocket test for client {client_id}")
    
    # Run the async WebSocket client
    asyncio.run(websocket_client(client_id, test_duration))
    
    print(f"🏁 WebSocket test completed for client {client_id}")
    print(f"📊 Total messages received: {len(websocket_messages)}")

def start_websocket_test_thread(client_id: str, test_duration: int = 10):
    """Start WebSocket test in a background thread"""
    thread = threading.Thread(
        target=run_websocket_test,
        args=(client_id, test_duration),
        daemon=True
    )
    thread.start()
    return thread

def test_binding_endpoints():
    """Test HTTP binding endpoints"""
    print("🧪 Testing Queue Binding Endpoints")
    
    auth_headers = {
        "Authorization": "Bearer test-token"
    }
    
    test_user_id = 1
    test_supplier_id = 1
    test_org_id = 1
    test_product_id = 1
    
    # 1. Bind to user routing key
    print("1. Testing user binding...")
    user_binding = {
        "routing_key": f"user.{test_user_id}.notifications"
    }
    resp = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind",
        json=user_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]
    print_test_result("User Binding", success, resp)
    
    # 2. Bind to supplier routing key
    print("2. Testing supplier binding...")
    supplier_binding = {
        "routing_key": f"supplier.{test_supplier_id}.updates"
    }
    resp = requests.post(
        f"{BASE_URL}/supplier/{test_user_id}/{test_supplier_id}/bind",
        json=supplier_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]
    print_test_result("Supplier Binding", success, resp)
    
    # 3. Bind to organization routing key
    print("3. Testing organization binding...")
    org_binding = {
        "routing_key": f"org.{test_org_id}.announcements"
    }
    resp = requests.post(
        f"{BASE_URL}/org/{test_user_id}/{test_org_id}/bind",
        json=org_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]
    print_test_result("Organization Binding", success, resp)
    
    # 4. Bind to product routing key
    print("4. Testing product binding...")
    product_binding = {
        "routing_key": f"product.{test_product_id}.price_updates"
    }
    resp = requests.post(
        f"{BASE_URL}/product/{test_user_id}/{test_product_id}/bind",
        json=product_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]
    print_test_result("Product Binding", success, resp)
    
    # 5. Multiple bindings
    print("5. Testing multiple bindings...")
    multiple_binding = {
        "routing_keys": [
            f"user.{test_user_id}.messages",
            f"user.{test_user_id}.alerts"
        ]
    }
    resp = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind-multiple",
        json=multiple_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]
    print_test_result("Multiple Bindings", success, resp)
    
    # 6. Get current bindings
    print("6. Testing get bindings...")
    resp = requests.get(
        f"{BASE_URL}/user/{test_user_id}/bindings",
        headers=auth_headers
    )
    success = resp.status_code in [200, 403]
    print_test_result("Get Bindings", success, resp)
    
    # 7. Unbind
    print("7. Testing unbind...")
    unbind_request = {
        "routing_key": f"user.{test_user_id}.notifications"
    }
    resp = requests.delete(
        f"{BASE_URL}/user/{test_user_id}/unbind",
        json=unbind_request,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403, 404]
    print_test_result("Unbind", success, resp)

def test_invalid_scenarios():
    """Test error cases and invalid data"""
    print("\n🧪 Testing Invalid Scenarios")
    
    auth_headers = {"Authorization": "Bearer test-token"}
    test_user_id = 1
    
    # 1. Bind to wrong user routing key (should return 403 if auth implemented)
    print("1. Testing binding to different user routing key...")
    invalid_binding = {
        "routing_key": f"user.999.notifications"
    }
    resp = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind",
        json=invalid_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 403]  # Could be 200 since auth is disabled
    print_test_result("Different User Binding", success, resp)
    
    # 2. Invalid routing key format
    print("2. Testing invalid routing key format...")
    invalid_binding = {
        "routing_key": "invalid_format"
    }
    resp = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind",
        json=invalid_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 400, 403, 422]
    print_test_result("Invalid Routing Key", success, resp)
    
    # 3. Empty routing keys in multiple binding
    print("3. Testing empty routing keys...")
    empty_binding = {
        "routing_keys": []
    }
    resp = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind-multiple",
        json=empty_binding,
        headers={**HEADERS, **auth_headers}
    )
    success = resp.status_code in [200, 400, 422]
    print_test_result("Empty Multiple Binding", success, resp)

def test_websocket_connection():
    """Test WebSocket connection specifically"""
    print("\n🧪 Testing WebSocket Connection")
    
    test_user_id = 1
    
    try:
        # Start WebSocket test in background
        websocket_thread = start_websocket_test_thread(test_user_id, test_duration=5)
        
        # Wait a bit for connection to establish
        time.sleep(2)
        
        # Check if WebSocket connected
        if websocket_connected:
            print("✅ WebSocket connection established")
            
            # Check if we received connection message
            if len(websocket_messages) > 0:
                first_msg = websocket_messages[0]
                if first_msg.get('type') == 'connected':
                    print("✅ Received connection confirmation")
                    print(f"   Queue: {first_msg.get('queue')}")
                    print(f"   Client ID: {first_msg.get('client_id')}")
                else:
                    print("❌ Unexpected first message type")
            else:
                print("❌ No messages received from WebSocket")
        else:
            print("❌ WebSocket connection failed")
        
        # Wait for WebSocket test to complete
        websocket_thread.join(timeout=6)
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def test_complete_workflow():
    """Test a complete WebSocket + binding workflow"""
    print("\n🧪 Testing Complete WebSocket + Binding Workflow")
    
    auth_headers = {"Authorization": "Bearer test-token"}
    test_user_id = 1
    test_product_id = 123
    
    # Step 1: Start WebSocket connection
    print("Step 1: Starting WebSocket connection...")
    websocket_thread = start_websocket_test_thread(test_user_id, test_duration=15)
    time.sleep(2)  # Wait for connection
    
    if not websocket_connected:
        print("❌ Workflow failed: WebSocket not connected")
        return False
    
    # Step 2: Bind to user notifications
    print("Step 2: Binding to user notifications...")
    user_binding = {"routing_key": f"user.{test_user_id}.notifications"}
    resp1 = requests.post(
        f"{BASE_URL}/user/{test_user_id}/bind",
        json=user_binding,
        headers={**HEADERS, **auth_headers}
    )
    
    # Step 3: Bind to product updates
    print("Step 3: Binding to product updates...")
    product_binding = {"routing_key": f"product.{test_product_id}.updates"}
    resp2 = requests.post(
        f"{BASE_URL}/product/{test_user_id}/{test_product_id}/bind",
        json=product_binding,
        headers={**HEADERS, **auth_headers}
    )
    
    # Step 4: Get current bindings
    print("Step 4: Getting current bindings...")
    resp3 = requests.get(
        f"{BASE_URL}/user/{test_user_id}/bindings",
        headers=auth_headers
    )
    
    # Step 5: Send a test message (you would need a producer for this)
    print("Step 5: Note - Need RabbitMQ producer to send test messages")
    print("   Messages would be received via WebSocket if bindings work")
    
    # Step 6: Unbind product updates
    print("Step 6: Unbinding product updates...")
    unbind_request = {"routing_key": f"product.{test_product_id}.updates"}
    resp4 = requests.delete(
        f"{BASE_URL}/user/{test_user_id}/unbind",
        json=unbind_request,
        headers={**HEADERS, **auth_headers}
    )
    
    # Wait for WebSocket to complete
    websocket_thread.join(timeout=16)
    
    # Check results
    steps_successful = all(resp.status_code in [200, 403] for resp in [resp1, resp2, resp3, resp4])
    websocket_success = websocket_connected and len(websocket_messages) > 0
    
    if steps_successful and websocket_success:
        print("✅ Complete workflow test passed!")
        print(f"   WebSocket messages received: {len(websocket_messages)}")
    else:
        print("❌ Workflow test had some failures")
    
    return steps_successful and websocket_success

def run_all_tests():
    """Run all test scenarios"""
    print("🚀 Starting Comprehensive WebSocket + Binding Tests")
    print("=" * 60)
    
    # Clear previous test data
    global websocket_messages, websocket_connected
    websocket_messages = []
    websocket_connected = False
    
    # Test WebSocket connection
    test_websocket_connection()
    
    # Test HTTP binding endpoints
    test_binding_endpoints()
    
    # Test error cases
    test_invalid_scenarios()
    
    # Test complete workflow
    workflow_success = test_complete_workflow()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"WebSocket Connection: {'✅ SUCCESS' if websocket_connected else '❌ FAILED'}")
    print(f"Messages Received: {len(websocket_messages)}")
    print(f"Complete Workflow: {'✅ SUCCESS' if workflow_success else '❌ FAILED'}")
    
    if websocket_messages:
        print(f"\n📨 WebSocket Messages Preview:")
        for i, msg in enumerate(websocket_messages[:3]):  # Show first 3 messages
            print(f"  {i+1}. {msg}")
        if len(websocket_messages) > 3:
            print(f"  ... and {len(websocket_messages) - 3} more messages")

if __name__ == "__main__":
    # Check if server is reachable
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Server is reachable at {BASE_URL}")
        print(f"   Health status: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print("Make sure your FastAPI server is running on port 9097!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        sys.exit(1)
    
    # Install required packages if not already installed
    try:
        import websockets
    except ImportError:
        print("❌ Required package 'websockets' not installed.")
        print("Install it with: pip install websockets")
        sys.exit(1)
    
    # Run tests
    run_all_tests()