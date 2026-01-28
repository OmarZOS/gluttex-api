from lib import get_path, get_cache_path

def test_get_path_creates_correct_structure(tmp_path, monkeypatch):
    monkeypatch.setattr("lib.BASE_STORAGE", tmp_path)

    path = get_path("products", "user1", "prod1")

    assert path == tmp_path / "products" / "user1" / "prod1"

def test_get_cache_path(tmp_path, monkeypatch):
    monkeypatch.setattr("lib.BASE_STORAGE", tmp_path)

    cache = get_cache_path("products", "user1", "prod1")

    assert "cache" in str(cache)
