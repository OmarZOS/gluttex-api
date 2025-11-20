from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import threading
import time

from api_server.routers.app_routers.notification_router import OrderNotificationRequest
from tests.test_rabbitmq_producer import RabbitMQTester, FlutterNotificationProducer

test_router = APIRouter(prefix="/test/rabbitmq", tags=["RabbitMQ Testing"])

# Global tester instance
tester = RabbitMQTester()

class TestResult(BaseModel):
    success: bool
    message: str
    details: Dict[str, Any] = {}

class QuickTestRequest(BaseModel):
    user_id: int = 1
    notification_code: str = "order_received"
    test_data: Dict[str, Any] = {
        "id": 999,
        "number": "API-TEST",
        "amount": 75.50,
        "supplier_name": "API Test Restaurant"
    }

@test_router.post("/quick-test", response_model=TestResult)
async def quick_rabbitmq_test(request: QuickTestRequest):
    """Quick test of RabbitMQ producer"""
    try:
        producer = FlutterNotificationProducer()
        
        producer.send_to_user(
            user_id=request.user_id,
            notification_code=request.notification_code,
            **request.test_data
        )
        
        producer.close()
        
        return TestResult(
            success=True,
            message=f"✅ Test message sent to user_{request.user_id}",
            details={
                "notification_code": request.notification_code,
                "user_id": request.user_id,
                "test_data": request.test_data
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@test_router.post("/test-order-notification", response_model=TestResult)
async def test_order_notification(request: OrderNotificationRequest):
    """Test order notification through RabbitMQ"""
    try:
        producer = FlutterNotificationProducer()
        
        producer.send_to_user(
            user_id=request.user_ref,
            notification_code='order_received',
            order_id=request.order_id,
            order_number=request.order_number,
            amount=request.amount,
            supplier_name=request.supplier_name,
            customer_name=request.customer_name,
            items_count=request.items_count
        )
        
        producer.close()
        
        return TestResult(
            success=True,
            message="✅ Order notification sent via RabbitMQ",
            details={
                "user_id": request.user_ref,
                "order_number": request.order_number,
                "amount": request.amount
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@test_router.post("/test-inventory-notification", response_model=TestResult)
async def test_inventory_notification(request: InventoryNotificationRequest):
    """Test inventory notification through RabbitMQ"""
    try:
        producer = FlutterNotificationProducer()
        
        producer.send_to_supplier(
            supplier_id=1,  # You might want to make this dynamic
            notification_code='product_stock_critical',
            product_id=request.product_id,
            product_name=request.product_name,
            current_stock=request.current_stock,
            min_stock=request.min_stock,
            supplier_name=request.supplier_name,
            unit=request.unit
        )
        
        producer.close()
        
        return TestResult(
            success=True,
            message="✅ Inventory notification broadcast via RabbitMQ",
            details={
                "product_name": request.product_name,
                "current_stock": request.current_stock,
                "min_stock": request.min_stock
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@test_router.post("/test-work-invitation", response_model=TestResult)
async def test_work_invitation(request: WorkInvitationRequest):
    """Test work invitation notification through RabbitMQ"""
    try:
        producer = FlutterNotificationProducer()
        
        producer.send_to_user(
            user_id=request.user_ref,
            notification_code='work_invitation',
            organization_id=request.organization_id,
            organization_name=request.organization_name,
            role=request.role,
            invited_by=request.invited_by,
            invitation_id=request.invitation_id
        )
        
        producer.close()
        
        return TestResult(
            success=True,
            message="✅ Work invitation sent via RabbitMQ",
            details={
                "user_id": request.user_ref,
                "organization_name": request.organization_name,
                "role": request.role
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@test_router.get("/comprehensive-test", response_model=TestResult)
async def run_comprehensive_test():
    """Run comprehensive RabbitMQ tests"""
    def run_tests():
        global tester
        tester.run_comprehensive_test()
    
    # Run tests in background thread
    thread = threading.Thread(target=run_tests, daemon=True)
    thread.start()
    
    return TestResult(
        success=True,
        message="🧪 Comprehensive tests started in background",
        details={"note": "Check server logs for detailed results"}
    )

@test_router.get("/connection-status", response_model=TestResult)
async def check_rabbitmq_connection():
    """Check RabbitMQ connection status"""
    success, message = tester.test_connection()
    
    return TestResult(
        success=success,
        message=message,
        details={"service": "RabbitMQ", "timestamp": time.time()}
    )

# Add to your main FastAPI app
def setup_test_routes(app):
    app.include_router(test_router)