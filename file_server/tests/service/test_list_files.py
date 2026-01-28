def test_list_user_files(client):
    client.put("/fs/upload/products/u1/p1/", files={"file": ("a.txt", b"x")})
    client.put("/fs/upload/products/u1/p2/", files={"file": ("b.txt", b"x")})

    res = client.get("/fs/files/products/u1/")

    assert res.status_code == 200
    data = res.json()
    assert "p1" in data["files"]
    assert "p2" in data["files"]


# def test_get_missing_file(client):
#     res = client.get("/fs/products/u1/p1/missing.txt")
#     assert res.status_code == 404
