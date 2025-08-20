



import io
import base64

from core.exception_handler import APIException
from core.messages import *
from communication.communication_broker import send_post_request, send_get_request, send_delete_request
from constants import (
    FILE_UPLOAD_ENDPOINT,FS_HOST,FS_PORT
)

async def upload_image(entity_type:str,owner_id:int,entity_id:int,image_data: str):
    """
    Register a new image with the authentication server.
    """
    if entity_type not in ["store","recipe","product","user"]:
        raise APIException(DATA_ERROR)

    url = f"http://{FS_HOST}:{FS_PORT}{FILE_UPLOAD_ENDPOINT}/{entity_type}/{owner_id}/{entity_id}"
    
    # Decode Base64 into binary data
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        raise APIException("Invalid Base64 encoding")
    # Create a file-like object
    file = {"file": (f"{entity_id}", io.BytesIO(image_bytes), "image/jpeg")}
    try:
        response = await send_post_request(url,file=file,flags={"headers": {"Content-Type": "application/json"}})
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json()
    except Exception as e:
        raise APIException(NETWORK_TIMEOUT)



async def get_image(entity_type: str, owner_id: int, entity_id: int, filename: str, detailed: bool = False):
    """
    Retrieve an image file from the server.
    """
    if entity_type not in ["store", "recipe", "product", "user"]:
        raise APIException(DATA_ERROR)
    
    url = f"http://{FS_HOST}:{FS_PORT}/fs/{entity_type}/{owner_id}/{entity_id}/{filename}?detailed={str(detailed).lower()}"
    
    try:
        response = await send_get_request(url)
        response.raise_for_status()
        return response.content  # Returns binary content of the image
    except Exception as e:
        raise APIException(f"Image retrieval failed: {e}")


async def delete_image(entity_type: str, owner_id: int, entity_id: int, filename: str):
    """
    Delete a specific image file from the server.
    """
    if entity_type not in ["store", "recipe", "product", "user"]:
        raise APIException(HTTP_EXCEPTION)
    
    url = f"http://{FS_HOST}:{FS_PORT}/fs/files/{entity_type}/{owner_id}/{entity_id}/{filename}"
    
    try:
        response = await send_delete_request(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise APIException(f"Image deletion failed: {e}")


async def list_images(entity_type: str, owner_id: int):
    """
    List all files and directories owned by a user.
    """
    if entity_type not in ["store", "recipe", "product", "user"]:
        raise APIException("Invalid entity type")
    
    url = f"http://{FS_HOST}:{FS_PORT}/fs/files/{entity_type}/{owner_id}/"
    
    try:
        response = await send_get_request(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise APIException(f"Listing images failed: {e}")
