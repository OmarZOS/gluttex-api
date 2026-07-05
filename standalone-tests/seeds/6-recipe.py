#!/usr/bin/env python3
"""
Recipe Endpoint Test Runner with Authentication from Context
Run with: python test_recipe_runner.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================================
# DATA CLASSES (imported from test_runner context)
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
class RecipeContext:
    """Recipe-specific test context"""
    users: List[TestUser] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    ingredients: List[Dict[str, Any]] = field(default_factory=list)
    created_recipes: List[Dict[str, Any]] = field(default_factory=list)
    created_ingredients: List[Dict[str, Any]] = field(default_factory=list)
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def save(self, filename: str = "recipe_test_context.json"):
        data = {
            'users': [u.to_dict() for u in self.users],
            'categories': self.categories,
            'ingredients': self.ingredients,
            'created_recipes': self.created_recipes,
            'created_ingredients': self.created_ingredients,
            'timestamp': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Recipe test context saved to {filename}")
    
    def load(self, filename: str = "recipe_test_context.json"):
        if Path(filename).exists():
            with open(filename, 'r') as f:
                data = json.load(f)
            self.users = [TestUser.from_dict(u) for u in data.get('users', [])]
            self.categories = data.get('categories', [])
            self.ingredients = data.get('ingredients', [])
            self.created_recipes = data.get('created_recipes', [])
            self.created_ingredients = data.get('created_ingredients', [])
            print(f"📂 Recipe test context loaded from {filename}")
            return True
        return False
    
    @property
    def user_ids(self) -> List[int]:
        return [u.id for u in self.users if u.id > 0]
    
    @property
    def category_ids(self) -> List[int]:
        ids = []
        for c in self.categories:
            cid = c.get('id_recipe_category') or c.get('id')
            if cid and isinstance(cid, int):
                ids.append(cid)
        return ids
    
    @property
    def ingredient_ids(self) -> List[int]:
        ids = []
        for i in self.ingredients:
            iid = i.get('id_ingredient') or i.get('id')
            if iid and isinstance(iid, int):
                ids.append(iid)
        return ids
    
    @property
    def recipe_ids(self) -> List[int]:
        ids = []
        for r in self.created_recipes:
            rid = r.get('id_recipe') or r.get('id')
            if rid and isinstance(rid, int):
                ids.append(rid)
        return ids
    
    def get_random_user(self) -> Optional[TestUser]:
        if not self.users:
            return None
        return random.choice(self.users)
    
    def get_random_user_id(self) -> int:
        user = self.get_random_user()
        return user.id if user else 0
    
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

def generate_unique_username() -> str:
    return f"recipeuser_{uuid.uuid4().hex[:8]}"

def generate_unique_email() -> str:
    return f"recipe_{uuid.uuid4().hex[:8]}@example.com"

def generate_strong_password() -> str:
    return f"Recipe_{uuid.uuid4().hex[:8]}!@#"

def generate_recipe_data(category_id: int = 0, user_id: int = 0) -> Dict[str, Any]:
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
    
    base_name = random.choice(recipe_names)
    unique_name = f"{base_name}_{uuid.uuid4().hex[:6]}"
    
    return {
        "id_recipe": 0,
        "recipe_category_id": category_id,
        "recipe_name": unique_name,
        "recipe_description": random.choice(recipe_descriptions),
        "recipe_instructions": f"Step 1: Prepare ingredients\nStep 2: Mix together\nStep 3: Cook for {random.choice([15, 30, 45, 60])} minutes\nStep 4: Serve hot",
        "recipe_preparation_time": f"{random.choice([15, 30, 45, 60, 90, 120])} minutes",
        "recipe_owner_id": user_id
    }

def generate_recipe_image_data(recipe_id: int = 0) -> Dict[str, Any]:
    return {
        "id_recipe_image": 0,
        "recipe_image_url": f"https://example.com/recipes/{uuid.uuid4().hex[:8]}.jpg",
        "recipe_ref_id": recipe_id
    }

def generate_ingredient_data(ensure_unique: bool = True) -> Dict[str, Any]:
    ingredient_names = [
        "Flour", "Sugar", "Eggs", "Butter", "Milk",
        "Chocolate", "Vanilla Extract", "Baking Powder",
        "Salt", "Cinnamon", "Nutmeg", "Ginger", "Garlic",
        "Onion", "Tomato", "Olive Oil", "Basil",
        "Oregano", "Thyme", "Rosemary", "Cumin",
        "Paprika", "Turmeric", "Coriander", "Cardamom"
    ]
    
    # Only use values that exist in the ENUM
    quantifiers = ['g', 'kg', 'mg', 'L', 'mL', 'pc', 'pkg', 'box', 'bag', 'slice', 'cup']
    
    name = random.choice(ingredient_names)
    if ensure_unique:
        name = f"{name}_{uuid.uuid4().hex[:6]}"
    
    return {
        "id_ingredient": 0,
        "ingredient_name": name,
        "ingredient_quantifier": random.choice(quantifiers),
        "ingredient_icon_url": f"https://example.com/icons/{uuid.uuid4().hex[:8]}.png"
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class RecipeTestRunner:
    def __init__(self, base_url: str = "http://localhost:9000", context_file: str = "test_context.json"):
        self.base_url = base_url
        self.context_file = context_file
        self.client = None
        self.context = RecipeContext()
        self.results = []
        self._loaded_from_context = False
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        # Try to load from main test context first, then recipe context
        if Path(self.context_file).exists():
            self._load_from_test_context(self.context_file)
        elif Path("recipe_test_context.json").exists():
            self.context.load("recipe_test_context.json")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def _load_from_test_context(self, filename: str):
        """Load users and tokens from the main test context"""
        if Path(filename).exists():
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Load users with their tokens
            users = [TestUser.from_dict(u) for u in data.get('users', [])]
            self.context.users = users
            
            print(f"📂 Loaded {len(users)} users from main test context")
            
            # Check token validity
            valid_tokens = 0
            for user in users:
                if user.is_token_valid():
                    valid_tokens += 1
                elif user.access_token:
                    print(f"   ⚠️ Token for {user.username} has expired")
            
            print(f"   🔐 {valid_tokens}/{len(users)} users have valid tokens")
            return True
        return False
    
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
        
        return 0
    
    # ==================== DATA FETCHING ====================
    
    async def fetch_categories(self) -> bool:
        """Fetch recipe categories"""
        print("\n📋 Fetching recipe categories...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/categories"
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.context.categories = data
                elif isinstance(data, dict):
                    self.context.categories = data.get("data", data.get("items", []))
                else:
                    self.context.categories = []
                
                print(f"   ✅ Found {len(self.context.categories)} categories")
                if self.context.category_ids:
                    print(f"   Category IDs: {self.context.category_ids}")
                return True
            else:
                print(f"   ❌ Failed to fetch categories: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error fetching categories: {e}")
            return False
    
    # ==================== RECIPE TESTS ====================
    
    async def test_create_recipe(self, user: TestUser) -> Optional[int]:
        """Test creating a recipe"""
        print(f"\n📦 Creating recipe for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        # Get or create category
        category_id = self.context.get_random_category_id()
        if not category_id:
            category_id = 1
            print(f"   ⚠️ No categories found, using default: {category_id}")
        
        # Generate recipe data
        recipe_data = generate_recipe_data(category_id, user.id)
        image_data = generate_recipe_image_data()
        
        print(f"   Recipe: {recipe_data['recipe_name']}")
        print(f"   Category ID: {category_id}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/recipes",
                json={
                    "recipe": recipe_data,
                    "image": image_data
                },
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                recipe_id = self.extract_id_from_response(
                    result, 
                    ['id_recipe', 'id', 'recipe_id']
                )
                
                if recipe_id > 0:
                    self.context.created_recipes.append(result)
                    print(f"   ✅ Created recipe: {recipe_id}")
                    self.print_result("Create Recipe", True, f"Recipe {recipe_id} created")
                    return recipe_id
                else:
                    print(f"   ⚠️ Could not extract recipe ID from response")
                    self.print_result("Create Recipe", True, "Recipe created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create recipe: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Create Recipe", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating recipe: {e}")
            self.print_result("Create Recipe", False, str(e))
            return None
    
    async def test_get_all_recipes(self) -> bool:
        """Test getting all recipes"""
        print("\n📋 Getting all recipes...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes",
                params={"offset": 0, "limit": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ Found {count} recipes")
                self.print_result("Get All Recipes", True, f"Count: {count}")
                return True
            else:
                print(f"   ❌ Failed to get recipes: {response.status_code}")
                self.print_result("Get All Recipes", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting recipes: {e}")
            self.print_result("Get All Recipes", False, str(e))
            return False
    
    async def test_get_recipes_by_category(self) -> bool:
        """Test getting recipes by category"""
        print("\n📋 Getting recipes by category...")
        
        category_id = self.context.get_random_category_id()
        if not category_id:
            category_id = 1
            print(f"   ⚠️ No categories found, using default: {category_id}")
        
        print(f"   Category ID: {category_id}")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes",
                params={"category_id": category_id, "offset": 0, "limit": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ Found {count} recipes in category {category_id}")
                self.print_result("Get Recipes by Category", True, f"Count: {count}")
                return True
            else:
                print(f"   ❌ Failed to get recipes: {response.status_code}")
                self.print_result("Get Recipes by Category", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting recipes: {e}")
            self.print_result("Get Recipes by Category", False, str(e))
            return False
    
    async def test_get_recipes_by_user(self, user: TestUser) -> bool:
        """Test getting recipes by user"""
        print(f"\n📋 Getting recipes for user: {user.username}")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes",
                params={"user_id": user.id, "offset": 0, "limit": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ Found {count} recipes for user {user.id}")
                self.print_result("Get Recipes by User", True, f"Count: {count}")
                return True
            else:
                print(f"   ❌ Failed to get recipes: {response.status_code}")
                self.print_result("Get Recipes by User", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting recipes: {e}")
            self.print_result("Get Recipes by User", False, str(e))
            return False
    
    async def test_get_recipe_by_id(self, recipe_id: int) -> bool:
        """Test getting a recipe by ID"""
        print(f"\n📋 Getting recipe by ID: {recipe_id}")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/{recipe_id}",
                params={"full": True}
            )
            
            if response.status_code == 200:
                data = response.json()
                name = data.get('recipe_name', 'Unknown')
                print(f"   ✅ Found recipe: {name}")
                self.print_result("Get Recipe by ID", True, f"Name: {name}")
                return True
            else:
                print(f"   ❌ Failed to get recipe: {response.status_code}")
                self.print_result("Get Recipe by ID", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting recipe: {e}")
            self.print_result("Get Recipe by ID", False, str(e))
            return False
    
    async def test_get_recipe_categories(self) -> bool:
        """Test getting recipe categories"""
        print("\n📋 Getting recipe categories...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/categories"
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ Found {count} categories")
                self.print_result("Get Recipe Categories", True, f"Count: {count}")
                return True
            else:
                print(f"   ❌ Failed to get categories: {response.status_code}")
                self.print_result("Get Recipe Categories", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting categories: {e}")
            self.print_result("Get Recipe Categories", False, str(e))
            return False
    
    async def test_update_recipe(self, user: TestUser, recipe_id: int) -> bool:
        """Test updating a recipe"""
        print(f"\n📝 Updating recipe: {recipe_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            get_response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/{recipe_id}",
                params={"full": True}
            )
            
            if get_response.status_code != 200:
                print(f"   ❌ Failed to get recipe: {get_response.status_code}")
                return False
            
            current = get_response.json()
            
            updated_recipe = {
                "id_recipe": recipe_id,
                "recipe_category_id": current.get('recipe_category_id', 1),
                "recipe_name": f"Updated Recipe {uuid.uuid4().hex[:6]}",
                "recipe_description": "This recipe has been updated with new details",
                "recipe_instructions": "Updated instructions: Step 1, Step 2, Step 3",
                "recipe_preparation_time": "45 minutes",
                "recipe_owner_id": user.id
            }
            
            updated_image = {
                "id_recipe_image": current.get('id_recipe_image', 0),
                "recipe_image_url": f"https://example.com/recipes/updated_{uuid.uuid4().hex[:8]}.jpg",
                "recipe_ref_id": recipe_id
            }
            
            response = await self.client.put(
                f"{self.base_url}/api/v1/recipes/{recipe_id}",
                json={
                    "recipe": updated_recipe,
                    "image": updated_image
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Updated recipe: {data.get('recipe_name', 'Unknown')}")
                self.print_result("Update Recipe", True, "Recipe updated successfully")
                return True
            else:
                print(f"   ❌ Failed to update recipe: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Update Recipe", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating recipe: {e}")
            self.print_result("Update Recipe", False, str(e))
            return False
    
    async def test_delete_recipe(self, user: TestUser, recipe_id: int) -> bool:
        """Test deleting a recipe"""
        print(f"\n🗑️ Deleting recipe: {recipe_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/v1/recipes/{recipe_id}",
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                print(f"   ✅ Recipe deleted successfully")
                self.print_result("Delete Recipe", True, "Recipe deleted")
                return True
            else:
                print(f"   ❌ Failed to delete recipe: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Delete Recipe", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error deleting recipe: {e}")
            self.print_result("Delete Recipe", False, str(e))
            return False
    
    # ==================== INGREDIENT TESTS ====================
    
    async def test_create_ingredient(self, user: TestUser) -> Optional[int]:
        """Test creating an ingredient"""
        print(f"\n🧂 Creating ingredient for user: {user.username}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return None
        
        ingredient_data = generate_ingredient_data(ensure_unique=True)
        print(f"   Ingredient: {ingredient_data['ingredient_name']}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/recipes/ingredients",
                json=ingredient_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ingredient_id = self.extract_id_from_response(
                    result,
                    ['id_ingredient', 'id', 'ingredient_id']
                )
                
                if ingredient_id > 0:
                    self.context.created_ingredients.append(result)
                    self.context.ingredients.append(result)
                    print(f"   ✅ Created ingredient: {ingredient_id}")
                    self.print_result("Create Ingredient", True, f"Ingredient {ingredient_id} created")
                    return ingredient_id
                else:
                    print(f"   ⚠️ Could not extract ingredient ID from response")
                    self.print_result("Create Ingredient", True, "Ingredient created but ID extraction failed")
                    return 0
            else:
                print(f"   ❌ Failed to create ingredient: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Create Ingredient", False, f"Status: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error creating ingredient: {e}")
            self.print_result("Create Ingredient", False, str(e))
            return None
    
    async def test_get_all_ingredients(self) -> bool:
        """Test getting all ingredients"""
        print("\n📋 Getting all ingredients...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/ingredients/all",
                params={"offset": 0, "limit": 50}
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(f"   ✅ Found {count} ingredients")
                self.print_result("Get All Ingredients", True, f"Count: {count}")
                return True
            else:
                print(f"   ❌ Failed to get ingredients: {response.status_code}")
                self.print_result("Get All Ingredients", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting ingredients: {e}")
            self.print_result("Get All Ingredients", False, str(e))
            return False
    
    async def test_get_ingredient_by_id(self, ingredient_id: int) -> bool:
        """Test getting an ingredient by ID"""
        print(f"\n📋 Getting ingredient by ID: {ingredient_id}")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/ingredients/{ingredient_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                name = data.get('ingredient_name', 'Unknown')
                print(f"   ✅ Found ingredient: {name}")
                self.print_result("Get Ingredient by ID", True, f"Name: {name}")
                return True
            else:
                print(f"   ❌ Failed to get ingredient: {response.status_code}")
                self.print_result("Get Ingredient by ID", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error getting ingredient: {e}")
            self.print_result("Get Ingredient by ID", False, str(e))
            return False
    
    async def test_update_ingredient(self, user: TestUser, ingredient_id: int) -> bool:
        """Test updating an ingredient"""
        print(f"\n📝 Updating ingredient: {ingredient_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        valid_quantifiers = ['g', 'kg', 'mg', 'L', 'mL', 'pc', 'pkg', 'box', 'bag', 'slice', 'cup']
        
        try:
            get_response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/ingredients/{ingredient_id}"
            )
            
            if get_response.status_code != 200:
                print(f"   ❌ Failed to get ingredient: {get_response.status_code}")
                return False
            
            current = get_response.json()
            
            updated_ingredient = {
                "id_ingredient": ingredient_id,
                "ingredient_name": f"Updated Ingredient {uuid.uuid4().hex[:6]}",
                "ingredient_quantifier": random.choice(valid_quantifiers),
                "ingredient_icon_url": f"https://example.com/icons/updated_{uuid.uuid4().hex[:8]}.png"
            }
            
            print(f"   Updated quantifier: {updated_ingredient['ingredient_quantifier']}")
            
            response = await self.client.put(
                f"{self.base_url}/api/v1/recipes/ingredients/{ingredient_id}",
                json=updated_ingredient,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Updated ingredient: {data.get('ingredient_name', 'Unknown')}")
                self.print_result("Update Ingredient", True, "Ingredient updated successfully")
                return True
            else:
                print(f"   ❌ Failed to update ingredient: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Update Ingredient", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating ingredient: {e}")
            self.print_result("Update Ingredient", False, str(e))
            return False
    
    async def test_delete_ingredient(self, user: TestUser, ingredient_id: int) -> bool:
        """Test deleting an ingredient"""
        print(f"\n🗑️ Deleting ingredient: {ingredient_id}")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No authentication token available")
            return False
        
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/v1/recipes/ingredients/{ingredient_id}",
                headers=headers
            )
            
            if response.status_code in [200, 204]:
                print(f"   ✅ Ingredient deleted successfully")
                self.print_result("Delete Ingredient", True, "Ingredient deleted")
                return True
            else:
                print(f"   ❌ Failed to delete ingredient: {response.status_code}")
                print(f"      {response.text[:200]}")
                self.print_result("Delete Ingredient", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error deleting ingredient: {e}")
            self.print_result("Delete Ingredient", False, str(e))
            return False
    
    # ==================== NEGATIVE TESTS ====================
    
    async def test_get_nonexistent_recipe(self) -> bool:
        """Test getting a non-existent recipe (should fail)"""
        print("\n❌ Getting non-existent recipe...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/999999"
            )
            
            passed = response.status_code == 404
            self.print_result("Get Non-existent Recipe", passed, f"Status: {response.status_code}")
            return passed
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.print_result("Get Non-existent Recipe", False, str(e))
            return False
    
    async def test_get_nonexistent_ingredient(self) -> bool:
        """Test getting a non-existent ingredient (should fail)"""
        print("\n❌ Getting non-existent ingredient...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/recipes/ingredients/999999"
            )
            
            passed = response.status_code == 404
            self.print_result("Get Non-existent Ingredient", passed, f"Status: {response.status_code}")
            return passed
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.print_result("Get Non-existent Ingredient", False, str(e))
            return False
    
    # ==================== MAIN RUNNER ====================
    
    async def run_tests(self, context_file: str = "test_context.json"):
        print("\n" + "="*70)
        print("🍽️ RECIPE ENDPOINT TEST RUNNER")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"📂 Using context from: {context_file}")
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Load users from the main test context
        if Path(context_file).exists():
            self._load_from_test_context(context_file)
        else:
            print(f"⚠️ Context file {context_file} not found!")
            print("   Please run the main test runner first to create test users.")
            return
        
        if not self.context.users:
            print("\n❌ No users found in context. Please run the main test runner first.")
            return
        
        # Get an authenticated user
        authenticated_users = [u for u in self.context.users if u.is_token_valid()]
        if not authenticated_users:
            print("\n⚠️ No valid tokens found. Trying to refresh tokens...")
            # Try to refresh tokens by logging in again
            for user in self.context.users:
                if user.access_token and not user.is_token_valid():
                    # Try to refresh token (if refresh endpoint exists)
                    # For now, just use the first user with any token
                    pass
            
            authenticated_users = [u for u in self.context.users if u.access_token]
            if not authenticated_users:
                print("\n❌ No authenticated users available.")
                print("   Please run the main test runner with login enabled.")
                return
        
        test_user = authenticated_users[0]
        print(f"\n👤 Using user '{test_user.username}' (ID: {test_user.id})")
        print(f"   🔐 Token valid until: {test_user.token_expires_at}")
        
        # Fetch categories
        await self.fetch_categories()
        
        # ==================== RUN TESTS ====================
        print("\n" + "="*70)
        print("🧪 Running Recipe Tests")
        print("="*70)
        
        # Recipe tests
        recipe_id = await self.test_create_recipe(test_user)
        
        if recipe_id and recipe_id > 0:
            self.context.created_recipes.append({"id_recipe": recipe_id})
            await self.test_get_recipe_by_id(recipe_id)
            await self.test_update_recipe(test_user, recipe_id)
        
        await self.test_get_all_recipes()
        await self.test_get_recipes_by_category()
        await self.test_get_recipes_by_user(test_user)
        await self.test_get_recipe_categories()
        
        # Negative tests
        await self.test_get_nonexistent_recipe()
        
        # Ingredient tests
        ingredient_id = await self.test_create_ingredient(test_user)
        
        if ingredient_id and ingredient_id > 0:
            self.context.created_ingredients.append({"id_ingredient": ingredient_id})
            self.context.ingredients.append({"id_ingredient": ingredient_id})
            await self.test_get_ingredient_by_id(ingredient_id)
            await self.test_update_ingredient(test_user, ingredient_id)
        
        await self.test_get_all_ingredients()
        
        # Negative tests
        await self.test_get_nonexistent_ingredient()
        
        # Delete tests
        if recipe_id and recipe_id > 0:
            await self.test_delete_recipe(test_user, recipe_id)
        
        if ingredient_id and ingredient_id > 0:
            await self.test_delete_ingredient(test_user, ingredient_id)
        
        # Save context
        print("\n💾 Saving Recipe Test Context")
        print("="*70)
        self.context.save("recipe_test_context.json")
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 RECIPE TEST SUMMARY")
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
        print(f"   🔐 Valid Tokens: {len([u for u in self.context.users if u.is_token_valid()])}")
        print(f"   📋 Categories: {len(self.context.categories)}")
        print(f"   🍽️  Recipes Created: {len(self.context.created_recipes)}")
        print(f"   🧂 Ingredients Created: {len(self.context.created_ingredients)}")
        
        if self.context.recipe_ids:
            print(f"\n📋 Recipe IDs: {', '.join(map(str, self.context.recipe_ids[:10]))}")
        
        if self.context.ingredient_ids:
            print(f"🧂 Ingredient IDs: {', '.join(map(str, self.context.ingredient_ids[:10]))}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
            print("\n💡 Common issues:")
            print("   1. Check if the recipe service is running")
            print("   2. Verify the database has recipe categories")
            print("   3. Ensure the authentication token is valid")
            print("   4. Check that the user has proper permissions")
        
        print("="*70)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Recipe Endpoint Test Runner")
    parser.add_argument("--url", default="http://localhost:9000", help="Base URL of the API")
    parser.add_argument("--context-file", default="test_context.json", help="Main test context file to load users from")
    
    args = parser.parse_args()
    
    async with RecipeTestRunner(args.url, args.context_file) as runner:
        await runner.run_tests(context_file=args.context_file)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)