
# routers/app_routers/auth_router.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.messages import *



# ==================== Order Response Models ====================

class OrderResponseModel(BaseModel):
    """Order response model"""
    order_id: int
    user_id: int
    status: str
    total_amount: float
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class OrderItemResponseModel(BaseModel):
    """Order item response model"""
    id: int
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float
    discount: Optional[float] = None
