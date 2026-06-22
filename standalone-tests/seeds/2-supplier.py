#!/usr/bin/env python3
"""
Test script for supplier creation using existing users as owners.
Run with: python test_supplier_with_existing_users.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS (mirroring the API models)
# ============================================================================

class CountryCode(str, Enum):
    DZ = "DZ"
    US = "US"
    GB = "GB"
    FR = "FR"
    DE = "DE"
    IT = "IT"
    ES = "ES"
    CA = "CA"
    AU = "AU"
    MA = "MA"
    TN = "TN"
    EG = "EG"
    SA = "SA"
    AE = "AE"


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def generate_unique_name(prefix: str = "") -> str:
    """Generate a unique name"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def generate_unique_email() -> str:
    """Generate a unique email"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def generate_random_location_data() -> Dict[str, Any]:
    """Generate random location data"""
    cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif", "Tizi Ouzou", "Bejaia"]
    streets = ["Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre", "Rue Larbi Ben Mhidi"]
    countries = [CountryCode.DZ.value, CountryCode.FR.value, CountryCode.US.value]
    
    return {
        "id_location": 0,
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": random.choice(["Main Office", "Branch Office", "Clinic", "Headquarters", "Medical Center"]),
        "id_address": 0,
        "address_street": f"{random.randint(1, 999)} {random.choice(streets)}",
        "address_city": random.choice(cities),
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": random.choice(countries)
    }


def generate_random_organisation_data() -> Dict[str, Any]:
    """Generate random organisation data"""
    org_names = [
        "HealthCare Plus", "MediCorp", "Wellness Center", 
        "Global Health Solutions", "Premium Care", "MediServe",
        "HealthFirst", "CarePlus", "MediHealth", "WellnessWorks"
    ]
    
    return {
        "id_provider_organisation": 0,
        "provider_organisation_name": f"{random.choice(org_names)} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Leading healthcare provider specializing in {random.choice(['cardiology', 'neurology', 'pediatrics', 'orthopedics', 'general medicine'])}"
    }


def generate_random_supplier_data(org_id: int = 0, owner_id: int = 0) -> Dict[str, Any]:
    """
    Generate random supplier data with owner ID.
    """
    provider_types = [
        {"id": 1, "desc": "Restaurant"},
        {"id": 2, "desc": "Bakery"},
        {"id": 3, "desc": "Factory"},
        {"id": 4, "desc": "Supermarket"},
        {"id": 5, "desc": "Grocery Store"},
        {"id": 6, "desc": "Distributor"}
    ]
    selected_type = random.choice(provider_types)
    
    provider_names = [
        "City Medical Center", "HealthFirst Clinic", "MediLab Services", 
        "PharmaCare", "Advanced Medical Supplies", "Precision Diagnostics",
        "Wellness Medical Group", "Prime Healthcare", "Elite Medical Services"
    ]
    
    return {
        "id_product_provider": 0,
        "id_provider_owner": owner_id,  # Now using the actual user ID
        "idprovider_details_id": 0,
        "id_product_provider_type": selected_type["id"],
        "id_provider_organisation": org_id,
        "product_provider_type_desc": selected_type["desc"],
        "provider_organisation_name": f"{random.choice(provider_names)} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Provider of {random.choice(['medical', 'dental', 'diagnostic', 'pharmaceutical', 'surgical'])} services",
        "provider_name": f"Provider_{uuid.uuid4().hex[:8]}",
        "provider_contact_info": json.dumps({
            "phone": f"+213-5{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}",
            "email": generate_unique_email(),
            "website": f"https://{uuid.uuid4().hex[:8]}.com"
        })
    }


def generate_random_provider_image_data() -> Dict[str, Any]:
    """Generate random provider image data"""
    return {
        "id_provider_image": 0,
        "provider_image_url": f"https://example.com/images/provider_{uuid.uuid4().hex[:8]}.jpg",
        "provider_ref_id": 0
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class SupplierTesterWithUsers:
    """Test runner that fetches existing users and uses them as owners"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.results = []
        self.existing_users = []
        self.existing_organisations = []
        self.created_organisations = []
        self.created_suppliers = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_result(self, test_name: str, passed: bool, details: str = "", response_data: Any = None):
        """Print test result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if details:
            print(f"     {details}")
        if response_data:
            try:
                response_str = json.dumps(response_data, indent=2, default=str)[:500]
                print(f"     Response: {response_str}")
            except:
                print(f"     Response: {response_data}")
        self.results.append({"name": test_name, "passed": passed, "details": details})
    
    # ==================== Data Fetching ====================
    
    async def fetch_existing_users(self) -> List[Dict[str, Any]]:
        """Fetch all existing users"""
        print("\n📋 Fetching existing users...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/app_user",
                params={"offset": 0, "limit": 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, list):
                    users = data
                elif isinstance(data, dict) and "data" in data:
                    users = data["data"]
                elif isinstance(data, dict) and "items" in data:
                    users = data["items"]
                elif isinstance(data, dict) and "result" in data:
                    users = data["result"]
                else:
                    users = []
                
                self.existing_users = users
                print(f"   Found {len(users)} existing users")
                
                # Display users with their IDs
                for i, user in enumerate(users[:10]):  # Show first 10
                    user_id = user.get('id_app_user', user.get('id', 'N/A'))
                    user_name = user.get('app_user_name', user.get('username', 'Unknown'))
                    user_email = user.get('app_user_email', user.get('email', 'N/A'))
                    print(f"     {i+1}. ID: {user_id}, Name: {user_name}, Email: {user_email}")
                
                if len(users) > 10:
                    print(f"     ... and {len(users) - 10} more")
                
                # Store user IDs for later use
                self.user_ids = [u.get('id_app_user', u.get('id', 0)) for u in users if u.get('id_app_user') or u.get('id')]
                print(f"   Available user IDs: {self.user_ids[:10]}{'...' if len(self.user_ids) > 10 else ''}")
                
                return users
            else:
                print(f"   Failed to fetch users: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"   Error fetching users: {e}")
            return []
    
    async def fetch_existing_organisations(self) -> List[Dict[str, Any]]:
        """Fetch all existing organisations"""
        print("\n📋 Fetching existing organisations...")
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/organisations",
                params={"offset": 0, "limit": 500}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle different response formats
                if isinstance(data, list):
                    organisations = data
                elif isinstance(data, dict) and "data" in data:
                    organisations = data["data"]
                elif isinstance(data, dict) and "items" in data:
                    organisations = data["items"]
                else:
                    organisations = []
                
                self.existing_organisations = organisations
                print(f"   Found {len(organisations)} existing organisations")
                for i, org in enumerate(organisations[:10]):  # Show first 10
                    org_id = org.get('idprovider_organisation', org.get('id', 'N/A'))
                    org_name = org.get('provider_organisation_name', 'Unknown')
                    print(f"     {i+1}. ID: {org_id}, Name: {org_name}")
                if len(organisations) > 10:
                    print(f"     ... and {len(organisations) - 10} more")
                return organisations
            else:
                print(f"   Failed to fetch organisations: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"   Error fetching organisations: {e}")
            return []
    
    # ==================== Organisation Tests ====================
    
    async def test_create_organisation(self) -> Optional[int]:
        """Test creating an organisation and return its ID"""
        print("\n🏢 Test: Create Organisation")
        
        org_data = generate_random_organisation_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/organisations",
                json={"organisation": org_data}
            )
            
            passed = response.status_code == 201
            if passed:
                result = response.json()
                self.created_organisations.append(result)
                org_id = result.get('idprovider_organisation', 0)
                details = f"Organisation '{org_data['provider_organisation_name']}' created with ID: {org_id}"
                self.print_result("Create Organisation", passed, details, result)
                return org_id
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                self.print_result("Create Organisation", passed, details)
                return None
            
        except Exception as e:
            self.print_result("Create Organisation", False, str(e))
            return None
    
    # ==================== Supplier Tests with User Owners ====================
    
    async def test_create_supplier_with_user_owner(self, user_id: int, org_id: int = 0):
        """
        Test creating a supplier with a specific user as owner.
        
        Args:
            user_id: The ID of the user to set as owner
            org_id: The ID of the organisation (0 = create new)
        """
        print(f"\n🏥 Test: Create Supplier with User Owner (User ID: {user_id})")
        
        # If no organisation provided, create one
        if org_id == 0:
            print("   Creating new organisation...")
            new_org_id = await self.test_create_organisation()
            if not new_org_id:
                self.print_result("Create Supplier with User Owner", False, "Failed to create organisation")
                return False
            org_id = new_org_id
        
        # Get user name for display
        user_name = "Unknown"
        for user in self.existing_users:
            uid = user.get('id_app_user', user.get('id', 0))
            if uid == user_id:
                user_name = user.get('app_user_name', user.get('username', 'Unknown'))
                break
        
        # Create supplier with the user as owner
        supplier_data = generate_random_supplier_data(org_id, user_id)
        location_data = generate_random_location_data()
        
        print(f"   Using organisation ID: {org_id}")
        print(f"   Using owner ID: {user_id} ({user_name})")
        print(f"   Supplier name: {supplier_data['provider_name']}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/suppliers",
                json={
                    "provider": supplier_data,
                    "location": location_data
                }
            )
            
            passed = response.status_code == 201
            if passed:
                result = response.json()
                self.created_suppliers.append(result)
                details = f"Supplier '{supplier_data['provider_name']}' created with owner '{user_name}' (ID: {user_id})"
                self.print_result(f"Create Supplier (Owner: {user_name})", passed, details, result)
                return True
            else:
                details = f"Status: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f", Error: {error_data.get('message', response.text[:100])}"
                    except:
                        details += f", Response: {response.text[:200]}"
                self.print_result(f"Create Supplier (Owner: {user_name})", passed, details)
                return False
            
        except Exception as e:
            self.print_result(f"Create Supplier (Owner: {user_name})", False, str(e))
            return False
    
    async def test_create_suppliers_for_all_users(self, org_id: int = 0):
        """Test creating suppliers for all existing users"""
        print("\n👥 Test: Create Suppliers for All Users")
        
        if not self.existing_users:
            print("   No existing users found. Skipping test.")
            self.print_result("Create Suppliers for All Users", False, "No users available")
            return False
        
        # If no organisation provided, create one
        if org_id == 0:
            print("   Creating new organisation...")
            new_org_id = await self.test_create_organisation()
            if not new_org_id:
                self.print_result("Create Suppliers for All Users", False, "Failed to create organisation")
                return False
            org_id = new_org_id
        
        success_count = 0
        total_count = min(len(self.existing_users), 5)  # Limit to first 5 users
        
        print(f"   Creating suppliers for {total_count} users (organisation ID: {org_id})")
        
        for i, user in enumerate(self.existing_users[:total_count]):
            user_id = user.get('id_app_user', user.get('id', 0))
            user_name = user.get('app_user_name', user.get('username', 'Unknown'))
            
            if user_id == 0:
                print(f"     {i+1}. ⏭️ Skipping user with invalid ID: {user_name}")
                continue
            
            supplier_data = generate_random_supplier_data(org_id, user_id)
            supplier_data["provider_name"] = f"{user_name}_Provider_{uuid.uuid4().hex[:4]}"
            location_data = generate_random_location_data()
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/suppliers",
                    json={
                        "provider": supplier_data,
                        "location": location_data
                    }
                )
                
                if response.status_code == 201:
                    success_count += 1
                    self.created_suppliers.append(response.json())
                    print(f"     {i+1}. ✅ Created for user: {user_name} (ID: {user_id})")
                else:
                    print(f"     {i+1}. ❌ Failed for user: {user_name} (ID: {user_id}) - {response.status_code}")
                    if response.text:
                        try:
                            error = response.json()
                            print(f"          Error: {error.get('message', response.text[:100])}")
                        except:
                            print(f"          Response: {response.text[:100]}")
                    
            except Exception as e:
                print(f"     {i+1}. ❌ Error for user: {user_name} - {str(e)}")
        
        passed = success_count == total_count
        details = f"Created {success_count}/{total_count} suppliers with user owners"
        
        self.print_result("Create Suppliers for All Users", passed, details)
        return passed
    
    async def test_create_supplier_with_specific_user(self):
        """Test creating a supplier with a specific user as owner"""
        print("\n🎯 Test: Create Supplier with Specific User")
        
        if not self.existing_users:
            print("   No existing users found. Skipping test.")
            self.print_result("Create Supplier with Specific User", False, "No users available")
            return False
        
        # Create organisation
        org_id = await self.test_create_organisation()
        if not org_id:
            self.print_result("Create Supplier with Specific User", False, "Failed to create organisation")
            return False
        
        # Use the first user
        user = self.existing_users[0]
        user_id = user.get('id_app_user', user.get('id', 0))
        user_name = user.get('app_user_name', user.get('username', 'Unknown'))
        
        print(f"   Using user: {user_name} (ID: {user_id})")
        
        return await self.test_create_supplier_with_user_owner(user_id, org_id)
    
    async def test_create_supplier_with_multiple_users(self):
        """Test creating suppliers with multiple users as owners"""
        print("\n👥 Test: Create Supplier with Multiple Users (Sequential)")
        
        if not self.existing_users or len(self.existing_users) < 2:
            print("   Not enough existing users found. Creating additional users...")
            # Create additional users if needed
            for i in range(3):
                # Try to create a user
                user_data = {
                    "app_user_name": f"testuser_{uuid.uuid4().hex[:8]}",
                    "app_user_password": "TestPass123!",
                    "app_user_email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                    "app_user_type": "customer",
                    "app_user_preferences": {"theme": "dark"}
                }
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/app_user",
                        json={"user": user_data}
                    )
                    if response.status_code == 201:
                        self.existing_users.append(response.json())
                        print(f"   Created test user: {user_data['app_user_name']}")
                except Exception as e:
                    print(f"   Failed to create test user: {e}")
        
        # Refresh users list
        await self.fetch_existing_users()
        
        if not self.existing_users:
            self.print_result("Create Supplier with Multiple Users", False, "No users available")
            return False
        
        # Create organisation
        org_id = await self.test_create_organisation()
        if not org_id:
            self.print_result("Create Supplier with Multiple Users", False, "Failed to create organisation")
            return False
        
        # Test for each user
        success_count = 0
        total_count = min(len(self.existing_users), 5)  # Limit to 5 users
        
        for i, user in enumerate(self.existing_users[:total_count]):
            user_id = user.get('id_app_user', user.get('id', 0))
            if user_id == 0:
                continue
            
            result = await self.test_create_supplier_with_user_owner(user_id, org_id)
            if result:
                success_count += 1
        
        passed = success_count == total_count
        details = f"Successfully created {success_count}/{total_count} suppliers with different owners"
        self.print_result("Create Supplier with Multiple Users", passed, details)
        return passed
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("🚀 STARTING SUPPLIER CREATION TESTS WITH USER OWNERS")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # First fetch existing data
        await self.fetch_existing_users()
        await self.fetch_existing_organisations()
        
        if not self.existing_users:
            print("\n⚠️  No existing users found. Please create users first via the /app_user endpoint.")
            print("   You can run test_user_insert.py to create test users.")
        
        print("\n" + "="*70)
        print("📝 RUNNING CREATION TESTS")
        print("="*70)
        
        # Tests
        await self.test_create_supplier_with_specific_user()
        await self.test_create_suppliers_for_all_users()
        await self.test_create_supplier_with_multiple_users()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        
        # Group results by category
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
        print(f"\n📊 Resources:")
        print(f"   👤 Users Available: {len(self.existing_users)}")
        print(f"   🏢 Organisations Created: {len(self.created_organisations)}")
        print(f"   🏥 Suppliers Created: {len(self.created_suppliers)}")
        
        # Show created suppliers with their owners
        if self.created_suppliers:
            print(f"\n📋 Created Suppliers:")
            for supplier in self.created_suppliers[:10]:
                name = supplier.get('provider_name', 'Unknown')
                owner_id = supplier.get('id_provider_owner', 'N/A')
                print(f"   - {name} (Owner ID: {owner_id})")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test supplier creation with existing users")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API server (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--user-id",
        type=int,
        help="Specific user ID to use as owner (default: first available user)"
    )
    
    args = parser.parse_args()
    
    async with SupplierTesterWithUsers(args.url) as tester:
        if args.user_id:
            # Use specific user ID
            await tester.fetch_existing_users()
            await tester.fetch_existing_organisations()
            
            # Create organisation
            org_id = await tester.test_create_organisation()
            if org_id:
                await tester.test_create_supplier_with_user_owner(args.user_id, org_id)
            tester.print_summary()
        else:
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