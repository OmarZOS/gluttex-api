
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class NotificationBuilder:
    """Base class for building notification parameters"""
    
    @staticmethod
    def build_params(**kwargs) -> str:
        """Convert parameters to JSON string"""
        # return json.dumps(kwargs, ensure_ascii=False)
        return kwargs
    
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()

class OrderNotificationBuilder(NotificationBuilder):
    """Builder for order-related notifications"""
    
    @staticmethod
    def order_received(order_id: int, order_number: str, amount: float, supplier_name: str, 
                      customer_name: Optional[str] = None, items_count: Optional[int] = None) -> str:
        """
        New order received notification
        
        Args:
            order_id: Internal order ID
            order_number: Human-readable order number (e.g., "ORD-7842")
            amount: Order total amount
            supplier_name: Name of the supplier/restaurant
            customer_name: Name of the customer (optional)
            items_count: Number of items in order (optional)
        """
        params = {
            "order_id": order_id,
            "order_number": order_number,
            "amount": f"{amount:.2f}",
            "supplier_name": supplier_name,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if customer_name:
            params["customer_name"] = customer_name
        if items_count:
            params["items_count"] = items_count
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def order_status_changed(order_id: int, order_number: str, old_status: str, 
                           new_status: str, supplier_name: str) -> str:
        """Order status changed notification"""
        return NotificationBuilder.build_params(
            order_id=order_id,
            order_number=order_number,
            old_status=old_status,
            new_status=new_status,
            supplier_name=supplier_name,
            timestamp=NotificationBuilder.get_current_timestamp()
        )

class InventoryNotificationBuilder(NotificationBuilder):
    """Builder for inventory-related notifications"""
    
    @staticmethod
    def product_stock_critical(product_id: int, product_name: str, current_stock: int, 
                              min_stock: int, supplier_name: str, unit: str = "units") -> str:
        """
        Product stock critically low notification
        
        Args:
            product_id: Internal product ID
            product_name: Name of the product
            current_stock: Current stock level
            min_stock: Minimum required stock level
            supplier_name: Name of the supplier/restaurant
            unit: Unit of measurement (e.g., "units", "kg", "liters")
        """
        return NotificationBuilder.build_params(
            product_id=product_id,
            product_name=product_name,
            current_stock=current_stock,
            min_stock=min_stock,
            supplier_name=supplier_name,
            unit=unit,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def product_run_out(product_id: int, product_name: str, supplier_name: str, 
                       last_restock: Optional[str] = None, unit: str = "units") -> str:
        """
        Product completely out of stock notification
        """
        params = {
            "product_id": product_id,
            "product_name": product_name,
            "supplier_name": supplier_name,
            "unit": unit,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if last_restock:
            params["last_restock"] = last_restock
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def product_restocked(product_id: int, product_name: str, new_stock: int, 
                         supplier_name: str, unit: str = "units") -> str:
        """Product successfully restocked notification"""
        return NotificationBuilder.build_params(
            product_id=product_id,
            product_name=product_name,
            new_stock=new_stock,
            supplier_name=supplier_name,
            unit=unit,
            timestamp=NotificationBuilder.get_current_timestamp()
        )

class SocialNotificationBuilder(NotificationBuilder):
    """Builder for social interactions (reactions, comments)"""
    
    @staticmethod
    def reaction_received(user_id: int, user_name: str, target_type: str, 
                         target_id: int, target_title: str, reaction_type: str = "liked") -> str:
        """
        Reaction received notification
        
        Args:
            user_id: ID of user who reacted
            user_name: Name of user who reacted
            target_type: Type of content (post, recipe, comment, etc.)
            target_id: ID of the target content
            target_title: Title/description of the target content
            reaction_type: Type of reaction (liked, loved, etc.)
        """
        return NotificationBuilder.build_params(
            user_id=user_id,
            user_name=user_name,
            target_type=target_type,
            target_id=target_id,
            target_title=target_title,
            reaction_type=reaction_type,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def comment_received(user_id: int, user_name: str, target_type: str, 
                        target_id: int, target_title: str, comment_preview: str,
                        user_role: Optional[str] = None) -> str:
        """
        Comment received notification
        """
        params = {
            "user_id": user_id,
            "user_name": user_name,
            "target_type": target_type,
            "target_id": target_id,
            "target_title": target_title,
            "comment_preview": comment_preview[:100],  # Limit preview length
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if user_role:
            params["user_role"] = user_role
            
        return NotificationBuilder.build_params(**params)

class RuleNotificationBuilder(NotificationBuilder):
    """Builder for rule-related notifications"""
    
    @staticmethod
    def rule_expiry(rule_id: int, rule_name: str, days_left: int, 
                   rule_type: str = "rule", supplier_name: Optional[str] = None) -> str:
        """
        Rule expiring soon notification
        
        Args:
            rule_id: Internal rule ID
            rule_name: Name of the rule
            days_left: Days until expiration (0 = expires today)
            rule_type: Type of rule (discount, pricing, policy, etc.)
            supplier_name: Name of the supplier (optional)
        """
        params = {
            "rule_id": rule_id,
            "rule_name": rule_name,
            "days_left": days_left,
            "rule_type": rule_type,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if supplier_name:
            params["supplier_name"] = supplier_name
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def new_rule_added(rule_id: int, role: str, rule_type: str, 
                      user_id: str, provider_id:int, organization_id:int, invited_by: Optional[int] = None) -> str:
        """
        New rule added notification
        """
        params = {
            "rule_id": rule_id,
            "role": role,
            "rule_type": rule_type,
            "user_id": user_id
            ,"provider_id":provider_id
            ,"organization_id":organization_id,
            # ,"invited_by":invited_by,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if invited_by:
            params["invited_by"] = invited_by
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def rule_activated(rule_id: int, rule_name: str, rule_type: str, 
                      supplier_name: Optional[str] = None) -> str:
        """Rule activated notification"""
        params = {
            "rule_id": rule_id,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if supplier_name:
            params["supplier_name"] = supplier_name
            
        return NotificationBuilder.build_params(**params)

class PersonnelNotificationBuilder(NotificationBuilder):
    """Builder for personnel and work-related notifications"""
    
    @staticmethod
    def work_invitation(organization_id: int, provider_id: int, role: str, 
                       invited_by: str, rule_id: Optional[int] = None) -> str:
        """
        Work invitation notification
        
        Args:
            organization_id: ID of the inviting organization
            organization_name: Name of the organization
            role: Role being offered (Manager, Chef, Staff, etc.)
            invited_by: Name of person who sent invitation
            invitation_id: Internal invitation ID (optional)
        """
        params = {
            "organization_id": organization_id,
            "provider_id": provider_id,
            "role": role,
            "invited_by": invited_by,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if rule_id:
            params["rule_id"] = rule_id
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def invitation_accepted(user_id: int, rule_name: str, organization_id: str, 
                           provider_id:int,role: str) -> str:
        """Work invitation accepted notification"""
        return NotificationBuilder.build_params(
            user_id=user_id,
            rule_name=rule_name,
            organization_id=organization_id,
            provider_id = provider_id,
            role=role,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def invitation_declined(user_id: int, user_name: str, organization_name: str) -> str:
        """Work invitation declined notification"""
        return NotificationBuilder.build_params(
            user_id=user_id,
            user_name=user_name,
            organization_name=organization_name,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def role_changed(user_id: int, user_name: str, old_role: str, 
                    new_role: str, organization_name: str) -> str:
        """User role changed notification"""
        return NotificationBuilder.build_params(
            user_id=user_id,
            user_name=user_name,
            old_role=old_role,
            new_role=new_role,
            organization_name=organization_name,
            timestamp=NotificationBuilder.get_current_timestamp()
        )

class RecipeNotificationBuilder(NotificationBuilder):
    """Builder for recipe-related notifications"""
    
    @staticmethod
    def recipe_reaction(user_id: int, user_name: str, recipe_id: int, 
                       recipe_name: str, reaction_type: str = "liked") -> str:
        """
        Recipe reaction received notification
        """
        return NotificationBuilder.build_params(
            user_id=user_id,
            user_name=user_name,
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            reaction_type=reaction_type,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def recipe_comment(user_id: int, user_name: str, recipe_id: int, 
                      recipe_name: str, comment_preview: str,
                      user_role: Optional[str] = None) -> str:
        """
        Recipe comment received notification
        """
        params = {
            "user_id": user_id,
            "user_name": user_name,
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "comment_preview": comment_preview[:100],
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if user_role:
            params["user_role"] = user_role
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def recipe_published(recipe_id: int, recipe_name: str, published_by: str) -> str:
        """Recipe published notification"""
        return NotificationBuilder.build_params(
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            published_by=published_by,
            timestamp=NotificationBuilder.get_current_timestamp()
        )

class SystemNotificationBuilder(NotificationBuilder):
    """Builder for system and administrative notifications"""
    
    @staticmethod
    def system_update(version: str, new_features: list, update_type: str = "minor") -> str:
        """
        System update notification
        """
        return NotificationBuilder.build_params(
            version=version,
            new_features=new_features,
            update_type=update_type,
            timestamp=NotificationBuilder.get_current_timestamp()
        )
    
    @staticmethod
    def maintenance_scheduled(start_time: str, end_time: str, 
                             reason: Optional[str] = None) -> str:
        """System maintenance scheduled notification"""
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if reason:
            params["reason"] = reason
            
        return NotificationBuilder.build_params(**params)
    
    @staticmethod
    def new_feature_available(feature_name: str, feature_description: str, 
                             available_from: Optional[str] = None) -> str:
        """New feature available notification"""
        params = {
            "feature_name": feature_name,
            "feature_description": feature_description,
            "timestamp": NotificationBuilder.get_current_timestamp()
        }
        
        if available_from:
            params["available_from"] = available_from
            
        return NotificationBuilder.build_params(**params)

# Main facade class for easy access
class NotificationFactory:
    """Facade class to provide easy access to all notification builders"""
    
    @staticmethod
    def dump_dict(kwargs:dict) -> str:
        """Convert parameters to JSON string"""
        return json.dumps(kwargs, ensure_ascii=False)
    
    # Order notifications
    order = OrderNotificationBuilder
    # Inventory notifications  
    inventory = InventoryNotificationBuilder
    # Social notifications
    social = SocialNotificationBuilder
    # Rule notifications
    rule = RuleNotificationBuilder
    # Personnel notifications
    personnel = PersonnelNotificationBuilder
    # Recipe notifications
    recipe = RecipeNotificationBuilder
    # System notifications
    system = SystemNotificationBuilder