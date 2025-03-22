from sqlalchemy import Column, Date, DateTime, Float, ForeignKeyConstraint, Index, Integer, LargeBinary, String, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql.sqltypes import NullType
from geoalchemy2 import Geometry
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import column_property
from sqlalchemy.sql import func

Base = declarative_base()


class Address(Base):
    __tablename__ = 'address'

    id_address = Column(Integer, primary_key=True)
    address_street = Column(String(45))
    address_city = Column(String(45))
    address_postal_code = Column(String(45))
    address_country = Column(String(45))

    location = relationship('Location', back_populates='location_address')


class AppUserType(Base):
    __tablename__ = 'app_user_type'

    id_app_user_type = Column(Integer, primary_key=True)
    app_user_type_desc = Column(String(45))

    app_user = relationship('AppUser', back_populates='app_user_type')


class BloodType(Base):
    __tablename__ = 'blood_type'

    id_blood_type = Column(Integer, primary_key=True)
    blood_type_desc = Column(String(45))

    person = relationship('Person', back_populates='person_blood_type')


class DiseaseSeverity(Base):
    __tablename__ = 'disease_severity'

    id_disease_severity = Column(Integer, primary_key=True)
    disease_severity_desc = Column(String(45))

    patient = relationship('Patient', back_populates='patient_disease_severity')


class Ingredient(Base):
    __tablename__ = 'ingredient'

    id_ingredient = Column(Integer, primary_key=True)
    ingredient_name = Column(String(45))
    ingredient_icon = Column(Text)

    recipe_contains_ingredient = relationship('RecipeContainsIngredient', back_populates='contained_ingredient')


class PersonDetails(Base):
    __tablename__ = 'person_details'

    id_person_details = Column(Integer, primary_key=True)
    person_first_name = Column(String(45))
    person_last_name = Column(String(45))
    person_birth_date = Column(Date)
    person_gender = Column(String(45))
    person_nationality = Column(String(45))

    person = relationship('Person', back_populates='person_details')


class ProductCategory(Base):
    __tablename__ = 'product_category'

    id_product_category = Column(Integer, primary_key=True)
    product_category_desc = Column(String(45))
    product_category_icon = Column(Text)

    product = relationship('Product', back_populates='product_category')


class ProductProviderType(Base):
    __tablename__ = 'product_provider_type'

    id_product_provider_type = Column(Integer, primary_key=True)
    product_provider_type_desc = Column(String(45))

    product_provider = relationship('ProductProvider', back_populates='product_provider_type')


class ProviderDetails(Base):
    __tablename__ = 'provider_details'

    idprovider_details_id = Column(Integer, primary_key=True)
    provider_name = Column(String(45))
    provider_contact_info = Column(Text)

    product_provider = relationship('ProductProvider', back_populates='product_provider_details')


class ProviderOrganisation(Base):
    __tablename__ = 'provider_organisation'

    idprovider_organisation = Column(Integer, primary_key=True)
    provider_organisation_name = Column(String(45))
    provider_organisation_desc = Column(String(300))

    product_provider = relationship('ProductProvider', back_populates='product_provider_org')


class RecipeCategory(Base):
    __tablename__ = 'recipe_category'

    id_recipe_category = Column(Integer, primary_key=True)
    recipe_category_desc = Column(String(45))
    recipe_category_icon = Column(Text)

    recipe = relationship('Recipe', back_populates='recipe_category')


class SerologyIndicator(Base):
    __tablename__ = 'serology_indicator'

    id_serology_indicator = Column(Integer, primary_key=True)
    serology_indicator_name = Column(String(45))
    serology_indicator_desc = Column(String(300))

    serology = relationship('Serology', back_populates='indicator')


class Symptom(Base):
    __tablename__ = 'symptom'

    id_symptom = Column(Integer, primary_key=True)
    symptom_name = Column(String(45))
    symptom_desc = Column(String(300))

    presented_symptom = relationship('PresentedSymptom', back_populates='symptom')


