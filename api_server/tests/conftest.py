# tests/conftest.py (additional database-specific fixtures)
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool
from server import app
import tempfile
import os


# Base = declarative_base()


# tests/conftest.py
import pytest
import tempfile
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch
import sys

# Import your actual models
from core.persistent_models import Base, metadata
from core.models import (
    Address, AppUserType, BloodType, Cart, Delivery, DiseaseSeverity,
    Ingredient, Invoice, Payment, PersonDetails, PlacedOrder, Plan,
    ProductCategory, ProductProviderType, ProvidedServiceCategory,
    ProviderDetails, Reaction, Receipt, RecipeCategory, SerologyIndicator,
    Symptom, Wallet, DeliveryBroker, Deposit, Iproduct, MoneyTransaction,
    ProviderOrganisation, LocationImage, OrganisationImage, Person,
    AppUser, Patient, Comment, Notification, ProductProvider, Recipe,
    Report, Serology, SymptomsOccurence, AdditionalFee, CommentReaction,
    Conversation, ManagementRule, PresentedSymptom, Product, ProvidedService,
    ProviderImage, ProviderReaction, RecipeContainsIngredient, RecipeImage,
    RecipeReaction, ServicePackage, OrderedItem, OrderedService,
    ProductImage, ProductReaction, ServiceContribution, ServicePackageItem,
    ServiceResourceRequirement, ServiceStaffRequirement, Location,
    
)

# Fixture for TestClient
@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

