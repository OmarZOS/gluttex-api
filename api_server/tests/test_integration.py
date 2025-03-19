def test_endpoints(client):
    response = client.get("/")
    assert response.status_code == 200