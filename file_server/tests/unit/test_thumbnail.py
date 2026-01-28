from pathlib import Path
from unittest.mock import MagicMock
import lib

def test_create_thumbnail_called(monkeypatch, tmp_path):
    src = tmp_path / "src.jpg"
    dst = tmp_path / "thumb.jpg"
    src.write_bytes(b"fake image")

    mock = MagicMock()
    monkeypatch.setattr(lib, "create_thumbnail", mock)

    lib.create_thumbnail(src, dst)

    mock.assert_called_once()
