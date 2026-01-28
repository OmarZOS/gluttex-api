from pathlib import Path
import shutil
import os

# --------------------------------------------------
# Base storage (original files)
# --------------------------------------------------

BASE_STORAGE = Path(
    os.getenv("FS_BASE_STORAGE", "fs/data")
)

# --------------------------------------------------
# Cache storage (thumbnails)
# --------------------------------------------------
CACHE_STORAGE = Path(
    os.getenv("FS_CACHE_STORAGE", str(BASE_STORAGE / "cache"))
)

def init_storage():
    """Initialize storage directories."""
    BASE_STORAGE.mkdir(parents=True, exist_ok=True)
    CACHE_STORAGE.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Path helpers
# --------------------------------------------------
def get_path(entity_type: str, owner_id: str, entity_id: str) -> Path:
    """Get the file path for an entity."""
    return BASE_STORAGE / entity_type / owner_id / entity_id

def get_cache_path(entity_type: str, owner_id: str, entity_id: str) -> Path:
    """Get the cache path for an entity (thumbnail storage)."""
    return CACHE_STORAGE / entity_type / owner_id / entity_id

# --------------------------------------------------
# Thumbnail generation
# --------------------------------------------------
def create_thumbnail(original: Path, thumbnail: Path):
    """Generate a thumbnail (placeholder logic)."""
    print(f"Creating thumbnail for {original} → {thumbnail}")

    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(original, thumbnail)
