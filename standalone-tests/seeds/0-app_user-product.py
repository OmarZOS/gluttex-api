#!/usr/bin/env python3
"""
Gluttex API Test Runner - Optimized Data Generation
Run with: python test_runner.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================================
# REALISTIC DATA - PRE-GENERATED FOR SPEED
# ============================================================================

REAL_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Ali", "Fatima", "Youssef", "Amina", "Karim", "Sara",
    "Nadia", "Rachid", "Leila", "Hassan", "Khadija", "Omar", "Soukaina",
    "Hamza", "Salma", "Mehdi", "Yasmina", "Anas", "Imane", "Reda", "Nour",
    "Zakaria", "Houda", "Ayoub", "Maryam", "Amine", "Sana", "Adil"
]

REAL_LAST_NAMES = [
    "Benali", "Khan", "Cohen", "Lopez", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Peterson", "Murphy", "Cook", "Morgan", "Bell",
    "Ward", "Watson", "Brooks", "Kelly", "Sanders", "Price"
]

REAL_ORG_NAMES = [
    "HealthCare Plus", "MediCorp", "Wellness Center", "Global Health",
    "Premium Care", "MediServe", "HealthFirst", "CarePlus", "MediHealth",
    "WellnessWorks", "City Medical", "Advanced Care", "Prime Health",
    "Elite Medical", "Family Care", "Specialist Center", "Medical Arts",
    "LifeLine Health", "CareBridge", "MediLink", "HealthWave", "VitalCare"
]

REAL_SUPPLIER_NAMES = [
    "City Medical Center", "HealthFirst Clinic", "MediLab Services",
    "PharmaCare", "Advanced Medical Supplies", "Precision Diagnostics",
    "Wellness Medical Group", "Prime Healthcare", "Elite Medical Services",
    "CarePlus Pharmacy", "MediHealth Solutions", "Global Medical Supply"
]

REAL_PRODUCT_NAMES = [
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Vitamin C", "Omega-3",
    "Antibiotic", "Pain Relief", "Allergy Medicine", "Cough Syrup",
    "Blood Pressure Monitor", "Stethoscope", "Syringe", "Bandage",
    "Antiseptic", "Thermometer", "Surgical Mask", "Hand Sanitizer"
]

REAL_STREETS = [
    "Rue Didouche Mourad", "Avenue du 1er Novembre", "Rue Larbi Ben Mhidi",
    "Boulevard Krim Belkacem", "Rue des Freres Bouadou", "Avenue de l'Independance",
    "Rue Ali Khodja", "Boulevard Colonel Amirouche", "Rue Emir Abdelkader"
]

REAL_CITIES = [
    "Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif",
    "Tizi Ouzou", "Bejaia", "Batna", "Sidi Bel Abbes", "Biskra", "Tebessa"
]

SPECIALITIES = [
    "cardiology", "neurology", "pediatrics", "orthopedics", "general medicine",
    "dermatology", "ophthalmology", "oncology", "gynecology", "urology",
    "psychiatry", "radiology", "dentistry", "emergency medicine", "surgery"
]

PROVIDER_TYPES = ["Medical", "Pharmacy", "Diagnostic", "Surgical", "Laboratory", "Dental"]


# ============================================================================
# ENUMS
# ============================================================================

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class AppUserType(str, Enum):
    PROVIDER = "provider"
    CUSTOMER = "customer"
    PATIENT = "patient"
    GUEST = "guest"

class CountryCode(str, Enum):
    DZ = "DZ"
    MA = "MA"
    TN = "MA"
    EG = "EG"
    SA = "SA"
    AE = "AE"
    US = "US"
    FR = "FR"
    DE = "DE"
    IT = "IT"
    ES = "ES"
    CA = "CA"
    GB = "GB"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestUser:
    id: int = 0
    username: str = ""
    email: str = ""
    password: str = ""
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
    created_organisations: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_staff_rules: List[int] = field(default_factory=list)
    user_org_mapping: Dict[int, List[int]] = field(default_factory=dict)
    user_supplier_mapping: Dict[int, List[int]] = field(default_factory=dict)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def save(self, filename: str = "test_context.json"):
        data = {
            'users': [u.to_dict() for u in self.users],
            'created_organisations': self.created_organisations,
            'created_suppliers': self.created_suppliers,
            'created_products': self.created_products,
            'created_staff_rules': self.created_staff_rules,
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
            self.created_organisations = data.get('created_organisations', [])
            self.created_suppliers = data.get('created_suppliers', [])
            self.created_products = data.get('created_products', [])
            self.created_staff_rules = data.get('created_staff_rules', [])
            self.user_org_mapping = data.get('user_org_mapping', {})
            self.user_supplier_mapping = data.get('user_supplier_mapping', {})
            print(f"📂 Test context loaded from {filename}")
            return True
        return False


# ============================================================================
# FAST GENERATORS
# ============================================================================

def get_random_item(lst: List) -> Any:
    return random.choice(lst)

def generate_user_data(user_type: str = None) -> Dict[str, Any]:
    first = get_random_item(REAL_FIRST_NAMES)
    last = get_random_item(REAL_LAST_NAMES)
    
    return {
        "app_user_name": f"{first.lower()}.{last.lower()}".replace(" ", ""),
        "app_user_password": "Test123!@#",
        "app_user_email": f"{first.lower()}.{last.lower()}@example.com".replace(" ", ""),
        "app_user_type": user_type or get_random_item([t.value for t in AppUserType]),
        "app_user_preferences": {
            "theme": get_random_item(["dark", "light"]),
            "notifications": random.choice([True, False]),
            "language": get_random_item(["en", "fr", "ar"])
        }
    }

def generate_person_data() -> Dict[str, Any]:
    return {
        "person_first_name": get_random_item(REAL_FIRST_NAMES),
        "person_last_name": get_random_item(REAL_LAST_NAMES),
        "person_birth_date": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "person_gender": get_random_item([Gender.MALE.value, Gender.FEMALE.value]),
        "person_country_code": get_random_item([c.value for c in CountryCode])
    }

def generate_location_data() -> Dict[str, Any]:
    return {
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": get_random_item(["Home", "Work", "Clinic", "Office", "Shop", "Warehouse"]),
        "address_street": f"{random.randint(1, 999)} {get_random_item(REAL_STREETS)}",
        "address_city": get_random_item(REAL_CITIES),
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": get_random_item([c.value for c in CountryCode])
    }

def generate_organisation_data() -> Dict[str, Any]:
    name = get_random_item(REAL_ORG_NAMES)
    return {
        "provider_organisation_name": f"{name} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Leading healthcare provider specializing in {get_random_item(SPECIALITIES)}"
    }

def generate_supplier_data(org_id: int, owner_id: int) -> Dict[str, Any]:
    name = get_random_item(REAL_SUPPLIER_NAMES)
    return {
        "id_provider_owner": owner_id,
        "id_provider_organisation": org_id,
        "id_product_provider_type": random.randint(1, 6),
        "product_provider_type_desc": get_random_item(PROVIDER_TYPES),
        "provider_organisation_name": f"{name} {uuid.uuid4().hex[:4]}",
        "provider_name": f"Provider_{uuid.uuid4().hex[:8]}",
        "provider_contact_info": json.dumps({
            "phone": f"+213-5{random.randint(10, 99):02d}{random.randint(10, 99):02d}{random.randint(10, 99):02d}",
            "email": f"contact_{uuid.uuid4().hex[:4]}@example.com"
        })
    }

def generate_product_data(provider_id: int, owner_id: int) -> Dict[str, Any]:
    return {
        "product_name": f"{get_random_item(REAL_PRODUCT_NAMES)} {uuid.uuid4().hex[:4]}",
        "product_brand": get_random_item(["BrandA", "BrandB", "BrandC", "Generic", "Premium"]),
        "product_provider_id": provider_id,
        "product_category_id": random.randint(1, 5),
        "product_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "product_description": f"High-quality {get_random_item(PROVIDER_TYPES).lower()} product",
        "product_price": round(random.uniform(5.0, 200.0), 2),
        "product_quantity": random.randint(10, 500),
        "product_quantifier": get_random_item(["mg", "g", "ml", "pack", "unit"]),
        "product_owner": owner_id
    }


# ============================================================================
# OPTIMIZED TEST RUNNER
# ============================================================================

class OptimizedTestRunner:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.context = TestContext()
        self.test_user = None
        self._used_assignments: Set[str] = set()
        
        # Pre-generate all data for speed
        self._pre_generated_users = []
        self._pre_generated_orgs = []
        self._pre_generated_suppliers = []
        self._pre_generated_products = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def get_auth_headers(self, user: TestUser) -> Dict[str, str]:
        if user.access_token:
            return {"Authorization": f"Bearer {user.access_token}"}
        return {}
    
    def extract_id(self, response_data: Dict[str, Any], keys: List[str]) -> int:
        if not response_data:
            return 0
        
        for key in keys:
            if key in response_data:
                try:
                    return int(response_data[key])
                except (ValueError, TypeError):
                    pass
        
        if 'data' in response_data and isinstance(response_data['data'], dict):
            return self.extract_id(response_data['data'], keys)
        
        return 0
    
    def print_result(self, name: str, passed: bool, details: str = ""):
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
        if details:
            print(f"     {details}")
        self.context.test_results.append({"name": name, "passed": passed, "details": details})
    
    # ==================== FAST BATCH OPERATIONS ====================
    
    async def create_user(self, user_data: Dict = None, person_data: Dict = None, 
                         location_data: Dict = None) -> Optional[TestUser]:
        if user_data is None:
            user_data = generate_user_data()
        
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
                user_id = self.extract_id(result, ['id_app_user', 'id', 'user_id'])
                
                if user_id > 0:
                    return TestUser(
                        id=user_id,
                        username=user_data.get('app_user_name', ''),
                        email=user_data.get('app_user_email', ''),
                        password=user_data.get('app_user_password', 'Test123!@#'),
                        user_data=user_data,
                        person_data=person_data or {},
                        location_data=location_data or {}
                    )
            return None
        except Exception:
            return None
    
    async def create_users_batch(self, count: int = 10) -> List[TestUser]:
        print(f"\n👥 Creating {count} users...")
        
        # Generate all data first
        users_data = []
        for i in range(count):
            user_type = ["provider", "customer", "patient", "guest"][i % 4]
            user_data = generate_user_data(user_type)
            person_data = generate_person_data()
            location_data = generate_location_data()
            users_data.append((user_data, person_data, location_data))
        
        # Create users in parallel
        tasks = [self.create_user(*data) for data in users_data]
        results = await asyncio.gather(*tasks)
        
        created = [u for u in results if u]
        for u in created:
            self.context.users.append(u)
        
        print(f"✅ Created {len(created)}/{count} users")
        return created
    
    async def login_user(self, user: TestUser) -> bool:
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
                token = result.get('access_token')
                if token:
                    user.access_token = token
                    user.refresh_token = result.get('refresh_token')
                    user.token_expires_at = datetime.now() + timedelta(hours=1)
                    return True
            return False
        except Exception:
            return False
    
    async def login_users_batch(self) -> int:
        print("\n🔐 Logging in users...")
        tasks = [self.login_user(u) for u in self.context.users]
        results = await asyncio.gather(*tasks)
        success_count = sum(1 for r in results if r)
        print(f"✅ Logged in {success_count}/{len(self.context.users)} users")
        return success_count
    
    # ==================== BATCH CREATION ====================
    
    async def create_organisations_batch(self, user: TestUser, count: int = 3) -> List[int]:
        print(f"\n🏢 Creating {count} organisations for user {user.id}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            return []
        
        org_ids = []
        tasks = []
        
        for _ in range(count):
            org_data = generate_organisation_data()
            tasks.append(self.client.post(
                f"{self.base_url}/api/v1/organisations",
                json={"organisation": org_data},
                headers=headers
            ))
        
        responses = await asyncio.gather(*tasks)
        
        for resp in responses:
            if resp.status_code in [200, 201]:
                org_id = self.extract_id(resp.json(), [
                    'idprovider_organisation', 'id_provider_organisation', 'id', 'organisation_id'
                ])
                if org_id > 0:
                    org_ids.append(org_id)
                    self.context.created_organisations.append(org_id)
        
        if org_ids:
            self.context.user_org_mapping[user.id] = org_ids
        
        print(f"✅ Created {len(org_ids)} organisations")
        return org_ids
    
    async def create_suppliers_batch(self, user: TestUser, org_ids: List[int], 
                                    count_per_org: int = 2) -> List[int]:
        print(f"\n🏥 Creating suppliers for user {user.id}...")
        
        headers = self.get_auth_headers(user)
        if not headers or not org_ids:
            return []
        
        supplier_ids = []
        tasks = []
        
        for org_id in org_ids:
            for _ in range(count_per_org):
                sup_data = generate_supplier_data(org_id, user.id)
                loc_data = generate_location_data()
                tasks.append(self.client.post(
                    f"{self.base_url}/api/v1/suppliers",
                    json={"provider": sup_data, "location": loc_data},
                    headers=headers
                ))
        
        responses = await asyncio.gather(*tasks)
        
        for resp in responses:
            if resp.status_code in [200, 201]:
                sup_id = self.extract_id(resp.json(), [
                    'id_product_provider', 'idprovider', 'id', 'supplier_id'
                ])
                if sup_id > 0:
                    supplier_ids.append(sup_id)
                    self.context.created_suppliers.append(sup_id)
        
        if supplier_ids:
            self.context.user_supplier_mapping[user.id] = supplier_ids
        
        print(f"✅ Created {len(supplier_ids)} suppliers")
        return supplier_ids
    
    async def create_products_batch(self, user: TestUser, supplier_ids: List[int],
                                   count_per_supplier: int = 2) -> int:
        print(f"\n📦 Creating products for user {user.id}...")
        
        headers = self.get_auth_headers(user)
        if not headers or not supplier_ids:
            return 0
        
        tasks = []
        for sup_id in supplier_ids:
            for _ in range(count_per_supplier):
                prod_data = generate_product_data(sup_id, user.id)
                tasks.append(self.client.post(
                    f"{self.base_url}/api/v1/products",
                    json={"product": prod_data},
                    headers=headers
                ))
        
        responses = await asyncio.gather(*tasks)
        count = 0
        
        for resp in responses:
            if resp.status_code == 201:
                prod_id = self.extract_id(resp.json(), ['id_product', 'id', 'product_id'])
                if prod_id > 0:
                    self.context.created_products.append(prod_id)
                    count += 1
        
        print(f"✅ Created {count} products")
        return count
    
    async def create_staff_rules_batch(self, owner_user: TestUser, supplier_ids: List[int],
                                      target_users: List[TestUser]) -> int:
        print(f"\n👥 Creating staff rules...")
        
        headers = self.get_auth_headers(owner_user)
        if not headers or not supplier_ids or not target_users:
            return 0
        
        # Get org for this user
        org_ids = self.context.user_org_mapping.get(owner_user.id, [])
        if not org_ids:
            return 0
        
        rule_codes = [27, 45, 60, 12, 33, 78, 91, 56, 23, 67]
        total_rules = 0
        
        for supplier_id in supplier_ids:
            # Skip if supplier owner is the target
            for target in target_users:
                # Check if target is the owner
                is_owner = False
                for uid, suppliers in self.context.user_supplier_mapping.items():
                    if supplier_id in suppliers:
                        if uid == target.id:
                            is_owner = True
                        break
                
                if is_owner:
                    continue
                
                # Check if already assigned
                key = f"{target.id}_{supplier_id}"
                if key in self._used_assignments:
                    continue
                
                rule_data = {
                    "rule_ref_org": org_ids[0],
                    "rule_ref_provider": supplier_id,
                    "rule_ref_user": target.id,
                    "management_rule_code": get_random_item(rule_codes),
                    "management_rule_status": get_random_item(["PENDING", "ACTIVE"]),
                    "management_rule_expiry": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat()
                }
                
                try:
                    resp = await self.client.post(
                        f"{self.base_url}/api/v1/staff",
                        json=rule_data,
                        headers=headers
                    )
                    if resp.status_code == 201:
                        self.context.created_staff_rules.append(1)
                        self._used_assignments.add(key)
                        total_rules += 1
                except Exception:
                    pass
        
        print(f"✅ Created {total_rules} staff rules")
        return total_rules
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, skip_user_creation: bool = False,
                       skip_login: bool = False,
                       context_file: str = "test_context.json"):
        print("\n" + "="*60)
        print("🚀 GLUTTEX API TEST RUNNER - OPTIMIZED")
        print("="*60)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        # Load context
        if Path(context_file).exists():
            self.context.load(context_file)
        
        # Create users
        if not skip_user_creation and not self.context.users:
            users = await self.create_users_batch(10)
        else:
            print(f"\n📋 Using {len(self.context.users)} existing users")
        
        if not self.context.users:
            print("\n❌ No users available")
            return
        
        # Login
        if not skip_login:
            await self.login_users_batch()
        
        authenticated = [u for u in self.context.users if u.access_token]
        if not authenticated:
            print("\n❌ No authenticated users")
            return
        
        self.test_user = authenticated[0]
        print(f"\n👤 Using primary user: {self.test_user.username} (ID: {self.test_user.id})")
        
        # Provider users for staff rules
        provider_users = [u for u in authenticated if u.user_data.get('app_user_type') == 'provider']
        if not provider_users:
            provider_users = authenticated[:3]
        
        print("\n" + "="*60)
        print("🧪 Running Tests")
        print("="*60)
        
        # 1. Create organisations
        orgs = await self.create_organisations_batch(self.test_user, count=3)
        
        # 2. Create suppliers
        suppliers = await self.create_suppliers_batch(self.test_user, orgs, count_per_org=2)
        
        # 3. Create products
        products_count = await self.create_products_batch(self.test_user, suppliers, count_per_supplier=2)
        
        # 4. Create staff rules
        if len(provider_users) > 1:
            staff_count = await self.create_staff_rules_batch(
                self.test_user, suppliers, provider_users[:2]
            )
        
        # Save context
        self.context.save(context_file)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total = len(self.context.test_results)
        passed = sum(1 for r in self.context.test_results if r["passed"])
        
        print(f"\n📈 Tests: {total} total, {passed} passed")
        print(f"👤 Users: {len(self.context.users)}")
        print(f"🔐 Authenticated: {len([u for u in self.context.users if u.access_token])}")
        print(f"🏢 Organisations: {len(self.context.created_organisations)}")
        print(f"🏥 Suppliers: {len(self.context.created_suppliers)}")
        print(f"📦 Products: {len(self.context.created_products)}")
        print(f"👥 Staff Rules: {len(self.context.created_staff_rules)}")
        print(f"📊 Staff Assignments: {len(self._used_assignments)}")
        
        print("\n" + "="*60)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gluttex API Test Runner - Optimized")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--skip-user-creation", action="store_true")
    parser.add_argument("--skip-login", action="store_true")
    parser.add_argument("--context-file", default="test_context.json")
    parser.add_argument("--clear-context", action="store_true")
    
    args = parser.parse_args()
    
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context file")
    
    async with OptimizedTestRunner(args.url) as runner:
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