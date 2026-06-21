#!/usr/bin/env python3
"""
Auth Server Local Test Script
Tests all endpoints of the authentication server locally.
Run with: python test_auth_server.py
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class AuthServerTester:
    """Test suite for Auth Server endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:9090"):
        self.base_url = base_url
        self.client = None
        self.test_results = []
        self.test_user = None
        self.test_token = None
        self.created_user_id = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Print test result with color"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if details:
            print(f"     {details}")
        self.test_results.append({"name": test_name, "passed": passed, "details": details})
    
    async def test_health_check(self):
        """Test health/metrics endpoint"""
        print("\n📊 Testing Health/Metrics Endpoint...")
        try:
            response = await self.client.get(f"{self.base_url}/metrics")
            passed = response.status_code == 200
            self.print_result(
                "Health Check", 
                passed, 
                f"Status: {response.status_code}" if not passed else "Service is healthy"
            )
            return passed
        except Exception as e:
            self.print_result("Health Check", False, str(e))
            return False
    
    async def test_register_user(self):
        """Test user registration"""
        print("\n📝 Testing User Registration...")
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "app_user_id": int(str(uuid.uuid4().int)[:8]),
            "phone_number": "+1234567890",
            "gender": "male",
            "roles": "user"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/register",
                json=user_data
            )
            
            passed = response.status_code == 200
            if passed:
                self.test_user = user_data
                result = response.json()
                self.created_user_id = result.get("id")
                self.test_user["id"] = self.created_user_id
                details = f"User '{user_data['username']}' created (ID: {self.created_user_id})"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("User Registration", passed, details)
            return passed
        except Exception as e:
            self.print_result("User Registration", False, str(e))
            return False
    
    async def test_register_duplicate_user(self):
        """Test registration with duplicate username"""
        print("\n🔁 Testing Duplicate Registration...")
        if not self.test_user:
            print("     ⚠️  No test user available, skipping test")
            return False
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/register",
                json=self.test_user
            )
            
            # Should fail with 409 Conflict or 422 Validation Error
            passed = response.status_code in [409, 422]
            self.print_result(
                "Duplicate Registration", 
                passed, 
                f"Correctly rejected duplicate user (Status: {response.status_code})"
            )
            return passed
        except Exception as e:
            self.print_result("Duplicate Registration", False, str(e))
            return False
    
    async def test_login(self):
        """Test user login"""
        print("\n🔐 Testing Login...")
        if not self.test_user:
            print("     ⚠️  No test user available, skipping test")
            return False
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],
            "grant_type": "password",
            "scope": ""
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                data=login_data,  # Form data
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            passed = response.status_code == 200
            if passed:
                result = response.json()
                self.test_token = result.get("access_token")
                details = f"Token obtained (expires in {result.get('expires_in', 0)}s)"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("Login", passed, details)
            return passed
        except Exception as e:
            self.print_result("Login", False, str(e))
            return False
    
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        print("\n❌ Testing Invalid Login...")
        if not self.test_user:
            print("     ⚠️  No test user available, skipping test")
            return False
        
        login_data = {
            "username": self.test_user["username"],
            "password": "WrongPassword123!",
            "grant_type": "password",
            "scope": ""
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            passed = response.status_code in [401, 403]
            self.print_result(
                "Invalid Login", 
                passed, 
                f"Correctly rejected invalid credentials (Status: {response.status_code})"
            )
            return passed
        except Exception as e:
            self.print_result("Invalid Login", False, str(e))
            return False
    
    async def test_get_current_user(self):
        """Test getting current user info"""
        print("\n👤 Testing Get Current User...")
        if not self.test_token:
            print("     ⚠️  No token available, skipping test")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/auth/users/me/",
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            passed = response.status_code == 200
            if passed:
                result = response.json()
                details = f"User: {result.get('username')} (ID: {result.get('id')})"
            else:
                details = f"Status: {response.status_code}"
            
            self.print_result("Get Current User", passed, details)
            return passed
        except Exception as e:
            self.print_result("Get Current User", False, str(e))
            return False
    
    async def test_change_password(self):
        """Test password change"""
        print("\n🔑 Testing Password Change...")
        if not self.test_token or not self.test_user:
            print("     ⚠️  No token or user available, skipping test")
            return False
        
        new_password = "NewPassword456!"
        update_data = {
            "username": self.test_user["username"],
            "app_user_id": self.test_user["app_user_id"],
            "new_password": new_password
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/change-password",
                json=update_data,
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            passed = response.status_code == 200
            if passed:
                result = response.json()
                details = f"Password changed for user: {result.get('username')}"
                # Store new password for later tests
                self.test_user["password"] = new_password
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("Change Password", passed, details)
            return passed
        except Exception as e:
            self.print_result("Change Password", False, str(e))
            return False
    
    async def test_login_after_password_change(self):
        """Test login with new password"""
        print("\n🔐 Testing Login After Password Change...")
        if not self.test_user:
            print("     ⚠️  No test user available, skipping test")
            return False
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],  # New password
            "grant_type": "password",
            "scope": ""
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            passed = response.status_code == 200
            if passed:
                result = response.json()
                new_token = result.get("access_token")
                details = "Successfully logged in with new password"
            else:
                details = f"Status: {response.status_code}"
            
            self.print_result("Login After Password Change", passed, details)
            return passed
        except Exception as e:
            self.print_result("Login After Password Change", False, str(e))
            return False
    
    async def test_delete_user(self):
        """Test user deletion"""
        print("\n🗑️  Testing User Deletion...")
        if not self.test_token or not self.test_user:
            print("     ⚠️  No token or user available, skipping test")
            return False
        
        delete_data = {
            "username": self.test_user["username"],
            "app_user_id": self.test_user["app_user_id"]
        }
        
        try:
            response = await self.client.request(
                method="DELETE",
                url=f"{self.base_url}/auth/delete-user",
                json=delete_data,
                headers={"Authorization": f"Bearer {self.test_token}"}
            )
            
            passed = response.status_code == 200
            if passed:
                details = f"User '{self.test_user['username']}' deleted successfully"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("Delete User", passed, details)
            return passed
        except Exception as e:
            self.print_result("Delete User", False, str(e))
            return False
    
    async def test_delete_already_deleted_user(self):
        """Test login after deletion (should fail)"""
        print("\n🧪 Testing Login After Deletion...")
        if not self.test_user:
            print("     ⚠️  No test user available, skipping test")
            return False
        
        login_data = {
            "username": self.test_user["username"],
            "password": self.test_user["password"],
            "grant_type": "password",
            "scope": ""
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Should fail with 401 or 403
            passed = response.status_code in [401, 403, 404]
            self.print_result(
                "Login After Deletion",
                passed,
                f"Correctly rejected deleted user (Status: {response.status_code})"
            )
            return passed
        except Exception as e:
            self.print_result("Login After Deletion", False, str(e))
            return False
    
    async def test_missing_fields_validation(self):
        """Test registration with missing required fields"""
        print("\n🔍 Testing Validation (Missing Fields)...")
        invalid_user = {
            "username": "testuser2",
            # Missing app_user_id and password (required)
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/register",
                json=invalid_user
            )
            
            passed = response.status_code == 422
            self.print_result(
                "Validation - Missing Fields",
                passed,
                f"Correctly rejected invalid request (Status: {response.status_code})"
            )
            return passed
        except Exception as e:
            self.print_result("Validation - Missing Fields", False, str(e))
            return False
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*60)
        print("🚀 STARTING AUTH SERVER TESTS")
        print("="*60)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Test 1: Health Check
        await self.test_health_check()
        
        # Test 2: Registration
        registration_success = await self.test_register_user()
        if not registration_success:
            print("\n⚠️  Registration failed, skipping dependent tests")
        
        # Test 3: Duplicate Registration (only if registration succeeded)
        if registration_success:
            await self.test_register_duplicate_user()
            
            # Test 4: Login
            login_success = await self.test_login()
            
            if login_success:
                # Test 5: Get Current User
                await self.test_get_current_user()
                
                # Test 6: Invalid Login
                await self.test_login_invalid_credentials()
                
                # Test 7: Change Password
                password_change_success = await self.test_change_password()
                
                if password_change_success:
                    # Test 8: Login After Password Change
                    await self.test_login_after_password_change()
                
                # Test 9: Delete User
                delete_success = await self.test_delete_user()
                
                if delete_success:
                    # Test 10: Login After Deletion
                    await self.test_delete_already_deleted_user()
            else:
                print("\n⚠️  Login failed, skipping user-specific tests")
        
        # Test 11: Validation (independent of registration)
        await self.test_missing_fields_validation()
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        
        # Print detailed results
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['name']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print("="*60)
        print(f"📈 Total: {total} tests")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Auth server is working correctly.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the output above.")
        
        print("="*60)


async def main():
    """Main entry point"""
    # Parse command line arguments for custom URL
    base_url = "http://localhost:9090"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    async with AuthServerTester(base_url) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        sys.exit(1)