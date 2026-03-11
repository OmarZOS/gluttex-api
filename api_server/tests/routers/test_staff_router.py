# #!/usr/bin/env python3
# """
# Simple script to test staff endpoints with correct ManagementRule_API model
# Run with: python test_staff_endpoints.py
# """

# import requests
# import json
# import sys
# from datetime import datetime, timedelta

# # Configuration
# BASE_URL = "http://localhost:9000/api"  # Change to your server URL
# HEADERS = {"Content-Type": "application/json"}

# def print_test_result(test_name, success, response=None, error=None):
#     """Helper to print test results"""
#     status = "✅ PASS" if success else "❌ FAIL"
#     print(f"{status} {test_name}")
    
#     if response:
#         print(f"   Status: {response.status_code}")
#         if response.text:
#             try:
#                 print(f"   Response: {json.dumps(response.json(), indent=2)}")
#             except:
#                 print(f"   Response: {response.text}")
    
#     if error:
#         print(f"   Error: {error}")
    
#     print("-" * 50)

# def test_get_staff():
#     """Test GET /staff endpoint"""
#     print("Testing GET /staff endpoint...")
#     try:
#         # Using the correct parameters from your router
#         url = f"{BASE_URL}/staff/1/1/123/1/0/10"
#         response = requests.get(url)
        
#         success = response.status_code in [200, 404]  # 404 might be valid if no data
#         print_test_result("GET Staff", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("GET Staff", False, error=str(e))
#         return False

# def test_create_staff():
#     """Test POST /staff/add endpoint"""
#     print("Testing POST /staff/add endpoint...")
#     try:
#         # Using correct field names from ManagementRule_API
#         staff_data = {
#             "id_management_rule": 0,  # Will be auto-generated probably
#             "rule_ref_org": 1,
#             "rule_ref_provider": 1,
#             "rule_ref_user": 1,  # Test user ID
#             "management_rule_code": 1,  # This is rule_id in your endpoint
#             "management_rule_status": "pending",
#             "management_rule_expiry": (datetime.now() + timedelta(days=30)).isoformat()
#         }
        
#         url = f"{BASE_URL}/staff/add"
#         response = requests.post(url, json=staff_data, headers=HEADERS)
        
#         success = response.status_code == 200
#         print_test_result("CREATE Staff", success, response)
        
#         # Return the created staff ID for later tests
#         if success and response.json():
#             response_data = response.json()
#             # Try to get the ID from different possible response formats
#             staff_id = (response_data.get('id_management_rule') or 
#                        response_data.get('id') or 
#                        response_data.get('staff_id'))
#             return staff_id
        
#         return None
        
#     except Exception as e:
#         print_test_result("CREATE Staff", False, error=str(e))
#         return None

# def test_update_staff(staff_id):
#     """Test PUT /staff/{staff_id} endpoint"""
#     print(f"Testing PUT /staff/{staff_id} endpoint...")
#     try:
#         update_data = {
#             "id_management_rule": staff_id,
#             "rule_ref_org": 1,
#             "rule_ref_provider": 1,
#             "rule_ref_user": 1,
#             "management_rule_code": 1,
#             "management_rule_status": "ACTIVE",  # Changed from pending to active
#             # "management_rule_expiry": (datetime.now() + timedelta(days=60)).isoformat()
#         }
        
#         url = f"{BASE_URL}/staff/{staff_id}"
#         response = requests.put(url, json=update_data, headers=HEADERS)
        
#         success = response.status_code == 200
#         print_test_result("UPDATE Staff", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("UPDATE Staff", False, error=str(e))
#         return False

# def test_answer_invitation(staff_id):
#     """Test PUT /rule/answer/{staff_id} endpoint"""
#     print(f"Testing PUT /rule/answer/{staff_id} endpoint...")
#     try:
#         # Test accepting invitation (answer=1)
#         url = f"{BASE_URL}/rule/answer/{staff_id}"
#         response = requests.put(url, params={"answer": 1})
        
#         success = response.status_code == 200
#         print_test_result("ANSWER Invitation (Accept)", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("ANSWER Invitation", False, error=str(e))
#         return False

# def test_delete_staff(staff_id):
#     """Test DELETE /staff/delete/{staff_id} endpoint"""
#     print(f"Testing DELETE /staff/delete/{staff_id} endpoint...")
#     try:
#         url = f"{BASE_URL}/staff/delete/{staff_id}"
#         response = requests.delete(url)
        
#         success = response.status_code == 200
#         print_test_result("DELETE Staff", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("DELETE Staff", False, error=str(e))
#         return False

# def test_invalid_data():
#     """Test endpoints with invalid data"""
#     print("Testing with invalid data...")
    
#     # Test 1: Create staff with missing required fields
#     try:
#         invalid_data = {
#             "management_rule_status": "pending"
#             # Missing required fields like rule_ref_org, rule_ref_provider, etc.
#         }
#         url = f"{BASE_URL}/staff/add"
#         response = requests.post(url, json=invalid_data, headers=HEADERS)
        
#         # Should probably return 422 (validation error) or 400
#         success = response.status_code in [400, 422]
#         print_test_result("CREATE Staff with Invalid Data", success, response)
        
