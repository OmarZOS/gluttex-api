from datetime import datetime
from sqlalchemy.orm import declarative_base
from typing import Optional,Dict
from pydantic import BaseModel

from constants import ReactionType

Base = declarative_base()
metadata = Base.metadata    


class API_Resolution(BaseModel):
    status: int
    error_code: str
    message: str


class Person_API(BaseModel):
    id_person: int
    person_details_id: Optional[int]

    # PersonDetails
    id_person_details: int
    person_first_name: Optional[str]
    person_last_name: Optional[str]
    person_birth_date: Optional[str]  # You might need to handle date formats
    person_gender: Optional[str]
    person_nationality: Optional[str]

    # Blood type
    id_blood_type: int

# -------------------------------------------------------------------------------------

class Location_API(BaseModel):
    id_location: int
    location_latitude: Optional[float]
    location_longitude: Optional[float]
    location_name: Optional[str]
    location_address_id: Optional[int]

    # Address
    id_address: int
    address_street: Optional[str]
    address_city: Optional[str]
    address_postal_code: Optional[str]
    address_country: Optional[str]

# -------------------------------------------------------------------------------------

class AppUser_API(BaseModel):
    id_app_user: int
    app_user_name: Optional[str]
    app_user_password: Optional[str]
    app_user_person_id: Optional[int]
    app_user_preferences: Optional[str]
    app_user_email: Optional[str]
    app_user_image_url: Optional[str]
    #  AppUserType
    app_user_type_id: Optional[int]

class AppUserUpdate_API(AppUser_API):
    username: str
    new_password: str

class AuthData_API(BaseModel):
    id_app_user: int
    app_user_name: Optional[str]
    app_user_password: Optional[str]

# -------------------------------------------------------------------------------------

class Patient_API(BaseModel):
    id_patient: int
    patient_person_id: Optional[int]
    patient_disease_severity_id: Optional[int]

class Serology_API(BaseModel):
    id_patient: int
    serology_indicator_id: int
    serology_indicator_value: str
    serology_date: str

class Symptoms_API(BaseModel):
    id_patient: int
    symptom_ids: list[int]
    symptoms_occurence_reason : Optional[str]
    reason_date : Optional[str]

# -------------------------------------------------------------------------------------

class Iproduct_API(BaseModel):

    id_iproduct : Optional[int] = 0
    iproduct_name : Optional[str] = ''
    iproduct_barcode : Optional[str] = ''
    iproduct_brand : Optional[str]  = ''
    iproduct_estimated_price : Optional[float] = 0.0
    iproduct_price_currency : Optional[str] = 'DZD'
    iproduct_gluten_status : Optional[str] = 'unknown'
    iproduct_info_source : Optional[str] = 'openai'
    iproduct_info_confidence : Optional[float] = 0.0
    iproduct_last_price_update :  Optional[str] = datetime.now()
    iproduct_created_at : Optional[str]= datetime.now()
    iproduct_last_update : Optional[str]= datetime.now()
    iproduct_model_name : Optional[str] = 'None'
    iproduct_image_url : Optional[str] = ''

class Product_API(BaseModel):
    id_product: Optional[int]
    product_provider_id: Optional[int]
    id_product_category: Optional[int]
    product_category_id: Optional[int]
    product_price : Optional[float]
    product_quantity : Optional[float]
    product_name: Optional[str]
    product_brand: Optional[str]
    product_barcode: Optional[str]
    product_description : Optional[str]
    product_quantifier: Optional[str]
    product_owner : Optional[int]
    # ProductCategory_API

class ProductImage_API(BaseModel):
    id_product_image: int
    product_image_url: Optional[str]
    product_ref_id: Optional[int]

class ProvidedService_API(BaseModel):
    provided_service_product_provider_id : int 
    provided_service_id : Optional[int] = 0
    provided_service_name : Optional[str] = ""
    provided_service_description : Optional[str] = ""
    provided_service_category_id : Optional[int] = 0
    provided_service_base_price : Optional[float] = 0
    provided_service_final_price : Optional[float] = 0
    provided_service_actual_duration : Optional[float] = 0
    provided_service_is_active : Optional[bool] = True
    provided_service_pricing_config : Optional[str] = ""


