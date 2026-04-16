# #!/usr/bin/env python3
# """
# Test script for Recipe Router Endpoints
# Run with: python test_recipe_endpoints.py
# """

# import requests
# import json
# import sys
# from datetime import datetime

# # Configuration
# BASE_URL = "http://localhost:9000/api"  # Change to your server URL
# HEADERS = {"Content-Type": "application/json"}

# def print_test_result(test_name, success, response=None, error=None):
#     """Helper to print test results"""
#     status = "✅ PASS" if success else "❌ FAIL"
#     print(f"{status} {test_name}")
    
#     if response:
#         print(f"   Status: {response.status_code}")
#         if response.text:
#             try:
#                 # Try to format JSON response nicely
#                 response_data = response.json()
#                 if isinstance(response_data, list) and len(response_data) > 3:
#                     print(f"   Response: List with {len(response_data)} items")
#                 else:
#                     print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
#             except:
#                 print(f"   Response: {response.text}")
    
#     if error:
#         print(f"   Error: {error}")
    
#     print("-" * 50)

# def test_get_recipe_categories():
#     """Test GET /recipe/category/all endpoint"""
#     print("Testing GET /recipe/category/all...")
#     try:
#         url = f"{BASE_URL}/recipe/category/all"
#         response = requests.get(url)
        
#         success = response.status_code == 200
#         print_test_result("Get Recipe Categories", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Get Recipe Categories", False, error=str(e))
#         return False

# def test_get_ingredients():
#     """Test GET /ingredient/{offset}/{limit} endpoint"""
#     print("Testing GET /ingredient/{offset}/{limit}...")
#     try:
#         url = f"{BASE_URL}/ingredient/0/10"
#         response = requests.get(url)
        
#         success = response.status_code == 200
#         print_test_result("Get Ingredients List", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Get Ingredients List", False, error=str(e))
#         return False

# def test_get_recipes_by_category():
#     """Test GET /recipe/{user_id}/{category_id}/{offset}/{limit} endpoint"""
#     print("Testing GET /recipe/{user_id}/{category_id}/{offset}/{limit}...")
#     try:
#         # Test with category ID 0 (might be "all categories") or 1
#         url = f"{BASE_URL}/recipe/1/1/0/5"  # user_id=1, category_id=1, offset=0, limit=5
#         response = requests.get(url)
        
#         success = response.status_code in [200, 404]  # 404 if no recipes found
#         print_test_result("Get Recipes by Category", success, response)
        
#         # If we got recipes, return the first recipe ID for later tests
#         if success and response.status_code == 200:
#             recipes = response.json()
#             if isinstance(recipes, list) and len(recipes) > 0:
#                 return recipes[0].get('id_recipe')
#         return None
        
#     except Exception as e:
#         print_test_result("Get Recipes by Category", False, error=str(e))
#         return None

# def test_get_recipe_by_id(recipe_id):
#     """Test GET /recipe/{recipe_id} endpoint"""
#     print(f"Testing GET /recipe/{recipe_id}...")
#     try:
#         url = f"{BASE_URL}/recipe/{recipe_id}"
#         response = requests.get(url)
        
#         success = response.status_code in [200, 404]  # 404 if recipe doesn't exist
#         print_test_result("Get Recipe by ID", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Get Recipe by ID", False, error=str(e))
#         return False

# def test_get_recipe_image():
#     """Test GET /image/recipe/{image_id} endpoint"""
#     print("Testing GET /image/recipe/{image_id}...")
#     try:
#         # Test with a likely image ID (1) or get from existing recipe
#         url = f"{BASE_URL}/image/recipe/1"
#         response = requests.get(url)
        
#         success = response.status_code in [200, 404]  # 404 if image doesn't exist
#         print_test_result("Get Recipe Image", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Get Recipe Image", False, error=str(e))
#         return False

# def test_create_ingredient():
#     """Test POST /ingredient/add endpoint"""
#     print("Testing POST /ingredient/add...")
#     try:
#         ingredient_data = {
#             "id_ingredient": 0,  # Will be auto-generated
#             "ingredient_name": "Test Ingredient",
#             "ingredient_description": "A test ingredient for API testing",
#             "ingredient_category": "test",
#             "ingredient_unit": "grams",
#             "ingredient_calories": 100,
#             "ingredient_protein": 5.0,
#             "ingredient_carbs": 15.0,
#             "ingredient_fat": 2.0
#         }
        
