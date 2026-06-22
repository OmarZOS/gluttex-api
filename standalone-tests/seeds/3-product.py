#!/usr/bin/env python3
"""
Test script for product creation endpoint.
Run with: python test_product_creation.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
class TestContext:
    """Test context containing all fetched data"""
    users: List[Dict[str, Any]] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    providers: List[Dict[str, Any]] = field(default_factory=list)
    created_products: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def user_ids(self) -> List[int]:
        """Extract user IDs from users list"""
        ids = []
        for u in self.users:
            uid = u.get('id_app_user')
            if uid is None:
                uid = u.get('id')
            if uid and isinstance(uid, int):
                ids.append(uid)
        return ids
    
    @property
    def category_ids(self) -> List[int]:
        """Extract category IDs from categories list"""
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
        """Extract provider IDs from providers list"""
        ids = []
        for p in self.providers:
            pid = p.get('id_product_provider')
            if pid is None:
                pid = p.get('id')
            if pid and isinstance(pid, int):
                ids.append(pid)
        return ids
    
    def get_random_user_id(self) -> int:
        if not self.user_ids:
            return 0
        return random.choice(self.user_ids)
    
    def get_random_category_id(self) -> int:
        if not self.category_ids:
            return 0
        return random.choice(self.category_ids)
    
    def get_random_provider_id(self) -> int:
        if not self.provider_ids:
            return 0
        return random.choice(self.provider_ids)


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_barcode() -> str:
    """Generate a random 13-digit barcode"""
    return str(random.randint(1000000000000, 9999999999999))


def generate_product_data(
    category_id: int = 0,
    provider_id: int = 0,
    owner_id: int = 0
) -> Dict[str, Any]:
    """Generate random product data"""
    
    names = [
        "Organic Quinoa", "Chia Seeds", "Coconut Oil", "Olive Oil",
        "Maple Syrup", "Vanilla Extract", "Cocoa Powder", "Protein Powder",
        "Almond Flour", "Brown Rice", "Stevia", "Honey", "Oats", "Barley"
    ]
    brands = [
        "HealthyLife", "NutriFood", "PureOrganic", "WholeFoods",
        "NaturalChoice", "GreenGarden", "FarmFresh", "OrganicHarvest"
    ]
    quantifiers = ["kg", "g", "L", "mL", "pc", "pkg", "box", "bag"]
    descriptions = ["organic", "natural", "premium", "artisan", "gluten-free"]
    
    return {
        "id_product": 0,
        "product_provider_id": provider_id,
        "product_category_id": category_id,
        "product_price": round(random.uniform(1.99, 99.99), 2),
        "product_quantity": round(random.uniform(1, 1000), 2),
        "product_name": random.choice(names),
        "product_brand": random.choice(brands),
        "product_barcode": generate_barcode(),
        "product_description": f"High-quality {random.choice(descriptions)} product",
        "product_quantifier": random.choice(quantifiers),
        "product_owner": owner_id
    }


def generate_image_data() -> Dict[str, Any]:
    """Generate random product image data"""
    return {
        "id_product_image": 0,
        "product_image_url": f"https://example.com/images/product_{uuid.uuid4().hex[:8]}.jpg",
        "product_ref_id": 0
    }


def generate_iproduct_data(category_id: int = 0) -> Dict[str, Any]:
    """Generate random iproduct data"""
    names = ["Organic Quinoa", "Chia Seeds", "Coconut Oil", "Olive Oil"]
    brands = ["HealthyLife", "NutriFood", "PureOrganic", "WholeFoods"]
    statuses = ["gluten_free", "contains_gluten", "may_contain_gluten", "unknown"]
    
    return {
        "id_iproduct": 0,
        "iproduct_name": random.choice(names),
        "iproduct_barcode": generate_barcode(),
        "iproduct_brand": random.choice(brands),
        "iproduct_estimated_price": round(random.uniform(1.99, 29.99), 2),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(statuses),
        "iproduct_category_id": category_id,
        "iproduct_image_url": f"https://example.com/images/iproduct_{uuid.uuid4().hex[:8]}.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": round(random.uniform(0.75, 0.99), 2),
        "iproduct_model_name": "gpt-4"
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class ProductTester:
    """Test runner for product creation endpoint"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None
        self.context = TestContext()
        self.results: List[TestResult] = []
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    # ==================== HTTP Helpers ====================
    
    async def _get(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        """Send GET request and return (status_code, data)"""
        try:
            response = await self.client.get(f"{self.base_url}{path}", params=params)
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _post(self, path: str, json_data: Dict) -> Tuple[int, Any]:
        """Send POST request and return (status_code, data)"""
        try:
            response = await self.client.post(f"{self.base_url}{path}", json=json_data)
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    # ==================== Data Fetching ====================
    
    async def fetch_users(self) -> bool:
        """Fetch existing users"""
        print("\n📋 Fetching existing users...")
        status, data = await self._get("/api/v1/app_user", {"offset": 0, "limit": 1000})
        
        if status != 200:
            print(f"   ❌ Failed to fetch users: {status}")
            return False
        
        # Handle different response formats
        if isinstance(data, list):
            self.context.users = data
        elif isinstance(data, dict):
            self.context.users = data.get("data", data.get("items", data.get("result", [])))
        else:
            self.context.users = []
        
        print(f"   ✅ Found {len(self.context.users)} users")
        print(f"   User IDs: {self.context.user_ids[:10]}{'...' if len(self.context.user_ids) > 10 else ''}")
        for user in self.context.users[:5]:
            uid = user.get('id_app_user', user.get('id', 'N/A'))
            name = user.get('app_user_name', user.get('username', 'Unknown'))
            print(f"      - ID: {uid}, Name: {name}")
        if len(self.context.users) > 5:
            print(f"      ... and {len(self.context.users) - 5} more")
        
        return True
    
    async def fetch_categories(self) -> bool:
        """Fetch product categories"""
        print("\n📋 Fetching product categories...")
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
        print(f"   Category IDs: {self.context.category_ids}")
        for cat in self.context.categories[:5]:
            cid = cat.get('id_product_category', cat.get('id', 'N/A'))
            name = cat.get('product_category_name', cat.get('name', 'Unknown'))
            print(f"      - ID: {cid}, Name: {name}")
        if len(self.context.categories) > 5:
            print(f"      ... and {len(self.context.categories) - 5} more")
        
        return True
    
    async def fetch_providers(self) -> bool:
        """Fetch providers"""
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
        print(f"   Provider IDs: {self.context.provider_ids[:10]}{'...' if len(self.context.provider_ids) > 10 else ''}")
        for prov in self.context.providers[:5]:
            pid = prov.get('id_product_provider', prov.get('id', 'N/A'))
            name = prov.get('provider_name', prov.get('name', 'Unknown'))
            print(f"      - ID: {pid}, Name: {name}")
        if len(self.context.providers) > 5:
            print(f"      ... and {len(self.context.providers) - 5} more")
        
        return True
    
    async def fetch_all_data(self) -> bool:
        """Fetch all required data"""
        print("\n" + "="*50)
        print("📊 FETCHING EXISTING DATA")
        print("="*50)
        
        user_ok = await self.fetch_users()
        cat_ok = await self.fetch_categories()
        prov_ok = await self.fetch_providers()
        
        if not cat_ok:
            print("\n⚠️  Could not fetch categories. Using fallback category IDs: 1-10")
            # Fallback categories if API fails
            for i in range(1, 11):
                self.context.categories.append({
                    "id_product_category": i,
                    "product_category_name": f"Category_{i}"
                })
            cat_ok = True
        
        return user_ok and cat_ok and prov_ok
    
    # ==================== Test Methods ====================
    
    def _add_result(self, name: str, passed: bool, details: str = "", response: Any = None):
        """Add a test result"""
        result = TestResult(name=name, passed=passed, details=details, response=response)
        self.results.append(result)
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
    
    async def _create_product(
        self,
        test_name: str,
        product_data: Dict[str, Any],
        image_data: Optional[Dict] = None,
        iproduct_data: Optional[Dict] = None,
        expect_success: bool = True
    ) -> bool:
        """Helper to create a product and record result"""
        payload = {"product": product_data}
        if image_data:
            payload["image"] = image_data
        if iproduct_data:
            payload["iproduct"] = iproduct_data
        
        status, data = await self._post("/api/v1/products", payload)
        
        if expect_success:
            passed = status == 201
            if passed and data:
                self.context.created_products.append(data)
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        else:
            passed = status in [400, 422]
            details = f"Correctly rejected (Status: {status})"
            if status == 404 and expect_success is False:
                # If we expected failure but got 404, that's also acceptable
                # since it means the validation failed before creating
                passed = True
                details = f"Correctly rejected (Status: {status}) - Resource not found"
        
        self._add_result(test_name, passed, details, data if passed else None)
        return passed
    
    # ==================== Test Cases ====================
    
    async def test_minimal_product(self) -> bool:
        """Test creating a product with minimal data"""
        print("\n📦 Test: Create Product (Minimal Data)")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not owner_id:
            self._add_result("Minimal Product", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Minimal Product", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, provider_id, owner_id)
        
        print(f"   Owner ID: {owner_id}")
        print(f"   Category ID: {category_id}")
        print(f"   Provider ID: {provider_id}")
        
        return await self._create_product("Minimal Product", product, expect_success=True)
    
    async def test_product_with_image(self) -> bool:
        """Test creating a product with image"""
        print("\n🖼️ Test: Create Product with Image")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not owner_id:
            self._add_result("Product with Image", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Product with Image", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, provider_id, owner_id)
        image = generate_image_data()
        
        return await self._create_product("Product with Image", product, image_data=image, expect_success=True)
    
    async def test_product_with_iproduct(self) -> bool:
        """Test creating a product with iproduct reference"""
        print("\n📦 Test: Create Product with Iproduct")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not owner_id:
            self._add_result("Product with Iproduct", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Product with Iproduct", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, provider_id, owner_id)
        iproduct = generate_iproduct_data(category_id)
        
        return await self._create_product("Product with Iproduct", product, iproduct_data=iproduct, expect_success=True)
    
    async def test_full_product(self) -> bool:
        """Test creating a product with all data"""
        print("\n📦 Test: Create Product (Full Data)")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not owner_id:
            self._add_result("Full Product", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Full Product", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, provider_id, owner_id)
        product["product_description"] = "Premium quality organic product"
        product["product_quantity"] = 100.0
        product["product_price"] = 49.99
        
        image = generate_image_data()
        image["product_image_url"] = f"https://example.com/images/premium_{uuid.uuid4().hex[:8]}.jpg"
        
        iproduct = generate_iproduct_data(category_id)
        iproduct["iproduct_info_confidence"] = 0.98
        
        return await self._create_product(
            "Full Product",
            product,
            image_data=image,
            iproduct_data=iproduct,
            expect_success=True
        )
    
    async def test_missing_name(self) -> bool:
        """Test creating a product with missing name (should fail)"""
        print("\n❌ Test: Missing Product Name")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        
        if not owner_id:
            self._add_result("Missing Name", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Missing Name", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, 1, owner_id)
        product["product_name"] = None
        
        return await self._create_product("Missing Name", product, expect_success=False)
    
    async def test_invalid_price(self) -> bool:
        """Test creating a product with invalid price (should fail)"""
        print("\n❌ Test: Invalid Product Price")
        
        owner_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        
        if not owner_id:
            self._add_result("Invalid Price", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Invalid Price", False, "No categories available")
            return False
        
        product = generate_product_data(category_id, 1, owner_id)
        product["product_price"] = -10.00
        
        return await self._create_product("Invalid Price", product, expect_success=False)
    
    async def test_multiple_products(self) -> bool:
        """Test creating multiple products"""
        print("\n👥 Test: Create Multiple Products")
        
        if not self.context.user_ids:
            self._add_result("Multiple Products", False, "No users available")
            return False
        
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not category_id:
            self._add_result("Multiple Products", False, "No categories available")
            return False
        
        success_count = 0
        total_count = 3
        
        for i in range(total_count):
            owner_id = self.context.get_random_user_id()
            product = generate_product_data(category_id, provider_id, owner_id)
            product["product_name"] = f"Product_{i+1}_{uuid.uuid4().hex[:4]}"
            
            status, data = await self._post("/api/v1/products", {"product": product})
            
            if status == 201:
                success_count += 1
                self.context.created_products.append(data)
                print(f"   {i+1}. ✅ Created (Owner: {owner_id})")
            else:
                error_msg = data.get('message', data.get('detail', 'Unknown error')) if data else 'Unknown'
                print(f"   {i+1}. ❌ Failed: {status} - {error_msg}")
        
        passed = success_count == total_count
        self._add_result("Multiple Products", passed, f"Created {success_count}/{total_count}")
        return passed
    
    async def test_different_owners(self) -> bool:
        """Test creating products with different owners"""
        print("\n👥 Test: Different Product Owners")
        
        if len(self.context.user_ids) < 2:
            self._add_result("Different Owners", False, f"Need at least 2 users, have {len(self.context.user_ids)}")
            return False
        
        category_id = self.context.get_random_category_id()
        provider_id = self.context.get_random_provider_id()
        
        if not category_id:
            self._add_result("Different Owners", False, "No categories available")
            return False
        
        success_count = 0
        total_count = min(len(self.context.user_ids), 3)
        
        for i, owner_id in enumerate(self.context.user_ids[:total_count]):
            product = generate_product_data(category_id, provider_id, owner_id)
            product["product_name"] = f"Owner_{owner_id}_{uuid.uuid4().hex[:4]}"
            
            status, data = await self._post("/api/v1/products", {"product": product})
            
            if status == 201:
                success_count += 1
                self.context.created_products.append(data)
                print(f"   {i+1}. ✅ Created (Owner: {owner_id})")
            else:
                error_msg = data.get('message', data.get('detail', 'Unknown error')) if data else 'Unknown'
                print(f"   {i+1}. ❌ Failed: {status} - {error_msg}")
        
        passed = success_count == total_count
        self._add_result("Different Owners", passed, f"Created {success_count}/{total_count} with different owners")
        return passed
    
    # ==================== Main Runner ====================
    
    async def run_all_tests(self) -> None:
        """Run all test suites"""
        print("\n" + "="*70)
        print("🚀 PRODUCT CREATION TESTS")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Fetch data
        if not await self.fetch_all_data():
            print("\n⚠️  Failed to fetch required data. Some tests may fail.")
        
        # Check requirements
        if not self.context.users:
            print("\n⚠️  No users found! Create users first with test_user_insert.py")
        
        if not self.context.category_ids:
            print("\n⚠️  No categories found! Please seed categories first.")
            print("   Using fallback category IDs: 1-10")
            self.context.categories = [
                {"id_product_category": i, "product_category_name": f"Category_{i}"}
                for i in range(1, 11)
            ]
        
        print("\n" + "="*70)
        print("📝 RUNNING TESTS")
        print("="*70)
        
        # Run tests
        await self.test_minimal_product()
        await self.test_product_with_image()
        await self.test_product_with_iproduct()
        await self.test_full_product()
        await self.test_missing_name()
        await self.test_invalid_price()
        await self.test_multiple_products()
        await self.test_different_owners()
        
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
        print(f"📦 Products Created: {len(self.context.created_products)}")
        print(f"👤 Users Available: {len(self.context.users)}")
        print(f"📋 Categories: {len(self.context.categories)}")
        print(f"🏥 Providers: {len(self.context.providers)}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            if not self.context.users:
                print("💡 No users found! Create users first with test_user_insert.py")
            if not self.context.category_ids:
                print("💡 No categories found! Seed categories with: python -m storage.seed")
            if self.context.category_ids and self.context.users:
                print("💡 Check that the product endpoint is working and the database is accessible.")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test product creation endpoint")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API server (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--category-id",
        type=int,
        help="Use specific category ID for all tests"
    )
    parser.add_argument(
        "--provider-id",
        type=int,
        help="Use specific provider ID for all tests"
    )
    parser.add_argument(
        "--user-id",
        type=int,
        help="Use specific user ID as owner for all tests"
    )
    
    args = parser.parse_args()
    
    async with ProductTester(args.url) as tester:
        # If specific IDs are provided, use them
        if args.category_id:
            tester.context.categories = [{"id_product_category": args.category_id, "product_category_name": "Custom"}]
        if args.provider_id:
            tester.context.providers = [{"id_product_provider": args.provider_id, "provider_name": "Custom"}]
        if args.user_id:
            tester.context.users = [{"id_app_user": args.user_id, "app_user_name": "Custom"}]
        
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