#!/usr/bin/env python3
"""
Staff/Rule Router Test Script
Reads users from the test context file and tests staff/rule endpoints.
Run with: python test_staff_rules.py
"""

import asyncio
import httpx
import json
import sys
import random
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import argparse


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for the staff/rule tester"""
    BASE_URL = "http://localhost:9000"
    CONTEXT_FILE = "test_context.json"
    
    # Realistic rule codes (role IDs)
    RULE_CODES = [27, 60, 45, 12, 33, 78, 91, 56, 23, 67]
    
    # Rule statuses matching database
    RULE_STATUSES = ["PENDING", "ACTIVE", "REJECTED", "EXPIRED"]
    
    # Rate limiting
    DELAY_BETWEEN_REQUESTS = 0.3


# ============================================================================
# STAFF/RULE TESTER
# ============================================================================

class StaffRuleTester:
    """Tests staff/rule endpoints using users from test context"""
    
    def __init__(self, base_url: str = Config.BASE_URL):
        self.base_url = base_url
        self.client = None
        self.auth_token = None
        self.user_id = None
        self.username = None
        self.context_users = []
        self.stats = {
            "tests_passed": 0,
            "tests_failed": 0,
            "rules_created": 0,
            "rules_updated": 0,
            "rules_deleted": 0,
            "invitations_answered": 0,
            "api_errors": 0
        }
        self.created_rule_ids = []
        self.results = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False, follow_redirects=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_status(self, message: str, emoji: str = "ℹ️"):
        """Print status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
    
    def print_result(self, test_name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if details:
            print(f"     {details}")
        self.results.append({"name": test_name, "passed": passed, "details": details})
        if passed:
            self.stats["tests_passed"] += 1
        else:
            self.stats["tests_failed"] += 1
    
    def load_context_users(self) -> bool:
        """Load users from the test context file"""
        context_file = Config.CONTEXT_FILE
        
        if not Path(context_file).exists():
            self.print_status(f"Context file {context_file} not found", "❌")
            return False
        
        try:
            with open(context_file, 'r') as f:
                data = json.load(f)
            
            self.context_users = data.get('users', [])
            
            # Also load created organisations and suppliers if available
            self.created_organisations = data.get('created_organisations', [])
            self.created_suppliers = data.get('created_suppliers', [])
            
            self.print_status(f"Loaded {len(self.context_users)} users from context", "📂")
            self.print_status(f"Found {len(self.created_organisations)} organisations", "🏢")
            self.print_status(f"Found {len(self.created_suppliers)} suppliers", "🏥")
            
            if self.context_users:
                for i, user in enumerate(self.context_users[:3]):
                    self.print_status(f"  User {i+1}: {user.get('username')} (ID: {user.get('id')})", "👤")
                if len(self.context_users) > 3:
                    self.print_status(f"  ... and {len(self.context_users) - 3} more", "👤")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error loading context: {e}", "❌")
            return False
    
    async def login_with_context_user(self, user_index: int = 0) -> bool:
        """Login using a user from the context"""
        if not self.context_users:
            self.print_status("No context users available", "❌")
            return False
        
        if user_index >= len(self.context_users):
            self.print_status(f"User index {user_index} out of range", "❌")
            return False
        
        user = self.context_users[user_index]
        username = user.get('username')
        password = user.get('password')
        
        self.print_status(f"Logging in as '{username}' (ID: {user.get('id')})", "🔐")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/authentication/token",
                json={
                    "app_user_name": username,
                    "app_user_password": password
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access_token')
                self.user_id = user.get('id')
                self.username = username
                self.print_status(f"✅ Login successful as {username}", "✅")
                return True
            else:
                self.print_status(f"Login failed: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.print_status(f"Login error: {e}", "❌")
            return False
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make an authenticated request with error handling"""
        if self.auth_token:
            headers = kwargs.pop('headers', {})
            headers["Authorization"] = f"Bearer {self.auth_token}"
            kwargs['headers'] = headers
        
        url = f"{self.base_url}/api/v1{endpoint}"
        
        try:
            response = await self.client.request(method, url, **kwargs)
            
            try:
                if response.content:
                    data = response.json()
                else:
                    data = None
                
                return {
                    "status": response.status_code,
                    "data": data
                }
            except json.JSONDecodeError:
                return {
                    "status": response.status_code,
                    "data": {"raw": response.text[:200] if response.text else None}
                }
        except Exception as e:
            self.print_status(f"Request error: {e}", "❌")
            self.stats["api_errors"] += 1
            return {"status": 500, "data": None, "error": str(e)}
    
    # ==================== STAFF/RULE TESTS ====================
    
    async def test_get_staff(self, org_id: int = None, provider_id: int = None) -> bool:
        """Test GET /staff - Get staff members"""
        self.print_status("Testing GET /staff", "📋")
        
        params = {"offset": 0, "limit": 50}
        if org_id:
            params["org_id"] = org_id
        if provider_id:
            params["provider_id"] = provider_id
        
        response = await self.make_request("GET", "/staff", params=params)
        
        if response["status"] == 200:
            data = response["data"]
            if data is None:
                data = []
            count = len(data) if isinstance(data, list) else 0
            self.print_status(f"Retrieved {count} staff members", "📋")
            self.print_result("GET /staff", True, f"Retrieved {count} staff members")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result("GET /staff", False, f"Status: {response['status']}")
            return False
    
    async def test_get_user_staff(self, user_id: int) -> bool:
        """Test GET /staff/user/{user_id} - Get staff assignments for a user"""
        self.print_status(f"Testing GET /staff/user/{user_id}", "📋")
        
        response = await self.make_request("GET", f"/staff/user/{user_id}")
        
        if response["status"] == 200:
            data = response["data"]
            if data is None:
                data = []
            count = len(data) if isinstance(data, list) else 0
            self.print_status(f"Retrieved {count} staff assignments for user {user_id}", "📋")
            self.print_result(f"GET /staff/user/{user_id}", True, f"Count: {count}")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"GET /staff/user/{user_id}", False, f"Status: {response['status']}")
            return False
    
    async def test_get_provider_staff(self, provider_id: int) -> bool:
        """Test GET /staff/provider/{provider_id} - Get provider staff"""
        self.print_status(f"Testing GET /staff/provider/{provider_id}", "📋")
        
        response = await self.make_request("GET", f"/staff/provider/{provider_id}", params={"active_only": True})
        
        if response["status"] == 200:
            data = response["data"]
            if data is None:
                data = []
            count = len(data) if isinstance(data, list) else 0
            self.print_status(f"Retrieved {count} staff members for provider {provider_id}", "📋")
            self.print_result(f"GET /staff/provider/{provider_id}", True, f"Count: {count}")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"GET /staff/provider/{provider_id}", False, f"Status: {response['status']}")
            return False
    
    async def test_get_pending_invitations(self, user_id: int) -> bool:
        """Test GET /staff/pending/{user_id} - Get pending invitations"""
        self.print_status(f"Testing GET /staff/pending/{user_id}", "📋")
        
        response = await self.make_request("GET", f"/staff/pending/{user_id}")
        
        if response["status"] == 200:
            data = response["data"]
            if data is None:
                data = []
            count = len(data) if isinstance(data, list) else 0
            self.print_status(f"Retrieved {count} pending invitations for user {user_id}", "📋")
            self.print_result(f"GET /staff/pending/{user_id}", True, f"Count: {count}")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"GET /staff/pending/{user_id}", False, f"Status: {response['status']}")
            return False
    
    async def test_create_staff_rule(self, org_id: int, provider_id: int, user_id: int) -> Optional[int]:
        """Test POST /staff - Create a staff assignment with realistic data"""
        self.print_status(f"Testing POST /staff", "📝")
        
        # Use realistic rule codes (role IDs)
        rule_code = random.choice(Config.RULE_CODES)
        
        rule_data = {
            "rule_ref_org": org_id,
            "rule_ref_provider": provider_id,
            "rule_ref_user": user_id,
            "management_rule_code": rule_code,
            "management_rule_status": "PENDING",
            "management_rule_expiry": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat()
        }
        
        response = await self.make_request("POST", "/staff", json=rule_data)
        
        if response["status"] == 201:
            data = response["data"]
            rule_id = None
            if data:
                rule_id = data.get('id_management_rule') or data.get('id') or data.get('staff_id')
            if rule_id:
                self.created_rule_ids.append(rule_id)
                self.stats["rules_created"] += 1
                self.print_status(f"Created staff rule: {rule_id} (role: {rule_code})", "✅")
                self.print_result("POST /staff", True, f"Rule {rule_id} created with role {rule_code}")
                return rule_id
            else:
                self.print_status("Rule created but no ID in response", "⚠️")
                self.print_result("POST /staff", True, "Rule created but ID extraction failed")
                return 0
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result("POST /staff", False, f"Status: {response['status']}")
            return None
    
    async def test_update_staff_rule(self, rule_id: int, org_id: int, provider_id: int, user_id: int) -> bool:
        """Test PUT /staff/{staff_id} - Update a staff assignment with realistic data"""
        self.print_status(f"Testing PUT /staff/{rule_id}", "✏️")
        
        # Use a different realistic role code
        rule_code = random.choice([c for c in Config.RULE_CODES if c != 27])  # Avoid same as initial
        
        update_data = {
            "rule_ref_org": org_id,
            "rule_ref_provider": provider_id,
            "rule_ref_user": user_id,
            "management_rule_code": rule_code,
            "management_rule_status": "ACTIVE",
            "management_rule_expiry": (datetime.now() + timedelta(days=random.randint(30, 60))).isoformat()
        }
        
        response = await self.make_request("PUT", f"/staff/{rule_id}", json=update_data)
        
        if response["status"] == 200:
            self.stats["rules_updated"] += 1
            self.print_status(f"Updated staff rule: {rule_id} (role: {rule_code})", "✅")
            self.print_result(f"PUT /staff/{rule_id}", True, f"Rule {rule_id} updated")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"PUT /staff/{rule_id}", False, f"Status: {response['status']}")
            return False
    
    async def test_answer_staff_invitation(self, rule_id: int, accept: bool = True) -> bool:
        """Test PUT /staff/answer/{staff_id} - Answer a staff invitation"""
        action = "accept" if accept else "reject"
        self.print_status(f"Testing PUT /staff/answer/{rule_id} ({action})", "📝")
        
        response = await self.make_request("PUT", f"/staff/answer/{rule_id}", params={"accept": str(accept).lower()})
        
        if response["status"] == 200:
            self.stats["invitations_answered"] += 1
            self.print_status(f"Staff invitation {action}ed: {rule_id}", "✅")
            self.print_result(f"PUT /staff/answer/{rule_id}", True, f"Invitation {action}ed")
            return True
        else:
            # 400 may indicate already processed - still a valid test result
            if response["status"] == 400:
                self.print_status(f"Invitation already processed: {rule_id}", "ℹ️")
                self.print_result(f"PUT /staff/answer/{rule_id}", True, "Already processed")
                return True
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"PUT /staff/answer/{rule_id}", False, f"Status: {response['status']}")
            return False
    
    async def test_delete_staff_rule(self, rule_id: int) -> bool:
        """Test DELETE /staff/delete/{staff_id} - Delete a staff assignment"""
        self.print_status(f"Testing DELETE /staff/delete/{rule_id}", "🗑️")
        
        response = await self.make_request("DELETE", f"/staff/delete/{rule_id}", params={"force_delete": "true"})
        
        if response["status"] == 204:
            self.stats["rules_deleted"] += 1
            if rule_id in self.created_rule_ids:
                self.created_rule_ids.remove(rule_id)
            self.print_status(f"Deleted staff rule: {rule_id}", "✅")
            self.print_result(f"DELETE /staff/delete/{rule_id}", True, f"Rule {rule_id} deleted")
            return True
        else:
            self.print_status(f"Failed: {response['status']}", "❌")
            self.print_result(f"DELETE /staff/delete/{rule_id}", False, f"Status: {response['status']}")
            return False
    
    # ==================== NEGATIVE TESTS ====================
    
    async def test_get_nonexistent_staff(self) -> bool:
        """Test GET /staff/user/{nonexistent} - Should return 404"""
        self.print_status("Testing GET /staff/user/999999 (should fail)", "❌")
        
        response = await self.make_request("GET", "/staff/user/999999")
        
        passed = response["status"] == 404
        self.print_status(f"Response: {response['status']}", "📊")
        self.print_result("GET /staff/user/999999", passed, f"Status: {response['status']}")
        return passed
    
    async def test_delete_nonexistent_staff(self) -> bool:
        """Test DELETE /staff/delete/{nonexistent} - Should return 404"""
        self.print_status("Testing DELETE /staff/delete/999999 (should fail)", "❌")
        
        response = await self.make_request("DELETE", "/staff/delete/999999", params={"force_delete": "true"})
        
        passed = response["status"] == 404
        self.print_status(f"Response: {response['status']}", "📊")
        self.print_result("DELETE /staff/delete/999999", passed, f"Status: {response['status']}")
        return passed
    
    # ==================== COMPLETE FLOW TEST ====================
    
    async def test_complete_rule_flow(self, user_id: int, org_id: int, provider_id: int) -> bool:
        """Test complete flow: Create → Update → Answer → Delete"""
        self.print_status("\n🔄 Testing complete rule flow", "🔄")
        print("="*70)
        
        # Step 1: Create
        rule_id = await self.test_create_staff_rule(org_id, provider_id, user_id)
        if not rule_id or rule_id == 0:
            self.print_status("❌ Complete flow failed at Create", "❌")
            return False
        
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Step 2: Get by user (verify creation)
        await self.test_get_user_staff(user_id)
        
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Step 3: Update
        update_success = await self.test_update_staff_rule(rule_id, org_id, provider_id, user_id)
        
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Step 4: Answer invitation
        if update_success:
            await self.test_answer_staff_invitation(rule_id, accept=True)
        else:
            self.print_status("Skipping answer invitation - update failed", "⚠️")
        
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Step 5: Delete
        await self.test_delete_staff_rule(rule_id)
        
        self.print_status("✅ Complete rule flow finished", "✅")
        return True
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, user_index: int = 0, org_id: int = None, provider_id: int = None):
        """Run all staff/rule tests"""
        print("\n" + "="*70)
        print("👥 STAFF/RULE ROUTER TESTER")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"📂 Context: {Config.CONTEXT_FILE}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Load context
        if not self.load_context_users():
            self.print_status("Failed to load context", "❌")
            return
        
        # Login
        if not await self.login_with_context_user(user_index):
            self.print_status("Failed to login", "❌")
            return
        
        # Determine org and provider IDs
        if org_id is None and self.created_organisations:
            org_id = self.created_organisations[0]
        elif org_id is None:
            org_id = 1
        
        if provider_id is None and self.created_suppliers:
            provider_id = self.created_suppliers[0]
        elif provider_id is None:
            provider_id = 1
        
        self.print_status(f"Using Org ID: {org_id}, Provider ID: {provider_id}", "🏢")
        
        # ==================== RUN TESTS ====================
        print("\n" + "="*70)
        print("🧪 Running Staff/Rule Tests")
        print("="*70)
        
        # List tests
        await self.test_get_staff(org_id, provider_id)
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        await self.test_get_user_staff(self.user_id)
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        await self.test_get_provider_staff(provider_id)
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        await self.test_get_pending_invitations(self.user_id)
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Negative tests
        await self.test_get_nonexistent_staff()
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        await self.test_delete_nonexistent_staff()
        await asyncio.sleep(Config.DELAY_BETWEEN_REQUESTS)
        
        # Complete flow test
        await self.test_complete_rule_flow(self.user_id, org_id, provider_id)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 STAFF/RULE TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        print("\n📈 Test Results:")
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"  {status} {result['name']}")
            if result["details"]:
                print(f"     {result['details']}")
        
        print("\n" + "="*70)
        print(f"📈 Total: {total} tests")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        print(f"\n📊 Statistics:")
        print(f"   👤 User: {self.username} (ID: {self.user_id})")
        print(f"   📋 Rules Created: {self.stats['rules_created']}")
        print(f"   ✏️ Rules Updated: {self.stats['rules_updated']}")
        print(f"   🗑️ Rules Deleted: {self.stats['rules_deleted']}")
        print(f"   📝 Invitations Answered: {self.stats['invitations_answered']}")
        
        if self.created_rule_ids:
            print(f"\n📋 Created Rule IDs: {', '.join(map(str, self.created_rule_ids))}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            print("\n💡 Common issues:")
            print("   1. Check if the staff router service is running")
            print("   2. Verify the database has proper relationships")
            print("   3. Ensure the authentication service is working")
            print("   4. Check that the user has proper permissions")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Staff/Rule Router Test Script")
    parser.add_argument("--url", default=Config.BASE_URL, help="Base URL of the API")
    parser.add_argument("--user-index", type=int, default=0, 
                       help="Index of user from context file to use (default: 0)")
    parser.add_argument("--org-id", type=int, default=None, 
                       help="Organisation ID to use (default: from context or 1)")
    parser.add_argument("--provider-id", type=int, default=None, 
                       help="Provider ID to use (default: from context or 1)")
    parser.add_argument("--context-file", default=Config.CONTEXT_FILE, 
                       help="Context file to load users from")
    parser.add_argument("--clear-context", action="store_true", 
                       help="Clear context before running")
    
    args = parser.parse_args()
    
    # Update config
    Config.CONTEXT_FILE = args.context_file
    
    # Clear context if requested
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context file")
    
    async with StaffRuleTester(args.url) as tester:
        await tester.run_tests(
            user_index=args.user_index,
            org_id=args.org_id,
            provider_id=args.provider_id
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)