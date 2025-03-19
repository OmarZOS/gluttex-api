from core.api_models import UserCreate

def test_user_create():
    user = UserCreate(username="testuser", email="test@example.com", password="securepassword")
    assert user.username == "testuser"