#         url = f"{BASE_URL}/ingredient/add"
#         response = requests.post(url, json=ingredient_data, headers=HEADERS)
        
#         success = response.status_code == 200
#         print_test_result("Create Ingredient", success, response)
        
#         # Return the created ingredient ID for later use
#         if success and response.json():
#             response_data = response.json()
#             ingredient_id = response_data.get('id_ingredient') or response_data.get('id')
#             return ingredient_id
        
#         return None
        
#     except Exception as e:
#         print_test_result("Create Ingredient", False, error=str(e))
#         return None

# def test_create_recipe():
#     """Test POST /recipe/add endpoint"""
#     print("Testing POST /recipe/add...")
#     try:
#         # First, let's get available categories and ingredients
#         categories_response = requests.get(f"{BASE_URL}/recipe/category/all")
#         ingredients_response = requests.get(f"{BASE_URL}/ingredient/0/10")
        
#         categories = categories_response.json() if categories_response.status_code == 200 else []
#         ingredients = ingredients_response.json() if ingredients_response.status_code == 200 else []
        
#         # Create recipe data
#         recipe_data = {
#             "id_recipe": 0,  # Will be auto-generated
#             "recipe_category_id": categories[0]['id_recipe_category'] if categories else 1,
#             "recipe_name": "Test Recipe API",
#             "recipe_owner_id": 1,
#             "recipe_preparation_time": "30 minutes",
#             "recipe_instructions": "1. Mix ingredients\n2. Cook until done\n3. Serve hot",
#             "recipe_description": "A test recipe created via API",
#             "recipe_ingredients": {
#                 ingredients[0]['id_ingredient']: "200g" if ingredients else {1: "200g"}
#             }
#         }
        
#         # Create image data
#         image_data = {
#             "id_recipe_image": 0,  # Will be auto-generated
#             "recipe_image_url": "https://example.com/test-recipe.jpg",
#             "recipe_ref_id": 0  # Will be set to the created recipe ID
#         }
        
#         # For simplicity, we'll send them as separate JSON objects
#         # In a real scenario, you might need to handle multipart form data
#         payload = {
#             "recipe": recipe_data,
#             "image": image_data
#         }
        
#         url = f"{BASE_URL}/recipe/add"
#         response = requests.post(url, json=payload, headers=HEADERS)
        
#         success = response.status_code == 200
#         print_test_result("Create Recipe", success, response)
        
#         # Return the created recipe ID for later tests
#         if success and response.json():
#             response_data = response.json()
#             recipe_id = response_data.get('id_recipe') or response_data.get('id')
#             return recipe_id
        
#         return None
        
#     except Exception as e:
#         print_test_result("Create Recipe", False, error=str(e))
#         return None

# def test_update_recipe(recipe_id):
#     """Test PUT /recipe/{recipe_id} endpoint"""
#     print(f"Testing PUT /recipe/{recipe_id}...")
#     try:
#         # Get the current recipe first to use as base
#         current_recipe_response = requests.get(f"{BASE_URL}/recipe/{recipe_id}")
#         if current_recipe_response.status_code != 200:
#             print("   Could not fetch current recipe for update")
#             return False
        
#         current_recipe = current_recipe_response.json()
        
#         # Update recipe data
#         recipe_data = {
#             "id_recipe": recipe_id,
#             "recipe_category_id": current_recipe.get('recipe_category_id', 1),
#             "recipe_name": f"Updated {current_recipe.get('recipe_name', 'Test Recipe')}",
#             "recipe_owner_id": current_recipe.get('recipe_owner_id', 1),
#             "recipe_preparation_time": "45 minutes",  # Updated time
#             "recipe_instructions": current_recipe.get('recipe_instructions', '') + "\n4. Updated step",
#             "recipe_description": f"Updated description - {datetime.now().isoformat()}",
#             "recipe_ingredients": current_recipe.get('recipe_ingredients', {})
#         }
        
#         # Update image data
#         image_data = {
#             "id_recipe_image": current_recipe.get('image', {}).get('id_recipe_image', 0),
#             "recipe_image_url": "https://example.com/updated-recipe.jpg",
#             "recipe_ref_id": recipe_id
#         }
        
#         payload = {
#             "recipe": recipe_data,
#             "image": image_data
#         }
        
