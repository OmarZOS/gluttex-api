def test_upload_file(client):
    response = client.put(
        "/fs/upload/products/u1/p1/",
        files={"file": ("test.txt", b"hello world")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "path" in data
    assert data["filename"] == "test.txt"