# Create test database in memory
@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database for testing."""
    # Use SQLite for testing (no PostGIS support, but that's okay for unit tests)
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def populated_db(db_session):
    """Populate the database with sample data for testing."""
    # Create basic reference data
    blood_type_a = BloodType(blood_type_desc="A")
    blood_type_b = BloodType(blood_type_desc="B")
    db_session.add_all([blood_type_a, blood_type_b])
    
    # Create app user types
    admin_type = AppUserType(app_user_type_desc="Admin")
    user_type = AppUserType(app_user_type_desc="User")
    db_session.add_all([admin_type, user_type])
    
    # Create product categories
    category1 = ProductCategory(product_category_desc="Food", product_category_icon="food.png")
    category2 = ProductCategory(product_category_desc="Electronics", product_category_icon="electronics.png")
    db_session.add_all([category1, category2])
    
    # Create recipe categories
    recipe_cat1 = RecipeCategory(recipe_category_desc="Dessert", recipe_category_icon="dessert.png")
    recipe_cat2 = RecipeCategory(recipe_category_desc="Main Course", recipe_category_icon="main.png")
    db_session.add_all([recipe_cat1, recipe_cat2])
    
    # Create reaction types
    like_reaction = Reaction(reaction_type="like")
    dislike_reaction = Reaction(reaction_type="dislike")
    db_session.add_all([like_reaction, dislike_reaction])
    
    # Create disease severity levels
    mild = DiseaseSeverity(disease_severity_desc="Mild")
    severe = DiseaseSeverity(disease_severity_desc="Severe")
    db_session.add_all([mild, severe])
    
    # Create symptoms
    headache = Symptom(symptom_name="Headache", symptom_desc="Pain in head")
    fever = Symptom(symptom_name="Fever", symptom_desc="Elevated body temperature")
    db_session.add_all([headache, fever])
    
    # Create serology indicators
    indicator1 = SerologyIndicator(serology_indicator_name="Gluten Antibody", serology_indicator_desc="Gluten sensitivity indicator")
    indicator2 = SerologyIndicator(serology_indicator_name="Celiac Marker", serology_indicator_desc="Celiac disease marker")
    db_session.add_all([indicator1, indicator2])
    
    # Create plan
    basic_plan = Plan(
        plan_name="Basic",
        plan_price=9.99,
        billing_cycle="monthly",
        plan_type="individual"
    )
    db_session.add(basic_plan)
    
    # Create address
    address = Address(
        address_street="123 Main St",
        address_city="Test City",
        address_postal_code="12345",
        address_country="Test Country"
    )
    db_session.add(address)
    
    # Create location
    location = Location(
        location_name="Test Location",
        location_address=address,
        location_postal_code=12345
    )
    db_session.add(location)
    
    # Create person details
    person_details = PersonDetails(
        person_first_name="John",
        person_last_name="Doe",
        person_gender="Male",
        person_phone="+1234567890"
    )
    db_session.add(person_details)
    
    # Create person
    person = Person(
        person_details=person_details,
        person_blood_type=blood_type_a,
        person_location=location
    )
    db_session.add(person)
    
    # Create wallet
    wallet = Wallet(
        wallet_type="personal",
        wallet_currency="USD",
        wallet_balance=1000.00,
        wallet_status="active"
    )
    db_session.add(wallet)
    
    # Create app user
    app_user = AppUser(
        app_user_name="johndoe",
        app_user_password="hashed_password",
        app_user_person=person,
        app_user_type=admin_type,
        app_user_email="john@example.com",
        app_user_wallet=wallet,
        plan=basic_plan
    )
    db_session.add(app_user)
    
    # Create provider details
    provider_details = ProviderDetails(
        provider_name="Test Provider Inc.",
        provider_contact_info="contact@testprovider.com"
    )
    db_session.add(provider_details)
    
    # Create provider type
    provider_type = ProductProviderType(
        product_provider_type_desc="Retail Store"
    )
    db_session.add(provider_type)
    
    # Create provider wallet
    provider_wallet = Wallet(
        wallet_type="business",
        wallet_currency="USD",
        wallet_balance=5000.00,
        wallet_status="active"
    )
    db_session.add(provider_wallet)
    
    # Create provider organisation
    provider_org = ProviderOrganisation(
        provider_organisation_name="Test Org",
        provider_organisation_desc="Test organisation for providers"
    )
    db_session.add(provider_org)
    
    # Create product provider
    product_provider = ProductProvider(
        product_provider_details=provider_details,
        product_provider_type=provider_type,
        product_provider_location=location,
        product_provider_org=provider_org,
        product_provider_owner=app_user,
        product_provider_wallet=provider_wallet
    )
    db_session.add(product_provider)
    
    # Create ingredient
    ingredient = Ingredient(
        ingredient_name="Flour",
        ingredient_icon_url="flour.png",
        ingredient_quantifier="grams"
    )
    db_session.add(ingredient)
    
    # Create recipe
    recipe = Recipe(
        recipe_owner=app_user,
        recipe_category=recipe_cat1,
        recipe_name="Gluten Free Cake",
        recipe_description="Delicious gluten free cake recipe",
        recipe_preparation_time="60 minutes",
        recipe_instructions="Mix all ingredients and bake at 350F for 45 minutes."
    )
    db_session.add(recipe)
    
    # Create recipe contains ingredient
    recipe_ingredient = RecipeContainsIngredient(
        containing_recipe=recipe,
        contained_ingredient=ingredient,
        contained_quantity="200g"
    )
    db_session.add(recipe_ingredient)
    
    # Create product
    product = Product(
        product_name="Gluten Free Bread",
        product_brand="HealthyBake",
        product_provider=product_provider,
        product_category=category1,
        product_description="Freshly baked gluten free bread",
        product_price=5.99,
        product_quantity=50,
        product_quantifier="loaf",
        product_owner=app_user
    )
    db_session.add(product)
    
    # Create cart
    cart = Cart(
        cart_product_provider=product_provider,
        cart_selling_user=app_user.id_app_user,
        cart_client_user=app_user.id_app_user,
        cart_status="open",
        cart_total_amount=11.98,
        cart_person_ref=person.id_person
    )
    db_session.add(cart)
    
    # Create invoice
    invoice = Invoice(
        invoice_cart=cart,
        invoice_number="INV-001",
        invoice_total_amount=11.98,
        invoice_status="unpaid",
        invoice_issue_date="2024-01-15",
        invoice_due_date="2024-02-15"
    )
    db_session.add(invoice)
    
    # Create payment
    payment = Payment(
        payment_invoice=invoice,
        payment_amount=11.98,
        payment_method="card",
        payment_status="completed",
        payment_reference="PAY-REF-001"
    )
    db_session.add(payment)
    
    # Create receipt
    receipt = Receipt(
        receipt_amount=11.98,
        receipt_payment=payment,
        receipt_number="REC-001",
        cart=cart
    )
    db_session.add(receipt)
    
    # Create placed order
    placed_order = PlacedOrder(
        ordering_user=app_user,
        total_price=11.98,
        invoice=invoice,
        receipt=receipt,
        location=location
    )
    db_session.add(placed_order)
    
    # Create ordered item
    ordered_item = OrderedItem(
        ordered_product=product,
        ordered_quantity=2,
        unit_price=5.99,
        placed_order=placed_order,
        cart=cart
    )
    db_session.add(ordered_item)
    
    # Create delivery broker
    delivery_broker_wallet = Wallet(
        wallet_type="delivery",
        wallet_currency="USD",
        wallet_balance=1000.00,
        wallet_status="active"
    )
    db_session.add(delivery_broker_wallet)
    
    delivery_broker = DeliveryBroker(
        delivery_broker_name="Fast Delivery",
        delivery_broker_label="FD",
        delivery_broker_logo_url="fast-delivery.png",
        delivery_broker_wallet=delivery_broker_wallet
    )
    db_session.add(delivery_broker)
    
    # Create delivery
    delivery = Delivery(
        delivery_address=address,
        delivery_current_address=address,
        delivery_status="PENDING",
        delivery_fee=5.00,
        delivery_placed_order=placed_order,
        delivery_provider=product_provider,
        delivery_broker=delivery_broker
    )
    db_session.add(delivery)
    
    # Add delivery reference to cart
    cart.cart_delivery = delivery.id_delivery
    
    # Create product reaction
    product_reaction = ProductReaction(
        product_reacting_user=app_user,
        product_reaction_ref=like_reaction,
        reacted_on_product=product,
        product_reaction_value=5.0
    )
    db_session.add(product_reaction)
    
    # Create provider reaction
    provider_reaction = ProviderReaction(
        product_reacting_user=app_user,
        product_reaction_ref=like_reaction,
        reacted_on_provider=product_provider,
        provider_reaction_value=4.5
    )
    db_session.add(provider_reaction)
    
    # Create comment
    comment = Comment(
        comment_owner=app_user,
        comment_content="Great product!",
        comment_visibility=1
    )
    db_session.add(comment)
    
    # Create notification
    notification = Notification(
        notification_code="ORDER_COMPLETED",
        notification_params='{"order_id": 1}',
        notification_user_ref=app_user.id_app_user
    )
    db_session.add(notification)
    
    db_session.commit()
    
    return {
        'blood_types': [blood_type_a, blood_type_b],
        'user_types': [admin_type, user_type],
        'categories': [category1, category2],
        'person': person,
        'app_user': app_user,
        'product_provider': product_provider,
        'product': product,
        'cart': cart,
        'invoice': invoice,
        'payment': payment,
        'receipt': receipt,
        'placed_order': placed_order,
        'ordered_item': ordered_item,
        'delivery': delivery,
        'recipe': recipe,
        'ingredient': ingredient,
        'comment': comment,
        'notification': notification
    }

@pytest.fixture
def db_engine_with_data(test_engine, populated_db):
    """Return engine with populated data."""
    return test_engine

@pytest.fixture
def db_module():
    """Import the database module to test."""
    # Mock the DB_URI constant
    import storage.storage_service.StorageService as db_module
    
    # Mock the DB_URI to use SQLite for testing
    with patch('storage.storage_service.StorageService.DB_URI', 'sqlite:///:memory:'):
        yield db_module

@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = MagicMock()
    request.session = {}
    return request

@pytest.fixture
def sample_conditions():
    """Sample conditions for testing."""
    return {"product_name": "Gluten Free Bread"}

@pytest.fixture
def sample_eager_load_depth():
    """Sample eager load depth configuration."""
    return ["product_provider", "product_category"]

@pytest.fixture
def sample_join_tables():
    """Sample join tables for testing."""
    return [Product.product_provider]

@pytest.fixture
def sample_search_fields():
    """Sample search fields for testing."""
    return ["product_name", "product_description", "product_provider.provider_details.provider_name"]


# Create test database in memory
@pytest.fixture(scope="session")
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_engine):
    """Create a fresh database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def populated_db(test_engine, db_session):
    """Populate the database with test data."""
    # Create blood types
    blood_type_a = BloodType(blood_type_name="A")
    blood_type_b = BloodType(blood_type_name="B")
    db_session.add_all([blood_type_a, blood_type_b])
    
    # Create persons
    person1 = Person(
        person_name="John Doe", 
        person_email="john@example.com",
        blood_type=blood_type_a
    )
    person2 = Person(
        person_name="Jane Smith", 
        person_email="jane@example.com",
        blood_type=blood_type_b
    )
    db_session.add_all([person1, person2])
    
    # Create user types
    admin_type = AppUserType(user_type_name="Admin")
    user_type = AppUserType(user_type_name="User")
    db_session.add_all([admin_type, user_type])
    
    # Create users
    user1 = AppUser(
        user_name="johndoe",
        user_password="password123",
        person=person1,
        user_type=admin_type
    )
    user2 = AppUser(
        user_name="janesmith",
        user_password="password456",
        person=person2,
        user_type=user_type
    )
    db_session.add_all([user1, user2])
    
    # Create products
    products = [
        Product(product_name="Product A", product_code="PA001", product_price=1000),
        Product(product_name="Product B", product_code="PB001", product_price=2000),
        Product(product_name="Product C", product_code="PC001", product_price=3000),
    ]
    db_session.add_all(products)
    
    db_session.commit()
    
    return {
        'blood_types': [blood_type_a, blood_type_b],
        'persons': [person1, person2],
        'user_types': [admin_type, user_type],
        'users': [user1, user2],
        'products': products
    }

@pytest.fixture
def db_engine_with_data(test_engine, populated_db):
    """Return engine with populated data."""
    return test_engine

@pytest.fixture
def db_module():
    """Import the database module to test."""
    # Adjust import path based on your project structure
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Mock the DB_URI constant since we're using in-memory database
    import storage.storage_service.StorageService as db_module
    return db_module