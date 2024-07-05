

async def process_data(input_data: dict):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ML_SERVER_URL}/compute", json=input_data)
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


