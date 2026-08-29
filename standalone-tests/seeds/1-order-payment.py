#!/usr/bin/env python3
"""
Order Router Test Runner - Optimized for Speed with Bulk Operations
Uses existing test_context.json data for fast order creation.
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
import time


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
    created_deliveries: List[int] = field(default_factory=list)
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
            'created_deliveries': self.created_deliveries,
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
            self.created_deliveries = data.get('created_deliveries', [])
            print(f"📂 Test context loaded from {filename}")
            return True
        return False


# ============================================================================
# OPTIMIZED TEST RUNNER
# ============================================================================

class OptimizedOrderTestRunner:
    def __init__(self, base_url: str = "http://localhost:9000", silo_url: str = "http://gluttex-silo:9096"):
        self.base_url = base_url
        self.silo_url = silo_url
        self.client = None
        self.context = TestContext()
        self.results = []
        self._product_cache = {}  # Cache product details
        self._user_cache = {}  # Cache user tokens
    
    async def __aenter__(self):
        # Use connection pooling for speed
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
        timeout = httpx.Timeout(30.0, connect=5.0)
        self.client = httpx.AsyncClient(timeout=timeout, verify=False, limits=limits)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_result(self, test_name: str, passed: bool, details: str = "", response_data: Any = None):
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if details:
            print(f"     {details}")
        self.results.append({"name": test_name, "passed": passed, "details": details})
    
    def get_auth_headers(self, user: TestUser) -> Dict[str, str]:
        if user.access_token:
            return {"Authorization": f"Bearer {user.access_token}"}
        return {}
    
    # ==================== BULK ORDER CREATION ====================
    
    async def create_orders_bulk(self, user: TestUser, product_ids: List[int], 
                                  num_orders: int = 20, include_delivery: bool = True) -> List[int]:
        """Create multiple orders in parallel for maximum speed"""
        
        headers = self.get_auth_headers(user)
        if not headers:
            print(f"   ❌ No auth token for user {user.id}")
            return []
        
        # Prepare order data for all orders
        order_tasks = []
        delivery_infos = []
        
        for i in range(num_orders):
            # Select random products (1-3 per order)
            num_products = random.randint(1, min(3, len(product_ids)))
            selected_products = random.sample(product_ids, num_products)
            
            # Create ordered items
            ordered_items = []
            for product_id in selected_products:
                product = self._get_cached_product(product_id)
                if product:
                    quantity = random.randint(1, 3)
                    ordered_items.append({
                        "ordered_product_id": product_id,
                        "ordered_quantity": quantity,
                        "unit_price": product.get('product_price', 50.0),
                        "applied_vat": round(random.uniform(0, 19), 2),
                        "product_discount": round(random.uniform(0, 10), 2)
                    })
            
            if not ordered_items:
                continue
            
            # Create order data
            order_data = {
                "placed_order_state": "PENDING",
                "payment_status": "PENDING",
                "payment_method": random.choice(["card", "cash", "bank_transfer"]),
                "order_discount": round(random.uniform(0, 10), 2),
                "ordering_user_id": user.id,
                "payment_ref": f"BULK-{uuid.uuid4().hex[:8]}"
            }
            
            request_data = {
                "ordered_items": ordered_items,
                "submitted_order": order_data
            }
            
            # Add delivery info
            if include_delivery and random.random() > 0.3:  # 70% chance of delivery
                delivery_info = self._generate_delivery_info()
                request_data["delivery_info"] = delivery_info
                delivery_infos.append(delivery_info)
            
            # Create task for concurrent execution
            order_tasks.append({
                "request_data": request_data,
                "payment_method": order_data["payment_method"],
                "order_index": i
            })
        
        # Execute all orders concurrently
        print(f"   🚀 Creating {len(order_tasks)} orders concurrently...")
        start_time = time.time()
        
        tasks = []
        for task_data in order_tasks:
            task = self.client.post(
                f"{self.base_url}/api/v1/business/orders",
                params={"payment_method": task_data["payment_method"]},
                json=task_data["request_data"],
                headers=headers
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"   ⏱️ Completed in {elapsed:.2f}s ({len(tasks)} orders)")
        
        # Process responses
        order_ids = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"   ❌ Order {i} failed: {response}")
                continue
            
            if response.status_code == 201:
                try:
                    result = response.json()
                    order_id = self._extract_order_id(result)
                    if order_id and order_id > 0:
                        order_ids.append(order_id)
                        self.context.created_orders.append(order_id)
                except:
                    pass
        
        print(f"   ✅ Created {len(order_ids)} orders successfully")
        return order_ids
    
    def _get_cached_product(self, product_id: int) -> Optional[Dict]:
        """Get product from cache or fetch it"""
        if product_id in self._product_cache:
            return self._product_cache[product_id]
        
        # Try to get from context first
        # Since we don't have product details in context, we'll use defaults
        return {
            'product_price': random.uniform(10, 200),
            'product_quantity': random.randint(50, 500)
        }
    
    def _generate_delivery_info(self) -> Dict[str, Any]:
        """Generate delivery info quickly"""
        cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida"]
        streets = ["Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre"]
        
        return {
            "destination_address": {
                "id_location": 0,
                "location_latitude": round(random.uniform(36.0, 37.0), 6),
                "location_longitude": round(random.uniform(-5.0, 8.0), 6),
                "location_name": random.choice(["Home", "Office", "Clinic"]),
                "location_address_id": 0,
                "id_address": 0,
                "address_street": f"{random.randint(1, 999)} {random.choice(streets)}",
                "address_city": random.choice(cities),
                "address_postal_code": f"{random.randint(1000, 9999)}",
                "address_country": "DZ"
            },
            "delivery_fee": round(random.uniform(0, 50), 2)
        }
    
    def _extract_order_id(self, response_data: Dict[str, Any]) -> int:
        """Extract order ID from response"""
        if 'order' in response_data and isinstance(response_data['order'], dict):
            return response_data['order'].get('id_placed_order', 0)
        if 'id_placed_order' in response_data:
            return response_data['id_placed_order']
        if 'id' in response_data:
            return response_data['id']
        return 0
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, context_file: str = "test_context.json", 
                        orders_per_user: int = 20, 
                        max_users: int = 5):
        print("\n" + "="*70)
        print("🚀 OPTIMIZED ORDER TEST RUNNER - BULK CREATION")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"📦 Orders per user: {orders_per_user}")
        print(f"👤 Max users: {max_users}")
        print("="*70)
        
        # Load context
        if not Path(context_file).exists():
            print(f"❌ Context file {context_file} not found!")
            print("   Run the main test runner first to generate data.")
            return
        
        self.context.load(context_file)
        print(f"📂 Loaded {len(self.context.users)} users")
        print(f"📦 Loaded {len(self.context.created_products)} products")
        print(f"🏢 Loaded {len(self.context.created_organisations)} organisations")
        print(f"🏥 Loaded {len(self.context.created_suppliers)} suppliers")
        
        # Check if we have products
        if not self.context.created_products:
            print("❌ No products found in context! Please run the main test runner first.")
            return
        
        # Get authenticated users with valid tokens
        authenticated_users = []
        for user in self.context.users[:max_users]:
            if user.access_token:
                authenticated_users.append(user)
            else:
                # Try to login if token is missing
                print(f"🔐 Attempting to login user {user.username}...")
                if await self._login_user(user):
                    authenticated_users.append(user)
        
        if not authenticated_users:
            print("❌ No authenticated users available! Please run the main test runner first.")
            return
        
        print(f"\n👤 Using {len(authenticated_users)} authenticated users")
        
        # Get product IDs
        product_ids = self.context.created_products
        print(f"📦 Using {len(product_ids)} products for orders")
        
        # Create orders in bulk for each user
        total_orders = 0
        start_time = time.time()
        
        for i, user in enumerate(authenticated_users):
            print(f"\n👤 User {i+1}/{len(authenticated_users)}: {user.username} (ID: {user.id})")
            
            # Create orders
            order_ids = await self.create_orders_bulk(
                user, 
                product_ids, 
                num_orders=orders_per_user,
                include_delivery=True
            )
            
            total_orders += len(order_ids)
            print(f"   📋 Created {len(order_ids)} orders for user {user.id}")
            
            # Small delay between users to avoid overwhelming the server
            await asyncio.sleep(0.2)
        
        elapsed = time.time() - start_time
        
        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"✅ Created {total_orders} orders in {elapsed:.2f}s")
        print(f"📈 Rate: {total_orders / elapsed:.1f} orders/second")
        print(f"👤 Used {len(authenticated_users)} users")
        print(f"📦 Products used: {len(product_ids)}")
        
        # Show order IDs
        if self.context.created_orders:
            unique_orders = list(set(self.context.created_orders))
            print(f"\n📋 Order IDs: {', '.join(map(str, unique_orders[:10]))}{'...' if len(unique_orders) > 10 else ''}")
        
        # Save updated context
        self.context.save(context_file)
        
        print("\n" + "="*70)
    
    async def _login_user(self, user: TestUser) -> bool:
        """Login a user and store token"""
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
                user.access_token = result.get('access_token')
                user.refresh_token = result.get('refresh_token')
                return True
            return False
        except:
            return False


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimized Order Test Runner - Bulk Creation")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--silo-url", default="http://gluttex-silo:9096")
    parser.add_argument("--context-file", default="test_context.json")
    parser.add_argument("--orders-per-user", type=int, default=20)
    parser.add_argument("--max-users", type=int, default=5)
    
    args = parser.parse_args()
    
    async with OptimizedOrderTestRunner(args.url, args.silo_url) as runner:
        await runner.run_tests(
            context_file=args.context_file,
            orders_per_user=args.orders_per_user,
            max_users=args.max_users
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)