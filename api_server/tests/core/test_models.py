from core.models import User

def test_create_user():
    user = User(id=1, username="testuser", email="test@example.com")
    assert user.username == "testuser"
