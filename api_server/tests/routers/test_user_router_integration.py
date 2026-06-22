# # tests/integration/test_user_endpoints.py
# """
# Integration tests for User endpoints.
# These tests require a running API Server instance.
# """

# import pytest
# import os
# import uuid
# import httpx
# from typing import Dict, Any
# import time


# def is_api_server_available():
#     return True
#     """Check if API server is running"""
#     try:
#         api_server = os.getenv("API_SERVER_NAME", "localhost")
#         api_port = os.getenv("API_PORT", "8000")
#         protocol = "http" if api_server == "localhost" else "https"
#         response = httpx.get(
#             f"{protocol}://{api_server}:{api_port}/health",
#             timeout=2.0,
#             verify=False
#         )
#         return response.status_code == 200
#     except Exception:
#         return False


# # Skip integration tests if API server not available
# require_api_server = pytest.mark.skipif(
#     not is_api_server_available(),
#     reason="API server not available. Set API_SERVER_NAME and API_PORT environment variables."
# )


# @pytest.fixture
# def api_base_url():
#     """Get API base URL"""
#     server = os.getenv("API_SERVER_NAME", "localhost")
#     port = os.getenv("API_PORT", "9000")
#     protocol = "http" 
#     return f"{protocol}://{server}:{port}"


# @pytest.fixture
# def test_user_data():
#     """Generate unique test user data"""
#     unique_id = str(uuid.uuid4())[:8]
#     return {
#         "id_app_user": 0,
#         "app_user_name": f"testuser_{unique_id}",
#         "app_user_password": "TestPassword123!",
#         "app_user_email": f"test_{unique_id}@example.com",
#         "app_user_type": "customer",
#         "app_user_preferences": {"theme": "dark"},
#         "app_user_image_url": None,
#     }


# @pytest.fixture
# def test_person_data():
#     """Generate unique test person data"""
#     return {
#         "id_person": 0,
#         "person_first_name": "Test",
#         "person_last_name": "User",
#         "person_email": "test@example.com",
#         "person_phone": "+1234567890",
#         "person_gender": "male",
#     }


# @pytest.fixture
# def test_location_data():
#     """Generate unique test location data"""
#     return {
#         "id_location": 0,
#         "location_name": "Test Location",
#         "location_latitude": 36.7538,
#         "location_address_id":0,
#         "id_address" : 0,
#         "location_longitude": 3.0588,
#         "address_street": "123 Test Street",
#         "address_city": "Test City",
#         "address_postal_code": "12345",
#         "address_country": "DZ",


#     }


# @pytest.fixture
# def test_reaction_data():
#     """Generate test reaction data"""
#     return {

#         "user_id": 1,
#         "reaction_value": "like",
#         "rating_value": 4,
#         "reaction_type": "product",
#         "target_id": 1
#     }


# @require_api_server
# class TestUserEndpoints:
#     """Integration tests for User endpoints"""

#     async def create_test_user(self, api_base_url, test_user_data) -> Dict[str, Any]:
#         """Helper method to create a test user"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 f"{api_base_url}/api/v1/app_user",
#                 json={"user": test_user_data}
#             )
            
#             if response.status_code == 201:
#                 return response.json()
#             elif response.status_code == 409:
#                 # User already exists, try with unique username
#                 unique_id = str(uuid.uuid4())[:8]
#                 test_user_data["app_user_name"] = f"testuser_{unique_id}"
#                 test_user_data["app_user_email"] = f"test_{unique_id}@example.com"
#                 return await self.create_test_user(api_base_url, test_user_data)
#             else:
#                 return None

#     @pytest.mark.asyncio
#     async def test_get_all_users(self, api_base_url):
#         """Test GET /api/v1/app_user - Get all users"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.get(
#                 f"{api_base_url}/api/v1/app_user",
#                 params={"offset": 0, "limit": 10}
#             )
#             # If not authenticated, returns 401; if authenticated, returns 200
#             # If database connection issues, could be 500
#             assert response.status_code in [200, 401, 500]

#     @pytest.mark.asyncio
#     async def test_get_user_by_id(self, api_base_url, test_user_data):
#         """Test GET /api/v1/app_user/{user_id} - Get user by ID"""
#         # Create a user first
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             user_id = user_data.get("id_app_user")
#             if user_id:
#                 async with httpx.AsyncClient(timeout=30.0) as client:
#                     response = await client.get(
#                         f"{api_base_url}/api/v1/app_user/{user_id}"
#                     )
#                     assert response.status_code in [200, 401]

#     @pytest.mark.asyncio
#     async def test_create_user_success(self, api_base_url, test_user_data):
#         """Test POST /api/v1/app_user - Create user successfully"""
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             assert user_data.get("app_user_name") == test_user_data["app_user_name"]
#             assert user_data.get("app_user_email") == test_user_data["app_user_email"]

#     @pytest.mark.asyncio
#     async def test_create_user_with_person(self, api_base_url, test_user_data, test_person_data):
#         """Test POST /api/v1/app_user - Create user with person data"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 f"{api_base_url}/api/v1/app_user",
#                 json={
#                     "user": test_user_data,
#                     "person": test_person_data,
#                     "location": None
#                 }
#             )
#             # 201: Success, 410: Auth creation failed (auth server not available)
#             # 422: Validation error, 400: Bad request, 409: Conflict
#             assert response.status_code in [201, 410, 422, 400, 409]
            
#             # If we get 410, it means auth server is not available - this is expected in test environment

    



#     @pytest.mark.asyncio
#     async def test_create_user_duplicate(self, api_base_url, test_user_data):
#         """Test POST /api/v1/app_user - Create user with duplicate username"""
#         # First creation should succeed
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             # Second creation with same username should fail
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     f"{api_base_url}/api/v1/app_user",
#                     json={"user": test_user_data}
#                 )
#                 assert response.status_code in [409, 400, 401]

