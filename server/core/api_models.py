from sqlalchemy.orm import declarative_base
from typing import Optional,Dict
from pydantic import BaseModel

Base = declarative_base()
metadata = Base.metadata    

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
    app_user_image: Optional[str]

    #  AppUserType
    app_user_type_id: Optional[int]


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

class Product_API(BaseModel):
    id_product: int
    product_provider_id: int
    id_product_category: int
    product_category_id: Optional[int]
    product_price : float
    product_quantity : int
    product_name: Optional[str]
    product_brand: Optional[str]
    product_barcode: Optional[str]
    product_description : Optional[str]

    # ProductCategory_API


class ProductImage_API(BaseModel):
    id_product_image: int
    product_image_data: Optional[str]
    product_ref_id: Optional[int]


class ProductProvider_API(BaseModel):
    id_product_provider: int
    product_provider_details_id: Optional[int]
    # provider type
    id_product_provider_type: int
    product_provider_type_desc: Optional[str]
    # provider details
    idprovider_details_id: int
    provider_name: Optional[str]
    provider_contact_info: Optional[str]


# -------------------------------------------------------------------------------------

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

class Ingredient_API(BaseModel):
    id_ingredient: int
    ingredient_name: Optional[str]


class RecipeImage_API(BaseModel):
    id_recipe_image: int
    recipe_image_data: Optional[str]
    recipe_ref_id: Optional[int]
