# Gluttex-FS File Server with Image Caching

## Overview
This is a FastAPI-based file server that allows users to upload, download, and cache compressed images. Images are stored in an organized directory structure based on owner and product IDs. Cached images (300x300 JPEG) are generated for faster retrieval unless a detailed image is requested.

## Features
- Upload files and organize them by owner and product.
- Retrieve original or compressed (cached) images.
- List all files under a specific product.
- Automatically resize images to 300x300 for caching.

## Requirements
Install dependencies using:
```sh
pip install -r requirements.txt
```

### Required Packages
- `fastapi` – API framework
- `uvicorn` – ASGI server for FastAPI
- `pillow` – Image processing library for compression

## Running the Server
Run the FastAPI server using Uvicorn:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints
### Upload File
```http
POST /upload/{owner_id}/{product_id}
```
Uploads a file under a specific owner and product.

### Get File (Compressed or Original)
```http
GET /files/{owner_id}/{product_id}/{filename}?detailed=false
```
- `detailed=true` → Returns the original image.
- `detailed=false` (default) → Returns the cached compressed image.

### List Files in a Product Directory
```http
GET /files/{owner_id}/{product_id}
```
Returns a list of all files for a given product.

## Directory Structure
```
/app/uploads/{owner_id}/{product_id}/original_files
/app/cache/{owner_id}/{product_id}/compressed_files
```

## Docker Deployment
To containerize the FastAPI file server:
1. Create a `Dockerfile` and build the image:
```sh
docker build -t gluttex-fs .
```
2. Run the container:
```sh
docker run -d -p 8000:8000 gluttex-fs
```

## License
MIT License