class Location(Base):
    __tablename__ = 'location'
    __table_args__ = (
        ForeignKeyConstraint(['location_address_id'], ['address.id_address'], name='fk_location_1'),
        Index('fk_location_1_idx', 'location_address_id'),
        Index('spatial', 'location_position')
    )

    id_location = Column(Integer, primary_key=True)
    location_position = Column(Geometry('POINT', srid=4326), nullable=False)
    location_name = Column(String(45))
    location_address_id = Column(Integer)
    # Computed column to always get the WKT representation
    position_wkt = column_property(func.ST_AsText(location_position)) 
    location_address = relationship('Address', back_populates='location')
    person = relationship('Person', back_populates='person_location')
    product_provider = relationship('ProductProvider', back_populates='product_provider_location')


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['person_blood_type_id'], ['blood_type.id_blood_type'], name='fk_person_2'),
        ForeignKeyConstraint(['person_details_id'], ['person_details.id_person_details'], name='fk_person_1'),
        ForeignKeyConstraint(['person_location_id'], ['location.id_location'], name='fk_person_3'),
        Index('fk_person_1_idx', 'person_details_id'),
        Index('fk_person_2_idx', 'person_blood_type_id'),
        Index('fk_person_3_idx', 'person_location_id')
    )

    id_person = Column(Integer, primary_key=True)
    person_details_id = Column(Integer)
    person_blood_type_id = Column(Integer)
    person_location_id = Column(Integer)

    person_blood_type = relationship('BloodType', back_populates='person')
    person_details = relationship('PersonDetails', back_populates='person')
    person_location = relationship('Location', back_populates='person')
    app_user = relationship('AppUser', back_populates='app_user_person')
    patient = relationship('Patient', back_populates='patient_person')


class AppUser(Base):
    __tablename__ = 'app_user'
    __table_args__ = (
        ForeignKeyConstraint(['app_user_person_id'], ['person.id_person'], name='fk_app_user_3'),
        ForeignKeyConstraint(['app_user_type_id'], ['app_user_type.id_app_user_type'], name='fk_app_user_1'),
        Index('fk_app_user_1_idx', 'app_user_type_id'),
        Index('fk_app_user_3_idx', 'app_user_person_id')
    )

    id_app_user = Column(Integer, primary_key=True)
    app_user_name = Column(String(100))
    app_user_password = Column(String(256))
    app_user_person_id = Column(Integer)
    app_user_type_id = Column(Integer)
    app_user_preferences = Column(Text)
    app_user_image = Column(LargeBinary)
    app_user_last_active = Column(DateTime)
    app_user_last_updated = Column(DateTime)
    app_user_creation = Column(DateTime)

    app_user_person = relationship('Person', back_populates='app_user')
    app_user_type = relationship('AppUserType', back_populates='app_user')
    placed_order = relationship('PlacedOrder', back_populates='ordering_user')
    product_provider = relationship('ProductProvider', back_populates='app_user')
    recipe = relationship('Recipe', back_populates='recipe_owner')
    report = relationship('Report', back_populates='app_user')
    product = relationship('Product', back_populates='app_user')


class Patient(Base):
    __tablename__ = 'patient'
    __table_args__ = (
        ForeignKeyConstraint(['patient_disease_severity_id'], ['disease_severity.id_disease_severity'], name='fk_patient_2'),
        ForeignKeyConstraint(['patient_person_id'], ['person.id_person'], name='fk_patient_1'),
        Index('fk_patient_1_idx', 'patient_person_id'),
        Index('fk_patient_2_idx', 'patient_disease_severity_id')
    )

    id_patient = Column(Integer, primary_key=True)
    patient_person_id = Column(Integer)
    patient_disease_severity_id = Column(Integer)

    patient_disease_severity = relationship('DiseaseSeverity', back_populates='patient')
    patient_person = relationship('Person', back_populates='patient')
    serology = relationship('Serology', back_populates='patient')
    symptoms_occurence = relationship('SymptomsOccurence', back_populates='patient')


class PlacedOrder(Base):
    __tablename__ = 'placed_order'
    __table_args__ = (
        ForeignKeyConstraint(['ordering_user_id'], ['app_user.id_app_user'], name='fk_placed_order_1'),
        Index('fk_placed_order_1_idx', 'ordering_user_id')
    )

    id_placed_order = Column(Integer, primary_key=True)
    ordered_timestamp = Column(DateTime)
    order_discount = Column(Float(asdecimal=True))
    total_price = Column(Float(asdecimal=True))
    ordering_user_id = Column(Integer)

    ordering_user = relationship('AppUser', back_populates='placed_order')
    ordered_item = relationship('OrderedItem', back_populates='placed_order')


