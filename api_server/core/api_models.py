from datetime import datetime
from sqlalchemy.orm import declarative_base
from typing import Optional,Dict
from pydantic import BaseModel

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
    id_management_rule: Optional[int]
    rule_ref_org : Optional[int]
    rule_ref_provider : Optional[int]
    rule_ref_user : Optional[int]
    management_rule_code : Optional[int]
    management_rule_status : Optional[str]
    management_rule_expiry : Optional[str]

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
    ordered_quantity : Optional[float]
    unit_price : Optional[float]
    applied_vat : Optional[float]