class OrderedService_API(BaseModel):
    ordered_service_service_id: Optional[int] = 0
    ordered_service_quantity: Optional[float] = 0.0
    ordered_service_unit_price: Optional[float] = 0.0
    ordered_service_total_price : Optional[float] = 0.0
    ordered_service_scheduled_at: Optional[str] = ""
    ordered_service_notes: Optional[str] = ""
    resource_requirement_id: Optional[int] = 0

class ServiceResourceRequirement_API(BaseModel):
    resource_requirement_id : Optional[int] = 0
    resource_requirement_service_id : Optional[int] = 0
    resource_requirement_name : Optional[str] = ""
    resource_requirement_type : Optional[str] = ""
    resource_requirement_quantity : Optional[float] = 0
    resource_requirement_cost_per_unit : Optional[float] = 0
    resource_requirement_is_consumable : Optional[bool] = 0
    resource_requirement_notes : Optional[str] = ""
    resource_requirement_product_ref : Optional[int] = 0

class ServiceStaffRequirement_API(BaseModel):
    service_staff_requirement_id :Optional[int]= 0
    service_staff_requirement_service_id :Optional[int]= 0
    service_staff_requirement_role : Optional[str] = ""
    service_staff_requirement_notes : Optional[str] = ""
    service_staff_requirement_min_count :Optional[float]=  0
    service_staff_requirement_max_count :  Optional[float]= 0
    service_staff_requirement_hourly_rate: Optional[float] = 0.0
    service_staff_requirement_allocated_hours : Optional[float] = 0.0

class Delivery_API(BaseModel):    
    id_delivery : Optional[int] = 0
    recipient_person : Optional[int] = 0
    recipient_provider : Optional[int] = 0
    delivery_package_count : Optional[int] = 0
    delivery_total_weight : Optional[float] = 0.0
    delivery_cargo_dimensions : Optional[str] = ""
    delivery_goods_description : Optional[str] = ""
    hs_code : Optional[str] = 0
    delivery_merchant_name : Optional[str] = 0
    delivery_shipping_method : Optional[str] = 0
    delivery_special_instructions : Optional[str] = 0
    delivery_status : Optional[str] = 0
    delivery_address_id : Optional[int] = 0
    delivery_current_address_id : Optional[int] = 0
    delivery_fee : Optional[float] = 0
    delivery_placed_order : Optional[int] = 0
    delivery_provider_id : Optional[int] = 0
    delivery_broker_id : Optional[int] = 0

    address_street: Optional[str] = ''
    address_city: Optional[str] = ''
    address_postal_code: Optional[str] = ''
    address_country: Optional[str] = ''


class Cart_API(BaseModel):
    cart_id : Optional[int] = 0
    cart_product_provider_id : Optional[int] = 0
    cart_selling_user : Optional[int] = 0
    cart_person_ref : Optional[int] = 0
    cart_client_user : Optional[int] = 0

    cart_due_date : Optional[str] = None
    cart_status : Optional[str] = "PENDING"
    cart_total_amount : Optional[float] = None
    cart_notes : Optional[str] = ""

    cart_invoice : Optional[bool] = False
    cart_receipt : Optional[bool] = False

    cart_deposit : Optional[bool] = False
    cart_payment : Optional[bool] = False
    cart_paid_money : Optional[float] = 0.0


class Payment_API(BaseModel):
    payment_id : Optional[int] = None
    payment_invoice_id : Optional[int] = None
    payment_amount : Optional[float] = 0.0
    payment_method : Optional[str] = ""
    payment_status : Optional[str] = ""
    payment_reference : Optional[str] = ""
    payment_notes : Optional[str] = ""

class Deposit_API(BaseModel):
    deposit_id : Optional[int] = None
    deposit_amount : Optional[float] = 0.0
    deposit_method : Optional[str] = ""
    deposit_cart_id : Optional[int] = None
    deposit_invoice_id : Optional[int] = None
    deposit_reference : Optional[str] = ""
    deposit_notes : Optional[str] = ""
    deposit_receipt_id : Optional[int] = None

class AdditionalFee_API(BaseModel):
    additional_fee_id : Optional[int] = None
    additional_fee_payment_id : Optional[int] = None
    additional_fee_name : Optional[str] = ""
    additional_fee_amount : Optional[float] = 0.0
    additional_fee_description : Optional[str] = ""
    additional_fee_document_url: Optional[str] = None
    additional_fee_user_id : int
    additional_fee_on_provider_id : int 



