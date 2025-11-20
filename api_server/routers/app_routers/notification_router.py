
import json
import logging
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from features.app.notification.builders.notification_builder import NotificationFactory


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


from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class OrderNotificationRequest(BaseModel):
    order_id: int = Field(..., example=12345)
    order_number: str = Field(..., example="ORD-7842")
    amount: float = Field(..., example=250.50)
    supplier_name: str = Field(..., example="Downtown Restaurant")
    customer_name: Optional[str] = Field(None, example="John Smith")
    items_count: Optional[int] = Field(None, example=5)
    user_ref: int = Field(..., example=1)

class OrderStatusChangeRequest(BaseModel):
    order_id: int = Field(..., example=12345)
    order_number: str = Field(..., example="ORD-7842")
    old_status: str = Field(..., example="pending")
    new_status: str = Field(..., example="confirmed")
    supplier_name: str = Field(..., example="Downtown Restaurant")
    user_ref: int = Field(..., example=1)

class InventoryNotificationRequest(BaseModel):
    product_id: int = Field(..., example=101)
    product_name: str = Field(..., example="Organic Tomatoes")
    current_stock: int = Field(..., example=5)
    min_stock: int = Field(..., example=10)
    supplier_name: str = Field(..., example="Central Kitchen")
    unit: str = Field("units", example="kg")
    user_ref: int = Field(..., example=1)

class ProductRunOutRequest(BaseModel):
    product_id: int = Field(..., example=102)
    product_name: str = Field(..., example="Fresh Milk")
    supplier_name: str = Field(..., example="Downtown Restaurant")
    unit: str = Field("units", example="liters")
    last_restock: Optional[str] = Field(None, example="2024-01-15")
    user_ref: int = Field(..., example=1)

class ProductRestockedRequest(BaseModel):
    product_id: int = Field(..., example=103)
    product_name: str = Field(..., example="Flour")
    new_stock: int = Field(..., example=50)
    supplier_name: str = Field(..., example="Bakery Central")
    unit: str = Field("units", example="kg")
    user_ref: int = Field(..., example=1)

class SocialReactionRequest(BaseModel):
    user_id: int = Field(..., example=201)
    user_name: str = Field(..., example="Sarah Johnson")
    target_type: str = Field(..., example="post")
    target_id: int = Field(..., example=301)
    target_title: str = Field(..., example="Weekly Specials")
    reaction_type: str = Field("liked", example="loved")
    user_ref: int = Field(..., example=1)

class SocialCommentRequest(BaseModel):
    user_id: int = Field(..., example=202)
    user_name: str = Field(..., example="Chef Michael")
    target_type: str = Field(..., example="recipe")
    target_id: int = Field(..., example=302)
    target_title: str = Field(..., example="Pasta Carbonara")
    comment_preview: str = Field(..., example="Great recipe! I added some truffle oil.")
    user_role: Optional[str] = Field(None, example="Executive Chef")
    user_ref: int = Field(..., example=1)

class RuleExpiryRequest(BaseModel):
    rule_id: int = Field(..., example=401)
    rule_name: str = Field(..., example="Summer Sale")
    days_left: int = Field(..., example=2)
    rule_type: str = Field("rule", example="discount")
    supplier_name: Optional[str] = Field(None, example="All Locations")
    user_ref: int = Field(..., example=1)

class NewRuleRequest(BaseModel):
    rule_id: int = Field(..., example=402)
    rule_name: str = Field(..., example="Bulk Discount")
    rule_type: str = Field(..., example="pricing")
    added_by: str = Field(..., example="Admin User")
    supplier_name: Optional[str] = Field(None, example="Central Kitchen")
    user_ref: int = Field(..., example=1)

class RuleActivatedRequest(BaseModel):
    rule_id: int = Field(..., example=403)
    rule_name: str = Field(..., example="Holiday Special")
    rule_type: str = Field(..., example="promotion")
    supplier_name: Optional[str] = Field(None, example="Main Restaurant")
    user_ref: int = Field(..., example=1)

class WorkInvitationRequest(BaseModel):
    organization_id: int = Field(..., example=501)
    organization_name: str = Field(..., example="Gourmet Bakery")
    role: str = Field(..., example="Manager")
    invited_by: str = Field(..., example="Chef Anna")
    invitation_id: Optional[int] = Field(None, example=601)
    user_ref: int = Field(..., example=1)

