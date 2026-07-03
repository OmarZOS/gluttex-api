#!/usr/bin/env python3
"""
Order Router Test Runner with Inventory Sync
Creates products and syncs them to the inventory service before creating orders.
Uses the same context file as the main test runner.
Run with: python test_order_runner.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestUser:
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
    created_orders: List[int] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    created_organisations: List[int] = field(default_factory=list)
    created_payments: List[int] = field(default_factory=list)
    created_invoices: List[int] = field(default_factory=list)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def save(self, filename: str = "test_context.json"):
        data = {
            'users': [u.to_dict() for u in self.users],
            'created_orders': self.created_orders,
            'created_products': self.created_products,
            'created_suppliers': self.created_suppliers,
            'created_organisations': self.created_organisations,
            'created_payments': self.created_payments,
            'created_invoices': self.created_invoices,
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
            self.created_orders = data.get('created_orders', [])
            self.created_products = data.get('created_products', [])
            self.created_suppliers = data.get('created_suppliers', [])
            self.created_organisations = data.get('created_organisations', [])
            self.created_payments = data.get('created_payments', [])
            self.created_invoices = data.get('created_invoices', [])
            print(f"📂 Test context loaded from {filename}")
            return True
        return False


# ============================================================================
# ENUMS
# ============================================================================

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


# ============================================================================
# TEST DATA GENERATORS
# ============================================================================

def generate_unique_username() -> str:
    return f"testuser_{uuid.uuid4().hex[:8]}"

def generate_unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:8]}@example.com"

def generate_strong_password() -> str:
    return f"Test_{uuid.uuid4().hex[:8]}!@#"

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
        "product_category_id": random.choice(categories),
        "product_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "product_description": f"High-quality {random.choice(['medical', 'healthcare', 'pharmaceutical'])} product",
        "product_price": round(random.uniform(5.0, 200.0), 2),
        "product_quantity": random.randint(50, 1000),
        "product_quantifier": random.choice(["mg", "g", "ml", "pack", "unit"]),
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
        "iproduct_brand": random.choice(["BrandA", "BrandB", "BrandC", "Generic"]),
        "iproduct_estimated_price": round(random.uniform(5.0, 200.0), 2),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(gluten_statuses),
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": round(random.uniform(0.5, 1.0), 2),
        "iproduct_category_id": random.choice(categories)
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class OrderTestRunner:
    def __init__(self, base_url: str = "http://localhost:9000", silo_url: str = "http://gluttex-silo:9096"):
        self.base_url = base_url
        self.silo_url = silo_url
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
        
        if 'order' in response_data and isinstance(response_data['order'], dict):
            return self.extract_id_from_response(response_data['order'], possible_keys)
        
        return 0
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_user(self) -> Optional[TestUser]:
        user_data = {
            "app_user_name": generate_unique_username(),
            "app_user_password": generate_strong_password(),
            "app_user_email": generate_unique_email(),
            "app_user_type": "customer",
            "app_user_preferences": {
                "theme": random.choice(["dark", "light"]),
                "notifications": random.choice([True, False]),
                "language": random.choice(["en", "fr", "ar"])
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json={"user": user_data}
            )
            
            if response.status_code == 201:
                result = response.json()
                user_id = self.extract_id_from_response(result, ['id_app_user', 'id', 'user_id', 'app_user_id'])
                
                test_user = TestUser(
                    id=user_id,
                    username=user_data.get('app_user_name', ''),
                    email=user_data.get('app_user_email', ''),
                    password=user_data.get('app_user_password', ''),
                    user_data=user_data
                )
                
                self.context.users.append(test_user)
                print(f"   ✅ Created user: {test_user.username} (ID: {test_user.id})")
                return test_user
            else:
                print(f"   ❌ Failed to create user: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating user: {e}")
            return None
    
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
    
    # ==================== SETUP: Create Supplier and Products ====================
    
    async def setup_supplier_and_products(self, user: TestUser) -> Dict[str, Any]:
        """Create a supplier, products, and sync them to inventory"""
        print("\n🏗️ Setting up supplier and products...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return {}
        
        # Create organisation
        org_data = {
            "provider_organisation_name": f"TestOrg_{uuid.uuid4().hex[:4]}",
            "provider_organisation_desc": "Test organisation for order testing"
        }
        
        org_response = await self.client.post(
            f"{self.base_url}/api/v1/organisations",
            json={"organisation": org_data},
            headers=headers
        )
        
        if org_response.status_code != 201:
            print(f"   ❌ Failed to create organisation: {org_response.status_code}")
            return {}
        
        org_result = org_response.json()
        org_id = self.extract_id_from_response(org_result, ['idprovider_organisation', 'id', 'organisation_id'])
        self.context.created_organisations.append(org_id)
        print(f"   ✅ Created organisation: {org_id}")
        
        # Create supplier
        supplier_data = {
            "id_provider_owner": user.id,
            "idprovider_details_id": 0,
            "id_product_provider_type": random.choice([1, 2, 3, 4, 5, 6]),
            "id_provider_organisation": org_id,
            "product_provider_type_desc": "Supplier for order testing",
            "provider_organisation_name": f"TestSupplier_{uuid.uuid4().hex[:4]}",
            "provider_organisation_desc": "Test supplier for order testing",
            "provider_name": f"OrderTestProvider_{uuid.uuid4().hex[:4]}",
            "provider_contact_info": json.dumps({
                "phone": f"+213-5{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}",
                "email": generate_unique_email()
            })
        }
        
        location_data = {
            "location_latitude": 36.7538,
            "location_longitude": 3.0588,
            "location_name": "Test Location",
            "address_street": "123 Test Street",
            "address_city": "Algiers",
            "address_postal_code": "16000",
            "address_country": "DZ"
        }
        
        supplier_response = await self.client.post(
            f"{self.base_url}/api/v1/suppliers",
            json={
                "provider": supplier_data,
                "location": location_data
            },
            headers=headers
        )
        
        if supplier_response.status_code != 201:
            print(f"   ❌ Failed to create supplier: {supplier_response.status_code}")
            return {}
        
        supplier_result = supplier_response.json()
        supplier_id = self.extract_id_from_response(supplier_result, ['id_product_provider', 'id', 'supplier_id'])
        self.context.created_suppliers.append(supplier_id)
        print(f"   ✅ Created supplier: {supplier_id}")
        
        # Create products
        products = []
        for i in range(3):
            product_data = generate_random_product_data(supplier_id, user.id)
            product_image = generate_random_product_image_data()
            iproduct_data = generate_random_iproduct_data()
            
            product_response = await self.client.post(
                f"{self.base_url}/api/v1/products",
                json={
                    "product": product_data,
                    "image": product_image,
                    "iproduct": iproduct_data
                },
                headers=headers
            )
            
            if product_response.status_code == 201:
                product_result = product_response.json()
                product_id = self.extract_id_from_response(product_result, ['id_product', 'id', 'product_id'])
                self.context.created_products.append(product_id)
                products.append({
                    "id": product_id,
                    "name": product_data["product_name"],
                    "price": product_data["product_price"],
                    "quantity": product_data["product_quantity"]
                })
                print(f"   ✅ Created product {i+1}: {product_id} - {product_data['product_name']}")
                
                # Sync product to inventory via the main API's product creation
                # The product should already be synced if the main API handles it
                try:
                    # Verify product exists in inventory
                    check_response = await self.client.post(
                        f"{self.silo_url}/esilo/inventory/stock/bulk",
                        json={"product_ids": [product_id]},
                        headers={"Content-Type": "application/json"}
                    )
                    if check_response.status_code == 200:
                        data = check_response.json()
                        if str(product_id) in data:
                            print(f"   ✅ Product {product_id} verified in inventory")
                        else:
                            print(f"   ⚠️ Product {product_id} not found in inventory, syncing...")
                            # Try to create in inventory
                            create_response = await self.client.post(
                                f"{self.silo_url}/esilo/inventory/products",
                                json={
                                    "product_id": product_id,
                                    "initial_quantity": product_data["product_quantity"],
                                    "reserved_quantity": 0
                                },
                                headers={"Content-Type": "application/json"}
                            )
                            if create_response.status_code in [200, 201]:
                                print(f"   ✅ Product {product_id} synced to inventory")
                            else:
                                print(f"   ⚠️ Could not sync product {product_id}: {create_response.status_code}")
                except Exception as e:
                    print(f"   ⚠️ Could not verify/sync product {product_id}: {e}")
            else:
                print(f"   ❌ Failed to create product {i+1}: {product_response.status_code}")
                print(f"      {product_response.text[:200]}")
        
        return {
            "org_id": org_id,
            "supplier_id": supplier_id,
            "products": products
        }
    
    # ==================== ORDER TESTS ====================
    
    async def test_create_order(self, user: TestUser, products: List[Dict], payment_method: str = "card") -> Optional[int]:
        """Test creating an order"""
        print(f"\n📦 Creating order for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        if not products:
            print("   ❌ No products available to create order")
            return None
        
        # Select products
        selected_products = products[:2] if len(products) >= 2 else products
        
        # Create ordered items
        ordered_items = []
        for product in selected_products:
            quantity = random.randint(1, 3)
            unit_price = product["price"]
            item = {
                "ordered_product_id": product["id"],
                "ordered_quantity": quantity,
                "unit_price": unit_price,
                "applied_vat": round(random.uniform(0, 19), 2),
                "product_discount": round(random.uniform(0, 10), 2)
            }
            ordered_items.append(item)
        
        # Create order data
        order_data = {
            "placed_order_state": "PENDING",
            "payment_status": "PENDING",
            "payment_method": payment_method,
            "order_discount": round(random.uniform(0, 10), 2),
            "ordering_user_id": user.id,
            "payment_ref": f"PAY-{uuid.uuid4().hex[:8]}"
        }
        
        print(f"   📝 Order items: {len(ordered_items)}")
        print(f"   💳 Payment method: {payment_method}")
        print(f"   👤 User ID: {user.id}")
        
        request_data = {
            "ordered_items": ordered_items,
            "submitted_order": order_data
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/business/orders",
                params={"payment_method": payment_method},
                json=request_data,
                headers=headers
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"   📥 Response: {json.dumps(result, indent=2)[:500]}")
                
                # Extract order ID
                order_id = 0
                if 'order' in result and isinstance(result['order'], dict):
                    order_id = self.extract_id_from_response(
                        result['order'],
                        ['id_placed_order', 'id', 'order_id']
                    )
                
                if order_id == 0 and 'id_placed_order' in result:
                    order_id = result['id_placed_order']
                
                if order_id == 0 and 'id' in result:
                    order_id = result['id']
                
                if order_id > 0:
                    self.context.created_orders.append(order_id)
                    print(f"   ✅ Created order: {order_id}")
                    print(f"   💰 Total: {result.get('order', {}).get('placed_order_total', 'N/A')}")
                    self.print_result("Create Order", True, f"Order {order_id} created")
                    return order_id
                else:
                    print(f"   ⚠️ Could not extract order ID from response: {result}")
                    self.print_result("Create Order", True, "Order created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create order: {response.status_code}")
                print(f"      {response.text[:500]}")
                self.print_result("Create Order", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Order creation error: {e}")
            import traceback
            traceback.print_exc()
            self.print_result("Create Order", False, str(e))
            return None
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, skip_user_creation: bool = False, 
                       skip_login: bool = False,
                       context_file: str = "test_context.json"):
        print("\n" + "="*70)
        print("🚀 ORDER ROUTER TEST RUNNER (with Inventory Sync)")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 SILO URL: {self.silo_url}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Load context from the main test context file
        if Path(context_file).exists():
            loaded = self.context.load(context_file)
            if loaded:
                print(f"📂 Loaded {len(self.context.users)} users from context")
                print(f"📦 Loaded {len(self.context.created_products)} products from context")
                print(f"📋 Loaded {len(self.context.created_orders)} orders from context")
        else:
            print(f"⚠️ Context file {context_file} not found. Creating new data...")
        
        # Create users if needed (only if no users in context)
        if not skip_user_creation and not self.context.users:
            print("\n📝 Creating Test Users")
            print("="*70)
            for i in range(2):
                user = await self.create_user()
                if user:
                    print(f"   ✅ Created user {i+1}: {user.username}")
        elif self.context.users:
            print(f"\n📋 Using {len(self.context.users)} existing users from context")
        
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
        
        # Get authenticated user
        authenticated_users = [u for u in self.context.users if u.access_token]
        if not authenticated_users:
            print("\n❌ No authenticated users available")
            return
        
        test_user = authenticated_users[0]
        print(f"\n👤 Using user '{test_user.username}' (ID: {test_user.id}) for tests")
        
        # Setup: Create supplier and products if needed
        if not self.context.created_products:
            print("\n" + "="*70)
            print("🏗️ SETUP: Creating Supplier and Products with Inventory Sync")
            print("="*70)
            setup_data = await self.setup_supplier_and_products(test_user)
            products = setup_data.get('products', [])
        else:
            products = []
            # Get product details from context
            for product_id in self.context.created_products:
                try:
                    headers = self.get_auth_headers(test_user)
                    response = await self.client.get(
                        f"{self.base_url}/api/v1/products/{product_id}",
                        headers=headers
                    )
                    if response.status_code == 200:
                        data = response.json()
                        products.append({
                            "id": product_id,
                            "name": data.get('product_name', 'Unknown'),
                            "price": data.get('product_price', 0),
                            "quantity": data.get('product_quantity', 0)
                        })
                except Exception as e:
                    print(f"   ⚠️ Could not get product {product_id}: {e}")
        
        print(f"\n📦 Available products: {len(products)}")
        
        if not products:
            print("\n❌ No products available. Creating new products...")
            setup_data = await self.setup_supplier_and_products(test_user)
            products = setup_data.get('products', [])
        
        # Run order tests
        print("\n" + "="*70)
        print("🧪 Running Order Tests")
        print("="*70)
        
        # Test: Create Order with different payment methods
        print("\n📝 CREATE ORDER TESTS")
        payment_methods = ["card", "cash", "bank_transfer"]
        
        for payment_method in payment_methods:
            order_id = await self.test_create_order(test_user, products, payment_method)
            if order_id and order_id > 0:
                self.context.created_orders.append(order_id)
                print(f"\n✅ Order created successfully with ID: {order_id} using {payment_method}")
            else:
                print(f"\n❌ Failed to create order with {payment_method}. Check the logs above.")
        
        # Save context
        print("\n💾 Saving Test Context")
        print("="*70)
        self.context.save(context_file)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 ORDER TEST SUMMARY")
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
        print(f"   👤 Users: {len(self.context.users)}")
        print(f"   🔐 Authenticated: {len([u for u in self.context.users if u.access_token])}")
        print(f"   🏢 Organisations: {len(self.context.created_organisations)}")
        print(f"   🏥 Suppliers: {len(self.context.created_suppliers)}")
        print(f"   📦 Products: {len(self.context.created_products)}")
        print(f"   📋 Orders: {len(self.context.created_orders)}")
        
        if self.context.created_orders:
            unique_orders = list(set(self.context.created_orders))
            print(f"\n📋 Order IDs: {', '.join(map(str, unique_orders))}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            print("\n💡 Common issues:")
            print("   1. Products need to be synced to the inventory service (SILO)")
            print("   2. Check if the inventory service is running")
            print("   3. Verify product quantities are sufficient")
        
        print("="*70)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Order Router Test Runner with Inventory Sync")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--silo-url", default="http://gluttex-silo:9096")
    parser.add_argument("--skip-user-creation", action="store_true")
    parser.add_argument("--skip-login", action="store_true")
    parser.add_argument("--context-file", default="test_context.json")  # Use main context file
    parser.add_argument("--clear-context", action="store_true")
    
    args = parser.parse_args()
    
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context file")
    
    async with OrderTestRunner(args.url, args.silo_url) as runner:
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