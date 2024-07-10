import httpx

async def send_post_request( endpoint: str, input_data: dict,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.post(url, json=input_data, **(flags or {}))
        return response

async def send_get_request( endpoint: str, params: dict = None,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.get(url, params=params, **(flags or {}))
        return response

async def send_put_request( endpoint: str, input_data: dict,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.put(url, json=input_data, **(flags or {}))
        return response

async def send_delete_request( endpoint: str, params: dict = None,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.delete(url, params=params, **(flags or {}))
        return response