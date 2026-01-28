def test_get_uploaded_file(client):
    upload = client.put(
        "/fs/upload/products/u1/p1/",
        files={"file": ("a.txt", b"content")}
    )

    path = upload.json()["path"]
    filename = path.split("/")[-1]

    res = client.get(f"/fs/products/u1/p1/{filename}?detailed=true")

    assert res.status_code == 200
    assert res.content == b"content"


def test_thumbnail_fallback(client, monkeypatch):
    upload = client.put(
        "/fs/upload/products/u1/p1/",
        files={"file": ("img.jpg", b"fake")}
    )

    filename = upload.json()["path"].split("/")[-1]

    monkeypatch.setattr("lib.create_thumbnail", lambda a, b: None)

    res = client.get(f"/fs/products/u1/p1/{filename}")

    assert res.status_code == 200
