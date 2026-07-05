#!/usr/bin/env python3
"""
Test script for Service endpoints with proper product references.
Run with: python test_service_endpoints.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestResult:
    """Test result container"""
    name: str
    passed: bool
    details: str = ""
    response: Any = None


@dataclass
class TestUser:
    """Test user with authentication data"""
    id: int = 0
    username: str = ""
    email: str = ""
    password: str = ""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    def is_token_valid(self) -> bool:
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at


@dataclass
class TestContext:
    """Test context containing all fetched data"""
    users: List[TestUser] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    providers: List[Dict[str, Any]] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    created_services: List[Dict[str, Any]] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_organisations: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    auth_token: Optional[str] = None
    
    @property
    def category_ids(self) -> List[int]:
        ids = []
        for c in self.categories:
            cid = c.get('id_product_category')
            if cid is None:
                cid = c.get('id')
            if cid and isinstance(cid, int):
                ids.append(cid)
        return ids
    
    @property
    def provider_ids(self) -> List[int]:
        ids = []
        for p in self.providers:
            pid = p.get('id_product_provider')
            if pid is None:
                pid = p.get('id')
            if pid and isinstance(pid, int):
                ids.append(pid)
        return ids
    
    @property
    def product_ids(self) -> List[int]:
        ids = []
        for p in self.products:
            pid = p.get('id_product')
            if pid is None:
                pid = p.get('id')
            if pid and isinstance(pid, int):
                ids.append(pid)
        return ids
    
    @property
    def service_ids(self) -> List[int]:
        ids = []
        for s in self.created_services:
            sid = s.get('provided_service_id')
            if sid is None:
                sid = s.get('id')
            if sid and isinstance(sid, int):
                ids.append(sid)
        return ids
    
    def get_random_category_id(self) -> int:
        if not self.category_ids:
            return 1
        return random.choice(self.category_ids)
    
    def get_random_provider_id(self) -> int:
        if not self.provider_ids:
            return 1
        return random.choice(self.provider_ids)
    
    def get_random_product_id(self) -> int:
        if not self.product_ids:
            return 0
        return random.choice(self.product_ids)
    
    def get_random_service_id(self) -> int:
        if not self.service_ids:
            return 0
        return random.choice(self.service_ids)
    
    def get_auth_headers(self) -> Dict[str, str]:
        for user in self.users:
            if user.is_token_valid():
                return {"Authorization": f"Bearer {user.access_token}"}
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    def get_first_valid_token(self) -> Optional[str]:
        for user in self.users:
            if user.is_token_valid():
                return user.access_token
        return self.auth_token
    
    def load_from_file(self, filename: str = "test_context.json") -> bool:
        if not Path(filename).exists():
            return False
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        user_data = data.get('users', [])
        for u in user_data:
            user = TestUser(
                id=u.get('id', 0),
                username=u.get('username', ''),
                email=u.get('email', ''),
                password=u.get('password', ''),
                access_token=u.get('access_token'),
                refresh_token=u.get('refresh_token')
            )
            expires_at = u.get('token_expires_at')
            if expires_at:
                try:
                    user.token_expires_at = datetime.fromisoformat(expires_at)
                except:
                    pass
            self.users.append(user)
        
        self.created_products = data.get('created_products', [])
        self.created_organisations = data.get('created_organisations', [])
        self.created_suppliers = data.get('created_suppliers', [])
        
        token = self.get_first_valid_token()
        if token:
            self.auth_token = token
        
        return True
    
    def save_to_file(self, filename: str = "test_context.json") -> None:
        data = {
            'users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'password': u.password,
                    'access_token': u.access_token,
                    'refresh_token': u.refresh_token,
                    'token_expires_at': u.token_expires_at.isoformat() if u.token_expires_at else None
                }
                for u in self.users
            ],
            'created_products': self.created_products,
            'created_organisations': self.created_organisations,
            'created_suppliers': self.created_suppliers,
            'created_services': self.created_services,
            'timestamp': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Context saved to {filename}")


# ============================================================================
# DATA GENERATORS - FIXED WITH VALID PRODUCT REFERENCES
# ============================================================================

def generate_service_data(
    provider_id: int = 0,
    category_id: int = 0
) -> Dict[str, Any]:
    """Generate random service data"""
    
    service_names = [
        "Premium Cleaning Service",
        "Professional Plumbing",
        "Electrical Installation",
        "HVAC Maintenance",
        "Landscaping Service",
        "Home Renovation",
        "Painting Service",
        "Carpentry Work",
        "Tile Installation",
        "Roofing Service",
        "Garden Design",
        "Pool Maintenance",
        "Security System Installation",
        "Home Automation",
        "Solar Panel Installation",
        "Water Heater Repair",
        "Appliance Repair",
        "Flooring Installation",
        "Window Replacement",
        "Insulation Service"
    ]
    
    service_desc = [
        "Professional service with certified staff",
        "Quality workmanship guaranteed",
        "Fast and reliable service",
        "Licensed and insured professionals",
        "Free consultation and estimate",
        "Emergency service available",
        "Competitive pricing",
        "High-quality materials used",
        "Expert technicians with years of experience",
        "Satisfaction guaranteed",
        "Eco-friendly solutions available",
        "Customized service plans"
    ]
    
    quantifiers = ["unit", "hour", "session", "package", "job"]
    durations = [15, 30, 45, 60, 90, 120, 180, 240, 300, 360]
    
    return {
        "provided_service_product_provider_id": provider_id,
        "provided_service_category_id": category_id,
        "provided_service_name": random.choice(service_names),
        "provided_service_description": random.choice(service_desc),
        "provided_service_base_price": round(random.uniform(50.00, 500.00), 2),
        "provided_service_final_price": round(random.uniform(60.00, 600.00), 2),
        "provided_service_actual_duration": random.choice(durations),
        "provided_service_is_active": True,
        "provided_service_quantifier": random.choice(quantifiers)
    }


def generate_resource_requirement(service_id: int = 0, product_id: int = 0) -> Dict[str, Any]:
    """Generate random resource requirement with valid product reference."""
    
    resource_names = [
        "Cleaning supplies",
        "Electric drill set",
        "Piping materials",
        "HVAC equipment",
        "Landscaping tools",
        "Paint and brushes",
        "Wood materials",
        "Tile and grout",
        "Roofing materials",
        "Safety equipment",
        "Protective gear",
        "Cleaning chemicals",
        "Spare parts kit",
        "Measurement tools",
        "Power tools"
    ]
    
    resource_types = ["consumable", "tool", "material", "equipment"]
    
    product_ref = product_id if product_id > 0 else 1
    
    return {
        "resource_requirement_service_id": service_id,
        "resource_requirement_name": random.choice(resource_names),
        "resource_requirement_type": random.choice(resource_types),
        "resource_requirement_quantity": random.randint(1, 20),
        "resource_requirement_cost_per_unit": round(random.uniform(10.00, 200.00), 2),
        "resource_requirement_is_consumable": random.choice([True, False]),
        "resource_requirement_notes": f"Test requirement {uuid.uuid4().hex[:6]}",
        "resource_requirement_product_ref": product_ref
    }



def generate_staff_requirement(service_id: int = 0) -> Dict[str, Any]:
    """Generate random staff requirement with valid role IDs."""
    
    # Staff role IDs (must exist in staff_role table)
    # Adjust these IDs based on your actual staff_role table data
    staff_role_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Mapping of role IDs to names (for display only)
    role_names = {
        1: "Technician",
        2: "Electrician",
        3: "Plumber",
        4: "Painter",
        5: "Carpenter",
        6: "Landscaper",
        7: "HVAC Specialist",
        8: "General Laborer",
        9: "Supervisor",
        10: "Project Manager"
    }
    
    role_id = random.choice(staff_role_ids)
    
    return {
        "service_staff_requirement_service_id": service_id,
        "service_staff_requirement_role": role_id,  # Now sending integer ID
        "service_staff_requirement_notes": f"Test staff req {uuid.uuid4().hex[:6]}",
        "service_staff_requirement_min_count": random.randint(1, 3),
        "service_staff_requirement_max_count": random.randint(3, 6),
        "service_staff_requirement_hourly_rate": round(random.uniform(20.00, 100.00), 2),
        "service_staff_requirement_allocated_hours": random.randint(2, 8)
    }



# ============================================================================
# TEST RUNNER
# ============================================================================

class ServiceTester:
    """Test runner for service endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None
        self.context = TestContext()
        self.results: List[TestResult] = []
        self.context_file = "test_context.json"
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    # ==================== HTTP Helpers ====================
    
    async def _get(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.get(
                f"{self.base_url}{path}", 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _post(self, path: str, json_data: Dict) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.post(
                f"{self.base_url}{path}", 
                json=json_data,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _put(self, path: str, json_data: Dict) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.put(
                f"{self.base_url}{path}", 
                json=json_data,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _delete(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.delete(
                f"{self.base_url}{path}", 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _patch(self, path: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.patch(
                f"{self.base_url}{path}", 
                json=json_data, 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    # ==================== Data Fetching ====================
    
    async def load_context(self) -> bool:
        loaded = self.context.load_from_file(self.context_file)
        if loaded:
            print(f"\n📂 Loaded context from {self.context_file}")
            print(f"   👤 Users: {len(self.context.users)}")
            print(f"   🏢 Organisations: {len(self.context.created_organisations)}")
            print(f"   🏥 Suppliers: {len(self.context.created_suppliers)}")
            print(f"   📦 Products: {len(self.context.created_products)}")
            
            token = self.context.get_first_valid_token()
            if token:
                print(f"   🔐 Valid authentication token found")
            else:
                print(f"   ⚠️ No valid authentication token found")
        return loaded
    
    async def fetch_categories(self) -> bool:
        print("\n📋 Fetching categories...")
        status, data = await self._get("/api/v1/products/category/all")
        
        if status != 200:
            print(f"   ❌ Failed to fetch categories: {status}")
            return False
        
        if isinstance(data, list):
            self.context.categories = data
        elif isinstance(data, dict):
            self.context.categories = data.get("data", data.get("items", []))
        else:
            self.context.categories = []
        
        print(f"   ✅ Found {len(self.context.categories)} categories")
        for cat in self.context.categories[:5]:
            cid = cat.get('id_product_category', cat.get('id', 'N/A'))
            name = cat.get('product_category_name', cat.get('name', 'Unknown'))
            print(f"      - ID: {cid}, Name: {name}")
        
        return True
    
    async def fetch_providers(self) -> bool:
        print("\n📋 Fetching providers...")
        status, data = await self._get("/api/v1/suppliers", {"offset": 0, "limit": 100})
        
        if status != 200:
            print(f"   ❌ Failed to fetch providers: {status}")
            return False
        
        if isinstance(data, list):
            self.context.providers = data
        elif isinstance(data, dict):
            self.context.providers = data.get("data", data.get("items", []))
        else:
            self.context.providers = []
        
        print(f"   ✅ Found {len(self.context.providers)} providers")
        for prov in self.context.providers[:5]:
            pid = prov.get('id_product_provider', prov.get('id', 'N/A'))
            name = prov.get('provider_name', prov.get('name', 'Unknown'))
            print(f"      - ID: {pid}, Name: {name}")
        
        return True
    
    async def fetch_products(self, provider_id: int) -> bool:
        print(f"\n📋 Fetching products for provider {provider_id}...")
        
        user_id = self.context.users[0].id if self.context.users else 0
        
        status, data = await self._get(
            f"/api/v1/products/{user_id}/{provider_id}/0/0/50",
            {}
        )
        
        if status != 200:
            print(f"   ❌ Failed to fetch products: {status}")
            return False
        
        if isinstance(data, list):
            self.context.products = data
        elif isinstance(data, dict):
            self.context.products = data.get("data", data.get("items", []))
        else:
            self.context.products = []
        
        print(f"   ✅ Found {len(self.context.products)} products")
        for prod in self.context.products[:5]:
            pid = prod.get('id_product', prod.get('id', 'N/A'))
            name = prod.get('product_name', 'Unknown')
            print(f"      - ID: {pid}, Name: {name}")
        
        return True
    
    async def fetch_all_data(self) -> bool:
        print("\n" + "="*50)
        print("📊 FETCHING EXISTING DATA")
        print("="*50)
        
        cat_ok = await self.fetch_categories()
        prov_ok = await self.fetch_providers()
        
        # Fetch products for the first provider
        if self.context.provider_ids:
            provider_id = self.context.provider_ids[0]
            await self.fetch_products(provider_id)
        
        if not cat_ok:
            print("\n⚠️  Could not fetch categories. Using fallback category IDs: 1-10")
            for i in range(1, 11):
                self.context.categories.append({
                    "id_product_category": i,
                    "product_category_name": f"Category_{i}"
                })
            cat_ok = True
        
        # Make sure we have products for resource requirements
        if not self.context.product_ids:
            print("\n⚠️  No products found! Using fallback product ID: 1")
            self.context.products.append({
                "id_product": 1,
                "product_name": "Fallback Product",
                "product_quantity": 100
            })
        
        return cat_ok and prov_ok
    
    # ==================== Test Methods ====================
    
    def _add_result(self, name: str, passed: bool, details: str = "", response: Any = None):
        result = TestResult(name=name, passed=passed, details=details, response=response)
        self.results.append(result)
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
    
    # ==================== Test Cases - Creation ====================
    
    async def test_create_service_minimal(self) -> bool:
        """Test creating a service with minimal data"""
        print("\n📦 Test: Create Service (Minimal Data)")
        
        provider_id = self.context.get_random_provider_id()
        category_id = self.context.get_random_category_id()
        
        if not provider_id:
            self._add_result("Create Service Minimal", False, "No providers available")
            return False
        
        if not category_id:
            self._add_result("Create Service Minimal", False, "No categories available")
            return False
        
        service = generate_service_data(provider_id, category_id)
        
        print(f"   Provider ID: {provider_id}")
        print(f"   Category ID: {category_id}")
        print(f"   Service Name: {service['provided_service_name']}")
        
        status, data = await self._post(
            "/api/v1/business/services",
            {
                "service": service,
                "requirements": [],
                "staff_requirements": []
            }
        )
        
        passed = status == 201
        if passed and data:
            self.context.created_services.append(data)
        
        details = f"Status: {status}"
        if data and isinstance(data, dict):
            details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Service Minimal", passed, details, data if passed else None)
        return passed
    
    async def test_create_service_with_requirements(self) -> bool:
        """Test creating a service with resource and staff requirements"""
        print("\n📦 Test: Create Service with Requirements")
        
        provider_id = self.context.get_random_provider_id()
        category_id = self.context.get_random_category_id()
        product_id = self.context.get_random_product_id()
        
        if not provider_id:
            self._add_result("Create Service with Requirements", False, "No providers available")
            return False
        
        if not category_id:
            self._add_result("Create Service with Requirements", False, "No categories available")
            return False
        
        # If no product found, use a default product ID (must exist in DB)
        if not product_id:
            product_id = 1  # Fallback to product 1
            print(f"   ⚠️ No product found, using product_id: {product_id}")
        
        service = generate_service_data(provider_id, category_id)
        service_name = f"Full Service {uuid.uuid4().hex[:6]}"
        service["provided_service_name"] = service_name
        
        # Create requirements with proper product references (non-zero)
        requirements = [
            generate_resource_requirement(0, product_id),
            generate_resource_requirement(0, product_id),
            generate_resource_requirement(0, product_id)
        ]
        
        staff_requirements = [
            generate_staff_requirement(0),
            generate_staff_requirement(0)
        ]
        
        print(f"   Service: {service['provided_service_name']}")
        print(f"   Product ID for resources: {product_id}")
        print(f"   Resource Requirements: {len(requirements)}")
        print(f"   Staff Requirements: {len(staff_requirements)}")
        
        # Log the request data for debugging
        request_data = {
            "service": service,
            "requirements": requirements,
            "staff_requirements": staff_requirements
        }
        print(f"   📤 Requirements: {json.dumps(requirements, indent=2)[:300]}...")
        
        status, data = await self._post(
            "/api/v1/business/services",
            request_data
        )
        
        passed = status == 201
        if passed and data:
            self.context.created_services.append(data)
            service_id = data.get('provided_service_id')
            if service_id:
                print(f"   ✅ Service ID: {service_id}")
        
        details = f"Status: {status}"
        if data and isinstance(data, dict):
            details += f" - {data.get('message', data.get('detail', ''))}"
            if status != 201:
                details += f"\n   Response: {json.dumps(data, indent=2)[:300]}"
        
        self._add_result("Create Service with Requirements", passed, details, data if passed else None)
        return passed
    
    async def test_create_service_with_max_requirements(self) -> bool:
        """Test creating a service with maximum requirements"""
        print("\n📦 Test: Create Service with Maximum Requirements")
        
        provider_id = self.context.get_random_provider_id()
        category_id = self.context.get_random_category_id()
        product_id = self.context.get_random_product_id()
        
        if not provider_id:
            self._add_result("Create Service Max Requirements", False, "No providers available")
            return False
        
        if not product_id:
            product_id = 1
            print(f"   ⚠️ No product found, using product_id: {product_id}")
        
        service = generate_service_data(provider_id, category_id)
        service["provided_service_name"] = f"Max Service {uuid.uuid4().hex[:6]}"
        
        # Create many requirements with product references
        requirements = [
            generate_resource_requirement(0, product_id) for _ in range(5)
        ]
        
        staff_requirements = [
            generate_staff_requirement(0) for _ in range(4)
        ]
        
        print(f"   Service: {service['provided_service_name']}")
        print(f"   Resource Requirements: {len(requirements)}")
        print(f"   Staff Requirements: {len(staff_requirements)}")
        
        status, data = await self._post(
            "/api/v1/business/services",
            {
                "service": service,
                "requirements": requirements,
                "staff_requirements": staff_requirements
            }
        )
        
        passed = status == 201
        if passed and data:
            self.context.created_services.append(data)
        
        details = f"Status: {status}"
        if data and isinstance(data, dict):
            details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Service Max Requirements", passed, details, data if passed else None)
        return passed
    
    async def test_create_service_invalid_provider(self) -> bool:
        """Test creating a service with invalid provider ID (should fail)"""
        print("\n❌ Test: Create Service with Invalid Provider")
        
        category_id = self.context.get_random_category_id()
        
        if not category_id:
            self._add_result("Invalid Provider", False, "No categories available")
            return False
        
        service = generate_service_data(99999, category_id)
        
        status, data = await self._post(
            "/api/v1/business/services",
            {
                "service": service,
                "requirements": [],
                "staff_requirements": []
            }
        )
        
        passed = status in [400, 404, 422]
        self._add_result("Invalid Provider", passed, f"Correctly rejected (Status: {status})")
        return passed
    
    async def test_create_service_invalid_category(self) -> bool:
        """Test creating a service with invalid category ID (should fail)"""
        print("\n❌ Test: Create Service with Invalid Category")
        
        provider_id = self.context.get_random_provider_id()
        
        if not provider_id:
            self._add_result("Invalid Category", False, "No providers available")
            return False
        
        service = generate_service_data(provider_id, 99999)
        
        status, data = await self._post(
            "/api/v1/business/services",
            {
                "service": service,
                "requirements": [],
                "staff_requirements": []
            }
        )
        
        passed = status in [400, 404, 422]
        self._add_result("Invalid Category", passed, f"Correctly rejected (Status: {status})")
        return passed
    
    async def test_create_service_duplicate(self) -> bool:
        """Test creating a duplicate service (should fail)"""
        print("\n❌ Test: Create Service Duplicate")
        
        if not self.context.service_ids:
            self._add_result("Create Service Duplicate", False, "No services to duplicate")
            return False
        
        service_id = self.context.get_random_service_id()
        status, existing = await self._get(f"/api/v1/business/services/{service_id}")
        
        if status != 200:
            self._add_result("Create Service Duplicate", False, f"Failed to fetch service: {status}")
            return False
        
        service = {k: v for k, v in existing.items() if k != 'provided_service_id'}
        
        status, data = await self._post(
            "/api/v1/business/services",
            {
                "service": service,
                "requirements": [],
                "staff_requirements": []
            }
        )
        
        passed = status in [409, 400, 422]
        self._add_result("Create Service Duplicate", passed, f"Correctly blocked (Status: {status})")
        return passed
    
    # ==================== Test Cases - Reading ====================
    
    async def test_get_service_by_id(self) -> bool:
        """Test getting a service by ID"""
        print("\n📋 Test: Get Service by ID")
        
        if not self.context.service_ids:
            self._add_result("Get Service by ID", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, data = await self._get(f"/api/v1/business/services/{service_id}")
        
        passed = status == 200 and data is not None
        details = f"Status: {status}"
        if passed:
            details += f" - Name: {data.get('provided_service_name', 'Unknown')}"
        self._add_result("Get Service by ID", passed, details)
        return passed
    
    async def test_get_service_by_id_not_found(self) -> bool:
        """Test getting a non-existent service (should fail)"""
        print("\n❌ Test: Get Non-existent Service")
        
        status, data = await self._get("/api/v1/business/services/999999")
        
        passed = status == 404
        self._add_result("Get Non-existent Service", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_get_all_services(self) -> bool:
        """Test getting all services with filters"""
        print("\n📋 Test: Get All Services")
        
        status, data = await self._get("/api/v1/business/services", {"offset": 0, "limit": 10})
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get All Services", passed, f"Status: {status}, Count: {count}")
        return passed
    
    async def test_get_services_by_category(self) -> bool:
        """Test getting services by category"""
        print("\n📋 Test: Get Services by Category")
        
        category_id = self.context.get_random_category_id()
        if not category_id:
            self._add_result("Get Services by Category", False, "No categories available")
            return False
        
        print(f"   Category ID: {category_id}")
        
        status, data = await self._get(f"/api/v1/business/services/category/{category_id}")
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Services by Category", passed, f"Status: {status}, Found: {count}")
        return passed
    
    async def test_get_services_by_provider(self) -> bool:
        """Test getting services by provider"""
        print("\n📋 Test: Get Services by Provider")
        
        provider_id = self.context.get_random_provider_id()
        if not provider_id:
            self._add_result("Get Services by Provider", False, "No providers available")
            return False
        
        print(f"   Provider ID: {provider_id}")
        
        status, data = await self._get(f"/api/v1/business/services/provider/{provider_id}")
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Services by Provider", passed, f"Status: {status}, Found: {count}")
        return passed
    
    async def test_get_services_active_only(self) -> bool:
        """Test getting only active services"""
        print("\n📋 Test: Get Active Services")
        
        status, data = await self._get(
            "/api/v1/business/services",
            {"active_only": True, "offset": 0, "limit": 10}
        )
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Active Services", passed, f"Status: {status}, Count: {count}")
        return passed
    
    async def test_get_service_requirements(self) -> bool:
        """Test getting service requirements"""
        print("\n📋 Test: Get Service Requirements")
        
        if not self.context.service_ids:
            self._add_result("Get Service Requirements", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, data = await self._get(f"/api/v1/business/services/{service_id}/requirements")
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Service Requirements", passed, f"Status: {status}, Found: {count}")
        return passed
    
    async def test_get_service_staff_requirements(self) -> bool:
        """Test getting service staff requirements"""
        print("\n📋 Test: Get Service Staff Requirements")
        
        if not self.context.service_ids:
            self._add_result("Get Service Staff Requirements", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, data = await self._get(f"/api/v1/business/services/{service_id}/staff-requirements")
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Service Staff Requirements", passed, f"Status: {status}, Found: {count}")
        return passed
    
    # ==================== Test Cases - Updates ====================
    
    async def test_update_service(self) -> bool:
        """Test updating a service"""
        print("\n📝 Test: Update Service")
        
        if not self.context.service_ids:
            self._add_result("Update Service", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, existing = await self._get(f"/api/v1/business/services/{service_id}")
        if status != 200:
            self._add_result("Update Service", False, f"Failed to fetch service: {status}")
            return False
        
        updated_service = existing.copy()
        updated_service["provided_service_name"] = f"Updated Service {uuid.uuid4().hex[:6]}"
        updated_service["provided_service_base_price"] = round(random.uniform(75.00, 300.00), 2)
        updated_service["provided_service_final_price"] = round(random.uniform(85.00, 350.00), 2)
        updated_service["provided_service_description"] = "Updated description with new details"
        updated_service["provided_service_actual_duration"] = random.choice([60, 90, 120, 150])
        
        status, data = await self._put(
            f"/api/v1/business/services/{service_id}",
            updated_service
        )
        
        passed = status == 200
        details = f"Status: {status}"
        if passed and data:
            details += f" - Name: {data.get('provided_service_name', 'Unknown')}"
        self._add_result("Update Service", passed, details)
        return passed
    
    async def test_update_service_invalid_id(self) -> bool:
        """Test updating a non-existent service (should fail)"""
        print("\n❌ Test: Update Non-existent Service")
        
        service = generate_service_data(1, 1)
        
        status, data = await self._put(
            "/api/v1/business/services/999999",
            service
        )
        
        passed = status == 404
        self._add_result("Update Non-existent Service", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_toggle_service_active(self) -> bool:
        """Test toggling service active status"""
        print("\n🔄 Test: Toggle Service Status")
        
        if not self.context.service_ids:
            self._add_result("Toggle Service Status", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, existing = await self._get(f"/api/v1/business/services/{service_id}")
        if status != 200:
            self._add_result("Toggle Service Status", False, f"Failed to fetch service: {status}")
            return False
        
        current_active = existing.get('provided_service_is_active', False)
        new_status = not current_active
        
        print(f"   Current: {'Active' if current_active else 'Inactive'}")
        print(f"   New: {'Active' if new_status else 'Inactive'}")
        
        status, data = await self._patch(
            f"/api/v1/business/services/{service_id}/toggle",
            params={"is_active": new_status}
        )
        
        passed = status == 200
        if passed and data:
            actually_active = data.get('provided_service_is_active')
            if actually_active == new_status:
                passed = True
                details = f"Successfully {'activated' if new_status else 'deactivated'}"
            else:
                passed = False
                details = f"Status changed to {actually_active} but expected {new_status}"
        else:
            details = f"Status: {status}"
        
        self._add_result("Toggle Service Status", passed, details)
        return passed
    
    async def test_toggle_service_invalid_id(self) -> bool:
        """Test toggling non-existent service (should fail)"""
        print("\n❌ Test: Toggle Non-existent Service")
        
        status, data = await self._patch(
            "/api/v1/business/services/999999/toggle",
            params={"is_active": True}
        )
        
        passed = status == 404
        self._add_result("Toggle Non-existent Service", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    # ==================== Test Cases - Deletion ====================
    
    async def test_delete_service(self) -> bool:
        """Test deleting a service"""
        print("\n🗑️  Test: Delete Service")
        
        if not self.context.service_ids:
            self._add_result("Delete Service", False, "No services created yet")
            return False
        
        service_id = self.context.get_random_service_id()
        print(f"   Service ID: {service_id}")
        
        status, data = await self._delete(
            f"/api/v1/business/services/{service_id}",
            params={"force_delete": False}
        )
        
        if status == 400:
            print("   Service has requirements, trying force delete...")
            status, data = await self._delete(
                f"/api/v1/business/services/{service_id}",
                params={"force_delete": True}
            )
        
        passed = status in [204, 200]
        
        if passed:
            self.context.created_services = [
                s for s in self.context.created_services
                if s.get('provided_service_id', s.get('id')) != service_id
            ]
            details = "Service deleted successfully"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Delete Service", passed, details)
        return passed
    
    async def test_delete_service_invalid_id(self) -> bool:
        """Test deleting a non-existent service (should fail)"""
        print("\n❌ Test: Delete Non-existent Service")
        
        status, data = await self._delete(
            "/api/v1/business/services/999999",
            params={"force_delete": True}
        )
        
        passed = status == 404
        self._add_result("Delete Non-existent Service", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_delete_service_without_force(self) -> bool:
        """Test deleting a service with requirements without force (should fail)"""
        print("\n❌ Test: Delete Service with Requirements (No Force)")
        
        service_id = 0
        for sid in self.context.service_ids:
            status, reqs = await self._get(f"/api/v1/business/services/{sid}/requirements")
            if status == 200 and reqs and len(reqs) > 0:
                service_id = sid
                break
        
        if not service_id:
            self._add_result("Delete Service No Force", False, "No service with requirements found")
            return False
        
        print(f"   Service ID: {service_id}")
        print("   Service has requirements, trying to delete without force...")
        
        status, data = await self._delete(
            f"/api/v1/business/services/{service_id}",
            params={"force_delete": False}
        )
        
        passed = status == 400 or status == 409
        self._add_result("Delete Service No Force", passed, f"Correctly blocked (Status: {status})")
        return passed
    
    # ==================== Main Runner ====================
    
    async def run_all_tests(self) -> None:
        """Run all test suites"""
        print("\n" + "="*70)
        print("🚀 SERVICE ENDPOINT TESTS")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        await self.load_context()
        
        if not await self.fetch_all_data():
            print("\n⚠️  Failed to fetch required data. Some tests may fail.")
        
        if not self.context.provider_ids:
            print("\n⚠️  No providers found! Please seed providers first.")
            print("   Run test_runner.py first to create providers.")
        
        if not self.context.category_ids:
            print("\n⚠️  No categories found! Please seed categories first.")
            print("   Using fallback category IDs: 1-10")
            self.context.categories = [
                {"id_product_category": i, "product_category_name": f"Category_{i}"}
                for i in range(1, 11)
            ]
        
        if not self.context.product_ids:
            print("\n⚠️  No products found! Using fallback product ID: 1")
            self.context.products = [{"id_product": 1, "product_name": "Fallback Product"}]
        
        if not self.context.get_auth_headers():
            print("\n⚠️  No authentication headers available. Tests may fail with 401.")
            print("   Run test_runner.py first to get authentication tokens.")
        
        print("\n" + "="*70)
        print("📝 RUNNING TESTS")
        print("="*70)
        
        # Create tests
        await self.test_create_service_minimal()
        await self.test_create_service_with_requirements()
        await self.test_create_service_with_max_requirements()
        await self.test_create_service_invalid_provider()
        await self.test_create_service_invalid_category()
        await self.test_create_service_duplicate()
        
        # Read tests
        await self.test_get_service_by_id()
        await self.test_get_service_by_id_not_found()
        await self.test_get_all_services()
        await self.test_get_services_by_category()
        await self.test_get_services_by_provider()
        await self.test_get_services_active_only()
        await self.test_get_service_requirements()
        await self.test_get_service_staff_requirements()
        
        # Update tests
        if self.context.service_ids:
            await self.test_update_service()
            await self.test_update_service_invalid_id()
            await self.test_toggle_service_active()
            await self.test_toggle_service_invalid_id()
        
        # Delete tests
        if self.context.service_ids:
            await self.test_delete_service()
            await self.test_delete_service_without_force()
            await self.test_delete_service_invalid_id()
        
        self.context.save_to_file(self.context_file)
        
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"  {status} {result.name}")
            if result.details:
                print(f"     {result.details}")
        
        print("="*70)
        print(f"📈 Total: {total} tests | ✅ Passed: {passed} | ❌ Failed: {failed}")
        print(f"📦 Services Created: {len(self.context.created_services)}")
        print(f"📋 Categories: {len(self.context.categories)}")
        print(f"🏥 Providers: {len(self.context.providers)}")
        print(f"📦 Products: {len(self.context.products)}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            if not self.context.provider_ids:
                print("💡 No providers found! Create providers first with test_runner.py")
            if not self.context.category_ids:
                print("💡 No categories found! Seed categories with: python -m storage.seed")
            if not self.context.product_ids:
                print("💡 No products found! Create products first with test_runner.py")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test service endpoints")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API server (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--provider-id",
        type=int,
        help="Use specific provider ID for all tests"
    )
    parser.add_argument(
        "--category-id",
        type=int,
        help="Use specific category ID for all tests"
    )
    parser.add_argument(
        "--context-file",
        default="test_context.json",
        help="Context file to load (default: test_context.json)"
    )
    
    args = parser.parse_args()
    
    async with ServiceTester(args.url) as tester:
        tester.context_file = args.context_file
        
        if args.provider_id:
            tester.context.providers = [{"id_product_provider": args.provider_id, "provider_name": "Custom"}]
        if args.category_id:
            tester.context.categories = [{"id_product_category": args.category_id, "product_category_name": "Custom"}]
        
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)