def test_login(client):
    response = client.put("/auth/login", json={"username": "testuser", "password": "password"})
    assert response.status == 200
