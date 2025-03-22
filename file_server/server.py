import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pathlib import Path
import shutil

from lib import *

app = FastAPI(
    openapi_url="/fs/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/fs/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/fs/redoc"  # Keep ReDoc at `/redoc`
)

@app.post("/fs/upload/{entity_type}/{owner_id}/{entity_id}/")
async def upload_file(entity_type: str, owner_id: str, entity_id: str, file: UploadFile = File(...)):
    """
    Uploads a file and stores it in the designated folder.
    """
    entity_path = get_path(entity_type, owner_id, entity_id)
    entity_path.mkdir(parents=True, exist_ok=True)

    file_path = entity_path / uuid.uuid4()

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return {"filename": file.filename, "path": str(file_path)}

@app.get("/fs/{entity_type}/{owner_id}/{entity_id}/{filename}")
async def get_file(entity_type: str, owner_id: str, entity_id: str, filename: str, detailed: bool = False):
    """
    Retrieve a file from the server.
    - If 'detailed' is True, return the original file.
    - If False, return a thumbnail (or generate one if missing).
    """

    # Construct file paths
    entity_path = get_path(entity_type, owner_id, entity_id)
    file_path = entity_path / filename

    print(f"🔍 Checking file: {file_path}")

    # Check if the original file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # If detailed is requested, return the original file
    if detailed:
        print(f"📂 Returning original file: {file_path}")
        return FileResponse(file_path, filename=filename)

    # Thumbnail processing
    cache_path = get_cache_path(entity_type, owner_id, entity_id) / filename

    if not cache_path.exists():
        print(f"⚠️ Thumbnail not found, generating one for {file_path}")
        create_thumbnail(file_path, cache_path)

        # If thumbnail creation failed, return original file as fallback
        if not cache_path.exists():
            print(f"❌ Thumbnail generation failed, returning original file")
            return FileResponse(file_path, filename=filename)

    print(f"📸 Returning thumbnail: {cache_path}")
    return FileResponse(cache_path, filename=f"thumbnail_{filename}")

@app.delete("/fs/files/{entity_type}/{owner_id}/{entity_id}/{filename}")
async def delete_file(entity_type: str, owner_id: str, entity_id: str, filename: str):
    """
    Deletes a specific file.
    """
    file_path = get_path(entity_type, owner_id, entity_id) / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.get("/fs/files/{entity_type}/{owner_id}/")
async def list_user_files(entity_type: str, owner_id: str):
    """
    Lists all directories (entities) owned by a user and their files.
    """
    user_path = BASE_STORAGE / entity_type / owner_id

    if not user_path.exists() or not user_path.is_dir():
        raise HTTPException(status_code=404, detail="User directory not found")

    files = {
        entity_id.name: [f.name for f in entity_id.iterdir() if f.is_file()]
        for entity_id in user_path.iterdir() if entity_id.is_dir()
    }

    return {"user_id": owner_id, "files": files}
