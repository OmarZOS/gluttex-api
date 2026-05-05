# constants/success_messages.py
"""Success messages for API responses"""

from enum import Enum


class SuccessMessage(str, Enum):
    """Success messages for different operations"""
    
    # Generic
    OPERATION_SUCCESS = "Operation completed successfully"
    
    # User operations
    USER_CREATED = "User account created successfully"
    USER_UPDATED = "User information updated successfully"
    USER_DELETED = "User account deleted successfully"
    USER_LOGGED_IN = "Login successful"
    USER_LOGGED_OUT = "Logout successful"
    
    # Product operations
    PRODUCT_CREATED = "Product added successfully"
    PRODUCT_UPDATED = "Product updated successfully"
    PRODUCT_DELETED = "Product deleted successfully"
    
    # Recipe operations
    RECIPE_CREATED = "Recipe created successfully"
    RECIPE_UPDATED = "Recipe updated successfully"
    RECIPE_DELETED = "Recipe deleted successfully"
    
    # Order operations
    ORDER_CREATED = "Order placed successfully"
    ORDER_UPDATED = "Order updated successfully"
    ORDER_CANCELLED = "Order cancelled successfully"
    
    # Cart operations
    CART_CREATED = "Cart created successfully"
    CART_UPDATED = "Cart updated successfully"
    CART_CLEARED = "Cart cleared successfully"
    
    # Payment operations
    PAYMENT_PROCESSED = "Payment processed successfully"
    PAYMENT_REFUNDED = "Payment refunded successfully"
    
    # Delivery operations
    DELIVERY_CREATED = "Delivery scheduled successfully"
    DELIVERY_UPDATED = "Delivery information updated"
    
    # Health records
    SEROLOGY_RECORDED = "Serology record added successfully"
    SYMPTOM_RECORDED = "Symptom recorded successfully"
    
    # Staff operations
    STAFF_INVITED = "Staff invitation sent successfully"
    STAFF_UPDATED = "Staff assignment updated"
    STAFF_REMOVED = "Staff member removed"
    
    # Notification operations
    NOTIFICATION_SENT = "Notification sent successfully"
    NOTIFICATION_READ = "Notification marked as read"
    NOTIFICATIONS_READ_ALL = "All notifications marked as read"
    
    # Database operations
    RECORD_CREATED = "Record created successfully"
    RECORD_UPDATED = "Record updated successfully"
    RECORD_DELETED = "Record deleted successfully"
    
    # Bulk operations
    BULK_OPERATION_SUCCESS = "Bulk operation completed successfully"


# Simple string constants for backward compatibility (if needed)
PUT_SUCCESS = "Resource updated successfully"