class ProductProvider(Base):
    __tablename__ = 'product_provider'
    __table_args__ = (
        ForeignKeyConstraint(['product_provider_details_id'], ['provider_details.idprovider_details_id'], name='fk_product_provider_3'),
        ForeignKeyConstraint(['product_provider_location_id'], ['location.id_location'], name='fk_product_provider_4'),
        ForeignKeyConstraint(['product_provider_org_id'], ['provider_organisation.idprovider_organisation'], name='fk_product_provider_2'),
        ForeignKeyConstraint(['product_provider_owner'], ['app_user.id_app_user'], name='fk_product_provider_5'),
        ForeignKeyConstraint(['product_provider_type_id'], ['product_provider_type.id_product_provider_type'], name='fk_product_provider_1'),
        Index('fk_product_provider_1_idx', 'product_provider_type_id'),
        Index('fk_product_provider_2_idx', 'product_provider_org_id'),
        Index('fk_product_provider_3_idx', 'product_provider_details_id'),
        Index('fk_product_provider_4_idx', 'product_provider_location_id'),
        Index('fk_product_provider_5_idx', 'product_provider_owner')
    )

    id_product_provider = Column(Integer, primary_key=True)
    product_provider_details_id = Column(Integer)
    product_provider_type_id = Column(Integer)
    product_provider_location_id = Column(Integer)
    product_provider_org_id = Column(Integer)
    product_provider_owner = Column(Integer)

    product_provider_details = relationship('ProviderDetails', back_populates='product_provider')
    product_provider_location = relationship('Location', back_populates='product_provider')
    product_provider_org = relationship('ProviderOrganisation', back_populates='product_provider')
    app_user = relationship('AppUser', back_populates='product_provider')
    product_provider_type = relationship('ProductProviderType', back_populates='product_provider')
    product = relationship('Product', back_populates='product_provider')


class Recipe(Base):
    __tablename__ = 'recipe'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_category_id'], ['recipe_category.id_recipe_category'], name='fk_recipe_2'),
        ForeignKeyConstraint(['recipe_owner_id'], ['app_user.id_app_user'], name='fk_recipe_1'),
        Index('fk_recipe_1_idx', 'recipe_owner_id'),
        Index('fk_recipe_2_idx', 'recipe_category_id')
    )

    id_recipe = Column(Integer, primary_key=True)
    recipe_owner_id = Column(Integer)
    recipe_category_id = Column(Integer)
    recipe_preparation_time = Column(String(45))
    recipe_instructions = Column(Text)
    recipe_name = Column(String(45))
    recipe_description = Column(String(300))
    recipe_creation = Column(DateTime)
    recipe_last_updated = Column(DateTime)

    recipe_category = relationship('RecipeCategory', back_populates='recipe')
    recipe_owner = relationship('AppUser', back_populates='recipe')
    recipe_contains_ingredient = relationship('RecipeContainsIngredient', back_populates='containing_recipe')
    recipe_image = relationship('RecipeImage', back_populates='recipe_ref')


class Report(Base):
    __tablename__ = 'report'
    __table_args__ = (
        ForeignKeyConstraint(['report_owner'], ['app_user.id_app_user'], name='fk_report_1'),
        Index('fk_report_1_idx', 'report_owner')
    )

    id_report = Column(Integer, primary_key=True)
    report_text = Column(Text)
    report_owner = Column(Integer)

    app_user = relationship('AppUser', back_populates='report')


class Serology(Base):
    __tablename__ = 'serology'
    __table_args__ = (
        ForeignKeyConstraint(['indicator_id'], ['serology_indicator.id_serology_indicator'], name='fk_serology_1'),
        ForeignKeyConstraint(['patient_id'], ['patient.id_patient'], name='fk_diagnosis_1'),
        Index('fk_diagnosis_1_idx', 'patient_id'),
        Index('fk_serology_1_idx', 'indicator_id')
    )

    id_serology = Column(Integer, primary_key=True)
    indicator_id = Column(Integer)
    serology_date = Column(Date)
    patient_id = Column(Integer)
    indicator_value = Column(String(45))

    indicator = relationship('SerologyIndicator', back_populates='serology')
    patient = relationship('Patient', back_populates='serology')


class SymptomsOccurence(Base):
    __tablename__ = 'symptoms_occurence'
    __table_args__ = (
        ForeignKeyConstraint(['symptoms_occurence_ref_patient'], ['patient.id_patient'], name='fk_symptoms_causality_1'),
        Index('fk_symptoms_causality_1_idx', 'symptoms_occurence_ref_patient')
    )

    id_symptoms_occurence = Column(Integer, primary_key=True)
    symptoms_occurence_submission_time = Column(DateTime)
    symptoms_occurence_reason = Column(String(300))
    reason_date = Column(DateTime)
    symptoms_occurence_ref_patient = Column(Integer)

    patient = relationship('Patient', back_populates='symptoms_occurence')
    presented_symptom = relationship('PresentedSymptom', back_populates='symptoms_occurence')