#         url = f"{BASE_URL}/recipe/{recipe_id}"
#         response = requests.put(url, json=payload, headers=HEADERS)
        
#         success = response.status_code == 200
#         print_test_result("Update Recipe", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Update Recipe", False, error=str(e))
#         return False

# def test_delete_recipe(recipe_id):
#     """Test DELETE /recipe/delete/{recipe_id} endpoint"""
#     print(f"Testing DELETE /recipe/delete/{recipe_id}...")
#     try:
#         url = f"{BASE_URL}/recipe/delete/{recipe_id}"
#         response = requests.delete(url)
        
#         success = response.status_code == 200
#         print_test_result("Delete Recipe", success, response)
#         return success
        
#     except Exception as e:
#         print_test_result("Delete Recipe", False, error=str(e))
#         return False

# def test_invalid_scenarios():
#     """Test endpoints with invalid data"""
#     print("Testing invalid scenarios...")
    
#     # Test 1: Get recipe with invalid ID
#     try:
#         url = f"{BASE_URL}/recipe/999999"  # Non-existent recipe
#         response = requests.get(url)
#         success = response.status_code in [200, 404]  # Both are acceptable
#         print_test_result("Get Non-existent Recipe", success, response)
#     except Exception as e:
#         print_test_result("Get Non-existent Recipe", False, error=str(e))
    
#     # Test 2: Create recipe with missing required fields
#     try:
#         invalid_recipe = {
#             "recipe_name": "Incomplete Recipe"
#             # Missing required fields like recipe_category_id
#         }
#         url = f"{BASE_URL}/recipe/add"
#         response = requests.post(url, json={"recipe": invalid_recipe}, headers=HEADERS)
#         success = response.status_code in [400, 422]  # Validation error expected
#         print_test_result("Create Recipe with Invalid Data", success, response)
#     except Exception as e:
#         print_test_result("Create Recipe with Invalid Data", False, error=str(e))
    
#     # Test 3: Update with invalid recipe ID
#     try:
#         update_data = {
#             "recipe": {"id_recipe": 999999, "recipe_name": "Non-existent"},
#             "image": {"id_recipe_image": 0}
#         }
#         url = f"{BASE_URL}/recipe/999999"
#         response = requests.put(url, json=update_data, headers=HEADERS)
#         success = response.status_code in [200, 404]  # Could be either
#         print_test_result("Update Non-existent Recipe", success, response)
#     except Exception as e:
#         print_test_result("Update Non-existent Recipe", False, error=str(e))

# def test_complete_workflow():
#     """Test a complete recipe management workflow"""
#     print("Testing complete recipe management workflow...")
    
#     # Step 1: Get available categories and ingredients
#     categories = requests.get(f"{BASE_URL}/recipe/category/all").json()
#     ingredients = requests.get(f"{BASE_URL}/ingredient/0/5").json()
    
#     if not categories or not ingredients:
#         print("❌ Need categories and ingredients to test workflow")
#         return False
    
#     # Step 2: Create a new recipe
#     recipe_data = {
#         "id_recipe": 0,
#         "recipe_category_id": categories[0]['id_recipe_category'],
#         "recipe_name": f"Workflow Test Recipe {datetime.now().strftime('%H%M%S')}",
#         "recipe_owner_id": 1,
#         "recipe_preparation_time": "35 minutes",
#         "recipe_instructions": "Workflow test instructions",
#         "recipe_description": "Recipe created for workflow testing",
#         "recipe_ingredients": {
#             ingredients[0]['id_ingredient']: "300g"
#         }
#     }
    
#     image_data = {
#         "id_recipe_image": 0,
#         "recipe_image_url": "https://example.com/workflow-test.jpg",
#         "recipe_ref_id": 0
#     }
    
#     create_response = requests.post(
#         f"{BASE_URL}/recipe/add",
#         json={"recipe": recipe_data, "image": image_data},
#         headers=HEADERS
#     )
    
#     if create_response.status_code != 200:
#         print("❌ Workflow failed at creation step")
#         return False
    
#     created_recipe = create_response.json()
#     recipe_id = created_recipe.get('id_recipe') or created_recipe.get('id')
    
#     if not recipe_id:
#         print("❌ Could not extract recipe ID from creation response")
#         return False
    
