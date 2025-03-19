def test_get_suppliers(client):
    response = client.get("/suppliers/")
    assert response.status_code == 200
