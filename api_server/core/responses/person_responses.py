
# routers/app_routers/auth_router.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.messages import *



# ==================== Person Response Models ====================

class BloodTypeResponseModel(BaseModel):
    """Blood type response model"""
    id: int
    name: str
    description: Optional[str] = None


class PersonDetailsResponseModel(BaseModel):
    """Person details response model"""
    first_name: str
    last_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None


class PersonResponseModel(BaseModel):
    """Person response model"""
    id: int
    details: PersonDetailsResponseModel
    blood_type: Optional[BloodTypeResponseModel] = None
    location_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None