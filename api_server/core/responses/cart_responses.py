
# routers/app_routers/auth_router.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.messages import *



# ==================== Cart Response Models ====================

class CartItemResponse(BaseModel):
    """Response model for cart item"""
    id: Optional[int] = None
    product_id: int
    product_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float
    discount: Optional[float] = None


class CartServiceResponse(BaseModel):
    """Response model for cart service"""
    service_id: int
    service_name: Optional[str] = None
    quantity: float
    unit_price: float
    total_price: float
    scheduled_at: Optional[str] = None


class CartSummaryResponse(BaseModel):
    """Response model for cart summary"""
    success: bool = True
    cart_id: int
    cart_status: str
    items: Dict[str, Any]
    services: Dict[str, Any]
    total_amount: float
    currency: str = "DZD"
    delivery: Optional[Dict[str, Any]] = None


class CartListResponse(BaseModel):
    """Response model for cart list"""
    success: bool = True
    data: List[Any]
    filter: Dict[str, Any]
    pagination: Dict[str, int]


class CreateCartResponse(BaseModel):
    """Response model for cart creation"""
    success: bool = True
    message: str
    cart_id: int
    financial_documents: Dict[str, bool]
    cart: Any
    summary: Dict[str, Any]
    warning: Optional[str] = None


class UpdateCartStatusResponse(BaseModel):
    """Response model for cart status update"""
    success: bool = True
    message: str
    data: Any
    cart_id: int
    new_status: str
    previous_status: Optional[str] = None


class DeleteCartResponse(BaseModel):
    """Response model for cart deletion"""
    success: bool
    message: str
    cart_id: int
    force_deleted: bool = False

