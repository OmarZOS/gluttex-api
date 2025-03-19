def test_get_businesses(client):
    response = client.get("/businesses/")
    assert response.status_code == 200
