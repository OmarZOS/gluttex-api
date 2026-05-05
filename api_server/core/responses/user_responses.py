
# routers/app_routers/auth_router.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.messages import *



# ==================== Response Models ====================
class UserResponseModel(BaseModel):
    """User response model"""
    id: int
    username: str
    email: Optional[str] = None
    image_url: Optional[str] = None
    user_type_id: Optional[int] = None
    person_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ReactionResponseModel(BaseModel):
    """Reaction response model"""
    success: bool
    message: str
    reaction_id: Optional[int] = None
    target_id: int
    target_type: str
    value: Optional[float] = None

