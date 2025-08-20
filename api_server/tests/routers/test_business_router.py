def test_get_businesses(client):
    response = client.get("/businesses/")
    assert response.status == 200
