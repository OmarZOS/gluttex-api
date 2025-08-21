import httpx

async def send_post_request( endpoint: str, json_data: dict=None, payload_data: dict=None,flags: dict = {}, file :bytes =None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        # print(input_data)
        # print(flags)
        response = await client.post(url,json=json_data, data= payload_data,headers= flags,files=file  )
        return response

async def send_get_request( endpoint: str, params: dict = None,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.get(url, params=params, **(flags or {}))
        return response

async def send_put_request( endpoint, input_data,flags=None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.put(url, json=input_data, **(flags or {}))
        return response

async def send_delete_request( endpoint: str, params: dict = None,flags: dict = None) -> httpx.Response:
    async with httpx.AsyncClient(verify=False) as client:
        url = f"{endpoint}"
        response = await client.delete(url, params=params, **(flags or {}))
        return response