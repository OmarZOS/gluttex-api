
import logging
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from features.notification.builders.notification_builder import NotificationFactory

notification_router = APIRouter()
logger = logging.getLogger("FastAPIApp")

class OrderNotificationRequest(BaseModel):
    order_id: int
    order_number: str
    amount: float
    supplier_name: str
    user_ref: int
    customer_name: Optional[str] = None
    items_count: Optional[int] = None

class InventoryNotificationRequest(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    min_stock: int
    supplier_name: str
    user_ref: int
    unit: str = "units"



@notification_router.post("/notifications/order-received")
async def create_order_notification(request: OrderNotificationRequest):
    """Create an order received notification"""
    try:
        params = NotificationFactory.order.order_received(
            order_id=request.order_id,
            order_number=request.order_number,
            amount=request.amount,
            supplier_name=request.supplier_name,
            customer_name=request.customer_name,
            items_count=request.items_count
        )
        
        # Here you would save to database
        notification_data = {
            'notification_code': 'order_received',
            'notification_params': params,
            'notification_user_ref': request.user_ref
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/notifications/stock-critical")
async def create_stock_notification(request: InventoryNotificationRequest):
    """Create a stock critical notification"""
    try:
        params = NotificationFactory.inventory.product_stock_critical(
            product_id=request.product_id,
            product_name=request.product_name,
            current_stock=request.current_stock,
            min_stock=request.min_stock,
            supplier_name=request.supplier_name,
            unit=request.unit
        )
        
        notification_data = {
            'notification_code': 'product_stock_critical',
            'notification_params': params,
            'notification_user_ref': request.user_ref
        }
        
        return {
            "success": True, 
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))














