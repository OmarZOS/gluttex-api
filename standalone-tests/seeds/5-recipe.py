#!/usr/bin/env python3
"""
Test script for Recipe endpoints.
Run with: python test_recipe_endpoints.py
"""

import asyncio
import httpx
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


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
    ingredients: List[Dict[str, Any]] = field(default_factory=list)
    created_recipes: List[Dict[str, Any]] = field(default_factory=list)
    created_ingredients: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def user_ids(self) -> List[int]:
        """Extract user IDs from users list"""
        ids = []
        for u in self.users:
            uid = u.get('id_app_user')
            if uid is None:
                uid = u.get('id')
                if uid is None:
                    uid = u.get('id_user')
            if uid and isinstance(uid, int):
                ids.append(uid)
        return ids
    
    @property
    def category_ids(self) -> List[int]:
        """Extract category IDs from categories list"""
        ids = []
        for c in self.categories:
            cid = c.get('id_recipe_category')
            if cid is None:
                cid = c.get('id')
                if cid is None:
                    cid = c.get('id_recipe_category')
            if cid and isinstance(cid, int):
                ids.append(cid)
        return ids
    
    @property
    def ingredient_ids(self) -> List[int]:
        """Extract ingredient IDs from ingredients list"""
        ids = []
        for i in self.ingredients:
            iid = i.get('id_ingredient')
            if iid is None:
                iid = i.get('id')
            if iid and isinstance(iid, int):
                ids.append(iid)
        return ids
    
    @property
    def recipe_ids(self) -> List[int]:
        """Extract recipe IDs from created_recipes list"""
        ids = []
        for r in self.created_recipes:
            rid = r.get('id_recipe')
            if rid is None:
                rid = r.get('id')
            if rid and isinstance(rid, int):
                ids.append(rid)
        return ids
    
    def get_random_user_id(self) -> int:
        if not self.user_ids:
            return 0
        return random.choice(self.user_ids)
    
    def get_random_category_id(self) -> int:
        if not self.category_ids:
            return 0
        return random.choice(self.category_ids)
    
    def get_random_ingredient_id(self) -> int:
        if not self.ingredient_ids:
            return 0
        return random.choice(self.ingredient_ids)
    
    def get_random_recipe_id(self) -> int:
        if not self.recipe_ids:
            return 0
        return random.choice(self.recipe_ids)


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_recipe_data(category_id: int = 0, user_id: int = 0) -> Dict[str, Any]:
    """Generate random recipe data with unique names"""
    
    recipe_names = [
        "Chocolate Cake", "Vanilla Cupcakes", "Pasta Carbonara", 
        "Chicken Curry", "Beef Stew", "Vegetable Soup", "Caesar Salad",
        "Pizza Margherita", "Sushi Rolls", "Tiramisu", "Lasagna",
        "Fried Rice", "Pad Thai", "Burger Deluxe", "Fish Tacos",
        "Mushroom Risotto", "Chocolate Chip Cookies", "Banana Bread",
        "Carrot Cake", "Apple Pie", "Cheesecake", "Brownies",
        "Chicken Tikka Masala", "Spaghetti Bolognese", "Chili Con Carne"
    ]
    
    recipe_descriptions = [
        "A delicious and easy to make recipe",
        "Perfect for family gatherings",
        "A classic recipe with a modern twist",
        "Quick and healthy meal option",
        "Comfort food at its best",
        "Authentic recipe from grandmother's kitchen",
        "A crowd-pleaser for all occasions",
        "Healthy and nutritious meal",
        "Gluten-free option available",
        "Vegan-friendly recipe",
        "Ready in under 30 minutes",
        "Perfect for meal prep",
        "Award-winning recipe"
    ]
    
    # Add UUID to ensure uniqueness
    base_name = random.choice(recipe_names)
    unique_name = f"{base_name}_{uuid.uuid4().hex[:6]}"
    
    return {
        "id_recipe": 0,
        "recipe_category_id": category_id,
        "recipe_name": unique_name,
        "recipe_description": random.choice(recipe_descriptions),
        "recipe_instructions": f"Step 1: Prepare ingredients\nStep 2: Mix together\nStep 3: Cook for 30 minutes\nStep 4: Serve hot",
        "recipe_preparation_time": f"{random.choice([15, 30, 45, 60, 90, 120])} minutes",
        "recipe_owner_id": user_id,
        "recipe_ingredients": {}
    }


