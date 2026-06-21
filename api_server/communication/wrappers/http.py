from typing import Any, Dict, Optional

import httpx

async def send_post_request(
    endpoint: str,
    json_data: Optional[Dict] = None,
    payload_data: Optional[Dict] = None,
    flags: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    file: Optional[Any] = None,
    timeout: int = 30
):
    """Send POST request with proper header handling"""
    async with httpx.AsyncClient(timeout=timeout) as client:
        # Merge headers properly
        request_headers = {}
        if headers:
            request_headers.update(headers)
        if flags:
            request_headers.update(flags)
        
        # Determine content type
        if file:
            # Multipart form data
            response = await client.post(
                endpoint,
                files=file,
                data=payload_data,
                headers=request_headers
            )
        elif json_data is not None:
            # JSON data
            response = await client.post(
                endpoint,
                json=json_data,
                headers=request_headers
            )
        elif payload_data is not None:
            # Form data (x-www-form-urlencoded)
            response = await client.post(
                endpoint,
                data=payload_data,
                headers=request_headers
            )
        else:
            # No body
            response = await client.post(
                endpoint,
                headers=request_headers
            )
        
        return response



async def send_get_request( endpoint: str, params: dict = None,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.get(url, params=params, **(flags or {}))
        return response

async def send_put_request( endpoint, json_data: dict=None, payload_data: dict=None,flags: dict = {}, file :bytes =None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        print(json_data)
        response = await client.put(url,json=json_data, data= payload_data,files=file, **(flags or {})   )
        return response

async def send_delete_request(
    endpoint: str,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 30
):
    """Send DELETE request with JSON body"""
    import json as json_lib
    
    async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
        request_headers = headers or {}
        if json_data is not None:
            request_headers["Content-Type"] = "application/json"
            # Use request method for DELETE with body
            response = await client.request(
                method="DELETE",
                url=endpoint,
                content=json_lib.dumps(json_data).encode('utf-8'),
                headers=request_headers
            )
        else:
            response = await client.delete(
                endpoint,
                headers=request_headers
            )
        return response