class PresentedSymptom(Base):
    __tablename__ = 'presented_symptom'
    __table_args__ = (
        ForeignKeyConstraint(['presented_symptom_ref_symptom'], ['symptom.id_symptom'], name='fk_presented_symptom_1'),
        ForeignKeyConstraint(['presented_symptom_ref_symptoms_occurence'], ['symptoms_occurence.id_symptoms_occurence'], name='fk_presented_symptom_2'),
        Index('fk_presented_symptom_1_idx', 'presented_symptom_ref_symptom'),
        Index('fk_presented_symptom_2_idx', 'presented_symptom_ref_symptoms_occurence')
    )

    id_presented_symptom = Column(Integer, primary_key=True)
    presented_symptom_ref_symptoms_occurence = Column(Integer)
    presented_symptom_ref_symptom = Column(Integer)

    symptom = relationship('Symptom', back_populates='presented_symptom')
    symptoms_occurence = relationship('SymptomsOccurence', back_populates='presented_symptom')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        ForeignKeyConstraint(['product_category_id'], ['product_category.id_product_category'], name='fk_product_2'),
        ForeignKeyConstraint(['product_owner'], ['app_user.id_app_user'], name='fk_product_3'),
        ForeignKeyConstraint(['product_provider_id'], ['product_provider.id_product_provider'], name='fk_product_1'),
        Index('fk_product_1_idx', 'product_provider_id'),
        Index('fk_product_2_idx', 'product_category_id'),
        Index('fk_product_3_idx', 'product_owner')
    )

    id_product = Column(Integer, primary_key=True)
    product_name = Column(String(45))
    product_brand = Column(String(45))
    product_provider_id = Column(Integer)
    product_category_id = Column(Integer)
    product_barcode = Column(String(45))
    last_updated = Column(DateTime)
    created = Column(DateTime)
    product_description = Column(String(300))
    product_price = Column(Float(asdecimal=True))
    product_quantity = Column(Integer)
    product_quantifier = Column(String(45))
    product_owner = Column(Integer)

    product_category = relationship('ProductCategory', back_populates='product')
    app_user = relationship('AppUser', back_populates='product')
    product_provider = relationship('ProductProvider', back_populates='product')
    ordered_item = relationship('OrderedItem', back_populates='ordered_product')
    product_image = relationship('ProductImage', back_populates='product_ref')


class RecipeContainsIngredient(Base):
    __tablename__ = 'recipe_contains_ingredient'
    __table_args__ = (
        ForeignKeyConstraint(['contained_ingredient_id'], ['ingredient.id_ingredient'], name='fk_recipe_contains_ingredient_2'),
        ForeignKeyConstraint(['containing_recipe_id'], ['recipe.id_recipe'], name='fk_recipe_contains_ingredient_1'),
        Index('fk_recipe_contains_ingredient_1_idx', 'containing_recipe_id'),
        Index('fk_recipe_contains_ingredient_2_idx', 'contained_ingredient_id')
    )

    idrecipe_contains_ingredient_id = Column(Integer, primary_key=True)
    containing_recipe_id = Column(Integer)
    contained_ingredient_id = Column(Integer)
    contained_quantity = Column(String(45))

    contained_ingredient = relationship('Ingredient', back_populates='recipe_contains_ingredient')
    containing_recipe = relationship('Recipe', back_populates='recipe_contains_ingredient')


class RecipeImage(Base):
    __tablename__ = 'recipe_image'
    __table_args__ = (
        ForeignKeyConstraint(['recipe_ref_id'], ['recipe.id_recipe'], name='fk_recipe_image_1'),
        Index('fk_recipe_image_1_idx', 'recipe_ref_id')
    )

    id_recipe_image = Column(Integer, primary_key=True)
    recipe_image_url = Column(String(255))
    recipe_ref_id = Column(Integer)

    recipe_ref = relationship('Recipe', back_populates='recipe_image')


class OrderedItem(Base):
    __tablename__ = 'ordered_item'
    __table_args__ = (
        ForeignKeyConstraint(['order_ref'], ['placed_order.id_placed_order'], name='fk_ordered_item_3'),
        ForeignKeyConstraint(['ordered_product_id'], ['product.id_product'], name='fk_ordered_item_1'),
        Index('fk_ordered_item_1_idx', 'ordered_product_id'),
        Index('fk_ordered_item_3_idx', 'order_ref')
    )

    id_ordered_item = Column(Integer, primary_key=True)
    ordered_product_id = Column(Integer)
    ordered_quantity = Column(String(100))
    applied_vat = Column(Float(asdecimal=True))
    order_ref = Column(Integer)
    unit_price = Column(Float(asdecimal=True))
    product_discount = Column(Float(asdecimal=True))

    placed_order = relationship('PlacedOrder', back_populates='ordered_item')
    ordered_product = relationship('Product', back_populates='ordered_item')


class ProductImage(Base):
    __tablename__ = 'product_image'
    __table_args__ = (
        ForeignKeyConstraint(['product_ref_id'], ['product.id_product'], name='fk_product_image_1'),
        Index('fk_product_image_1_idx', 'product_ref_id')
    )

    id_product_image = Column(Integer, primary_key=True)
    product_image_url = Column(String(255))
    product_ref_id = Column(Integer)

    product_ref = relationship('Product', back_populates='product_image')