def generate_ingredient_data(ensure_unique: bool = True) -> Dict[str, Any]:
    """Generate random ingredient data with unique name"""
    
    ingredient_names = [
        "Flour", "Sugar", "Eggs", "Butter", "Milk",
        "Chocolate", "Vanilla Extract", "Baking Powder",
        "Salt", "Cinnamon", "Nutmeg", "Ginger", "Garlic",
        "Onion", "Tomato", "Olive Oil", "Basil",
        "Oregano", "Thyme", "Rosemary", "Cumin",
        "Paprika", "Turmeric", "Coriander", "Cardamom"
    ]
    
    quantifiers = ["g", "kg", "ml", "L", "tsp", "tbsp", "cup", "pc", "slice", "pinch", "oz", "lb"]
    
    name = random.choice(ingredient_names)
    if ensure_unique:
        name = f"{name}_{uuid.uuid4().hex[:6]}"
    
    return {
        "id_ingredient": 0,
        "ingredient_name": name,
        "ingredient_quantifier": random.choice(quantifiers),
        "ingredient_icon_url": f"https://example.com/icons/{uuid.uuid4().hex[:8]}.png"
    }


def generate_recipe_image_data(recipe_id: int = 0) -> Dict[str, Any]:
    """Generate random recipe image data"""
    return {
        "id_recipe_image": 0,
        "recipe_image_url": f"https://example.com/recipes/{uuid.uuid4().hex[:8]}.jpg",
        "recipe_ref_id": recipe_id
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class RecipeTester:
    """Test runner for recipe endpoints"""
    
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
    
    async def _put(self, path: str, json_data: Dict) -> Tuple[int, Any]:
        """Send PUT request and return (status_code, data)"""
        try:
            response = await self.client.put(f"{self.base_url}{path}", json=json_data)
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _delete(self, path: str) -> Tuple[int, Any]:
        """Send DELETE request and return (status_code, data)"""
        try:
            response = await self.client.delete(f"{self.base_url}{path}")
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
        if self.context.user_ids:
            print(f"   User IDs: {self.context.user_ids[:10]}{'...' if len(self.context.user_ids) > 10 else ''}")
            for user in self.context.users[:5]:
                uid = user.get('id_app_user', user.get('id', user.get('id_user', 'N/A')))
                name = user.get('app_user_name', user.get('username', user.get('name', 'Unknown')))
                print(f"      - ID: {uid}, Name: {name}")
            if len(self.context.users) > 5:
                print(f"      ... and {len(self.context.users) - 5} more")
        else:
            print("   ⚠️  No user IDs found in the response")
        
        return True
    
    async def fetch_categories(self) -> bool:
        """Fetch recipe categories"""
        print("\n📋 Fetching recipe categories...")
        status, data = await self._get("/api/v1/recipes/categories")
        
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
        if self.context.category_ids:
            print(f"   Category IDs: {self.context.category_ids}")
            for cat in self.context.categories[:5]:
                cid = cat.get('id_recipe_category', cat.get('id', 'N/A'))
                name = cat.get('recipe_category_name', cat.get('name', 'Unknown'))
                print(f"      - ID: {cid}, Name: {name}")
            if len(self.context.categories) > 5:
                print(f"      ... and {len(self.context.categories) - 5} more")
        
        return True
    
    async def fetch_ingredients(self) -> bool:
        """Fetch existing ingredients"""
        print("\n📋 Fetching existing ingredients...")
        status, data = await self._get("/api/v1/recipes/ingredients/all", {"offset": 0, "limit": 100})
        
        if status != 200:
            print(f"   ❌ Failed to fetch ingredients: {status}")
            return False
        
        if isinstance(data, list):
            self.context.ingredients = data
        elif isinstance(data, dict):
            self.context.ingredients = data.get("data", data.get("items", []))
        else:
            self.context.ingredients = []
        
        print(f"   ✅ Found {len(self.context.ingredients)} ingredients")
        if self.context.ingredient_ids:
            print(f"   Ingredient IDs: {self.context.ingredient_ids[:10]}{'...' if len(self.context.ingredient_ids) > 10 else ''}")
            for ing in self.context.ingredients[:5]:
                iid = ing.get('id_ingredient', ing.get('id', 'N/A'))
                name = ing.get('ingredient_name', ing.get('name', 'Unknown'))
                print(f"      - ID: {iid}, Name: {name}")
            if len(self.context.ingredients) > 5:
                print(f"      ... and {len(self.context.ingredients) - 5} more")
        
        return True
    
    async def fetch_all_data(self) -> bool:
        """Fetch all required data"""
        print("\n" + "="*50)
        print("📊 FETCHING EXISTING DATA")
        print("="*50)
        
        user_ok = await self.fetch_users()
        cat_ok = await self.fetch_categories()
        ing_ok = await self.fetch_ingredients()
        
        # Fallback categories if API fails
        if not cat_ok:
            print("\n⚠️  Could not fetch categories. Using fallback category IDs: 1-10")
            for i in range(1, 11):
                self.context.categories.append({
                    "id_recipe_category": i,
                    "recipe_category_name": f"Category_{i}"
                })
            cat_ok = True
        
        return user_ok and cat_ok and ing_ok
    
    # ==================== Test Methods ====================
    
    def _add_result(self, name: str, passed: bool, details: str = "", response: Any = None):
        """Add a test result"""
        result = TestResult(name=name, passed=passed, details=details, response=response)
        self.results.append(result)
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
    
    # ==================== Recipe Test Cases ====================
    
    async def _create_recipe(
        self,
        test_name: str,
        recipe_data: Dict[str, Any],
        image_data: Optional[Dict] = None,
        expect_success: bool = True
    ) -> bool:
        """Helper to create a recipe and record result"""
        payload = {"recipe": recipe_data}
        if image_data:
            payload["image"] = image_data
        
        status, data = await self._post("/api/v1/recipes", payload)
        
        if expect_success:
            passed = status == 200
            if passed and data:
                self.context.created_recipes.append(data)
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                if data.get('message'):
                    details += f" - {data.get('message')}"
                elif data.get('detail'):
                    details += f" - {data.get('detail')}"
        else:
            # For negative tests, we expect 400, 404, 409, or 422
            passed = status in [400, 404, 409, 422]
            details = f"Correctly rejected (Status: {status})"
            if data and isinstance(data, dict):
                if data.get('detail'):
                    details += f" - {data.get('detail')}"
                elif data.get('message'):
                    details += f" - {data.get('message')}"
        
        self._add_result(test_name, passed, details, data if passed else None)
        return passed
    
    async def test_create_recipe_minimal(self) -> bool:
        """Test creating a recipe with minimal data"""
        print("\n📦 Test: Create Recipe (Minimal Data)")
        
        user_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        
        if not user_id:
            self._add_result("Create Recipe Minimal", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Create Recipe Minimal", False, "No categories available")
            return False
        
        recipe = generate_recipe_data(category_id, user_id)
        image = generate_recipe_image_data()
        
        print(f"   User ID: {user_id}")
        print(f"   Category ID: {category_id}")
        print(f"   Recipe Name: {recipe['recipe_name']}")
        
        return await self._create_recipe("Create Recipe Minimal", recipe, image_data=image, expect_success=True)
    
    async def test_create_recipe_full(self) -> bool:
        """Test creating a recipe with all data"""
        print("\n📦 Test: Create Recipe (Full Data)")
        
        user_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        
        if not user_id:
            self._add_result("Create Recipe Full", False, "No users available as owners")
            return False
        
        if not category_id:
            self._add_result("Create Recipe Full", False, "No categories available")
            return False
        
        recipe = generate_recipe_data(category_id, user_id)
        recipe["recipe_description"] = "A premium gourmet recipe with detailed instructions"
        recipe["recipe_instructions"] = "Step 1: Prepare all ingredients\nStep 2: Mix dry ingredients\nStep 3: Add wet ingredients\nStep 4: Bake at 350°F for 45 minutes\nStep 5: Let cool and serve"
        recipe["recipe_preparation_time"] = "90 minutes"
        
        image = generate_recipe_image_data()
        image["recipe_image_url"] = f"https://example.com/recipes/gourmet_{uuid.uuid4().hex[:8]}.jpg"
        
        print(f"   User ID: {user_id}")
        print(f"   Category ID: {category_id}")
        print(f"   Recipe Name: {recipe['recipe_name']}")
        
        return await self._create_recipe("Create Recipe Full", recipe, image_data=image, expect_success=True)
    
    async def test_create_recipe_invalid_category(self) -> bool:
        """Test creating a recipe with invalid category (should fail)"""
        print("\n❌ Test: Create Recipe with Invalid Category")
        
        user_id = self.context.get_random_user_id()
        
        if not user_id:
            self._add_result("Invalid Category", False, "No users available")
            return False
        
        recipe = generate_recipe_data(99999, user_id)  # Invalid category
        image = generate_recipe_image_data()
        
        print(f"   Using invalid category ID: 99999")
        
        return await self._create_recipe("Invalid Category", recipe, image_data=image, expect_success=False)
    
    async def test_create_recipe_invalid_user(self) -> bool:
        """Test creating a recipe with invalid user (should fail)"""
        print("\n❌ Test: Create Recipe with Invalid User")
        
        category_id = self.context.get_random_category_id()
        
        if not category_id:
            self._add_result("Invalid User", False, "No categories available")
            return False
        
        recipe = generate_recipe_data(category_id, 99999)  # Invalid user
        image = generate_recipe_image_data()
        
        print(f"   Using invalid user ID: 99999")
        
        return await self._create_recipe("Invalid User", recipe, image_data=image, expect_success=False)
    
    async def test_create_recipe_duplicate(self) -> bool:
        """Test creating a duplicate recipe (should fail)"""
        print("\n❌ Test: Create Duplicate Recipe")
        
        # First, ensure we have a recipe to duplicate
        if not self.context.recipe_ids:
            # Create a test recipe first
            print("   Creating a test recipe first...")
            user_id = self.context.get_random_user_id()
            category_id = self.context.get_random_category_id()
            
            if not user_id or not category_id:
                self._add_result("Duplicate Recipe", False, "No users or categories available")
                return False
            
            recipe = generate_recipe_data(category_id, user_id)
            image = generate_recipe_image_data()
            
            status, data = await self._post("/api/v1/recipes", {"recipe": recipe, "image": image})
            if status == 200 and data:
                self.context.created_recipes.append(data)
            else:
                self._add_result("Duplicate Recipe", False, "Failed to create initial recipe")
                return False
        
        # Get an existing recipe
        recipe_id = self.context.get_random_recipe_id()
        status, existing = await self._get(f"/api/v1/recipes/{recipe_id}")
        
        if status != 200:
            self._add_result("Duplicate Recipe", False, f"Failed to fetch recipe: {status}")
            return False
        
        # Try to create duplicate (remove ID and use same name)
        recipe_data = {k: v for k, v in existing.items() 
                      if k not in ['id_recipe', 'id', 'recipe_owner_id']}
        recipe_data['recipe_owner_id'] = existing.get('recipe_owner_id', 0)
        
        image = generate_recipe_image_data()
        
        print(f"   Attempting to duplicate recipe ID: {recipe_id}")
        
        return await self._create_recipe("Duplicate Recipe", recipe_data, image_data=image, expect_success=False)
    
    async def test_get_all_recipes(self) -> bool:
        """Test getting all recipes"""
        print("\n📋 Test: Get All Recipes")
        
        status, data = await self._get("/api/v1/recipes", {"offset": 0, "limit": 50})
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get All Recipes", passed, f"Status: {status}, Count: {count}")
        return passed
    
    async def test_get_recipes_by_category(self) -> bool:
        """Test getting recipes by category"""
        print("\n📋 Test: Get Recipes by Category")
        
        category_id = self.context.get_random_category_id()
        if not category_id:
            self._add_result("Get Recipes by Category", False, "No categories available")
            return False
        
        print(f"   Category ID: {category_id}")
        
        status, data = await self._get(
            "/api/v1/recipes",
            {"category_id": category_id, "offset": 0, "limit": 50}
        )
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Recipes by Category", passed, f"Status: {status}, Found: {count}")
        return passed
    
    async def test_get_recipes_by_user(self) -> bool:
        """Test getting recipes by user"""
        print("\n📋 Test: Get Recipes by User")
        
        user_id = self.context.get_random_user_id()
        if not user_id:
            self._add_result("Get Recipes by User", False, "No users available")
            return False
        
        print(f"   User ID: {user_id}")
        
        status, data = await self._get(
            "/api/v1/recipes",
            {"user_id": user_id, "offset": 0, "limit": 50}
        )
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Recipes by User", passed, f"Status: {status}, Found: {count}")
        return passed
    
    async def test_get_recipe_by_id(self) -> bool:
        """Test getting a recipe by ID"""
        print("\n📋 Test: Get Recipe by ID")
        
        # Ensure we have a recipe
        if not self.context.recipe_ids:
            # Create a test recipe first
            print("   Creating a test recipe first...")
            user_id = self.context.get_random_user_id()
            category_id = self.context.get_random_category_id()
            
            if not user_id or not category_id:
                self._add_result("Get Recipe by ID", False, "No users or categories available")
                return False
            
            recipe = generate_recipe_data(category_id, user_id)
            image = generate_recipe_image_data()
            
            status, data = await self._post("/api/v1/recipes", {"recipe": recipe, "image": image})
            if status == 200 and data:
                self.context.created_recipes.append(data)
            else:
                self._add_result("Get Recipe by ID", False, "Failed to create test recipe")
                return False
        
        recipe_id = self.context.get_random_recipe_id()
        print(f"   Recipe ID: {recipe_id}")
        
        status, data = await self._get(f"/api/v1/recipes/{recipe_id}")
        
        passed = status == 200 and data is not None
        details = f"Status: {status}"
        if passed:
            details += f" - Name: {data.get('recipe_name', 'Unknown')}"
        self._add_result("Get Recipe by ID", passed, details)
        return passed
    
    async def test_get_recipe_by_id_not_found(self) -> bool:
        """Test getting a non-existent recipe (should fail)"""
        print("\n❌ Test: Get Non-existent Recipe")
        
        status, data = await self._get("/api/v1/recipes/999999")
        
        passed = status == 404
        self._add_result("Get Non-existent Recipe", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_get_recipe_categories(self) -> bool:
        """Test getting recipe categories"""
        print("\n📋 Test: Get Recipe Categories")
        
        status, data = await self._get("/api/v1/recipes/categories")
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get Recipe Categories", passed, f"Status: {status}, Count: {count}")
        return passed
    
    async def test_update_recipe(self) -> bool:
        """Test updating a recipe"""
        print("\n📝 Test: Update Recipe")
        
        # Ensure we have a recipe
        if not self.context.recipe_ids:
            print("   Creating a test recipe first...")
            user_id = self.context.get_random_user_id()
            category_id = self.context.get_random_category_id()
            
            if not user_id or not category_id:
                self._add_result("Update Recipe", False, "No users or categories available")
                return False
            
            recipe = generate_recipe_data(category_id, user_id)
            image = generate_recipe_image_data()
            
            status, data = await self._post("/api/v1/recipes", {"recipe": recipe, "image": image})
            if status == 200 and data:
                self.context.created_recipes.append(data)
            else:
                self._add_result("Update Recipe", False, "Failed to create test recipe")
                return False
        
        recipe_id = self.context.get_random_recipe_id()
        print(f"   Recipe ID: {recipe_id}")
        
        # Get current recipe
        status, existing = await self._get(f"/api/v1/recipes/{recipe_id}")
        if status != 200:
            self._add_result("Update Recipe", False, f"Failed to fetch recipe: {status}")
            return False
        
        # Update with new data
        updated_recipe = existing.copy()
        updated_recipe["recipe_name"] = f"Updated Recipe {uuid.uuid4().hex[:6]}"
        updated_recipe["recipe_description"] = "Updated description with new details"
        updated_recipe["recipe_preparation_time"] = f"{random.choice([15, 30, 45, 60])} minutes"
        
        updated_image = {
            "id_recipe_image": existing.get('id_recipe_image', 0),
            "recipe_image_url": f"https://example.com/recipes/updated_{uuid.uuid4().hex[:8]}.jpg",
            "recipe_ref_id": recipe_id
        }
        
        status, data = await self._put(
            f"/api/v1/recipes/{recipe_id}",
            {"recipe": updated_recipe, "image": updated_image}
        )
        
        passed = status == 200
        details = f"Status: {status}"
        if passed and data:
            details += f" - Name: {data.get('recipe_name', 'Unknown')}"
        self._add_result("Update Recipe", passed, details)
        return passed
    
    async def test_update_recipe_invalid_id(self) -> bool:
        """Test updating a non-existent recipe (should fail)"""
        print("\n❌ Test: Update Non-existent Recipe")
        
        user_id = self.context.get_random_user_id()
        category_id = self.context.get_random_category_id()
        
        if not user_id or not category_id:
            self._add_result("Update Non-existent Recipe", False, "No users or categories available")
            return False
        
        recipe = generate_recipe_data(category_id, user_id)
        recipe["id_recipe"] = 999999
        
        image = {
            "id_recipe_image": 0,
            "recipe_image_url": "https://example.com/recipe.jpg",
            "recipe_ref_id": 999999
        }
        
        status, data = await self._put(
            "/api/v1/recipes/999999",
            {"recipe": recipe, "image": image}
        )
        
        passed = status == 404
        self._add_result("Update Non-existent Recipe", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_delete_recipe(self) -> bool:
        """Test deleting a recipe"""
        print("\n🗑️ Test: Delete Recipe")
        
        # Ensure we have a recipe
        if not self.context.recipe_ids:
            print("   Creating a test recipe first...")
            user_id = self.context.get_random_user_id()
            category_id = self.context.get_random_category_id()
            
            if not user_id or not category_id:
                self._add_result("Delete Recipe", False, "No users or categories available")
                return False
            
            recipe = generate_recipe_data(category_id, user_id)
            image = generate_recipe_image_data()
            
            status, data = await self._post("/api/v1/recipes", {"recipe": recipe, "image": image})
            if status == 200 and data:
                self.context.created_recipes.append(data)
            else:
                self._add_result("Delete Recipe", False, "Failed to create test recipe")
                return False
        
        recipe_id = self.context.get_random_recipe_id()
        print(f"   Recipe ID: {recipe_id}")
        
        status, data = await self._delete(f"/api/v1/recipes/{recipe_id}")
        
        passed = status in [200, 204]
        
        if passed:
            # Remove from context
            self.context.created_recipes = [
                r for r in self.context.created_recipes
                if r.get('id_recipe', r.get('id')) != recipe_id
            ]
            details = "Recipe deleted successfully"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Delete Recipe", passed, details)
        return passed
    
    async def test_delete_recipe_invalid_id(self) -> bool:
        """Test deleting a non-existent recipe (should fail)"""
        print("\n❌ Test: Delete Non-existent Recipe")
        
        status, data = await self._delete("/api/v1/recipes/999999")
        
        passed = status == 404
        self._add_result("Delete Non-existent Recipe", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    # ==================== Ingredient Test Cases ====================
    
    async def test_create_ingredient(self) -> bool:
        """Test creating an ingredient"""
        print("\n📦 Test: Create Ingredient")
        
        ingredient = generate_ingredient_data(ensure_unique=True)
        print(f"   Ingredient Name: {ingredient['ingredient_name']}")
        
        status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
        
        passed = status == 200
        if passed and data:
            self.context.created_ingredients.append(data)
            self.context.ingredients.append(data)
        
        details = f"Status: {status}"
        if passed and data:
            details += f" - Name: {data.get('ingredient_name', 'Unknown')}"
        elif not passed and data:
            details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Ingredient", passed, details, data if passed else None)
        return passed
    
    async def test_create_ingredient_duplicate(self) -> bool:
        """Test creating a duplicate ingredient (should fail)"""
        print("\n❌ Test: Create Duplicate Ingredient")
        
        # First, ensure we have an ingredient to duplicate
        if not self.context.ingredient_ids:
            # Create a test ingredient first
            print("   Creating a test ingredient first...")
            ingredient = generate_ingredient_data(ensure_unique=True)
            status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
            if status == 200 and data:
                self.context.created_ingredients.append(data)
                self.context.ingredients.append(data)
            else:
                self._add_result("Duplicate Ingredient", False, "Failed to create initial ingredient")
                return False
        
        # Get an existing ingredient
        ing_id = self.context.get_random_ingredient_id()
        status, existing = await self._get(f"/api/v1/recipes/ingredients/{ing_id}")
        
        if status != 200:
            self._add_result("Duplicate Ingredient", False, f"Failed to fetch ingredient: {status}")
            return False
        
        # Remove ID and try to create duplicate
        ingredient = {k: v for k, v in existing.items() if k not in ['id_ingredient', 'id']}
        
        print(f"   Attempting to duplicate ingredient: {ingredient.get('ingredient_name')}")
        
        status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
        
        passed = status in [409, 400, 422]
        self._add_result("Duplicate Ingredient", passed, f"Correctly blocked (Status: {status})")
        return passed
    
    async def test_get_all_ingredients(self) -> bool:
        """Test getting all ingredients"""
        print("\n📋 Test: Get All Ingredients")
        
        status, data = await self._get("/api/v1/recipes/ingredients/all", {"offset": 0, "limit": 50})
        
        passed = status == 200
        count = len(data) if isinstance(data, list) else 0
        self._add_result("Get All Ingredients", passed, f"Status: {status}, Count: {count}")
        return passed
    
    async def test_get_ingredient_by_id(self) -> bool:
        """Test getting an ingredient by ID"""
        print("\n📋 Test: Get Ingredient by ID")
        
        # Ensure we have an ingredient
        if not self.context.ingredient_ids:
            # Create a test ingredient first
            print("   Creating a test ingredient first...")
            ingredient = generate_ingredient_data(ensure_unique=True)
            status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
            if status == 200 and data:
                self.context.created_ingredients.append(data)
                self.context.ingredients.append(data)
            else:
                self._add_result("Get Ingredient by ID", False, "Failed to create test ingredient")
                return False
        
        ingredient_id = self.context.get_random_ingredient_id()
        print(f"   Ingredient ID: {ingredient_id}")
        
        status, data = await self._get(f"/api/v1/recipes/ingredients/{ingredient_id}")
        
        passed = status == 200 and data is not None
        details = f"Status: {status}"
        if passed:
            details += f" - Name: {data.get('ingredient_name', 'Unknown')}"
        self._add_result("Get Ingredient by ID", passed, details)
        return passed
    
    async def test_get_ingredient_by_id_not_found(self) -> bool:
        """Test getting a non-existent ingredient (should fail)"""
        print("\n❌ Test: Get Non-existent Ingredient")
        
        status, data = await self._get("/api/v1/recipes/ingredients/999999")
        
        passed = status == 404
        self._add_result("Get Non-existent Ingredient", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_update_ingredient(self) -> bool:
        """Test updating an ingredient"""
        print("\n📝 Test: Update Ingredient")
        
        # Ensure we have an ingredient
        if not self.context.ingredient_ids:
            # Create a test ingredient first
            print("   Creating a test ingredient first...")
            ingredient = generate_ingredient_data(ensure_unique=True)
            status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
            if status == 200 and data:
                self.context.created_ingredients.append(data)
                self.context.ingredients.append(data)
            else:
                self._add_result("Update Ingredient", False, "Failed to create test ingredient")
                return False
        
        ingredient_id = self.context.get_random_ingredient_id()
        print(f"   Ingredient ID: {ingredient_id}")
        
        # Get current ingredient
        status, existing = await self._get(f"/api/v1/recipes/ingredients/{ingredient_id}")
        if status != 200:
            self._add_result("Update Ingredient", False, f"Failed to fetch ingredient: {status}")
            return False
        
        # Update with new data
        updated_ingredient = existing.copy()
        updated_ingredient["ingredient_name"] = f"Updated Ingredient {uuid.uuid4().hex[:6]}"
        updated_ingredient["ingredient_quantifier"] = random.choice(["g", "kg", "ml", "tsp", "tbsp", "cup"])
        
        status, data = await self._put(
            f"/api/v1/recipes/ingredients/{ingredient_id}",
            updated_ingredient
        )
        
        passed = status == 200
        details = f"Status: {status}"
        if passed and data:
            details += f" - Name: {data.get('ingredient_name', 'Unknown')}"
        self._add_result("Update Ingredient", passed, details)
        return passed
    
    async def test_update_ingredient_invalid_id(self) -> bool:
        """Test updating a non-existent ingredient (should fail)"""
        print("\n❌ Test: Update Non-existent Ingredient")
        
        ingredient = generate_ingredient_data(ensure_unique=True)
        ingredient["id_ingredient"] = 999999
        
        status, data = await self._put("/api/v1/recipes/ingredients/999999", ingredient)
        
        passed = status == 404
        self._add_result("Update Non-existent Ingredient", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    async def test_delete_ingredient(self) -> bool:
        """Test deleting an ingredient"""
        print("\n🗑️ Test: Delete Ingredient")
        
        # Ensure we have an ingredient
        if not self.context.ingredient_ids:
            # Create a test ingredient first
            print("   Creating a test ingredient first...")
            ingredient = generate_ingredient_data(ensure_unique=True)
            status, data = await self._post("/api/v1/recipes/ingredients", ingredient)
            if status == 200 and data:
                self.context.created_ingredients.append(data)
                self.context.ingredients.append(data)
            else:
                self._add_result("Delete Ingredient", False, "Failed to create test ingredient")
                return False
        
        ingredient_id = self.context.get_random_ingredient_id()
        print(f"   Ingredient ID: {ingredient_id}")
        
        status, data = await self._delete(f"/api/v1/recipes/ingredients/{ingredient_id}")
        
        passed = status in [200, 204]
        
        if passed:
            # Remove from context
            self.context.created_ingredients = [
                i for i in self.context.created_ingredients
                if i.get('id_ingredient', i.get('id')) != ingredient_id
            ]
            self.context.ingredients = [
                i for i in self.context.ingredients
                if i.get('id_ingredient', i.get('id')) != ingredient_id
            ]
            details = "Ingredient deleted successfully"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Delete Ingredient", passed, details)
        return passed
    
    async def test_delete_ingredient_invalid_id(self) -> bool:
        """Test deleting a non-existent ingredient (should fail)"""
        print("\n❌ Test: Delete Non-existent Ingredient")
        
        status, data = await self._delete("/api/v1/recipes/ingredients/999999")
        
        passed = status == 404
        self._add_result("Delete Non-existent Ingredient", passed, f"Correctly returned 404 (Status: {status})")
        return passed
    
    # ==================== Main Runner ====================
    
    async def run_all_tests(self) -> None:
        """Run all test suites"""
        print("\n" + "="*70)
        print("🍽️ RECIPE ENDPOINT TESTS")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Fetch data
        if not await self.fetch_all_data():
            print("\n⚠️  Failed to fetch required data. Some tests may fail.")
        
        # Check requirements
        if not self.context.users:
            print("\n⚠️  No users found! Please create users first.")
            print("   Test will attempt to use fallback user ID: 1")
            self.context.users = [{"id_app_user": 1, "app_user_name": "Test User"}]
        
        if not self.context.category_ids:
            print("\n⚠️  No categories found! Using fallback category IDs: 1-10")
            self.context.categories = [
                {"id_recipe_category": i, "recipe_category_name": f"Category_{i}"}
                for i in range(1, 11)
            ]
        
        print("\n" + "="*70)
        print("📝 RUNNING TESTS")
        print("="*70)
        
        # Recipe tests
        await self.test_create_recipe_minimal()
        await self.test_create_recipe_full()
        await self.test_create_recipe_invalid_category()
        await self.test_create_recipe_invalid_user()
        await self.test_create_recipe_duplicate()
        await self.test_get_all_recipes()
        await self.test_get_recipes_by_category()
        await self.test_get_recipes_by_user()
        await self.test_get_recipe_by_id()
        await self.test_get_recipe_by_id_not_found()
        await self.test_get_recipe_categories()
        
        # Only run update and delete if we have recipes
        if self.context.recipe_ids:
            await self.test_update_recipe()
            await self.test_update_recipe_invalid_id()
            await self.test_delete_recipe()
            await self.test_delete_recipe_invalid_id()
        else:
            print("\n⚠️  No recipes created. Skipping update/delete tests.")
        
        # Ingredient tests
        await self.test_create_ingredient()
        await self.test_create_ingredient_duplicate()
        await self.test_get_all_ingredients()
        await self.test_get_ingredient_by_id()
        await self.test_get_ingredient_by_id_not_found()
        
        # Only run update and delete if we have ingredients
        if self.context.ingredient_ids:
            await self.test_update_ingredient()
            await self.test_update_ingredient_invalid_id()
            await self.test_delete_ingredient()
            await self.test_delete_ingredient_invalid_id()
        else:
            print("\n⚠️  No ingredients created. Skipping ingredient update/delete tests.")
        
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
        print(f"📦 Recipes Created: {len(self.context.created_recipes)}")
        print(f"🧂 Ingredients Created: {len(self.context.created_ingredients)}")
        print(f"👤 Users Available: {len(self.context.users)}")
        print(f"📋 Categories: {len(self.context.categories)}")
        print(f"🍽️  Total Ingredients in DB: {len(self.context.ingredients)}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            if not self.context.users:
                print("💡 No users found! Create users first.")
            if not self.context.category_ids:
                print("💡 No categories found! Seed categories first.")
            if self.context.users and self.context.category_ids:
                print("💡 Check that the recipe endpoints are working and the database is accessible.")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test recipe endpoints")
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
        "--user-id",
        type=int,
        help="Use specific user ID as owner for all tests"
    )
    
    args = parser.parse_args()
    
    async with RecipeTester(args.url) as tester:
        # If specific IDs are provided, use them
        if args.category_id:
            tester.context.categories = [{"id_recipe_category": args.category_id, "recipe_category_name": "Custom"}]
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