#     except Exception as e:
#         print_test_result("CREATE Staff with Invalid Data", False, error=str(e))
    
#     # Test 2: Update with invalid staff ID
#     try:
#         invalid_id = "invalid_id"
#         update_data = {
#             "id_management_rule": 999999,  # Non-existent ID
#             "rule_ref_org": 1,
#             "rule_ref_provider": 1,
#             "rule_ref_user": 1,
#             "management_rule_code": 1,
#             "management_rule_status": "active"
#         }
#         url = f"{BASE_URL}/staff/{invalid_id}"
#         response = requests.put(url, json=update_data, headers=HEADERS)
        
#         # Could be 404 or 422 (validation error)
#         success = response.status_code in [200, 404, 422]
#         print_test_result("UPDATE with Invalid Staff ID", success, response)
        
#     except Exception as e:
#         print_test_result("UPDATE with Invalid Staff ID", False, error=str(e))

# def test_complete_workflow():
#     """Test a complete staff management workflow"""
#     print("Testing complete staff management workflow...")
    
#     # Step 1: Create a staff member
#     staff_data = {
#         "id_management_rule": 0,
#         "rule_ref_org": 1,
#         "rule_ref_provider": 1,
#         "rule_ref_user": 1,  # Different user ID for workflow test
#         "management_rule_code": 2,
#         "management_rule_status": "PENDING",
#         "management_rule_expiry": (datetime.now() + timedelta(days=30)).isoformat()
#     }
    
#     create_response = requests.post(f"{BASE_URL}/staff/add", json=staff_data, headers=HEADERS)
#     if create_response.status_code != 200:
#         print("❌ Workflow failed at creation step")
#         return False
    
#     created_staff = create_response.json()
#     staff_id = (created_staff.get('id_management_rule') or 
#                 created_staff.get('id') or 
#                 created_staff.get('staff_id'))
    
#     if not staff_id:
#         print("❌ Could not extract staff ID from creation response")
#         return False
    
#     print(f"✅ Created staff with ID: {staff_id}")
    
#     # Step 2: Update the staff member
#     staff_data["management_rule_status"] = "active"
#     staff_data["id_management_rule"] = staff_id
    
#     update_response = requests.put(f"{BASE_URL}/staff/{staff_id}", json=staff_data, headers=HEADERS)
#     if update_response.status_code != 200:
#         print("❌ Workflow failed at update step")
#         return False
    
#     print("✅ Successfully updated staff")
    
#     # Step 3: Answer invitation
#     answer_response = requests.put(f"{BASE_URL}/rule/answer/{staff_id}", params={"answer": 1})
#     if answer_response.status_code != 200:
#         print("❌ Workflow failed at answer invitation step")
#         return False
    
#     print("✅ Successfully answered invitation")
    
#     # Step 4: Delete the staff member
#     delete_response = requests.delete(f"{BASE_URL}/staff/delete/{staff_id}")
#     if delete_response.status_code != 200:
#         print("❌ Workflow failed at delete step")
#         return False
    
#     print("✅ Successfully deleted staff")
#     print("🎉 Complete workflow test passed!")
#     return True

# def run_all_tests():
#     """Run all test scenarios"""
#     print("🚀 Starting Staff Endpoints Tests")
#     print("=" * 50)
    
#     results = {
#         "get_staff": False,
#         "create_staff": False,
#         "update_staff": False,
#         "answer_invitation": False,
#         "delete_staff": False,
#         "complete_workflow": False
#     }
    
#     # Test 1: Get staff (should work even if no data)
#     results["get_staff"] = test_get_staff()
    
#     # Test 2: Create a new staff member
#     created_staff_id = test_create_staff()
#     results["create_staff"] = created_staff_id is not None
    
#     if created_staff_id:
#         # Test 3: Update the created staff
#         results["update_staff"] = test_update_staff(created_staff_id)
        
#         # Test 4: Answer invitation
#         results["answer_invitation"] = test_answer_invitation(created_staff_id)
        
#         # Test 5: Delete the created staff
#         results["delete_staff"] = test_delete_staff(created_staff_id)
    
#     # Test 6: Invalid data scenarios
#     test_invalid_data()
    
#     # Test 7: Complete workflow
#     results["complete_workflow"] = test_complete_workflow()
    
#     # Summary
#     print("\n📊 TEST SUMMARY")
#     print("=" * 50)
#     for test_name, passed in results.items():
#         status = "✅ PASS" if passed else "❌ FAIL"
#         print(f"{status} {test_name}")
    
#     passed_count = sum(results.values())
#     total_count = len(results)
#     print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
#     if passed_count == total_count:
#         print("🎉 All tests passed!")
#         return True
#     else:
#         print("💥 Some tests failed!")
#         return False

# if __name__ == "__main__":
#     # Check if server is reachable
#     try:
#         response = requests.get(BASE_URL, timeout=5)
#         print(f"✅ Server is reachable at {BASE_URL}")
#     except requests.exceptions.ConnectionError:
#         print(f"❌ Cannot connect to server at {BASE_URL}")
#         print("Make sure your FastAPI server is running!")
#         sys.exit(1)
    
#     # Run tests
#     success = run_all_tests()
#     sys.exit(0 if success else 1)