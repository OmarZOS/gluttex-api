from pathlib import Path
import shutil



# Base directories for original files and cache
BASE_STORAGE = Path("/fs/data")
CACHE_STORAGE = Path("/fs/cache")

# Ensure directories exist
BASE_STORAGE.mkdir(parents=True, exist_ok=True)
CACHE_STORAGE.mkdir(parents=True, exist_ok=True)

def get_path(entity_type: str, owner_id: str, entity_id: str) -> Path:
    """Get the file path for an entity."""
    return BASE_STORAGE / entity_type / owner_id / entity_id

def get_cache_path(entity_type: str, owner_id: str, entity_id: str) -> Path:
    """Get the cache path for an entity (thumbnail storage)."""
    return CACHE_STORAGE / entity_type / owner_id / entity_id

def create_thumbnail(original: Path, thumbnail: Path):
    """Generate a thumbnail by copying the original file (placeholder logic)."""
    print(f"Creating thumbnail for {original} → {thumbnail}")
    
    # Ensure the parent directory exists
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    
    # Simulate thumbnail generation (replace with actual resizing logic)
    shutil.copyfile(original, thumbnail)
