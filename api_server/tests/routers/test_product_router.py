def test_get_products(client):
    response = client.get("/products/")
    assert response.status == 200
