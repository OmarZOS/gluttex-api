def test_delete_file(client):
    upload = client.put(
        "/fs/upload/products/u1/p1/",
        files={"file": ("del.txt", b"x")}
    )

    filename = upload.json()["path"].split("/")[-1]

    res = client.delete(f"/fs/files/products/u1/p1/{filename}")

    assert res.status_code == 200
