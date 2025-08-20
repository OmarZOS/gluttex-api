def test_get_users(client):
    response = client.get("/users/")
    assert response.status == 200
