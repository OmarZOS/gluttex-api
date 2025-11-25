from pydantic import BaseModel



class API_Resolution(BaseModel):
    status: int
    error_code: str
    message: str