class InvitationAcceptedRequest(BaseModel):
    user_id: int = Field(..., example=203)
    user_name: str = Field(..., example="David Wilson")
    organization_name: str = Field(..., example="Riverside Cafe")
    role: str = Field(..., example="Manager")
    user_ref: int = Field(..., example=1)

class InvitationDeclinedRequest(BaseModel):
    user_id: int = Field(..., example=204)
    user_name: str = Field(..., example="Lisa Brown")
    organization_name: str = Field(..., example="City Bistro")
    user_ref: int = Field(..., example=1)

class RoleChangedRequest(BaseModel):
    user_id: int = Field(..., example=205)
    user_name: str = Field(..., example="Mike Thompson")
    old_role: str = Field(..., example="Staff")
    new_role: str = Field(..., example="Supervisor")
    organization_name: str = Field(..., example="Riverside Cafe")
    user_ref: int = Field(..., example=1)

class RecipeReactionRequest(BaseModel):
    user_id: int = Field(..., example=206)
    user_name: str = Field(..., example="Emma Davis")
    recipe_id: int = Field(..., example=701)
    recipe_name: str = Field(..., example="Chocolate Cake")
    reaction_type: str = Field("liked", example="loved")
    user_ref: int = Field(..., example=1)

class RecipeCommentRequest(BaseModel):
    user_id: int = Field(..., example=207)
    user_name: str = Field(..., example="Chef Anna")
    recipe_id: int = Field(..., example=702)
    recipe_name: str = Field(..., example="Beef Wellington")
    comment_preview: str = Field(..., example="The cooking time should be adjusted based on oven type.")
    user_role: Optional[str] = Field(None, example="Master Chef")
    user_ref: int = Field(..., example=1)

class RecipePublishedRequest(BaseModel):
    recipe_id: int = Field(..., example=703)
    recipe_name: str = Field(..., example="Tiramisu")
    published_by: str = Field(..., example="Chef Marco")
    user_ref: int = Field(..., example=1)

class SystemUpdateRequest(BaseModel):
    version: str = Field(..., example="2.1.0")
    new_features: List[str] = Field(..., example=["Dark Mode", "Advanced Analytics"])
    update_type: str = Field("minor", example="major")
    user_ref: int = Field(..., example=1)

class MaintenanceScheduledRequest(BaseModel):
    start_time: str = Field(..., example="2024-02-01T02:00:00Z")
    end_time: str = Field(..., example="2024-02-01T04:00:00Z")
    reason: Optional[str] = Field(None, example="Database maintenance")
    user_ref: int = Field(..., example=1)

class NewFeatureRequest(BaseModel):
    feature_name: str = Field(..., example="AI Inventory Predictions")
    feature_description: str = Field(..., example="Get AI-powered stock level predictions")
    available_from: Optional[str] = Field(None, example="2024-02-01")
    user_ref: int = Field(..., example=1)


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