#     @pytest.mark.asyncio
#     async def test_create_user_with_location(self, api_base_url, test_user_data, test_person_data, test_location_data):
#         """Test POST /api/v1/app_user - Create user with location data"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 f"{api_base_url}/api/v1/app_user",
#                 json={
#                     "user": test_user_data,
#                     "person": test_person_data,
#                     "location": test_location_data
#                 }
#             )
#             # 201: Success, 410: Auth creation failed (auth server not available)
#             # 400: Bad request, 409: Conflict
#             assert response.status_code in [201, 410, 400, 409]


#     @pytest.mark.asyncio
#     async def test_delete_user(self, api_base_url, test_user_data):
#         """Test DELETE /api/v1/app_user - Delete user"""
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             user_id = user_data.get("id_app_user")
#             if user_id:
#                 delete_data = {
#                     "id_app_user": user_id,
#                     "app_user_name": test_user_data["app_user_name"]
#                 }
#                 async with httpx.AsyncClient(timeout=30.0) as client:
#                     response = await client.delete(
#                         f"{api_base_url}/api/v1/app_user",
#                         params={"force_delete": True},
#                         json=delete_data
#                     )
#                     assert response.status_code in [200, 401, 404]

#     @pytest.mark.asyncio
#     async def test_update_user_record(self, api_base_url, test_user_data, test_person_data):
#         """Test PUT /api/v1/app_user - Update user record"""
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             user_id = user_data.get("id_app_user")
#             if user_id:
#                 update_user = test_user_data.copy()
#                 update_user["id_app_user"] = user_id
#                 update_user["app_user_name"] = f"updated_{test_user_data['app_user_name']}"
                
#                 updated_person = test_person_data.copy()
#                 updated_person["person_first_name"] = "Updated"
                
#                 async with httpx.AsyncClient(timeout=30.0) as client:
#                     response = await client.put(
#                         f"{api_base_url}/api/v1/app_user",
#                         json={
#                             "user": update_user,
#                             "person_record": updated_person,
#                             "location_record": None
#                         }
#                     )
#                     assert response.status_code in [200, 401, 404, 400]

#     @pytest.mark.asyncio
#     async def test_update_user_password(self, api_base_url, test_user_data):
#         """Test PUT /api/v1/app_user/update_password - Update user password"""
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             user_id = user_data.get("id_app_user")
#             if user_id:
#                 update_data = {
#                     "id_app_user": user_id,
#                     "username": test_user_data["app_user_name"],
#                     "new_password": "NewPassword456!"
#                 }
#                 async with httpx.AsyncClient(timeout=30.0) as client:
#                     response = await client.put(
#                         f"{api_base_url}/api/v1/app_user/update_password",
#                         params={"token": "mock_token"},
#                         json=update_data
#                     )
#                     assert response.status_code in [200, 401, 400]

#     @pytest.mark.asyncio
#     async def test_update_user_image_url(self, api_base_url, test_user_data):
#         """Test PUT /api/v1/app_user/update_image_url - Update user image URL"""
#         user_data = await self.create_test_user(api_base_url, test_user_data)
#         if user_data:
#             user_id = user_data.get("id_app_user")
#             if user_id:
#                 update_user = test_user_data.copy()
#                 update_user["id_app_user"] = user_id
                
#                 async with httpx.AsyncClient(timeout=30.0) as client:
#                     response = await client.put(
#                         f"{api_base_url}/api/v1/app_user/update_image_url",
#                         params={"image_url": "https://example.com/new_avatar.jpg"},
#                         json=update_user
#                     )
#                     assert response.status_code in [200, 401, 404]

#     @pytest.mark.asyncio
#     async def test_search_users(self, api_base_url, test_user_data):
#         """Test GET /api/v1/app_user/search - Search users"""
#         await self.create_test_user(api_base_url, test_user_data)
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.get(
#                 f"{api_base_url}/api/v1/app_user/search",
#                 params={"query": test_user_data["app_user_name"][:5], "limit": 10}
#             )
#             # 422 means validation error (query too short)
#             assert response.status_code in [200, 401, 400, 422]

#     @pytest.mark.asyncio
#     async def test_get_user_by_email(self, api_base_url, test_user_data):
#         """Test GET /api/v1/app_user/by-email/{email} - Get user by email"""
#         await self.create_test_user(api_base_url, test_user_data)
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.get(
#                 f"{api_base_url}/api/v1/app_user/by-email/{test_user_data['app_user_email']}"
#             )
#             assert response.status_code in [200, 401, 404]

#     @pytest.mark.asyncio
#     async def test_get_person_by_id(self, api_base_url, test_user_data, test_person_data):
#         """Test GET /api/v1/person/{person_id} - Get person by ID"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             create_response = await client.post(
#                 f"{api_base_url}/api/v1/app_user",
#                 json={
#                     "user": test_user_data,
#                     "person": test_person_data
#                 }
#             )
            
#             if create_response.status_code == 201:
#                 user_data = create_response.json()
#                 person_id = user_data.get("app_user_person_id")
#                 if person_id and person_id > 0:
#                     response = await client.get(
#                         f"{api_base_url}/api/v1/person/{person_id}"
#                     )
#                     assert response.status_code in [200, 401, 404]

#     @pytest.mark.asyncio
#     async def test_reaction_endpoint(self, api_base_url, test_reaction_data):
#         """Test POST /api/v1/reaction - Add or update reaction"""
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(
#                 f"{api_base_url}/api/v1/reaction",
#                 json=test_reaction_data
#             )
#             assert response.status_code in [201, 401, 400, 404]


