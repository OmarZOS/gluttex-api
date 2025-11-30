from pydantic import BaseModel

from typing import List, Optional


# Pydantic models for requests
class BindingRequest(BaseModel):
    routing_key: str
    queue_name: Optional[str] = None  # If not provided, uses user's default queue

class MultipleBindingRequest(BaseModel):
    routing_keys: List[str]
    queue_name: Optional[str] = None

class BindingResponse(BaseModel):
    success: bool
    message: str
    binding_count: Optional[int] = None
    queue_name: str

class BindingInfo(BaseModel):
    routing_key: str
    queue_name: str
    binding_key: str