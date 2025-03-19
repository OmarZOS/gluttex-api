def test_get_recipes(client):
    response = client.get("/recipes/")
    assert response.status_code == 200