#     print(f"✅ Created recipe with ID: {recipe_id}")
    
#     # Step 3: Verify recipe was created by fetching it
#     get_response = requests.get(f"{BASE_URL}/recipe/{recipe_id}")
#     if get_response.status_code != 200:
#         print("❌ Workflow failed at get recipe step")
#         return False
    
#     print("✅ Successfully retrieved created recipe")
    
#     # Step 4: Update the recipe
#     recipe_data['id_recipe'] = recipe_id
#     recipe_data['recipe_name'] = f"Updated Workflow Recipe {datetime.now().strftime('%H%M%S')}"
#     image_data['recipe_ref_id'] = recipe_id
    
#     update_response = requests.put(
#         f"{BASE_URL}/recipe/{recipe_id}",
#         json={"recipe": recipe_data, "image": image_data},
#         headers=HEADERS
#     )
    
#     if update_response.status_code != 200:
#         print("❌ Workflow failed at update step")
#         return False
    
#     print("✅ Successfully updated recipe")
    
#     # Step 5: Delete the recipe
#     delete_response = requests.delete(f"{BASE_URL}/recipe/delete/{recipe_id}")
#     if delete_response.status_code != 200:
#         print("❌ Workflow failed at delete step")
#         return False
    
#     print("✅ Successfully deleted recipe")
#     print("🎉 Complete recipe workflow test passed!")
#     return True

# def run_all_tests():
#     """Run all test scenarios"""
#     print("🚀 Starting Recipe Endpoints Tests")
#     print("=" * 50)
    
#     results = {
#         "get_categories": False,
#         "get_ingredients": False,
#         "get_recipes_by_category": False,
#         "get_recipe_by_id": False,
#         "get_recipe_image": False,
#         "create_ingredient": False,
#         "create_recipe": False,
#         "update_recipe": False,
#         "delete_recipe": False,
#         "complete_workflow": False
#     }
    
#     # Test 1: Get recipe categories
#     results["get_categories"] = test_get_recipe_categories()
    
#     # Test 2: Get ingredients list
#     results["get_ingredients"] = test_get_ingredients()
    
#     # Test 3: Get recipes by category
#     existing_recipe_id = test_get_recipes_by_category()
#     results["get_recipes_by_category"] = existing_recipe_id is not None
    
#     # Test 4: Get specific recipe by ID (if we found one)
#     if existing_recipe_id:
#         results["get_recipe_by_id"] = test_get_recipe_by_id(existing_recipe_id)
    
#     # Test 5: Get recipe image
#     results["get_recipe_image"] = test_get_recipe_image()
    
#     # Test 6: Create ingredient
#     created_ingredient_id = test_create_ingredient()
#     results["create_ingredient"] = created_ingredient_id is not None
    
#     # Test 7: Create recipe
#     created_recipe_id = test_create_recipe()
#     results["create_recipe"] = created_recipe_id is not None
    
#     # Test 8: Update recipe (if we created one)
#     if created_recipe_id:
#         results["update_recipe"] = test_update_recipe(created_recipe_id)
    
#     # Test 9: Delete recipe (if we created one)
#     if created_recipe_id:
#         results["delete_recipe"] = test_delete_recipe(created_recipe_id)
    
#     # Test 10: Invalid scenarios
#     test_invalid_scenarios()
    
#     # Test 11: Complete workflow
#     results["complete_workflow"] = test_complete_workflow()
    
#     # Summary
#     print("\n📊 TEST SUMMARY")
#     print("=" * 50)
#     for test_name, passed in results.items():
#         status = "✅ PASS" if passed else "❌ FAIL"
#         print(f"{status} {test_name}")
    
#     passed_count = sum(results.values())
#     total_count = len(results)
#     print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
#     if passed_count == total_count:
#         print("🎉 All tests passed!")
#         return True
#     else:
#         print("💥 Some tests failed!")
#         return False

# if __name__ == "__main__":
#     # Check if server is reachable
#     try:
#         response = requests.get(BASE_URL, timeout=5)
#         print(f"✅ Server is reachable at {BASE_URL}")
#     except requests.exceptions.ConnectionError:
#         print(f"❌ Cannot connect to server at {BASE_URL}")
#         print("Make sure your FastAPI server is running!")
#         sys.exit(1)
    
#     # Run tests
#     success = run_all_tests()
#     sys.exit(0 if success else 1)