notification_router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Order Notifications
@notification_router.post("/order-received")
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
        
        notification_data = {
            'notification_code': 'order_received',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/order-status-changed")
async def create_order_status_notification(request: OrderStatusChangeRequest):
    """Create an order status changed notification"""
    try:
        params = NotificationFactory.order.order_status_changed(
            order_id=request.order_id,
            order_number=request.order_number,
            old_status=request.old_status,
            new_status=request.new_status,
            supplier_name=request.supplier_name
        )
        
        notification_data = {
            'notification_code': 'order_status_changed',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Inventory Notifications
@notification_router.post("/product-stock-critical")
async def create_stock_critical_notification(request: InventoryNotificationRequest):
    """Create a product stock critical notification"""
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
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/product-run-out")
async def create_product_run_out_notification(request: ProductRunOutRequest):
    """Create a product run out notification"""
    try:
        params = NotificationFactory.inventory.product_run_out(
            product_id=request.product_id,
            product_name=request.product_name,
            supplier_name=request.supplier_name,
            last_restock=request.last_restock,
            unit=request.unit
        )
        
        notification_data = {
            'notification_code': 'product_run_out',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/product-restocked")
async def create_product_restocked_notification(request: ProductRestockedRequest):
    """Create a product restocked notification"""
    try:
        params = NotificationFactory.inventory.product_restocked(
            product_id=request.product_id,
            product_name=request.product_name,
            new_stock=request.new_stock,
            supplier_name=request.supplier_name,
            unit=request.unit
        )
        
        notification_data = {
            'notification_code': 'product_restocked',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Social Notifications
@notification_router.post("/reaction-received")
async def create_reaction_notification(request: SocialReactionRequest):
    """Create a reaction received notification"""
    try:
        params = NotificationFactory.social.reaction_received(
            user_id=request.user_id,
            user_name=request.user_name,
            target_type=request.target_type,
            target_id=request.target_id,
            target_title=request.target_title,
            reaction_type=request.reaction_type
        )
        
        notification_data = {
            'notification_code': 'reaction_received',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/comment-received")
async def create_comment_notification(request: SocialCommentRequest):
    """Create a comment received notification"""
    try:
        params = NotificationFactory.social.comment_received(
            user_id=request.user_id,
            user_name=request.user_name,
            target_type=request.target_type,
            target_id=request.target_id,
            target_title=request.target_title,
            comment_preview=request.comment_preview,
            user_role=request.user_role
        )
        
        notification_data = {
            'notification_code': 'comment_received',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rule Notifications
@notification_router.post("/rule-expiry")
async def create_rule_expiry_notification(request: RuleExpiryRequest):
    """Create a rule expiry notification"""
    try:
        params = NotificationFactory.rule.rule_expiry(
            rule_id=request.rule_id,
            rule_name=request.rule_name,
            days_left=request.days_left,
            rule_type=request.rule_type,
            supplier_name=request.supplier_name
        )
        
        notification_data = {
            'notification_code': 'rule_expiry',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/new-rule-added")
async def create_new_rule_notification(request: NewRuleRequest):
    """Create a new rule added notification"""
    try:
        params = NotificationFactory.rule.new_rule_added(
            rule_id=request.rule_id,
            rule_name=request.rule_name,
            rule_type=request.rule_type,
            added_by=request.added_by,
            supplier_name=request.supplier_name
        )
        
        notification_data = {
            'notification_code': 'new_rule_added',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/rule-activated")
async def create_rule_activated_notification(request: RuleActivatedRequest):
    """Create a rule activated notification"""
    try:
        params = NotificationFactory.rule.rule_activated(
            rule_id=request.rule_id,
            rule_name=request.rule_name,
            rule_type=request.rule_type,
            supplier_name=request.supplier_name
        )
        
        notification_data = {
            'notification_code': 'rule_activated',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Personnel Notifications
@notification_router.post("/work-invitation")
async def create_work_invitation_notification(request: WorkInvitationRequest):
    """Create a work invitation notification"""
    try:
        params = NotificationFactory.personnel.work_invitation(
            organization_id=request.organization_id,
            organization_name=request.organization_name,
            role=request.role,
            invited_by=request.invited_by,
            invitation_id=request.invitation_id
        )
        
        notification_data = {
            'notification_code': 'work_invitation',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/invitation-accepted")
async def create_invitation_accepted_notification(request: InvitationAcceptedRequest):
    """Create an invitation accepted notification"""
    try:
        params = NotificationFactory.personnel.invitation_accepted(
            user_id=request.user_id,
            user_name=request.user_name,
            organization_name=request.organization_name,
            role=request.role
        )
        
        notification_data = {
            'notification_code': 'invitation_accepted',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/invitation-declined")
async def create_invitation_declined_notification(request: InvitationDeclinedRequest):
    """Create an invitation declined notification"""
    try:
        params = NotificationFactory.personnel.invitation_declined(
            user_id=request.user_id,
            user_name=request.user_name,
            organization_name=request.organization_name
        )
        
        notification_data = {
            'notification_code': 'invitation_declined',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/role-changed")
async def create_role_changed_notification(request: RoleChangedRequest):
    """Create a role changed notification"""
    try:
        params = NotificationFactory.personnel.role_changed(
            user_id=request.user_id,
            user_name=request.user_name,
            old_role=request.old_role,
            new_role=request.new_role,
            organization_name=request.organization_name
        )
        
        notification_data = {
            'notification_code': 'role_changed',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Recipe Notifications
@notification_router.post("/recipe-reaction")
async def create_recipe_reaction_notification(request: RecipeReactionRequest):
    """Create a recipe reaction notification"""
    try:
        params = NotificationFactory.recipe.recipe_reaction(
            user_id=request.user_id,
            user_name=request.user_name,
            recipe_id=request.recipe_id,
            recipe_name=request.recipe_name,
            reaction_type=request.reaction_type
        )
        
        notification_data = {
            'notification_code': 'recipe_reaction',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/recipe-comment")
async def create_recipe_comment_notification(request: RecipeCommentRequest):
    """Create a recipe comment notification"""
    try:
        params = NotificationFactory.recipe.recipe_comment(
            user_id=request.user_id,
            user_name=request.user_name,
            recipe_id=request.recipe_id,
            recipe_name=request.recipe_name,
            comment_preview=request.comment_preview,
            user_role=request.user_role
        )
        
        notification_data = {
            'notification_code': 'recipe_comment',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/recipe-published")
async def create_recipe_published_notification(request: RecipePublishedRequest):
    """Create a recipe published notification"""
    try:
        params = NotificationFactory.recipe.recipe_published(
            recipe_id=request.recipe_id,
            recipe_name=request.recipe_name,
            published_by=request.published_by
        )
        
        notification_data = {
            'notification_code': 'recipe_published',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Notifications
@notification_router.post("/system-update")
async def create_system_update_notification(request: SystemUpdateRequest):
    """Create a system update notification"""
    try:
        params = NotificationFactory.system.system_update(
            version=request.version,
            new_features=request.new_features,
            update_type=request.update_type
        )
        
        notification_data = {
            'notification_code': 'system_update',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/maintenance-scheduled")
async def create_maintenance_notification(request: MaintenanceScheduledRequest):
    """Create a maintenance scheduled notification"""
    try:
        params = NotificationFactory.system.maintenance_scheduled(
            start_time=request.start_time,
            end_time=request.end_time,
            reason=request.reason
        )
        
        notification_data = {
            'notification_code': 'maintenance_scheduled',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@notification_router.post("/new-feature")
async def create_new_feature_notification(request: NewFeatureRequest):
    """Create a new feature available notification"""
    try:
        params = NotificationFactory.system.new_feature_available(
            feature_name=request.feature_name,
            feature_description=request.feature_description,
            available_from=request.available_from
        )
        
        notification_data = {
            'notification_code': 'new_feature_available',
            'notification_params': params,
            'notification_user_ref': request.user_ref,
            'parsed_params': json.loads(params)
        }
        
        return {
            "success": True,
            "notification": notification_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test All Endpoint
@notification_router.get("/test-all")
async def test_all_notifications():
    """Test all notification types with sample data"""
    test_results = {}
    
    try:
        # Test Order Notifications
        test_results["order_received"] = json.loads(NotificationFactory.order.order_received(
            order_id=12345, order_number="ORD-7842", amount=250.50, 
            supplier_name="Downtown Restaurant", customer_name="John Smith", items_count=5
        ))
        
        # Test Inventory Notifications
        test_results["product_stock_critical"] = json.loads(NotificationFactory.inventory.product_stock_critical(
            product_id=101, product_name="Organic Tomatoes", current_stock=5,
            min_stock=10, supplier_name="Central Kitchen", unit="kg"
        ))
        
        # Test Social Notifications
        test_results["reaction_received"] = json.loads(NotificationFactory.social.reaction_received(
            user_id=201, user_name="Sarah Johnson", target_type="post",
            target_id=301, target_title="Weekly Specials", reaction_type="loved"
        ))
        
        # Test Rule Notifications
        test_results["rule_expiry"] = json.loads(NotificationFactory.rule.rule_expiry(
            rule_id=401, rule_name="Summer Sale", days_left=2,
            rule_type="discount", supplier_name="All Locations"
        ))
        
        # Test Personnel Notifications
        test_results["work_invitation"] = json.loads(NotificationFactory.personnel.work_invitation(
            organization_id=501, organization_name="Gourmet Bakery",
            role="Manager", invited_by="Chef Anna", invitation_id=601
        ))
        
        # Test Recipe Notifications
        test_results["recipe_reaction"] = json.loads(NotificationFactory.recipe.recipe_reaction(
            user_id=206, user_name="Emma Davis", recipe_id=701,
            recipe_name="Chocolate Cake", reaction_type="loved"
        ))
        
        # Test System Notifications
        test_results["system_update"] = json.loads(NotificationFactory.system.system_update(
            version="2.1.0", new_features=["Dark Mode", "Advanced Analytics"], update_type="major"
        ))
        
        return {
            "success": True,
            "tested_notifications": len(test_results),
            "results": test_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))