class ProductProvider_API(BaseModel):
    id_product_provider: int
    id_provider_owner: int
    idprovider_details_id: int
    id_product_provider_type: int
    id_provider_organisation : int
    # provider type
    product_provider_type_desc: Optional[str]
    provider_organisation_name : Optional[str]
    provider_organisation_desc : Optional[str]
    # provider details
    provider_name: Optional[str]
    provider_contact_info: Optional[str]

class ProviderOrganisation_API(BaseModel):
    id_provider_organisation : int
    provider_organisation_name : Optional[str]
    provider_organisation_desc : Optional[str]

class OrganisationImage_API(BaseModel):
    id_org_image : int
    org_image_url : Optional[str]
    org_ref_id : Optional[int]


class ManagementRule_API(BaseModel):
    id_management_rule: Optional[int] = 0
    rule_ref_org : Optional[int]
    rule_ref_provider : Optional[int]
    rule_ref_user : Optional[int]
    management_rule_code : Optional[int]
    management_rule_status : Optional[str] = None
    management_rule_expiry : Optional[str] = None

class Notification_API(BaseModel):
    id_notification: Optional[int] = 0
    notification_code: Optional[str]
    notification_params : Optional[str]
    notification_user_ref : Optional[int] 
    notification_created_at : Optional[str] = None
    notification_read_at : Optional[str] = None

class ReactionBase(BaseModel):
    user_id: int
    reaction_id: int
    value: Optional[float] = None
    type: ReactionType
    target_id: int   # product_id, recipe_id, provider_id, comment_id




class Reaction_API(BaseModel):

    id_reaction: Optional[int] = 3

    recipe_reaction_ref: Optional[int] = 3
    product_reaction_ref: Optional[int] = 3
    comment_reaction_ref: Optional[int] = 3
    
    id_product_reaction : Optional[int] = 0
    id_recipe_reaction: Optional[int] = 0
    id_comment_reaction: Optional[int] = 0
    
    reacted_on_product : Optional[int] = 0
    reacted_on_provider: Optional[int] = 0
    reacted_on_recipe: Optional[int] = 0
    reacted_on_comment: Optional[int] = 0

    recipe_reacting_user: Optional[int] = 0
    product_reacting_user: Optional[int] = 0
    comment_reacting_user: Optional[int] = 0

    provider_reaction_value: Optional[float] = 0.0
    product_reaction_value: Optional[float] = 0.0


# -------------------------------------------------------------------------------------

class Ingredient_API(BaseModel):
    id_ingredient : int
    ingredient_name : Optional[str]
    ingredient_icon_url : Optional[str]
    ingredient_quantifier : Optional[str]

class Recipe_API(BaseModel):
    id_recipe: int
    recipe_category_id: int
    recipe_name : str
    recipe_owner_id: Optional[int]
    recipe_preparation_time: Optional[str]
    recipe_instructions: Optional[str]
    recipe_description : Optional[str]
    recipe_ingredients: Optional[Dict[int, str]]

class RecipeContainsIngredient_API(BaseModel):
    idrecipe_contains_ingredient_id: int
    containing_recipe_id: Optional[int]
    contained_ingredient_id: Optional[int]
    contained_quantity: Optional[str]


class RecipeImage_API(BaseModel):
    id_recipe_image: int
    recipe_image_url: Optional[str]
    recipe_ref_id: Optional[int]

class ProviderImage_API(BaseModel):
    id_provider_image: int
    provider_image_url: Optional[str]
    provider_ref_id: Optional[int]


class PlacedOrder_API(BaseModel):
    id_placed_order : Optional[int]
    ordered_timestamp : Optional[str]
    order_discount : Optional[float]
    placed_order_last_mod : Optional[str]
    payment_status : Optional[str]
    payment_ref : Optional[str]
    placed_order_state : Optional[str]
    payment_method : Optional[str]
    ordering_user_id : Optional[int]

class OrderedItem_API(BaseModel):
    id_ordered_item : Optional[int]
    ordered_product_id : Optional[int]
    order_ref : Optional[int]
    
    product_discount : Optional[float]
    ordered_quantity : Optional[int]
    unit_price : Optional[float]
    applied_vat : Optional[float]



