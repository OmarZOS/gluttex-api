
# routers/app_routers/auth_router.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from core.messages import *



# ==================== Response Models ====================

class TokenResponse(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    app_user_id: int
    username: str


class LogoutResponse(BaseModel):
    """Response model for logout"""
    success: bool
    message: str
    timestamp: datetime


class ErrorResponseModel(BaseModel):
    """Error response model for OpenAPI documentation"""
    success: bool = False
    status_code: int
    code: str
    message: str
    details: Optional[Dict] = None
    request_id: Optional[str] = None
    timestamp: str
    path: Optional[str] = None

