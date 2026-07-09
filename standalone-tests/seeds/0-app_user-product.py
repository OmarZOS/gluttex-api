#!/usr/bin/env python3
"""
Gluttex API Test Runner - Massive Data Generation with Distribution
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
    created_staff_rules: List[int] = field(default_factory=list)
    created_deliveries: List[int] = field(default_factory=list)
    user_org_mapping: Dict[int, List[int]] = field(default_factory=dict)
    user_supplier_mapping: Dict[int, List[int]] = field(default_factory=dict)
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
            'created_staff_rules': self.created_staff_rules,
            'created_deliveries': self.created_deliveries,
            'user_org_mapping': self.user_org_mapping,
            'user_supplier_mapping': self.user_supplier_mapping,
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
            self.created_staff_rules = data.get('created_staff_rules', [])
            self.created_deliveries = data.get('created_deliveries', [])
            self.user_org_mapping = data.get('user_org_mapping', {})
            self.user_supplier_mapping = data.get('user_supplier_mapping', {})
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


# ============================================================================
# TEST DATA GENERATORS - ENHANCED
# ============================================================================

def generate_unique_username() -> str:
    return f"testuser_{uuid.uuid4().hex[:8]}"

def generate_unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_strong_password() -> str:
    return f"Test_{uuid.uuid4().hex[:8]}!@#"

def generate_random_person_data() -> Dict[str, Any]:
    first_names = [
        "John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", 
        "Maria", "Ahmed", "Sarah", "Michael", "Emma", "David", "Sophia", 
        "James", "Olivia", "Daniel", "Isabella", "Matthew", "Amelia", 
        "Joseph", "Mia", "Samuel", "Charlotte", "David", "Ava", "Andrew"
    ]
    last_names = [
        "Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
        "Miller", "Benali", "Khan", "Cohen", "Lopez", "Martin", "Lee", 
        "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", 
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres"
    ]
    
    return {
        "person_first_name": random.choice(first_names),
        "person_last_name": random.choice(last_names),
        "person_birth_date": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "person_gender": random.choice([Gender.MALE.value, Gender.FEMALE.value]),
        "person_country_code": random.choice([c.value for c in CountryCode]),
        "blood_type": random.choice([b.value for b in BloodType])
    }

def generate_random_location_data() -> Dict[str, Any]:
    cities = [
        "Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif", 
        "Tizi Ouzou", "Bejaia", "Batna", "Sidi Bel Abbes", "Biskra", 
        "Tebessa", "El Oued", "Ghardaia", "Tamanrasset", "Mostaganem", 
        "Skikda", "Tipaza", "Boumerdes", "Relizane", "Saida", "M'sila"
    ]
    streets = [
        "Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre", 
        "Rue Larbi Ben Mhidi", "Boulevard Krim Belkacem", 
        "Rue des Freres Bouadou", "Avenue de l'Independance", 
        "Rue Ali Khodja", "Boulevard Colonel Amirouche", "Rue Emir Abdelkader"
    ]
    
    return {
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": random.choice(["Home", "Work", "Clinic", "Office", "Shop", "Warehouse", "Distribution Center", "Hospital", "Pharmacy"]),
        "address_street": f"{random.randint(1, 999)} {random.choice(streets)}",
        "address_city": random.choice(cities),
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": random.choice([c.value for c in CountryCode])
    }

def generate_random_user_data(user_type: Optional[str] = None) -> Dict[str, Any]:
    return {
        "app_user_name": generate_unique_username(),
        "app_user_password": generate_strong_password(),
        "app_user_email": generate_unique_email(),
        "app_user_type": user_type or random.choice([t.value for t in AppUserType]),
        "app_user_preferences": {
            "theme": random.choice(["dark", "light"]),
            "notifications": random.choice([True, False]),
            "language": random.choice(["en", "fr", "ar"])
        },
        "app_user_image_url": f"https://example.com/avatars/{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_organisation_data() -> Dict[str, Any]:
    org_names = [
        "HealthCare Plus", "MediCorp", "Wellness Center", "Global Health Solutions", 
        "Premium Care", "MediServe", "HealthFirst", "CarePlus", "MediHealth", 
        "WellnessWorks", "City Medical Group", "Advanced Care", "Prime Health",
        "Elite Medical", "Family Care", "Specialist Center", "Medical Arts",
        "LifeLine Health", "CareBridge", "MediLink", "HealthWave", "VitalCare",
        "Optimum Health", "Pulse Medical", "Core Wellness", "Apex Healthcare",
        "Zenith Medical", "Nova Health", "Virtue Care", "Harmony Medical",
        "Pinnacle Health", "Radiant Care", "Summit Medical", "Tranquil Health"
    ]
    
    return {
        "provider_organisation_name": f"{random.choice(org_names)} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Leading healthcare provider specializing in {random.choice(['cardiology', 'neurology', 'pediatrics', 'orthopedics', 'general medicine', 'dermatology', 'ophthalmology', 'oncology', 'gynecology', 'urology', 'psychiatry', 'radiology'])}"
    }

def generate_random_supplier_data(org_id: int = 0, owner_id: int = 0) -> Dict[str, Any]:
    provider_types = [1, 2, 3, 4, 5, 6]
    provider_names = [
        "City Medical Center", "HealthFirst Clinic", "MediLab Services", 
        "PharmaCare", "Advanced Medical Supplies", "Precision Diagnostics",
        "Wellness Medical Group", "Prime Healthcare", "Elite Medical Services",
        "CarePlus Pharmacy", "MediHealth Solutions", "Global Medical Supply",
        "MediTech Services", "HealthBridge", "Vitality Medical", "Apex Diagnostics",
        "CuraMed", "NovaCare", "Virtue Health", "Optimum Medical",
        "Pulse Healthcare", "Zenith Medical Supply", "Radiant Health", "Core Medical"
    ]
    
    return {
        "id_provider_owner": owner_id,
        "idprovider_details_id": 0,
        "id_product_provider_type": random.choice(provider_types),
        "id_provider_organisation": org_id,
        "product_provider_type_desc": random.choice(["Medical", "Pharmacy", "Diagnostic", "Surgical", "Laboratory", "Dental", "Optical", "Therapeutic"]),
        "provider_organisation_name": f"{random.choice(provider_names)} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Provider of {random.choice(['medical', 'dental', 'diagnostic', 'pharmaceutical', 'surgical', 'laboratory', 'therapeutic', 'rehabilitation'])} services",
        "provider_name": f"Provider_{uuid.uuid4().hex[:8]}",
        "provider_contact_info": json.dumps({
            "phone": f"+213-5{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}",
            "email": generate_unique_email(),
            "website": f"https://{uuid.uuid4().hex[:8]}.com"
        })
    }

def generate_random_product_data(provider_id: int = 0, owner_id: int = 0) -> Dict[str, Any]:
    product_names = [
        "Paracetamol", "Ibuprofen", "Amoxicillin", "Vitamin C", "Omega-3",
        "Antibiotic", "Pain Relief", "Allergy Medicine", "Cough Syrup",
        "Medical Device", "Surgical Mask", "Hand Sanitizer", "Thermometer",
        "Blood Pressure Monitor", "Stethoscope", "Syringe", "Bandage", "Antiseptic",
        "Antibiotic Cream", "Painkiller", "Antihistamine", "Decongestant", "Antacid"
    ]
    categories = [1, 2, 3, 4, 5]
    
    return {
        "product_name": f"{random.choice(product_names)} {uuid.uuid4().hex[:4]}",
        "product_brand": random.choice(["BrandA", "BrandB", "BrandC", "Generic", "Premium", "MedicalPro", "HealthPlus", "CareMed"]),
        "product_provider_id": provider_id,
        "product_category_id": random.choice(categories),
        "product_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "product_description": f"High-quality {random.choice(['medical', 'healthcare', 'pharmaceutical', 'surgical', 'diagnostic'])} product",
        "product_price": round(random.uniform(5.0, 200.0), 2),
        "product_quantity": random.randint(10, 1000),
        "product_quantifier": random.choice(["mg", "g", "ml", "pack", "unit", "tablet", "capsule", "bottle"]),
        "product_owner": owner_id
    }

def generate_random_product_image_data() -> Dict[str, Any]:
    return {
        "product_image_url": f"https://example.com/images/product_{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_random_iproduct_data() -> Dict[str, Any]:
    gluten_statuses = ["gluten_free", "contains_gluten", "may_contain", "unknown"]
    categories = [1, 2, 3, 4, 5]
    
    return {
        "iproduct_name": f"Product_{uuid.uuid4().hex[:8]}",
        "iproduct_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "iproduct_brand": random.choice(["BrandA", "BrandB", "BrandC", "Generic", "Premium"]),
        "iproduct_estimated_price": round(random.uniform(5.0, 200.0), 2),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(gluten_statuses),
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": round(random.uniform(0.5, 1.0), 2),
        "iproduct_category_id": random.choice(categories)
    }


# ============================================================================
# ENHANCED TEST RUNNER
# ============================================================================

class EnhancedTestRunner:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.context = TestContext()
        self.results = []
        self.test_user = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=60.0, verify=False)
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
                if response.text:
                    print(f"      {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating user: {e}")
            return None
    
    async def create_multiple_users(self, count: int = 20) -> List[TestUser]:
        print(f"\n👥 Creating {count} test users...")
        created_users = []
        
        user_types = ["provider", "customer", "patient", "guest"]
        
        for i in range(count):
            user_type = user_types[i % len(user_types)]
            user_data = generate_random_user_data(user_type)
            person_data = generate_random_person_data()
            location_data = generate_random_location_data()
            
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
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/organisations",
                json={"organisation": org_data},
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                org_id = self.extract_id_from_response(result, [
                    'idprovider_organisation',
                    'id_provider_organisation',
                    'id',
                    'organisation_id',
                    'org_id'
                ])
                
                if org_id > 0:
                    self.context.created_organisations.append(org_id)
                    
                    if user.id not in self.context.user_org_mapping:
                        self.context.user_org_mapping[user.id] = []
                    self.context.user_org_mapping[user.id].append(org_id)
                    
                    print(f"   ✅ Created organisation: {org_id} for user {user.id}")
                    self.print_result("Create Organisation", True, f"Organisation {org_id} created")
                    return org_id
                else:
                    print(f"   ⚠️ Could not extract ID from response")
                    return 0
            else:
                print(f"   ❌ Failed to create organisation: {response.status_code}")
                self.print_result("Create Organisation", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Organisation creation error: {e}")
            self.print_result("Create Organisation", False, str(e))
            return None
    
    async def create_organisations_for_all_users(self, orgs_per_user: int = 3):
        """Create organisations for all authenticated users"""
        print(f"\n🏢 Creating {orgs_per_user} organisations per user...")
        
        authenticated_users = [u for u in self.context.users if u.access_token]
        total_orgs = 0
        
        for user in authenticated_users:
            for i in range(orgs_per_user):
                org_id = await self.test_create_organisation(user)
                if org_id and org_id > 0:
                    total_orgs += 1
        
        print(f"✅ Created {total_orgs} organisations across {len(authenticated_users)} users")
        return total_orgs
    
    # ==================== SUPPLIER TESTS ====================
    
    async def test_create_supplier(self, user: TestUser, org_id: int) -> Optional[int]:
        if org_id <= 0:
            return None
            
        print(f"\n🏥 Creating supplier for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        supplier_data = generate_random_supplier_data(org_id, user.id)
        location_data = generate_random_location_data()
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/suppliers",
                json={
                    "provider": supplier_data,
                    "location": location_data
                },
                headers=headers
            )
            
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
                    
                    if user.id not in self.context.user_supplier_mapping:
                        self.context.user_supplier_mapping[user.id] = []
                    self.context.user_supplier_mapping[user.id].append(supplier_id)
                    
                    print(f"   ✅ Created supplier: {supplier_id} for user {user.id}")
                    self.print_result("Create Supplier", True, f"Supplier {supplier_id} created")
                    return supplier_id
                else:
                    print(f"   ⚠️ Could not extract supplier ID from response")
                    return 0
            else:
                print(f"   ❌ Failed to create supplier: {response.status_code}")
                self.print_result("Create Supplier", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Supplier creation error: {e}")
            self.print_result("Create Supplier", False, str(e))
            return None
    
    async def create_suppliers_for_all_users(self, suppliers_per_org: int = 3):
        """Create suppliers for all organisations"""
        print(f"\n🏥 Creating {suppliers_per_org} suppliers per organisation...")
        
        authenticated_users = [u for u in self.context.users if u.access_token]
        total_suppliers = 0
        
        for user in authenticated_users:
            orgs = self.context.user_org_mapping.get(user.id, [])
            for org_id in orgs:
                for i in range(suppliers_per_org):
                    supplier_id = await self.test_create_supplier(user, org_id)
                    if supplier_id and supplier_id > 0:
                        total_suppliers += 1
        
        print(f"✅ Created {total_suppliers} suppliers across all organisations")
        return total_suppliers
    
    # ==================== PRODUCT TESTS ====================
    
    async def test_create_product(self, user: TestUser, supplier_id: int) -> Optional[int]:
        if supplier_id <= 0:
            return None
            
        headers = self.get_auth_headers(user)
        if not headers:
            return None
        
        product_data = generate_random_product_data(supplier_id, user.id)
        product_image = generate_random_product_image_data()
        iproduct_data = generate_random_iproduct_data()
        
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
            
            if response.status_code == 201:
                result = response.json()
                product_id = self.extract_id_from_response(result, ['id_product', 'id', 'product_id'])
                if product_id > 0:
                    self.context.created_products.append(product_id)
                    print(f"   ✅ Created product: {product_id}")
                    return product_id
            return None
        except Exception as e:
            print(f"   ❌ Error creating product: {e}")
            return None
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, skip_user_creation: bool = False, 
                       skip_login: bool = False,
                       context_file: str = "test_context.json"):
        print("\n" + "="*70)
        print("🚀 GLUTTEX API TEST RUNNER - MASSIVE DATA")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Load context
        if Path(context_file).exists():
            loaded = self.context.load(context_file)
            if loaded:
                print(f"📂 Loaded {len(self.context.users)} users from context")
        
        # Create users
        if not skip_user_creation and not self.context.users:
            print("\n📝 Creating Test Users")
            print("="*70)
            await self.create_multiple_users(20)  # 20 users
        elif self.context.users:
            print(f"\n📋 Using {len(self.context.users)} existing users")
        
        if not self.context.users:
            print("\n❌ No users available. Cannot continue.")
            return
        
        # Login
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
        
        self.test_user = authenticated_users[0]
        print(f"\n👤 Using user '{self.test_user.username}' (ID: {self.test_user.id})")
        
        # ==================== RUN TESTS ====================
        print("\n" + "="*70)
        print("🧪 Running Tests")
        print("="*70)
        
        # Step 1: Create Organisations (3 per user)
        print("\n🏢 STEP 1: Creating Organisations")
        print("="*70)
        await self.create_organisations_for_all_users(orgs_per_user=3)
        
        # Step 2: Create Suppliers (3 per organisation)
        print("\n🏥 STEP 2: Creating Suppliers")
        print("="*70)
        await self.create_suppliers_for_all_users(suppliers_per_org=3)
        
        # Step 3: Create Products (5 per supplier)
        print("\n📦 STEP 3: Creating Products")
        print("="*70)
        product_count = 0
        for user in authenticated_users:
            suppliers = self.context.user_supplier_mapping.get(user.id, [])
            for supplier_id in suppliers[:5]:  # Limit to 5 suppliers per user
                for i in range(5):
                    product_id = await self.test_create_product(user, supplier_id)
                    if product_id:
                        product_count += 1
        print(f"✅ Created {product_count} products")
        
        # Step 4: Create Staff Rules
        print("\n👥 STEP 4: Creating Staff Rules")
        print("="*70)
        rule_count = 0
        for user in authenticated_users:
            suppliers = self.context.user_supplier_mapping.get(user.id, [])
            for supplier_id in suppliers[:3]:
                # Create a staff rule for each supplier
                rule_codes = [27, 45, 60, 12, 33, 78, 91, 56, 23, 67]
                rule_data = {
                    "rule_ref_org": self.context.user_org_mapping.get(user.id, [0])[0],
                    "rule_ref_provider": supplier_id,
                    "rule_ref_user": user.id,
                    "management_rule_code": random.choice(rule_codes),
                    "management_rule_status": random.choice(["PENDING", "ACTIVE"]),
                    "management_rule_expiry": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat()
                }
                
                try:
                    headers = self.get_auth_headers(user)
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/staff",
                        json=rule_data,
                        headers=headers
                    )
                    if response.status_code == 201:
                        self.context.created_staff_rules.append(1)  # Just track count
                        rule_count += 1
                except:
                    pass
        
        print(f"✅ Created {rule_count} staff rules")
        
        # Save context
        print("\n💾 Saving Test Context")
        print("="*70)
        self.context.save(context_file)
        
        # Summary
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
        print(f"   👥 Staff Rules: {len(self.context.created_staff_rules)}")
        
        # User distribution stats
        print(f"\n📊 Distribution:")
        print(f"   👤 Users with Orgs: {len(self.context.user_org_mapping)}")
        print(f"   👤 Users with Suppliers: {len(self.context.user_supplier_mapping)}")
        
        # Expected totals
        expected_users = len(self.context.users)
        expected_orgs = len(self.context.created_organisations)
        expected_suppliers = len(self.context.created_suppliers)
        expected_products = len(self.context.created_products)
        
        print(f"\n📈 Expected Totals:")
        print(f"   👤 Users: {expected_users}")
        print(f"   🏢 Organisations: {expected_orgs} (3 per user)")
        print(f"   🏥 Suppliers: {expected_suppliers} (3 per org)")
        print(f"   📦 Products: {expected_products} (5 per supplier)")
        
        if self.context.created_organisations:
            print(f"\n🏢 Org IDs: {', '.join(map(str, self.context.created_organisations[:10]))}{'...' if len(self.context.created_organisations) > 10 else ''}")
        if self.context.created_suppliers:
            print(f"🏥 Supplier IDs: {', '.join(map(str, self.context.created_suppliers[:10]))}{'...' if len(self.context.created_suppliers) > 10 else ''}")
        if self.context.created_products:
            print(f"📦 Product IDs: {', '.join(map(str, self.context.created_products[:10]))}{'...' if len(self.context.created_products) > 10 else ''}")
        
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
    
    parser = argparse.ArgumentParser(description="Gluttex API Test Runner - Massive Data")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--skip-user-creation", action="store_true")
    parser.add_argument("--skip-login", action="store_true")
    parser.add_argument("--context-file", default="test_context.json")
    parser.add_argument("--clear-context", action="store_true")
    
    args = parser.parse_args()
    
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context file")
    
    async with EnhancedTestRunner(args.url) as runner:
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