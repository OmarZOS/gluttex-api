def test_login(client):
    response = client.post("/auth/login", json={"username": "testuser", "password": "password"})
    assert response.status == 200
