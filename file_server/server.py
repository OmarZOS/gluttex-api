import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
from fastapi.middleware.cors import CORSMiddleware
from core.exception_handler import APIException
from core.models import API_Resolution
from core.messages import *
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app

from lib import (
    BASE_STORAGE,
    get_path,
    get_cache_path,
    create_thumbnail,
    init_storage,
)

app = FastAPI(
    openapi_url="/fs/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/fs/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/fs/redoc"  # Keep ReDoc at `/redoc`
)

app.mount("/metrics", make_asgi_app())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_storage()
    yield


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If it's a known APIException
    if isinstance(exc, APIException):
        resolution = API_Resolution(
            status=exc.status,
            error_code=exc.code,
            message=str(exc.details),
        )
        return JSONResponse(
            status_code=exc.status,
            content=resolution.dict(),
        )
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    # If it's an unexpected internal error
    resolution = API_Resolution(
        status=status_code,
        error_code=INTERNAL_SERVER_ERROR,
        message=str(exc),
    )
    return JSONResponse(
        status_code=status_code,
        content=resolution.dict(),
    )



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.put("/fs/upload/{entity_type}/{owner_id}/{entity_id}/")
async def upload_file(entity_type: str, owner_id: str, entity_id: str, file: UploadFile = File(...)):
    """
    Uploads a file and stores it in the designated folder.
    """
    entity_path = get_path(entity_type, owner_id, entity_id)
    entity_path.mkdir(parents=True, exist_ok=True)

    file_path = entity_path / f"{uuid.uuid4()}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {file_path}")
    except Exception as e:
        raise APIException(status=500,code= HTTP_410_GONE,details=f"File upload failed: {str(e)}")
    access_path = str(file_path).replace("/fs/data","/fs/files")
    return {"filename": file.filename, "path": access_path}

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
        raise APIException(status=404,code= HTTP_404_NOT_FOUND,details="File not found")

    # If detailed is requested, return the original file
    if detailed:
        print(f"📂 Returning original file: {file_path}")
        return FileResponse(file_path, filename=filename)

    # Thumbnail processing
    cache_path = get_cache_path(entity_type, owner_id, entity_id) / filename

    if not cache_path.exists():
        print(f"⚠️ Thumbnail not found, generating one for {file_path}")
        try:
            create_thumbnail(file_path, cache_path)
        except Exception as e:
            print(f"Thumbnail error: {e}")

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
        raise APIException(status=404,code= HTTP_404_NOT_FOUND,details="File not found")

    try:
        file_path.unlink()
        return {"message": f"File '{filename}' deleted successfully"}
    except Exception as e:
        raise APIException(status=500,code= HTTP_417_EXPECTATION_FAILED,details=f"Error deleting file: {str(e)}")

@app.get("/fs/files/{entity_type}/{owner_id}/")
async def list_user_files(entity_type: str, owner_id: str):
    user_path = BASE_STORAGE / entity_type / owner_id

    if not user_path.exists():
        raise APIException(
            status=404,
            code=HTTP_404_NOT_FOUND,
            details="User directory not found",
        )

    files = {
        entity.name: [f.name for f in entity.iterdir() if f.is_file()]
        for entity in user_path.iterdir()
        if entity.is_dir()
    }

    return {"user_id": owner_id, "files": files}
