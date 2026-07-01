#!/usr/bin/env python3
"""
Gluttex API Test Runner - Fixed for Product API
Run with: python test_runner.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestUser:
    """Represents a test user with authentication data"""
    id: int
    username: str
    email: str
    password: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    user_data: Dict[str, Any] = field(default_factory=dict)
    person_data: Dict[str, Any] = field(default_factory=dict)
    location_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'user_data': self.user_data,
            'person_data': self.person_data,
            'location_data': self.location_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestUser':
        expires_at = data.get('token_expires_at')
        return cls(
            id=data.get('id', 0),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
            user_data=data.get('user_data', {}),
            person_data=data.get('person_data', {}),
            location_data=data.get('location_data', {})
        )
    
    def is_token_valid(self) -> bool:
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at


@dataclass
class TestContext:
    users: List[TestUser] = field(default_factory=list)
    created_invoices: List[int] = field(default_factory=list)
    created_payments: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    created_organisations: List[int] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_categories: List[int] = field(default_factory=list)
    created_orders: List[int] = field(default_factory=list)
    created_services: List[int] = field(default_factory=list)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def save(self, filename: str = "test_context.json"):
        data = {
            'users': [u.to_dict() for u in self.users],
            'created_invoices': self.created_invoices,
            'created_payments': self.created_payments,
            'created_suppliers': self.created_suppliers,
            'created_organisations': self.created_organisations,
            'created_products': self.created_products,
            'created_categories': self.created_categories,
            'created_orders': self.created_orders,
            'created_services': self.created_services,
            'timestamp': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Test context saved to {filename}")
    
    def load(self, filename: str = "test_context.json"):
        if Path(filename).exists():
            with open(filename, 'r') as f:
                data = json.load(f)
            self.users = [TestUser.from_dict(u) for u in data.get('users', [])]
            self.created_invoices = data.get('created_invoices', [])
            self.created_payments = data.get('created_payments', [])
            self.created_suppliers = data.get('created_suppliers', [])
            self.created_organisations = data.get('created_organisations', [])
            self.created_products = data.get('created_products', [])
            self.created_categories = data.get('created_categories', [])
            self.created_orders = data.get('created_orders', [])
            self.created_services = data.get('created_services', [])
            print(f"📂 Test context loaded from {filename}")
            return True
        return False


# ============================================================================
# ENUMS
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

class GlutenStatus(str, Enum):
    GLUTEN_FREE = "gluten_free"
    CONTAINS_GLUTEN = "contains_gluten"
    MAY_CONTAIN = "may_contain"
    UNKNOWN = "unknown"


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def generate_unique_username() -> str:
    return f"testuser_{uuid.uuid4().hex[:8]}"

def generate_unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_strong_password() -> str:
    return f"Test_{uuid.uuid4().hex[:8]}!@#"

def generate_random_person_data() -> Dict[str, Any]:
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Maria", "Ahmed"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Benali", "Khan"]
    
    return {
        "person_first_name": random.choice(first_names),
        "person_last_name": random.choice(last_names),
        "person_birth_date": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "person_gender": random.choice([Gender.MALE.value, Gender.FEMALE.value]),
        "person_country_code": random.choice([c.value for c in CountryCode]),
        "blood_type": random.choice([b.value for b in BloodType])
    }

def generate_random_location_data() -> Dict[str, Any]:
    cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif", "Tizi Ouzou", "Bejaia"]
    streets = ["Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre", "Rue Larbi Ben Mhidi"]
    
    return {
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": random.choice(["Home", "Work", "Clinic", "Office", "Shop"]),
        "address_street": f"{random.randint(1, 999)} {random.choice(streets)}",
        "address_city": random.choice(cities),
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": random.choice([c.value for c in CountryCode])
    }

def generate_random_user_data() -> Dict[str, Any]:
    return {
        "app_user_name": generate_unique_username(),
        "app_user_password": generate_strong_password(),
        "app_user_email": generate_unique_email(),
        "app_user_type": random.choice([t.value for t in AppUserType]),
        "app_user_preferences": {
            "theme": random.choice(["dark", "light"]),
            "notifications": random.choice([True, False]),
            "language": random.choice(["en", "fr", "ar"])
        },
        "app_user_image_url": f"https://example.com/avatars/{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_organisation_data() -> Dict[str, Any]:
    org_names = [
        "HealthCare Plus", "MediCorp", "Wellness Center", 
        "Global Health Solutions", "Premium Care", "MediServe",
        "HealthFirst", "CarePlus", "MediHealth", "WellnessWorks",
        "City Medical Group", "Advanced Care", "Prime Health"
    ]
    
    return {
        "provider_organisation_name": f"{random.choice(org_names)} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Leading healthcare provider specializing in {random.choice(['cardiology', 'neurology', 'pediatrics', 'orthopedics', 'general medicine'])}"
    }

def generate_random_organisation_image_data() -> Dict[str, Any]:
    return {
        "org_image_url": f"https://example.com/images/org_{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_supplier_data(org_id: int = 0, owner_id: int = 0) -> Dict[str, Any]:
    provider_types = [1, 2, 3, 4, 5, 6]
    provider_names = [
        "City Medical Center", "HealthFirst Clinic", "MediLab Services", 
        "PharmaCare", "Advanced Medical Supplies", "Precision Diagnostics",
        "Wellness Medical Group", "Prime Healthcare", "Elite Medical Services",
        "CarePlus Pharmacy", "MediHealth Solutions"
    ]
    
    return {
        "id_provider_owner": owner_id,
        "idprovider_details_id": 0,
        "id_product_provider_type": random.choice(provider_types),
        "id_provider_organisation": org_id,
        "product_provider_type_desc": random.choice(["Restaurant", "Bakery", "Factory", "Supermarket", "Grocery Store", "Distributor"]),
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
    return {
        "provider_image_url": f"https://example.com/images/provider_{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_product_data(provider_id: int = 0, owner_id: int = 0) -> Dict[str, Any]:
    product_names = [
        "Paracetamol", "Ibuprofen", "Amoxicillin", "Vitamin C", "Omega-3",
        "Antibiotic", "Pain Relief", "Allergy Medicine", "Cough Syrup",
        "Medical Device", "Surgical Mask", "Hand Sanitizer", "Thermometer"
    ]
    categories = [1, 2, 3, 4, 5]
    
    return {
        "product_name": f"{random.choice(product_names)} {uuid.uuid4().hex[:4]}",
        "product_brand": random.choice(["BrandA", "BrandB", "BrandC", "Generic", "Premium"]),
        "product_provider_id": provider_id,
        "product_category_id": random.choice(categories),  # Note: using product_category_id (not id_product_category)
        "product_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "product_description": f"High-quality {random.choice(['medical', 'healthcare', 'pharmaceutical'])} product",
        "product_price": round(random.uniform(5.0, 200.0), 2),
        "product_quantity": random.randint(10, 1000),
        "product_quantifier": random.choice(["mg", "g", "ml", "pack", "unit"]),
        "product_owner": owner_id
    }

def generate_random_product_image_data() -> Dict[str, Any]:
    return {
        "product_image_url": f"https://example.com/images/product_{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_iproduct_data() -> Dict[str, Any]:
    """Generate iproduct data - using string values for enums"""
    gluten_statuses = ["gluten_free", "contains_gluten", "may_contain", "unknown"]
    categories = [1, 2, 3, 4, 5]
    
    return {
        "iproduct_name": f"Product_{uuid.uuid4().hex[:8]}",
        "iproduct_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "iproduct_brand": random.choice(["BrandA", "BrandB", "BrandC", "Generic"]),
        "iproduct_estimated_price": round(random.uniform(5.0, 200.0), 2),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(gluten_statuses),  # String value, not enum
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": round(random.uniform(0.5, 1.0), 2),
        "iproduct_category_id": random.choice(categories)  # Add category ID
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.context = TestContext()
        self.results = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_result(self, test_name: str, passed: bool, details: str = "", response_data: Any = None):
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
    
    def get_auth_headers(self, user: TestUser) -> Dict[str, str]:
        if user.access_token:
            return {"Authorization": f"Bearer {user.access_token}"}
        return {}
    
    def extract_id_from_response(self, response_data: Dict[str, Any], possible_keys: List[str]) -> int:
        """Extract ID from response by trying multiple possible key names."""
        if not response_data:
            return 0
        
        for key in possible_keys:
            if key in response_data:
                value = response_data[key]
                if value is not None:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        pass
        
        if 'data' in response_data and isinstance(response_data['data'], dict):
            return self.extract_id_from_response(response_data['data'], possible_keys)
        
        if 'result' in response_data and isinstance(response_data['result'], dict):
            return self.extract_id_from_response(response_data['result'], possible_keys)
        
        if 'items' in response_data and isinstance(response_data['items'], list) and response_data['items']:
            return self.extract_id_from_response(response_data['items'][0], possible_keys)
        
        return 0
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_user(self, user_data: Dict[str, Any] = None, 
                         person_data: Dict[str, Any] = None,
                         location_data: Dict[str, Any] = None) -> Optional[TestUser]:
        if user_data is None:
            user_data = generate_random_user_data()
        
        payload = {"user": user_data}
        if person_data:
            payload["person"] = person_data
        if location_data:
            payload["location"] = location_data
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                user_id = self.extract_id_from_response(result, ['id_app_user', 'id', 'user_id', 'app_user_id'])
                
                test_user = TestUser(
                    id=user_id,
                    username=user_data.get('app_user_name', ''),
                    email=user_data.get('app_user_email', ''),
                    password=user_data.get('app_user_password', ''),
                    user_data=user_data,
                    person_data=person_data or {},
                    location_data=location_data or {}
                )
                
                self.context.users.append(test_user)
                print(f"   ✅ Created user: {test_user.username} (ID: {test_user.id})")
                return test_user
            else:
                print(f"   ❌ Failed to create user: {response.status_code}")
                print(f"      {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating user: {e}")
            return None
    
    async def create_multiple_users(self, count: int = 5) -> List[TestUser]:
        print(f"\n👥 Creating {count} test users...")
        created_users = []
        
        for i in range(count):
            print(f"\n  Creating user {i+1}/{count}:")
            user_data = generate_random_user_data()
            person_data = generate_random_person_data() if random.choice([True, False]) else None
            location_data = generate_random_location_data() if random.choice([True, False]) else None
            
            user = await self.create_user(user_data, person_data, location_data)
            if user:
                created_users.append(user)
        
        print(f"\n✅ Created {len(created_users)} users")
        return created_users
    
    async def login_user(self, user: TestUser) -> bool:
        print(f"\n🔐 Logging in user: {user.username}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/authentication/token",
                json={
                    "app_user_name": user.username,
                    "app_user_password": user.password
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                access_token = result.get('access_token')
                refresh_token = result.get('refresh_token')
                expires_in = result.get('expires_in', 3600)
                
                if access_token:
                    user.access_token = access_token
                    user.refresh_token = refresh_token
                    user.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    print(f"   ✅ Login successful")
                    return True
                else:
                    print(f"   ❌ No access token in response")
                    return False
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                if response.text:
                    print(f"      {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    async def login_all_users(self) -> int:
        print("\n🔐 Logging in all users...")
        success_count = 0
        
        for user in self.context.users:
            if await self.login_user(user):
                success_count += 1
        
        print(f"\n✅ Logged in {success_count}/{len(self.context.users)} users")
        return success_count
    
    # ==================== ORGANISATION TESTS ====================
    
    async def test_create_organisation(self, user: TestUser) -> Optional[int]:
        print(f"\n🏢 Creating organisation for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        org_data = generate_random_organisation_data()
        org_image = generate_random_organisation_image_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/organisations",
                json={
                    "organisation": org_data,
                    "org_image": org_image
                },
                headers=headers
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   Response data: {json.dumps(result, indent=2)[:500]}")
                
                org_id = self.extract_id_from_response(result, [
                    'idprovider_organisation',
                    'id_provider_organisation',
                    'id',
                    'organisation_id',
                    'org_id'
                ])
                
                if org_id > 0:
                    self.context.created_organisations.append(org_id)
                    print(f"   ✅ Created organisation: {org_id}")
                    print(f"   📝 Name: {org_data['provider_organisation_name']}")
                    self.print_result("Create Organisation", True, f"Organisation {org_id} created")
                    return org_id
                else:
                    print(f"   ⚠️ Could not extract ID from response: {result}")
                    self.context.created_organisations.append(0)
                    self.print_result("Create Organisation", True, "Organisation created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create organisation: {response.status_code}")
                print(f"      {response.text[:300]}")
                self.print_result("Create Organisation", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Organisation creation error: {e}")
            self.print_result("Create Organisation", False, str(e))
            return None
    
    async def test_get_organisation(self, user: TestUser, org_id: int) -> bool:
        if org_id <= 0:
            print(f"\n⚠️ Skipping get organisation - invalid ID: {org_id}")
            return False
            
        print(f"\n📋 Getting organisation {org_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/organisations/{org_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Organisation retrieved: {result.get('provider_organisation_name', 'Unknown')}")
                self.print_result("Get Organisation", True, f"Organisation {org_id} retrieved")
                return True
            else:
                print(f"   ❌ Failed to get organisation: {response.status_code}")
                self.print_result("Get Organisation", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get organisation error: {e}")
            self.print_result("Get Organisation", False, str(e))
            return False
    
    async def test_get_all_organisations(self, user: TestUser) -> bool:
        print(f"\n📋 Getting all organisations")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/organisations",
                params={"offset": 0, "limit": 100},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else 0
                print(f"   ✅ Retrieved {count} organisations")
                self.print_result("Get All Organisations", True, f"Retrieved {count} organisations")
                return True
            else:
                print(f"   ❌ Failed to get organisations: {response.status_code}")
                self.print_result("Get All Organisations", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get organisations error: {e}")
            self.print_result("Get All Organisations", False, str(e))
            return False
    
    # ==================== SUPPLIER TESTS ====================
    
    async def test_create_supplier(self, user: TestUser, org_id: int) -> Optional[int]:
        if org_id <= 0:
            print(f"\n⚠️ Skipping create supplier - invalid organisation ID: {org_id}")
            return None
            
        print(f"\n🏥 Creating supplier for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        supplier_data = generate_random_supplier_data(org_id, user.id)
        location_data = generate_random_location_data()
        image_data = generate_random_provider_image_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/suppliers",
                json={
                    "provider": supplier_data,
                    "location": location_data,
                    "image": image_data
                },
                headers=headers
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                
                supplier_id = self.extract_id_from_response(result, [
                    'id_product_provider',
                    'idprovider',
                    'id',
                    'supplier_id',
                    'provider_id'
                ])
                
                if supplier_id > 0:
                    self.context.created_suppliers.append(supplier_id)
                    print(f"   ✅ Created supplier: {supplier_id}")
                    self.print_result("Create Supplier", True, f"Supplier {supplier_id} created")
                    return supplier_id
                else:
                    print(f"   ⚠️ Could not extract supplier ID from response")
                    self.print_result("Create Supplier", True, "Supplier created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create supplier: {response.status_code}")
                print(f"      {response.text[:300]}")
                self.print_result("Create Supplier", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Supplier creation error: {e}")
            self.print_result("Create Supplier", False, str(e))
            return None
    
    async def test_get_supplier(self, user: TestUser, supplier_id: int) -> bool:
        if supplier_id <= 0:
            print(f"\n⚠️ Skipping get supplier - invalid ID: {supplier_id}")
            return False
            
        print(f"\n📋 Getting supplier {supplier_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/suppliers/{supplier_id}",
                params={"full": True},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Supplier retrieved: {result.get('provider_name', 'Unknown')}")
                self.print_result("Get Supplier", True, f"Supplier {supplier_id} retrieved")
                return True
            else:
                print(f"   ❌ Failed to get supplier: {response.status_code}")
                self.print_result("Get Supplier", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get supplier error: {e}")
            self.print_result("Get Supplier", False, str(e))
            return False
    
    async def test_get_all_suppliers(self, user: TestUser) -> bool:
        print(f"\n📋 Getting all suppliers")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/suppliers",
                params={"offset": 0, "limit": 100},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else 0
                print(f"   ✅ Retrieved {count} suppliers")
                self.print_result("Get All Suppliers", True, f"Retrieved {count} suppliers")
                return True
            else:
                print(f"   ❌ Failed to get suppliers: {response.status_code}")
                self.print_result("Get All Suppliers", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get suppliers error: {e}")
            self.print_result("Get All Suppliers", False, str(e))
            return False
    
    # ==================== PRODUCT TESTS ====================
    
    async def test_get_categories(self, user: TestUser) -> bool:
        print(f"\n📋 Getting product categories")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/products/category/all",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else 0
                print(f"   ✅ Retrieved {count} categories")
                self.print_result("Get Categories", True, f"Retrieved {count} categories")
                return True
            else:
                print(f"   ❌ Failed to get categories: {response.status_code}")
                self.print_result("Get Categories", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get categories error: {e}")
            self.print_result("Get Categories", False, str(e))
            return False
    
    async def test_create_product(self, user: TestUser, supplier_id: int) -> Optional[int]:
        if supplier_id <= 0:
            print(f"\n⚠️ Skipping create product - invalid supplier ID: {supplier_id}")
            return None
            
        print(f"\n📦 Creating product for supplier {supplier_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        product_data = generate_random_product_data(supplier_id, user.id)
        product_image = generate_random_product_image_data()
        iproduct_data = generate_random_iproduct_data()
        
        # Log the data being sent
        print(f"   Product data: {json.dumps(product_data, indent=2)[:300]}")
        print(f"   IProduct data: {json.dumps(iproduct_data, indent=2)[:300]}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/products",
                json={
                    "product": product_data,
                    "image": product_image,
                    "iproduct": iproduct_data
                },
                headers=headers
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                
                product_id = self.extract_id_from_response(result, [
                    'id_product',
                    'id',
                    'product_id'
                ])
                
                if product_id > 0:
                    self.context.created_products.append(product_id)
                    print(f"   ✅ Created product: {product_id}")
                    print(f"   📝 Name: {product_data['product_name']}")
                    print(f"   💰 Price: {product_data['product_price']}")
                    self.print_result("Create Product", True, f"Product {product_id} created")
                    return product_id
                else:
                    print(f"   ⚠️ Could not extract product ID from response: {result}")
                    self.print_result("Create Product", True, "Product created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create product: {response.status_code}")
                print(f"      {response.text[:500]}")
                self.print_result("Create Product", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Product creation error: {e}")
            self.print_result("Create Product", False, str(e))
            return None
    
    async def test_get_product(self, user: TestUser, product_id: int) -> bool:
        if product_id <= 0:
            print(f"\n⚠️ Skipping get product - invalid ID: {product_id}")
            return False
            
        print(f"\n📋 Getting product {product_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/products/{product_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Product retrieved: {result.get('product_name', 'Unknown')}")
                print(f"   💰 Price: {result.get('product_price', 0)}")
                print(f"   📦 Quantity: {result.get('product_quantity', 0)}")
                self.print_result("Get Product", True, f"Product {product_id} retrieved")
                return True
            else:
                print(f"   ❌ Failed to get product: {response.status_code}")
                self.print_result("Get Product", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get product error: {e}")
            self.print_result("Get Product", False, str(e))
            return False
    
    async def test_update_product(self, user: TestUser, product_id: int) -> bool:
        if product_id <= 0:
            print(f"\n⚠️ Skipping update product - invalid ID: {product_id}")
            return False
            
        print(f"\n✏️ Updating product {product_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        # Use product_category_id (not id_product_category)
        update_data = {
            "product_name": f"Updated_Product_{uuid.uuid4().hex[:4]}",
            "product_price": round(random.uniform(10.0, 300.0), 2),
            "product_quantity": random.randint(50, 2000),
            "product_description": "Updated product description",
            "product_category_id": random.choice([1, 2, 3, 4, 5])  # Use product_category_id
        }
        image_data = generate_random_product_image_data()
        
        print(f"   Update data: {json.dumps(update_data, indent=2)[:300]}")
        
        try:
            response = await self.client.put(
                f"{self.base_url}/api/v1/products/{product_id}",
                json={
                    "product": update_data,
                    "image": image_data
                },
                headers=headers
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Product updated: {result.get('product_name', 'Unknown')}")
                self.print_result("Update Product", True, f"Product {product_id} updated")
                return True
            else:
                print(f"   ❌ Failed to update product: {response.status_code}")
                print(f"      {response.text[:500]}")
                self.print_result("Update Product", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Update product error: {e}")
            self.print_result("Update Product", False, str(e))
            return False
    
    async def test_get_all_products(self, user: TestUser, supplier_id: int) -> bool:
        if supplier_id <= 0:
            print(f"\n⚠️ Skipping get all products - invalid supplier ID: {supplier_id}")
            return False
            
        print(f"\n📋 Getting all products for supplier {supplier_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/products/{user.id}/{supplier_id}/0/0/10",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                count = len(result) if isinstance(result, list) else 0
                print(f"   ✅ Retrieved {count} products")
                self.print_result("Get All Products", True, f"Retrieved {count} products")
                return True
            else:
                print(f"   ❌ Failed to get products: {response.status_code}")
                self.print_result("Get All Products", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Get products error: {e}")
            self.print_result("Get All Products", False, str(e))
            return False
    
    # ==================== COMPLETE FLOW TEST ====================
    
    async def test_complete_product_flow(self, user: TestUser) -> bool:
        print(f"\n🔄 Testing complete product flow for user: {user.username}")
        
        org_id = await self.test_create_organisation(user)
        if not org_id or org_id == 0:
            print("   ❌ Failed to create organisation or got invalid ID")
            self.print_result("Complete Product Flow", False, "Failed to create organisation")
            return False
        
        await self.test_get_organisation(user, org_id)
        
        supplier_id = await self.test_create_supplier(user, org_id)
        if not supplier_id or supplier_id == 0:
            print("   ❌ Failed to create supplier or got invalid ID")
            self.print_result("Complete Product Flow", False, "Failed to create supplier")
            return False
        
        await self.test_get_supplier(user, supplier_id)
        await self.test_get_categories(user)
        
        product_id = await self.test_create_product(user, supplier_id)
        if not product_id or product_id == 0:
            print("   ❌ Failed to create product or got invalid ID")
            self.print_result("Complete Product Flow", False, "Failed to create product")
            return False
        
        await self.test_get_product(user, product_id)
        await self.test_update_product(user, product_id)
        await self.test_get_all_products(user, supplier_id)
        
        self.print_result("Complete Product Flow", True, 
                        f"Org {org_id}, Supplier {supplier_id}, Product {product_id} tested")
        return True
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, skip_user_creation: bool = False, 
                       skip_login: bool = False,
                       context_file: str = "test_context.json"):
        print("\n" + "="*70)
        print("🚀 GLUTTEX API TEST RUNNER")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        if Path(context_file).exists():
            loaded = self.context.load(context_file)
            if loaded:
                print(f"📂 Loaded {len(self.context.users)} users from context")
        
        if not skip_user_creation and not self.context.users:
            print("\n📝 Creating Test Users")
            print("="*70)
            await self.create_multiple_users(5)
        elif self.context.users:
            print(f"\n📋 Using {len(self.context.users)} existing users")
        
        if not self.context.users:
            print("\n❌ No users available. Cannot continue.")
            return
        
        if not skip_login:
            print("\n🔐 Logging In Users")
            print("="*70)
            await self.login_all_users()
        else:
            print("\n⏭️ Skipping login step")
        
        authenticated_users = [u for u in self.context.users if u.access_token]
        if not authenticated_users:
            print("\n❌ No authenticated users available")
            return
        
        test_user = authenticated_users[0]
        print(f"\n👤 Using user '{test_user.username}' (ID: {test_user.id})")
        
        print("\n🧪 Running Tests")
        print("="*70)
        
        # Organisation Tests
        print("\n🏢 ORGANISATION TESTS")
        await self.test_get_all_organisations(test_user)
        org_id = await self.test_create_organisation(test_user)
        if org_id and org_id > 0:
            await self.test_get_organisation(test_user, org_id)
        
        # Supplier Tests
        print("\n🏥 SUPPLIER TESTS")
        supplier_id = None
        if org_id and org_id > 0:
            supplier_id = await self.test_create_supplier(test_user, org_id)
            if supplier_id and supplier_id > 0:
                await self.test_get_supplier(test_user, supplier_id)
                await self.test_get_all_suppliers(test_user)
        
        # Product Tests
        print("\n📦 PRODUCT TESTS")
        await self.test_get_categories(test_user)
        
        if supplier_id and supplier_id > 0:
            product_id = await self.test_create_product(test_user, supplier_id)
            if product_id and product_id > 0:
                await self.test_get_product(test_user, product_id)
                await self.test_update_product(test_user, product_id)
                await self.test_get_all_products(test_user, supplier_id)
        
        # Complete Flow
        print("\n🔄 COMPLETE FLOW TEST")
        await self.test_complete_product_flow(test_user)
        
        print("\n💾 Saving Test Context")
        print("="*70)
        self.context.save(context_file)
        
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
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
        
        print(f"\n📊 Resources:")
        print(f"   👤 Total Users: {len(self.context.users)}")
        print(f"   🔐 Authenticated: {len([u for u in self.context.users if u.access_token])}")
        print(f"   🏢 Organisations: {len(self.context.created_organisations)}")
        print(f"   🏥 Suppliers: {len(self.context.created_suppliers)}")
        print(f"   📦 Products: {len(self.context.created_products)}")
        
        if self.context.created_organisations:
            valid_orgs = [o for o in self.context.created_organisations if o > 0]
            if valid_orgs:
                print(f"\n🏢 Org IDs: {', '.join(map(str, valid_orgs))}")
        
        if self.context.created_suppliers:
            valid_suppliers = [s for s in self.context.created_suppliers if s > 0]
            if valid_suppliers:
                print(f"🏥 Supplier IDs: {', '.join(map(str, valid_suppliers))}")
        
        if self.context.created_products:
            valid_products = [p for p in self.context.created_products if p > 0]
            if valid_products:
                print(f"📦 Product IDs: {', '.join(map(str, valid_products))}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
        
        print("="*70)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gluttex API Test Runner")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--skip-user-creation", action="store_true")
    parser.add_argument("--skip-login", action="store_true")
    parser.add_argument("--context-file", default="test_context.json")
    parser.add_argument("--clear-context", action="store_true")
    
    args = parser.parse_args()
    
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context file")
    
    async with TestRunner(args.url) as runner:
        await runner.run_tests(
            skip_user_creation=args.skip_user_creation,
            skip_login=args.skip_login,
            context_file=args.context_file
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)