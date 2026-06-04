# api_models.py
"""
API Models for Gluttex System
All models include proper types, default values, and validation.
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from constants import ReactionType

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class CartStatus(str, Enum):
    PENDING = "PENDING"
    CHECKED_OUT = "CHECKED_OUT"
    ABANDONED = "ABANDONED"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class GlutenStatus(str, Enum):
    GLUTEN_FREE = "gluten_free"
    CONTAINS_GLUTEN = "contains_gluten"
    MAY_CONTAIN = "may_contain"
    UNKNOWN = "unknown"

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class API_Resolution(BaseModel):
    """Standard API response wrapper"""
    status: int = Field(..., description="HTTP status code")
    error_code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human readable message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "error_code": "SUCCESS",
                "message": "Operation completed successfully"
            }
        }

# ============================================================================
# PERSON & LOCATION MODELS
# ============================================================================

class Person_API(BaseModel):
    """Person information model"""
    id_person: int = Field(default=0, ge=0, description="Person ID")
    person_details_id: Optional[int] = Field(default=None, description="Reference to person details")
    
    # PersonDetails
    id_person_details: int = Field(default=0, description="Person details ID")
    person_first_name: Optional[str] = Field(default=None, max_length=100, description="First name")
    person_last_name: Optional[str] = Field(default=None, max_length=100, description="Last name")
    person_birth_date: Optional[date] = Field(default=None, description="Birth date (YYYY-MM-DD)")
    person_gender: Optional[Gender] = Field(default=None, description="Gender")
    person_nationality: Optional[str] = Field(default=None, max_length=50, description="Nationality")
    
    # Blood type
    id_blood_type: int = Field(default=0, ge=0, description="Blood type ID")

class Location_API(BaseModel):
    """Location and address model"""
    id_location: int = Field(default=0, ge=0, description="Location ID")
    location_latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude")
    location_longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude")
    location_name: Optional[str] = Field(default=None, max_length=200, description="Location name")
    location_address_id: Optional[int] = Field(default=None, description="Address reference")
    
    # Address
    id_address: int = Field(default=0, description="Address ID")
    address_street: Optional[str] = Field(default=None, max_length=255, description="Street address")
    address_city: Optional[str] = Field(default=None, max_length=100, description="City")
    address_postal_code: Optional[str] = Field(default=None, max_length=20, description="Postal code")
    address_country: Optional[str] = Field(default=None, max_length=100, description="Country")

# ============================================================================
# USER MODELS
# ============================================================================

class AppUser_API(BaseModel):
    """Application user model"""
    id_app_user: int = Field(default=0, ge=0, description="User ID")
    app_user_name: Optional[str] = Field(default=None, min_length=3, max_length=50, description="Username")
    app_user_password: Optional[str] = Field(default=None, min_length=6, description="Password (hashed)")
    app_user_person_id: Optional[int] = Field(default=None, description="Person reference")
    app_user_preferences: Optional[str] = Field(default=None, description="User preferences (JSON)")
    app_user_email: Optional[str] = Field(default=None, max_length=100, description="Email address")
    app_user_image_url: Optional[str] = Field(default=None, max_length=500, description="Profile image URL")
    app_user_type_id: Optional[int] = Field(default=1, ge=1, description="User type ID")

class AppUserUpdate_API(AppUser_API):
    """User update model with password change"""
    username: str = Field(..., min_length=3, max_length=50, description="New username")
    new_password: Optional[str] = Field(default=None, min_length=6, description="New password (optional)")

class AuthData_API(BaseModel):
    """Authentication data model"""
    id_app_user: int = Field(default=0, description="User ID")
    app_user_name: Optional[str] = Field(default=None, description="Username")
    app_user_password: Optional[str] = Field(default=None, description="Password")

# ============================================================================
# PATIENT MODELS
# ============================================================================

class Patient_API(BaseModel):
    """Patient information model"""
    id_patient: int = Field(default=0, ge=0, description="Patient ID")
    patient_person_id: Optional[int] = Field(default=None, description="Person reference")
    patient_disease_severity_id: Optional[int] = Field(default=None, description="Disease severity ID")

class Serology_API(BaseModel):
    """Serology test results"""
    id_patient: int = Field(..., gt=0, description="Patient ID")
    serology_indicator_id: int = Field(..., gt=0, description="Indicator ID")
    serology_indicator_value: str = Field(..., max_length=50, description="Indicator value")
    serology_date: date = Field(..., description="Test date")

class Symptoms_API(BaseModel):
    """Patient symptoms model"""
    id_patient: int = Field(..., gt=0, description="Patient ID")
    symptom_ids: List[int] = Field(default_factory=list, description="List of symptom IDs")
    symptoms_occurence_reason: Optional[str] = Field(default=None, max_length=500, description="Reason for symptoms")
    reason_date: Optional[date] = Field(default=None, description="Date of symptoms")

# ============================================================================
# PRODUCT & IPRODUCT MODELS
# ============================================================================

class Iproduct_API(BaseModel):
    """External/imported product information"""
    id_iproduct: Optional[int] = Field(default=0, ge=0, description="IProduct ID")
    iproduct_name: Optional[str] = Field(default="", max_length=200, description="Product name")
    iproduct_barcode: Optional[str] = Field(default="", max_length=100, description="Barcode")
    iproduct_brand: Optional[str] = Field(default="", max_length=100, description="Brand name")
    iproduct_estimated_price: Optional[float] = Field(default=0.0, ge=0, description="Estimated price")
    iproduct_price_currency: Optional[str] = Field(default="DZD", max_length=3, description="Currency code")
    iproduct_gluten_status: Optional[GlutenStatus] = Field(default=GlutenStatus.UNKNOWN, description="Gluten status")
    iproduct_info_source: Optional[str] = Field(default="openai", max_length=50, description="Information source")
    iproduct_info_confidence: Optional[float] = Field(default=0.0, ge=0, le=1, description="Confidence score")
    iproduct_last_price_update: Optional[datetime] = Field(default_factory=datetime.now, description="Last price update")
    iproduct_created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    iproduct_last_update: Optional[datetime] = Field(default_factory=datetime.now, description="Last update timestamp")
    iproduct_model_name: Optional[str] = Field(default="None", max_length=100, description="AI model used")
    iproduct_image_url: Optional[str] = Field(default="", max_length=500, description="Product image URL")

class Product_API(BaseModel):
    """Main product model"""
    id_product: Optional[int] = Field(default=0, ge=0, description="Product ID")
    product_provider_id: Optional[int] = Field(default=None, description="Provider ID")
    id_product_category: Optional[int] = Field(default=None, description="Product category ID")
    product_category_id: Optional[int] = Field(default=None, description="Category ID (alias)")
    product_price: Optional[float] = Field(default=0.0, ge=0, description="Product price")
    product_quantity: Optional[float] = Field(default=0.0, ge=0, description="Available quantity")
    product_name: Optional[str] = Field(default=None, max_length=200, description="Product name")
    product_brand: Optional[str] = Field(default=None, max_length=100, description="Brand name")
    product_barcode: Optional[str] = Field(default=None, max_length=100, description="Barcode")
    product_description: Optional[str] = Field(default=None, max_length=1000, description="Product description")
    product_quantifier: Optional[str] = Field(default="unit", max_length=50, description="Unit of measurement")
    product_owner: Optional[int] = Field(default=None, description="Owner user ID")

class ProductImage_API(BaseModel):
    """Product image model"""
    id_product_image: int = Field(default=0, ge=0, description="Product image ID")
    product_image_url: Optional[str] = Field(default=None, max_length=500, description="Image URL")
    product_ref_id: Optional[int] = Field(default=None, description="Product reference")

# ============================================================================
# SERVICE MODELS
# ============================================================================

class ProvidedService_API(BaseModel):
    """Service offered by provider"""
    provided_service_product_provider_id: int = Field(..., gt=0, description="Provider ID")
    provided_service_id: Optional[int] = Field(default=0, ge=0, description="Service ID")
    provided_service_name: Optional[str] = Field(default="", max_length=200, description="Service name")
    provided_service_description: Optional[str] = Field(default="", max_length=1000, description="Service description")
    provided_service_category_id: Optional[int] = Field(default=0, description="Service category ID")
    provided_service_base_price: Optional[float] = Field(default=0.0, ge=0, description="Base price")
    provided_service_final_price: Optional[float] = Field(default=0.0, ge=0, description="Final price")
    provided_service_actual_duration: Optional[float] = Field(default=0.0, ge=0, description="Duration in minutes")
    provided_service_is_active: Optional[bool] = Field(default=True, description="Is service active")
    provided_service_pricing_config: Optional[str] = Field(default="", description="Pricing configuration (JSON)")

class OrderedService_API(BaseModel):
    """Service ordered by customer"""
    ordered_service_service_id: Optional[int] = Field(default=0, description="Service ID")
    ordered_service_quantity: Optional[float] = Field(default=1.0, gt=0, description="Quantity")
    ordered_service_unit_price: Optional[float] = Field(default=0.0, ge=0, description="Unit price")
    ordered_service_total_price: Optional[float] = Field(default=0.0, ge=0, description="Total price")
    ordered_service_scheduled_at: Optional[datetime] = Field(default=None, description="Scheduled date/time")
    ordered_service_notes: Optional[str] = Field(default="", max_length=500, description="Order notes")
    resource_requirement_id: Optional[int] = Field(default=0, description="Resource requirement ID")

class ServiceResourceRequirement_API(BaseModel):
    """Resource requirements for a service"""
    resource_requirement_id: Optional[int] = Field(default=0, description="Requirement ID")
    resource_requirement_service_id: Optional[int] = Field(default=0, description="Service ID")
    resource_requirement_name: Optional[str] = Field(default="", max_length=200, description="Resource name")
    resource_requirement_type: Optional[str] = Field(default="", max_length=50, description="Resource type")
    resource_requirement_quantity: Optional[float] = Field(default=0.0, ge=0, description="Quantity needed")
    resource_requirement_cost_per_unit: Optional[float] = Field(default=0.0, ge=0, description="Cost per unit")
    resource_requirement_is_consumable: Optional[bool] = Field(default=True, description="Is consumable")
    resource_requirement_notes: Optional[str] = Field(default="", max_length=500, description="Notes")
    resource_requirement_product_ref: Optional[int] = Field(default=0, description="Product reference")

class ServiceStaffRequirement_API(BaseModel):
    """Staff requirements for a service"""
    service_staff_requirement_id: Optional[int] = Field(default=0, description="Requirement ID")
    service_staff_requirement_service_id: Optional[int] = Field(default=0, description="Service ID")
    service_staff_requirement_role: Optional[str] = Field(default="", max_length=100, description="Staff role")
    service_staff_requirement_notes: Optional[str] = Field(default="", max_length=500, description="Notes")
    service_staff_requirement_min_count: Optional[float] = Field(default=0.0, ge=0, description="Minimum staff count")
    service_staff_requirement_max_count: Optional[float] = Field(default=0.0, ge=0, description="Maximum staff count")
    service_staff_requirement_hourly_rate: Optional[float] = Field(default=0.0, ge=0, description="Hourly rate")
    service_staff_requirement_allocated_hours: Optional[float] = Field(default=0.0, ge=0, description="Allocated hours")

# ============================================================================
# DELIVERY MODELS
# ============================================================================

class Delivery_API(BaseModel):
    """Delivery information"""
    id_delivery: Optional[int] = Field(default=0, ge=0, description="Delivery ID")
    recipient_person: Optional[int] = Field(default=None, description="Recipient person ID")
    recipient_provider: Optional[int] = Field(default=None, description="Recipient provider ID")
    delivery_package_count: Optional[int] = Field(default=1, ge=1, description="Number of packages")
    delivery_total_weight: Optional[float] = Field(default=0.0, ge=0, description="Total weight (kg)")
    delivery_cargo_dimensions: Optional[str] = Field(default="", max_length=100, description="Dimensions (LxWxH)")
    delivery_goods_description: Optional[str] = Field(default="", max_length=500, description="Goods description")
    hs_code: Optional[str] = Field(default="", max_length=20, description="HS code")
    delivery_merchant_name: Optional[str] = Field(default="", max_length=200, description="Merchant name")
    delivery_shipping_method: Optional[str] = Field(default="standard", max_length=50, description="Shipping method")
    delivery_special_instructions: Optional[str] = Field(default="", max_length=500, description="Special instructions")
    delivery_status: Optional[str] = Field(default="PENDING", max_length=50, description="Delivery status")
    delivery_address_id: Optional[int] = Field(default=None, description="Delivery address ID")
    delivery_current_address_id: Optional[int] = Field(default=None, description="Current location address ID")
    delivery_fee: Optional[float] = Field(default=0.0, ge=0, description="Delivery fee")
    delivery_placed_order: Optional[int] = Field(default=None, description="Associated order ID")
    delivery_provider_id: Optional[int] = Field(default=None, description="Delivery provider ID")
    delivery_broker_id: Optional[int] = Field(default=None, description="Broker ID")
    
    # Address fields
    address_street: Optional[str] = Field(default="", max_length=255, description="Street")
    address_city: Optional[str] = Field(default="", max_length=100, description="City")
    address_postal_code: Optional[str] = Field(default="", max_length=20, description="Postal code")
    address_country: Optional[str] = Field(default="", max_length=100, description="Country")

# ============================================================================
# CART & PAYMENT MODELS
# ============================================================================

class Cart_API(BaseModel):
    """Shopping cart model"""
    cart_id: Optional[int] = Field(default=0, ge=0, description="Cart ID")
    cart_product_provider_id: Optional[int] = Field(default=None, description="Provider ID")
    cart_selling_user: Optional[int] = Field(default=None, description="Seller user ID")
    cart_person_ref: Optional[int] = Field(default=None, description="Person reference")
    cart_client_user: Optional[int] = Field(default=None, description="Client user ID")
    
    cart_due_date: Optional[datetime] = Field(default=None, description="Due date")
    cart_status: Optional[CartStatus] = Field(default=CartStatus.PENDING, description="Cart status")
    cart_total_amount: Optional[float] = Field(default=0.0, ge=0, description="Total amount")
    cart_notes: Optional[str] = Field(default="", max_length=500, description="Cart notes")
    
    cart_invoice: Optional[bool] = Field(default=False, description="Has invoice")
    cart_receipt: Optional[bool] = Field(default=False, description="Has receipt")
    
    cart_deposit: Optional[bool] = Field(default=False, description="Has deposit")
    cart_payment: Optional[bool] = Field(default=False, description="Has payment")
    cart_paid_money: Optional[float] = Field(default=0.0, ge=0, description="Amount paid")

class Payment_API(BaseModel):
    """Payment information"""
    payment_id: Optional[int] = Field(default=0, ge=0, description="Payment ID")
    payment_invoice_id: Optional[int] = Field(default=None, description="Invoice ID")
    payment_amount: Optional[float] = Field(default=0.0, ge=0, description="Payment amount")
    payment_method: Optional[str] = Field(default="cash", max_length=50, description="Payment method")
    payment_status: Optional[PaymentStatus] = Field(default=PaymentStatus.PENDING, description="Payment status")
    payment_reference: Optional[str] = Field(default="", max_length=100, description="Payment reference")
    payment_notes: Optional[str] = Field(default="", max_length=500, description="Payment notes")

class Deposit_API(BaseModel):
    """Deposit information"""
    deposit_id: Optional[int] = Field(default=0, ge=0, description="Deposit ID")
    deposit_amount: Optional[float] = Field(default=0.0, ge=0, description="Deposit amount")
    deposit_method: Optional[str] = Field(default="cash", max_length=50, description="Deposit method")
    deposit_cart_id: Optional[int] = Field(default=None, description="Cart ID")
    deposit_invoice_id: Optional[int] = Field(default=None, description="Invoice ID")
    deposit_reference: Optional[str] = Field(default="", max_length=100, description="Deposit reference")
    deposit_notes: Optional[str] = Field(default="", max_length=500, description="Deposit notes")
    deposit_receipt_id: Optional[int] = Field(default=None, description="Receipt ID")

class AdditionalFee_API(BaseModel):
    """Additional fees"""
    additional_fee_id: Optional[int] = Field(default=0, description="Fee ID")
    additional_fee_payment_id: Optional[int] = Field(default=None, description="Payment ID")
    additional_fee_name: Optional[str] = Field(default="", max_length=200, description="Fee name")
    additional_fee_amount: Optional[float] = Field(default=0.0, ge=0, description="Fee amount")
    additional_fee_description: Optional[str] = Field(default="", max_length=500, description="Fee description")
    additional_fee_document_url: Optional[str] = Field(default=None, max_length=500, description="Document URL")
    additional_fee_user_id: int = Field(..., gt=0, description="User ID")
    additional_fee_on_provider_id: int = Field(..., gt=0, description="Provider ID")

# ============================================================================
# PROVIDER MODELS
# ============================================================================

class ProductProvider_API(BaseModel):
    """Product provider (supplier) model"""
    id_product_provider: int = Field(default=0, ge=0, description="Provider ID")
    id_provider_owner: int = Field(default=0, ge=0, description="Owner ID")
    idprovider_details_id: int = Field(default=0, ge=0, description="Provider details ID")
    id_product_provider_type: int = Field(default=0, ge=0, description="Provider type ID")
    id_provider_organisation: int = Field(default=0, ge=0, description="Organization ID")
    
    # Provider type
    product_provider_type_desc: Optional[str] = Field(default="", max_length=200, description="Provider type description")
    provider_organisation_name: Optional[str] = Field(default="", max_length=200, description="Organization name")
    provider_organisation_desc: Optional[str] = Field(default="", max_length=500, description="Organization description")
    
    # Provider details
    provider_name: Optional[str] = Field(default="", max_length=200, description="Provider name")
    provider_contact_info: Optional[str] = Field(default="", max_length=500, description="Contact information (JSON)")

class ProviderOrganisation_API(BaseModel):
    """Provider organization model"""
    id_provider_organisation: int = Field(default=0, ge=0, description="Organization ID")
    provider_organisation_name: Optional[str] = Field(default="", max_length=200, description="Organization name")
    provider_organisation_desc: Optional[str] = Field(default="", max_length=500, description="Organization description")

class OrganisationImage_API(BaseModel):
    """Organization image model"""
    id_org_image: int = Field(default=0, ge=0, description="Organization image ID")
    org_image_url: Optional[str] = Field(default=None, max_length=500, description="Image URL")
    org_ref_id: Optional[int] = Field(default=None, description="Organization reference")

class ProviderImage_API(BaseModel):
    """Provider image model"""
    id_provider_image: int = Field(default=0, ge=0, description="Provider image ID")
    provider_image_url: Optional[str] = Field(default=None, max_length=500, description="Image URL")
    provider_ref_id: Optional[int] = Field(default=None, description="Provider reference")

# ============================================================================
# RULES & NOTIFICATIONS
# ============================================================================

class ManagementRule_API(BaseModel):
    """Management rule model"""
    id_management_rule: Optional[int] = Field(default=0, description="Rule ID")
    rule_ref_org: Optional[int] = Field(default=None, description="Organization reference")
    rule_ref_provider: Optional[int] = Field(default=None, description="Provider reference")
    rule_ref_user: Optional[int] = Field(default=None, description="User reference")
    management_rule_code: Optional[int] = Field(default=None, description="Rule code")
    management_rule_status: Optional[str] = Field(default=None, max_length=50, description="Rule status")
    management_rule_expiry: Optional[datetime] = Field(default=None, description="Expiry date")

class Notification_API(BaseModel):
    """Notification model"""
    id_notification: Optional[int] = Field(default=0, description="Notification ID")
    notification_code: Optional[str] = Field(default=None, max_length=100, description="Notification code")
    notification_params: Optional[str] = Field(default=None, description="Parameters (JSON)")
    notification_user_ref: Optional[int] = Field(default=None, description="User reference")
    notification_created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    notification_read_at: Optional[datetime] = Field(default=None, description="Read timestamp")

# ============================================================================
# REACTION MODELS
# ============================================================================

class ReactionBase(BaseModel):
    """Base reaction model"""
    user_id: int = Field(..., gt=0, description="User ID")
    reaction_id: int = Field(..., gt=0, description="Reaction ID")
    value: Optional[float] = Field(default=None, description="Reaction value (for ratings)")
    type: ReactionType = Field(..., description="Reaction type")
    target_id: int = Field(..., gt=0, description="Target ID (product/recipe/provider/comment)")

class Reaction_API(BaseModel):
    """Reaction model"""
    id_reaction: Optional[int] = Field(default=0, description="Reaction ID")
    
    recipe_reaction_ref: Optional[int] = Field(default=0, description="Recipe reaction reference")
    product_reaction_ref: Optional[int] = Field(default=0, description="Product reaction reference")
    comment_reaction_ref: Optional[int] = Field(default=0, description="Comment reaction reference")
    
    id_product_reaction: Optional[int] = Field(default=0, description="Product reaction ID")
    id_recipe_reaction: Optional[int] = Field(default=0, description="Recipe reaction ID")
    id_comment_reaction: Optional[int] = Field(default=0, description="Comment reaction ID")
    
    reacted_on_product: Optional[int] = Field(default=0, description="Reacted product ID")
    reacted_on_provider: Optional[int] = Field(default=0, description="Reacted provider ID")
    reacted_on_recipe: Optional[int] = Field(default=0, description="Reacted recipe ID")
    reacted_on_comment: Optional[int] = Field(default=0, description="Reacted comment ID")
    
    recipe_reacting_user: Optional[int] = Field(default=0, description="Recipe reacting user ID")
    product_reacting_user: Optional[int] = Field(default=0, description="Product reacting user ID")
    comment_reacting_user: Optional[int] = Field(default=0, description="Comment reacting user ID")
    
    provider_reaction_value: Optional[float] = Field(default=0.0, description="Provider rating value")
    product_reaction_value: Optional[float] = Field(default=0.0, description="Product rating value")

# ============================================================================
# RECIPE MODELS
# ============================================================================

class Ingredient_API(BaseModel):
    """Ingredient model"""
    id_ingredient: int = Field(default=0, ge=0, description="Ingredient ID")
    ingredient_name: Optional[str] = Field(default=None, max_length=200, description="Ingredient name")
    ingredient_icon_url: Optional[str] = Field(default=None, max_length=500, description="Icon URL")
    ingredient_quantifier: Optional[str] = Field(default="unit", max_length=50, description="Unit of measurement")

class Recipe_API(BaseModel):
    """Recipe model"""
    id_recipe: int = Field(default=0, ge=0, description="Recipe ID")
    recipe_category_id: int = Field(..., gt=0, description="Recipe category ID")
    recipe_name: str = Field(..., max_length=200, description="Recipe name")
    recipe_owner_id: Optional[int] = Field(default=None, description="Owner user ID")
    recipe_preparation_time: Optional[str] = Field(default=None, max_length=50, description="Preparation time (ISO duration)")
    recipe_instructions: Optional[str] = Field(default=None, max_length=5000, description="Instructions")
    recipe_description: Optional[str] = Field(default=None, max_length=1000, description="Description")
    recipe_ingredients: Optional[Dict[int, str]] = Field(default_factory=dict, description="Ingredients mapping (ID -> quantity)")

class RecipeContainsIngredient_API(BaseModel):
    """Recipe-Ingredient association model"""
    idrecipe_contains_ingredient_id: int = Field(default=0, description="Association ID")
    containing_recipe_id: Optional[int] = Field(default=None, description="Recipe ID")
    contained_ingredient_id: Optional[int] = Field(default=None, description="Ingredient ID")
    contained_quantity: Optional[str] = Field(default=None, max_length=50, description="Quantity")

class RecipeImage_API(BaseModel):
    """Recipe image model"""
    id_recipe_image: int = Field(default=0, description="Recipe image ID")
    recipe_image_url: Optional[str] = Field(default=None, max_length=500, description="Image URL")
    recipe_ref_id: Optional[int] = Field(default=None, description="Recipe reference")

# ============================================================================
# ORDER MODELS
# ============================================================================

class PlacedOrder_API(BaseModel):
    """Placed order model"""
    id_placed_order: Optional[int] = Field(default=0, description="Order ID")
    ordered_timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Order timestamp")
    order_discount: Optional[float] = Field(default=0.0, ge=0, description="Order discount")
    placed_order_last_mod: Optional[datetime] = Field(default_factory=datetime.now, description="Last modification")
    payment_status: Optional[PaymentStatus] = Field(default=PaymentStatus.PENDING, description="Payment status")
    payment_ref: Optional[str] = Field(default="", max_length=100, description="Payment reference")
    placed_order_state: Optional[OrderStatus] = Field(default=OrderStatus.PENDING, description="Order status")
    payment_method: Optional[str] = Field(default="cash", max_length=50, description="Payment method")
    ordering_user_id: Optional[int] = Field(default=None, description="Ordering user ID")

class OrderedItem_API(BaseModel):
    """Ordered item model"""
    id_ordered_item: Optional[int] = Field(default=0, description="Ordered item ID")
    ordered_product_id: Optional[int] = Field(default=None, description="Product ID")
    order_ref: Optional[int] = Field(default=None, description="Order reference")
    
    product_discount: Optional[float] = Field(default=0.0, ge=0, le=100, description="Product discount percentage")
    ordered_quantity: Optional[int] = Field(default=1, gt=0, description="Quantity ordered")
    unit_price: Optional[float] = Field(default=0.0, ge=0, description="Unit price")
    applied_vat: Optional[float] = Field(default=0.0, ge=0, le=100, description="VAT percentage")
    
    @field_validator('ordered_quantity')
    @classmethod
    def validate_quantity(cls, v: Optional[int]) -> int:
        if v is not None and v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v or 1