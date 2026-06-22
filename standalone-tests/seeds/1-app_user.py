#!/usr/bin/env python3
"""
Test script for inserting users via the /app_user endpoint.
Run with: python test_user_insert.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional
from datetime import datetime, date
from enum import Enum


# ============================================================================
# ENUMS (mirroring the API models)
# ============================================================================

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "Unknown"

class AppUserType(str, Enum):
    PROVIDER = "provider"
    CUSTOMER = "customer"
    PATIENT = "patient"
    GUEST = "guest"

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

def generate_unique_username() -> str:
    """Generate a unique username"""
    return f"testuser_{uuid.uuid4().hex[:8]}"


def generate_unique_email() -> str:
    """Generate a unique email"""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def generate_random_user_data() -> Dict[str, Any]:
    """Generate random user data"""
    return {
        "app_user_name": generate_unique_username(),
        "app_user_password": "TestPass123!",
        "app_user_email": generate_unique_email(),
        "app_user_type": random.choice([t.value for t in AppUserType]),
        "app_user_preferences": {
            "theme": random.choice(["dark", "light"]),
            "notifications": random.choice([True, False])
        },
        "app_user_image_url": f"https://example.com/avatars/{uuid.uuid4().hex[:8]}.jpg"
    }


def generate_random_person_data() -> Dict[str, Any]:
    """Generate random person data"""
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    genders = [Gender.MALE.value, Gender.FEMALE.value]
    
    return {
        "person_first_name": random.choice(first_names),
        "person_last_name": random.choice(last_names),
        "person_birth_date": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "person_gender": random.choice(genders),
        "person_country_code": random.choice([c.value for c in CountryCode]),
        "blood_type": random.choice([b.value for b in BloodType])
    }


def generate_random_location_data() -> Dict[str, Any]:
    """Generate random location data"""
    cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif", "Tizi Ouzou", "Bejaia"]
    streets = ["Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre", "Rue Larbi Ben Mhidi"]
    countries = [CountryCode.DZ.value, CountryCode.FR.value, CountryCode.US.value]
    
    return {
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": random.choice(["Home", "Work", "Clinic", "Office", "Shop"]),
        "address_street": f"{random.randint(1, 999)} {random.choice(streets)}",
        "address_city": random.choice(cities),
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": random.choice(countries)
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class UserInsertTester:
    """Test runner for user insertion endpoint"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.results = []
        self.created_users = []
    
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
            print(f"     Response: {json.dumps(response_data, indent=2, default=str)[:500]}")
        self.results.append({"name": test_name, "passed": passed, "details": details})
    
    async def test_insert_user_minimal(self):
        """Test inserting a user with minimal data (user only)"""
        print("\n📝 Test: Insert User (Minimal Data)")
        
        user_data = generate_random_user_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={"user": user_data}
            )
            
            passed = response.status_code == 201
            if passed:
                self.created_users.append(response.json())
                details = f"User '{user_data['app_user_name']}' created successfully"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("Minimal User Insert", passed, details, response.json() if passed else None)
            return passed
            
        except Exception as e:
            self.print_result("Minimal User Insert", False, str(e))
            return False
    
    async def test_insert_user_with_person(self):
        """Test inserting a user with person data"""
        print("\n👤 Test: Insert User with Person Data")
        
        user_data = generate_random_user_data()
        person_data = generate_random_person_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={
                    "user": user_data,
                    "person": person_data
                }
            )
            
            passed = response.status_code == 201
            if passed:
                self.created_users.append(response.json())
                details = f"User '{user_data['app_user_name']}' created with person '{person_data['person_first_name']} {person_data['person_last_name']}'"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("User with Person", passed, details, response.json() if passed else None)
            return passed
            
        except Exception as e:
            self.print_result("User with Person", False, str(e))
            return False
    
    async def test_insert_user_with_location(self):
        """Test inserting a user with location data"""
        print("\n📍 Test: Insert User with Location Data")
        
        user_data = generate_random_user_data()
        person_data = generate_random_person_data()
        location_data = generate_random_location_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={
                    "user": user_data,
                    "person": person_data,
                    "location": location_data
                }
            )
            
            passed = response.status_code == 201
            if passed:
                self.created_users.append(response.json())
                details = f"User '{user_data['app_user_name']}' created with location at {location_data['address_city']}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("User with Location", passed, details, response.json() if passed else None)
            return passed
            
        except Exception as e:
            self.print_result("User with Location", False, str(e))
            return False
    
    async def test_insert_duplicate_user(self):
        """Test inserting a duplicate user (should fail)"""
        print("\n🔁 Test: Insert Duplicate User")
        
        user_data = generate_random_user_data()
        
        # First insertion should succeed
        response1 = await self.client.post(
            f"{self.base_url}/api/v1/app_user",
            json={"user": user_data}
        )
        
        if response1.status_code != 201:
            self.print_result("Duplicate User", False, "First insertion failed, cannot test duplicate")
            return False
        
        self.created_users.append(response1.json())
        
        # Second insertion should fail with 409
        response2 = await self.client.post(
            f"{self.base_url}/api/v1/app_user",
            json={"user": user_data}
        )
        
        passed = response2.status_code == 409
        details = f"Correctly rejected duplicate (Status: {response2.status_code})" if passed else f"Expected 409, got {response2.status_code}"
        
        self.print_result("Duplicate User", passed, details)
        return passed
    
    async def test_insert_user_invalid_password(self):
        """Test inserting a user with invalid password (should fail)"""
        print("\n🔒 Test: Insert User with Invalid Password")
        
        invalid_user_data = generate_random_user_data()
        invalid_user_data["app_user_password"] = "weak"  # Too short
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={"user": invalid_user_data}
            )
            
            # Should fail with 400 or 422
            passed = response.status_code in [400, 422]
            details = f"Correctly rejected invalid password (Status: {response.status_code})"
            
            self.print_result("Invalid Password", passed, details)
            return passed
            
        except Exception as e:
            self.print_result("Invalid Password", False, str(e))
            return False
    
    async def test_insert_user_with_provider(self):
        """Test inserting a user with OAuth provider"""
        print("\n🔐 Test: Insert User with OAuth Provider")
        
        user_data = generate_random_user_data()
        # Remove password for OAuth users
        user_data["app_user_password"] = None
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={"user": user_data},
                params={"provider": "google"}
            )
            
            # Should succeed (OAuth users don't need password)
            passed = response.status_code == 201
            if passed:
                self.created_users.append(response.json())
                details = f"User '{user_data['app_user_name']}' created with Google OAuth"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("OAuth Provider", passed, details, response.json() if passed else None)
            return passed
            
        except Exception as e:
            self.print_result("OAuth Provider", False, str(e))
            return False
    
    async def test_insert_user_missing_username(self):
        """Test inserting a user with missing username (should fail)"""
        print("\n❌ Test: Insert User with Missing Username")
        
        user_data = generate_random_user_data()
        user_data["app_user_name"] = None
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={"user": user_data}
            )
            
            passed = response.status_code in [400, 422]
            details = f"Correctly rejected missing username (Status: {response.status_code})"
            
            self.print_result("Missing Username", passed, details)
            return passed
            
        except Exception as e:
            self.print_result("Missing Username", False, str(e))
            return False
    
    async def test_insert_user_with_full_data(self):
        """Test inserting a user with complete data (user + person + location)"""
        print("\n📦 Test: Insert User with Complete Data")
        
        user_data = generate_random_user_data()
        person_data = generate_random_person_data()
        location_data = generate_random_location_data()
        
        # Add some extra data
        user_data["app_user_preferences"] = {
            "theme": "dark",
            "notifications": True,
            "language": "en",
            "timezone": "UTC+1"
        }
        
        person_data["person_country_code"] = "DZ"
        person_data["blood_type"] = "O+"
        
        location_data["location_name"] = "Primary Location"
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={
                    "user": user_data,
                    "person": person_data,
                    "location": location_data
                }
            )
            
            passed = response.status_code == 201
            if passed:
                self.created_users.append(response.json())
                details = f"User '{user_data['app_user_name']}' created with complete data"
            else:
                details = f"Status: {response.status_code}, Response: {response.text[:200]}"
            
            self.print_result("Complete Data", passed, details, response.json() if passed else None)
            return passed
            
        except Exception as e:
            self.print_result("Complete Data", False, str(e))
            return False
    
    async def test_insert_multiple_users(self):
        """Test inserting multiple users in sequence"""
        print("\n👥 Test: Insert Multiple Users")
        
        success_count = 0
        total_count = 5
        
        for i in range(total_count):
            user_data = generate_random_user_data()
            person_data = generate_random_person_data() if random.choice([True, False]) else None
            
            payload = {"user": user_data}
            if person_data:
                payload["person"] = person_data
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/app_user",
                    json=payload
                )
                
                if response.status_code == 201:
                    success_count += 1
                    self.created_users.append(response.json())
                    print(f"     {i+1}. ✅ Created: {user_data['app_user_name']}")
                else:
                    print(f"     {i+1}. ❌ Failed: {user_data['app_user_name']} ({response.status_code})")
                    
            except Exception as e:
                print(f"     {i+1}. ❌ Error: {str(e)}")
        
        passed = success_count == total_count
        details = f"Created {success_count}/{total_count} users"
        
        self.print_result("Multiple Users", passed, details)
        return passed
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("🚀 STARTING USER INSERTION TESTS")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Run tests
        await self.test_insert_user_minimal()
        await self.test_insert_user_with_person()
        await self.test_insert_user_with_location()
        await self.test_insert_user_with_full_data()
        await self.test_insert_user_with_provider()
        await self.test_insert_user_invalid_password()
        await self.test_insert_user_missing_username()
        await self.test_insert_duplicate_user()
        await self.test_insert_multiple_users()
        
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
        
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['name']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print("="*70)
        print(f"📈 Total: {total} tests")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"👤 Users Created: {len(self.created_users)}")
        
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
    
    parser = argparse.ArgumentParser(description="Test user insertion endpoint")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API server (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--user-only",
        action="store_true",
        help="Only run minimal user tests"
    )
    
    args = parser.parse_args()
    
    async with UserInsertTester(args.url) as tester:
        if args.user_only:
            await tester.test_insert_user_minimal()
            await tester.test_insert_user_with_person()
            await tester.test_insert_user_with_location()
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