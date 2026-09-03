#!/usr/bin/env python3
"""
Gluttex API Test Runner - Comprehensive Data Generation
Run with: python test_runner.py
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path


# ============================================================================
# REALISTIC DATA - EXPANDED
# ============================================================================

REAL_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Ali", "Fatima", "Youssef", "Amina", "Karim", "Sara",
    "Nadia", "Rachid", "Leila", "Hassan", "Khadija", "Omar", "Soukaina",
    "Hamza", "Salma", "Mehdi", "Yasmina", "Anas", "Imane", "Reda", "Nour",
    "Zakaria", "Houda", "Ayoub", "Maryam", "Amine", "Sana", "Adil", "Malak",
    "Adam", "Lina", "Rayane", "Ines", "Yacine", "Lydia", "Selim", "Nora",
    "Sofiane", "Amira", "Rayan", "Hana", "Kamel", "Mona", "Fares", "Dina"
]

REAL_LAST_NAMES = [
    "Benali", "Khan", "Cohen", "Lopez", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Peterson", "Murphy", "Cook", "Morgan", "Bell",
    "Ward", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood",
    "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", "Perry", "Powell", "Long",
    "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons", "Foster", "Gonzales"
]

REAL_ORG_NAMES = [
    "HealthCare Plus", "MediCorp", "Wellness Center", "Global Health",
    "Premium Care", "MediServe", "HealthFirst", "CarePlus", "MediHealth",
    "WellnessWorks", "City Medical", "Advanced Care", "Prime Health",
    "Elite Medical", "Family Care", "Specialist Center", "Medical Arts",
    "LifeLine Health", "CareBridge", "MediLink", "HealthWave", "VitalCare",
    "Optimum Health", "Pulse Medical", "Core Wellness", "Apex Healthcare",
    "Zenith Medical", "Nova Health", "Virtue Care", "Harmony Medical",
    "Pinnacle Health", "Radiant Care", "Summit Medical", "Tranquil Health"
]

REAL_SUPPLIER_NAMES = [
    "City Medical Center", "HealthFirst Clinic", "MediLab Services",
    "PharmaCare", "Advanced Medical Supplies", "Precision Diagnostics",
    "Wellness Medical Group", "Prime Healthcare", "Elite Medical Services",
    "CarePlus Pharmacy", "MediHealth Solutions", "Global Medical Supply",
    "MediTech Services", "HealthBridge", "Vitality Medical", "Apex Diagnostics",
    "CuraMed", "NovaCare", "Virtue Health", "Optimum Medical",
    "Pulse Healthcare", "Zenith Medical Supply", "Radiant Health", "Core Medical"
]

REAL_PRODUCT_NAMES = [
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Vitamin C", "Omega-3",
    "Antibiotic", "Pain Relief", "Allergy Medicine", "Cough Syrup",
    "Medical Device", "Surgical Mask", "Hand Sanitizer", "Thermometer",
    "Blood Pressure Monitor", "Stethoscope", "Syringe", "Bandage", "Antiseptic",
    "Antibiotic Cream", "Painkiller", "Antihistamine", "Decongestant", "Antacid",
    "Insulin", "Vaccine", "Antiviral", "Antifungal", "Antiparasitic",
    "Hemostatic Agent", "Suture Kit", "Surgical Gloves", "Medical Tape",
    "Wound Dressing", "Compression Bandage", "First Aid Kit", "Splint"
]

REAL_STREETS = [
    "Rue Didouche Mourad", "Avenue du 1er Novembre", "Rue Larbi Ben Mhidi",
    "Boulevard Krim Belkacem", "Rue des Freres Bouadou", "Avenue de l'Independance",
    "Rue Ali Khodja", "Boulevard Colonel Amirouche", "Rue Emir Abdelkader",
    "Avenue Ahmed Ben Bella", "Rue de la Liberte", "Boulevard des Martyrs",
    "Rue Abane Ramdane", "Avenue Franklin Roosevelt", "Rue de l'Alma",
    "Boulevard Zighout Youcef", "Rue des Freres Addad", "Avenue du Docteur Benzerdjeb",
    "Rue de Constantine", "Boulevard de la Republique", "Rue du 11 Decembre 1960"
]

REAL_CITIES = [
    "Algiers", "Oran", "Constantine", "Annaba", "Blida", "Setif",
    "Tizi Ouzou", "Bejaia", "Batna", "Sidi Bel Abbes", "Biskra", "Tebessa",
    "El Oued", "Ghardaia", "Tamanrasset", "Mostaganem", "Skikda", "Tipaza",
    "Boumerdes", "Relizane", "Saida", "M'sila", "Medea", "Tlemcen",
    "Chlef", "Bechar", "Adrar", "Laghouat", "Bouira", "Guelma"
]

SPECIALITIES = [
    "cardiology", "neurology", "pediatrics", "orthopedics", "general medicine",
    "dermatology", "ophthalmology", "oncology", "gynecology", "urology",
    "psychiatry", "radiology", "dentistry", "emergency medicine", "surgery",
    "nephrology", "gastroenterology", "pulmonology", "hematology", "immunology",
    "rheumatology", "endocrinology", "fertility", "audiology", "physiotherapy"
]

PROVIDER_TYPES = ["Medical", "Pharmacy", "Diagnostic", "Surgical", "Laboratory", "Dental", "Optical", "Therapeutic", "Rehabilitation"]

BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
COUNTRIES = ["DZ", "MA", "TN", "EG", "SA", "AE", "US", "FR", "DE", "IT", "ES", "CA", "GB"]

MEDICAL_SERVICE_TYPES = [
    "Consultation", "Surgery", "Laboratory Test", "Radiology", "Pharmacy",
    "Physical Therapy", "Mental Health", "Dental Care", "Vision Care", "Hearing Care",
    "Nutritional Counseling", "Fitness Assessment", "Vaccination", "Screening"
]


# ============================================================================
# ENUMS
# ============================================================================

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class AppUserType(str, Enum):
    PROVIDER = "provider"
    CUSTOMER = "customer"
    PATIENT = "patient"
    GUEST = "guest"
    ADMIN = "admin"
    STAFF = "staff"
    DOCTOR = "doctor"
    NURSE = "nurse"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TestUser:
    id: int = 0
    username: str = ""
    email: str = ""
    password: str = ""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    user_data: Dict[str, Any] = field(default_factory=dict)
    person_data: Dict[str, Any] = field(default_factory=dict)
    location_data: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'user_data': self.user_data,
            'person_data': self.person_data,
            'location_data': self.location_data,
            'roles': self.roles
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestUser':
        expires_at = data.get('token_expires_at')
        return cls(
            id=data.get('id', 0),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password=data.get('password', ''),
            access_token=data.get('access_token'),
            refresh_token=data.get('refresh_token'),
            token_expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
            user_data=data.get('user_data', {}),
            person_data=data.get('person_data', {}),
            location_data=data.get('location_data', {}),
            roles=data.get('roles', [])
        )


@dataclass
class TestContext:
    users: List[TestUser] = field(default_factory=list)
    created_organisations: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_staff_rules: List[int] = field(default_factory=list)
    created_invoices: List[int] = field(default_factory=list)
    created_orders: List[int] = field(default_factory=list)
    created_deliveries: List[int] = field(default_factory=list)
    user_org_mapping: Dict[int, List[int]] = field(default_factory=dict)
    user_supplier_mapping: Dict[int, List[int]] = field(default_factory=dict)
    user_roles: Dict[int, List[str]] = field(default_factory=dict)
    
    def save(self, filename: str = "test_context.json"):
        data = {
            'users': [u.to_dict() for u in self.users],
            'created_organisations': self.created_organisations,
            'created_suppliers': self.created_suppliers,
            'created_products': self.created_products,
            'created_staff_rules': self.created_staff_rules,
            'created_invoices': self.created_invoices,
            'created_orders': self.created_orders,
            'created_deliveries': self.created_deliveries,
            'user_org_mapping': self.user_org_mapping,
            'user_supplier_mapping': self.user_supplier_mapping,
            'user_roles': self.user_roles,
            'timestamp': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Test context saved to {filename}")
    
    def load(self, filename: str = "test_context.json"):
        if Path(filename).exists():
            with open(filename, 'r') as f:
                data = json.load(f)
            self.users = [TestUser.from_dict(u) for u in data.get('users', [])]
            self.created_organisations = data.get('created_organisations', [])
            self.created_suppliers = data.get('created_suppliers', [])
            self.created_products = data.get('created_products', [])
            self.created_staff_rules = data.get('created_staff_rules', [])
            self.created_invoices = data.get('created_invoices', [])
            self.created_orders = data.get('created_orders', [])
            self.created_deliveries = data.get('created_deliveries', [])
            self.user_org_mapping = data.get('user_org_mapping', {})
            self.user_supplier_mapping = data.get('user_supplier_mapping', {})
            self.user_roles = data.get('user_roles', {})
            print(f"📂 Test context loaded from {filename}")
            return True
        return False


# ============================================================================
# ENHANCED GENERATORS
# ============================================================================

def get_random_item(lst: List) -> Any:
    return random.choice(lst) if lst else None

def random_date(start_year: int = 1950, end_year: int = 2005) -> str:
    return f"{random.randint(start_year, end_year)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"

def random_phone() -> str:
    return f"+213-5{random.randint(10, 99):02d}{random.randint(10, 99):02d}{random.randint(10, 99):02d}"

def random_price(min_price: float = 5.0, max_price: float = 200.0) -> float:
    return round(random.uniform(min_price, max_price), 2)

def generate_user_data(user_type: str = None) -> Dict[str, Any]:
    first = get_random_item(REAL_FIRST_NAMES) or "Test"
    last = get_random_item(REAL_LAST_NAMES) or "User"
    
    all_types = [t.value for t in AppUserType]
    return {
        "app_user_name": f"{first.lower()}_{last.lower()}".replace(" ", ""),
        "app_user_password": "Test123!@#",
        "app_user_email": f"{first.lower()}.{last.lower()}@example.com".replace(" ", ""),
        "app_user_type": user_type or random.choice(all_types),
        "app_user_preferences": {
            "theme": random.choice(["dark", "light"]),
            "notifications": random.choice([True, False]),
            "language": random.choice(["en", "fr", "ar"]),
            "timezone": random.choice(["UTC+1", "UTC+2", "UTC+3"]),
            "currency": "DZD",
            "date_format": random.choice(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        },
        "app_user_image_url": f"https://example.com/avatars/{uuid.uuid4().hex[:8]}.jpg"
    }

def generate_person_data(extended: bool = False) -> Dict[str, Any]:
    data = {
        "person_first_name": get_random_item(REAL_FIRST_NAMES) or "Test",
        "person_last_name": get_random_item(REAL_LAST_NAMES) or "User",
        "person_birth_date": random_date(1950, 2005),
        "person_gender": random.choice([Gender.MALE.value, Gender.FEMALE.value]),
        "person_country_code": random.choice(COUNTRIES),
    }
    
    if extended:
        data.update({
            "blood_type": random.choice(BLOOD_TYPES),
            "person_email": f"person_{uuid.uuid4().hex[:4]}@example.com",
            "person_phone": random_phone(),
            "person_id_number": f"{random.randint(100000000, 999999999)}",
            "person_id_type": random.choice(["Passport", "National ID", "Driver License"]),
            "person_languages": random.choice([["ar", "fr"], ["en", "ar"], ["fr", "en"], ["ar", "fr", "en"]]),
            "person_job_title": random.choice(["Doctor", "Nurse", "Pharmacist", "Patient", "Administrator", "Specialist"]),
            "person_job_ref": f"JOB-{uuid.uuid4().hex[:6].upper()}"
        })
    
    return data

def generate_location_data(extended: bool = False) -> Dict[str, Any]:
    data = {
        "location_latitude": round(random.uniform(35.0, 37.0), 6),
        "location_longitude": round(random.uniform(-5.0, 8.0), 6),
        "location_name": get_random_item(["Home", "Work", "Clinic", "Office", "Shop", "Warehouse", "Distribution Center", "Hospital", "Pharmacy"]) or "Office",
        "address_street": f"{random.randint(1, 999)} {get_random_item(REAL_STREETS) or 'Main St'}",
        "address_city": get_random_item(REAL_CITIES) or "Algiers",
        "address_postal_code": f"{random.randint(1000, 9999)}",
        "address_country": random.choice(COUNTRIES)
    }
    
    if extended:
        data.update({
            "address_building": f"Building {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            "address_floor": random.randint(1, 12),
            "address_apartment": f"APT {random.randint(1, 100)}",
            "address_landmark": get_random_item(["Near Hospital", "Next to Mall", "Opposite School", "Near Station", "Downtown"]),
            "address_timezone": random.choice(["UTC+1", "UTC+2", "UTC+3"])
        })
    
    return data

def generate_organisation_data() -> Dict[str, Any]:
    name = get_random_item(REAL_ORG_NAMES) or "HealthCare Plus"
    return {
        "provider_organisation_name": f"{name} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Leading healthcare provider specializing in {get_random_item(SPECIALITIES) or 'medicine'}",
        "provider_organisation_naming": get_random_item(["LLC", "Inc", "Group", "Clinic", "Center", "Hospital", "Services"]),
        "provider_organisation_icon_url": f"https://example.com/logos/{uuid.uuid4().hex[:8]}.png",
        "verified_organisation": random.choice([True, False])
    }

def generate_supplier_data(org_id: int, owner_id: int) -> Dict[str, Any]:
    name = get_random_item(REAL_SUPPLIER_NAMES) or "Medical Center"
    provider_types = [1, 2, 3, 4, 5, 6]
    
    return {
        "id_provider_owner": owner_id,
        "id_provider_organisation": org_id,
        "id_product_provider_type": random.choice(provider_types),
        "product_provider_type_desc": get_random_item(PROVIDER_TYPES) or "Medical",
        "provider_organisation_name": f"{name} {uuid.uuid4().hex[:4]}",
        "provider_organisation_desc": f"Provider of {get_random_item(['medical', 'dental', 'diagnostic', 'pharmaceutical', 'surgical', 'laboratory', 'therapeutic', 'rehabilitation'])} services",
        "provider_name": f"Provider_{uuid.uuid4().hex[:8]}",
        "provider_contact_info": json.dumps({
            "phone": random_phone(),
            "email": f"contact_{uuid.uuid4().hex[:4]}@example.com",
            "website": f"https://{uuid.uuid4().hex[:8]}.com",
            "fax": f"+213-5{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}",
            "emergency_contact": random_phone()
        }),
        "provider_rating": round(random.uniform(1.0, 5.0), 1),
        "provider_reviews": random.randint(0, 1000),
        "verified_provider": random.choice([True, False]),
        "provider_available": random.choice([True, False])
    }

def generate_product_data(provider_id: int, owner_id: int) -> Dict[str, Any]:
    categories = [1, 2, 3, 4, 5]
    gluten_statuses = ["gluten_free", "contains_gluten", "may_contain", "unknown"]
    product_types = ["medication", "device", "supplement", "supply", "equipment", "consumable"]
    
    return {
        "product_name": f"{get_random_item(REAL_PRODUCT_NAMES) or 'Product'} {uuid.uuid4().hex[:4]}",
        "product_brand": get_random_item(["BrandA", "BrandB", "BrandC", "Generic", "Premium", "MedicalPro", "HealthPlus", "CareMed"]) or "Generic",
        "product_provider_id": provider_id,
        "product_category_id": random.choice(categories),
        "product_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "product_description": f"High-quality {get_random_item(product_types) or 'medical'} product",
        "product_price": random_price(5.0, 200.0),
        "product_quantity": random.randint(10, 1000),
        "product_quantifier": get_random_item(["mg", "g", "ml", "pack", "unit", "tablet", "capsule", "bottle"]) or "unit",
        "product_owner": owner_id,
        "product_sku": f"SKU-{uuid.uuid4().hex[:8].upper()}",
        "product_weight": round(random.uniform(0.1, 10.0), 2),
        "product_dimensions": f"{random.randint(1, 30)}x{random.randint(1, 30)}x{random.randint(1, 30)} cm",
        "product_manufacturer": get_random_item(["Manufacturer A", "Manufacturer B", "Manufacturer C", "Generic Corp"]),
        "product_gluten_status": random.choice(gluten_statuses),
        "product_shelf_life_months": random.randint(6, 36),
        "product_requires_prescription": random.choice([True, False]),
        "product_tax_rate": round(random.uniform(5.0, 20.0), 1),
        "product_is_active": random.choice([True, False])
    }

def generate_product_image_data() -> Dict[str, Any]:
    return {
        "product_image_url": f"https://example.com/images/product_{uuid.uuid4().hex[:8]}.jpg",
        "product_image_alt": f"Product image {uuid.uuid4().hex[:4]}",
        "product_image_order": random.randint(1, 5),
        "product_image_primary": random.choice([True, False])
    }

def generate_iproduct_data() -> Dict[str, Any]:
    gluten_statuses = ["gluten_free", "contains_gluten", "may_contain", "unknown"]
    categories = [1, 2, 3, 4, 5]
    
    return {
        "iproduct_name": f"Product_{uuid.uuid4().hex[:8]}",
        "iproduct_barcode": f"{random.randint(1000000000000, 9999999999999)}",
        "iproduct_brand": get_random_item(["BrandA", "BrandB", "BrandC", "Generic", "Premium"]) or "Generic",
        "iproduct_estimated_price": random_price(5.0, 200.0),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(gluten_statuses),
        "iproduct_info_source": random.choice(["openai", "manual", "csv_import", "api", "user_submitted"]),
        "iproduct_info_confidence": round(random.uniform(0.5, 1.0), 2),
        "iproduct_category_id": random.choice(categories),
        "iproduct_verified": random.choice([True, False]),
        "iproduct_ingredients": random.choice([
            ["Active ingredient A", "Excipient B", "Preservative C"],
            ["Ingredient X", "Ingredient Y", "Ingredient Z"],
            ["Component 1", "Component 2", "Component 3"]
        ]),
        "iproduct_nutrition_facts": {
            "calories": random.randint(0, 500),
            "protein": round(random.uniform(0.0, 30.0), 1),
            "carbs": round(random.uniform(0.0, 50.0), 1),
            "fat": round(random.uniform(0.0, 20.0), 1),
            "fiber": round(random.uniform(0.0, 15.0), 1)
        }
    }

def generate_invoice_data(user_id: int, supplier_id: int, org_id: int) -> Dict[str, Any]:
    total = random_price(100.0, 5000.0)
    tax = round(total * random.uniform(0.05, 0.20), 2)
    
    return {
        "invoice_number": f"INV-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}",
        "invoice_user_id": user_id,
        "invoice_supplier_id": supplier_id,
        "invoice_org_id": org_id,
        "invoice_date": datetime.now().isoformat(),
        "invoice_due_date": (datetime.now() + timedelta(days=random.randint(7, 30))).isoformat(),
        "invoice_total_amount": total,
        "invoice_tax_amount": tax,
        "invoice_discount": round(random.uniform(0.0, 50.0), 2),
        "invoice_final_amount": total + tax - round(random.uniform(0.0, 50.0), 2),
        "invoice_status": random.choice(["pending", "paid", "overdue", "cancelled"]),
        "invoice_notes": f"Order invoice for supplier {supplier_id}",
        "invoice_type": random.choice(["standard", "credit", "debit", "adjustment"]),
        "payment_method": random.choice(["cash", "card", "bank_transfer", "mobile_payment"]),
        "payment_status": random.choice(["pending", "completed", "failed", "refunded"])
    }

def generate_order_data(user_id: int, supplier_id: int, org_id: int) -> Dict[str, Any]:
    order_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "refunded"]
    
    return {
        "order_number": f"ORD-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}",
        "order_user_id": user_id,
        "order_supplier_id": supplier_id,
        "order_org_id": org_id,
        "order_date": datetime.now().isoformat(),
        "order_status": random.choice(order_statuses),
        "order_total": random_price(50.0, 2000.0),
        "order_tax": random_price(5.0, 200.0),
        "order_shipping_fee": random_price(0.0, 50.0),
        "order_discount": random_price(0.0, 100.0),
        "order_notes": f"Order for supplier {supplier_id}",
        "shipping_address": {
            "street": f"{random.randint(1, 999)} {get_random_item(REAL_STREETS) or 'Main St'}",
            "city": get_random_item(REAL_CITIES) or "Algiers",
            "postal_code": f"{random.randint(1000, 9999)}",
            "country": random.choice(COUNTRIES)
        },
        "payment_method": random.choice(["cash", "card", "bank_transfer"]),
        "delivery_method": random.choice(["standard", "express", "pickup"]),
        "priority": random.choice(["low", "medium", "high"])
    }

def generate_delivery_data(order_id: int, supplier_id: int, user_id: int) -> Dict[str, Any]:
    statuses = ["pending", "processing", "ready_for_pickup", "in_transit", "out_for_delivery", "delivered", "cancelled", "failed"]
    shipping_methods = ["standard", "express", "overnight", "courier", "pickup"]
    
    return {
        "order_id": order_id,
        "supplier_id": supplier_id,
        "user_id": user_id,
        "delivery_address": f"{random.randint(1, 999)} {get_random_item(REAL_STREETS) or 'Main St'}, {get_random_item(REAL_CITIES) or 'Algiers'}",
        "delivery_status": random.choice(statuses),
        "shipping_method": random.choice(shipping_methods),
        "tracking_number": f"TRK-{uuid.uuid4().hex[:12].upper()}",
        "estimated_delivery": (datetime.now() + timedelta(days=random.randint(1, 7))).isoformat(),
        "actual_delivery": None,
        "delivery_fee": random_price(0.0, 50.0),
        "package_count": random.randint(1, 5),
        "total_weight": round(random.uniform(0.5, 50.0), 2),
        "special_instructions": random.choice(["Leave at front door", "Call upon arrival", "Deliver to reception", "No signature required", ""]),
        "recipient_name": f"{get_random_item(REAL_FIRST_NAMES)} {get_random_item(REAL_LAST_NAMES)}",
        "recipient_phone": random_phone()
    }


# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.context = TestContext()
        self.test_user = None
        self._used_assignments: Set[str] = set()
        self.stats = {
            "users": 0,
            "organisations": 0,
            "suppliers": 0,
            "products": 0,
            "staff_rules": 0,
            "invoices": 0,
            "orders": 0,
            "deliveries": 0
        }
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def get_auth_headers(self, user: TestUser) -> Dict[str, str]:
        if user.access_token:
            return {"Authorization": f"Bearer {user.access_token}"}
        return {}
    
    def extract_id(self, data: Dict[str, Any]) -> int:
        if not data:
            return 0
        
        for key in ['id_app_user', 'id_product_provider', 'idprovider_organisation', 
                   'id_product', 'id', 'user_id', 'supplier_id', 'organisation_id',
                   'invoice_id', 'order_id', 'delivery_id']:
            if key in data:
                try:
                    return int(data[key])
                except (ValueError, TypeError):
                    pass
        
        for nested in ['data', 'result', 'user', 'provider', 'product', 'invoice', 'order']:
            if nested in data and isinstance(data[nested], dict):
                return self.extract_id(data[nested])
        
        return 0
    
    # ==================== USER MANAGEMENT ====================
    
    async def create_user(self, user_type: str = None, extended: bool = False) -> Optional[TestUser]:
        user_data = generate_user_data(user_type)
        person_data = generate_person_data(extended)
        location_data = generate_location_data(extended)
        
        payload = {
            "user": user_data,
            "person": person_data,
            "location": location_data
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/app_user",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                user_id = self.extract_id(result)
                
                if user_id > 0:
                    user = TestUser(
                        id=user_id,
                        username=user_data.get('app_user_name', ''),
                        email=user_data.get('app_user_email', ''),
                        password=user_data.get('app_user_password', 'Test123!@#'),
                        user_data=user_data,
                        person_data=person_data,
                        location_data=location_data
                    )
                    
                    # Assign roles based on user type
                    user_type_val = user_data.get('app_user_type', 'guest')
                    if user_type_val == 'provider':
                        user.roles = ['provider', 'business_owner']
                    elif user_type_val == 'customer':
                        user.roles = ['customer', 'consumer']
                    elif user_type_val == 'patient':
                        user.roles = ['patient']
                    elif user_type_val == 'admin':
                        user.roles = ['admin', 'super_user']
                    elif user_type_val == 'staff':
                        user.roles = ['staff', 'support']
                    elif user_type_val == 'doctor':
                        user.roles = ['doctor', 'medical_staff']
                    elif user_type_val == 'nurse':
                        user.roles = ['nurse', 'medical_staff']
                    else:
                        user.roles = ['guest']
                    
                    self.context.user_roles[user_id] = user.roles
                    return user
            return None
        except Exception:
            return None
    
    async def create_users(self, count: int = 10) -> List[TestUser]:
        print(f"\n👥 Creating {count} users...")
        
        created = []
        user_types = ["provider", "customer", "patient", "guest", "doctor", "nurse", "staff", "admin"]
        
        for i in range(count):
            user_type = user_types[i % len(user_types)]
            extended = i % 2 == 0  # Alternate between basic and extended data
            print(f"  [{i+1}/{count}] Creating {user_type} user{' (extended)' if extended else ''}...")
            user = await self.create_user(user_type, extended)
            if user:
                self.context.users.append(user)
                created.append(user)
                self.stats["users"] += 1
                print(f"   ✅ User {i+1}: {user.username} (ID: {user.id}, Roles: {', '.join(user.roles)})")
            else:
                print(f"   ❌ Failed to create user {i+1}")
            await asyncio.sleep(0.1)  # Small delay to avoid rate limiting
        
        print(f"\n✅ Created {len(created)}/{count} users")
        return created
    
    async def login_user(self, user: TestUser) -> bool:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/authentication/token",
                json={
                    "app_user_name": user.username,
                    "app_user_password": user.password
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                token = result.get('access_token')
                if token:
                    user.access_token = token
                    user.refresh_token = result.get('refresh_token')
                    user.token_expires_at = datetime.now() + timedelta(hours=1)
                    return True
            return False
        except Exception:
            return False
    
    async def login_users(self) -> int:
        print("\n🔐 Logging in users...")
        success = 0
        
        for user in self.context.users:
            if await self.login_user(user):
                success += 1
                print(f"   ✅ {user.username}")
            else:
                print(f"   ❌ {user.username}")
        
        print(f"✅ Logged in {success}/{len(self.context.users)} users")
        return success
    
    # ==================== ORGANISATIONS ====================
    
    async def create_organisations(self, user: TestUser, count: int = 3) -> List[int]:
        print(f"\n🏢 Creating {count} organisations for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return []
        
        org_ids = []
        
        for i in range(count):
            data = generate_organisation_data()
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/organisations",
                    json={"organisation": data},
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    org_id = self.extract_id(response.json())
                    if org_id > 0:
                        org_ids.append(org_id)
                        self.context.created_organisations.append(org_id)
                        self.stats["organisations"] += 1
                        print(f"   ✅ Organisation {i+1}: {org_id}")
                    else:
                        print(f"   ⚠️ Could not extract org ID")
                else:
                    print(f"   ❌ HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            await asyncio.sleep(0.1)
        
        if org_ids:
            self.context.user_org_mapping[user.id] = org_ids
        
        print(f"✅ Created {len(org_ids)} organisations")
        return org_ids
    
    # ==================== SUPPLIERS ====================
    
    async def create_suppliers(self, user: TestUser, org_ids: List[int], 
                              count_per_org: int = 3) -> List[int]:
        if not org_ids:
            return []
        
        print(f"\n🏥 Creating suppliers for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return []
        
        supplier_ids = []
        total = len(org_ids) * count_per_org
        count = 0
        
        for org_id in org_ids:
            for i in range(count_per_org):
                sup_data = generate_supplier_data(org_id, user.id)
                loc_data = generate_location_data(extended=True)
                
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/suppliers",
                        json={"provider": sup_data, "location": loc_data},
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        sup_id = self.extract_id(response.json())
                        if sup_id > 0:
                            supplier_ids.append(sup_id)
                            self.context.created_suppliers.append(sup_id)
                            self.stats["suppliers"] += 1
                            count += 1
                            print(f"   ✅ Supplier {count}/{total}: {sup_id}")
                        else:
                            print(f"   ⚠️ Could not extract supplier ID")
                    else:
                        print(f"   ❌ HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                await asyncio.sleep(0.1)
        
        if supplier_ids:
            self.context.user_supplier_mapping[user.id] = supplier_ids
        
        print(f"✅ Created {len(supplier_ids)} suppliers")
        return supplier_ids
    
    # ==================== PRODUCTS ====================
    
    async def create_products(self, user: TestUser, supplier_ids: List[int],
                             count_per_supplier: int = 5) -> int:
        if not supplier_ids:
            return 0
        
        print(f"\n📦 Creating products for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return 0
        
        total = len(supplier_ids) * count_per_supplier
        count = 0
        
        for sup_id in supplier_ids:
            for i in range(count_per_supplier):
                prod_data = generate_product_data(sup_id, user.id)
                img_data = generate_product_image_data()
                iprod_data = generate_iproduct_data()
                
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/products",
                        json={
                            "product": prod_data,
                            "image": img_data,
                            "iproduct": iprod_data
                        },
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        prod_id = self.extract_id(response.json())
                        if prod_id > 0:
                            self.context.created_products.append(prod_id)
                            self.stats["products"] += 1
                            count += 1
                            print(f"   ✅ Product {count}/{total}: {prod_id}")
                        else:
                            print(f"   ⚠️ Could not extract product ID")
                    else:
                        print(f"   ❌ HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                await asyncio.sleep(0.1)
        
        print(f"✅ Created {count} products")
        return count
    
    # ==================== STAFF RULES ====================
    
    async def create_staff_rules(self, owner: TestUser, supplier_ids: List[int],
                                target_users: List[TestUser], rules_per_supplier: int = 2) -> int:
        if not supplier_ids or not target_users:
            return 0
        
        print(f"\n👥 Creating staff rules...")
        
        headers = self.get_auth_headers(owner)
        if not headers:
            print("   ❌ No auth token")
            return 0
        
        org_ids = self.context.user_org_mapping.get(owner.id, [])
        if not org_ids:
            print("   ⚠️ No organisation found")
            return 0
        
        rule_codes = [27, 45, 60, 12, 33, 78, 91, 56, 23, 67]
        statuses = ["ACTIVE", "PENDING", "EXPIRED"]
        total = 0
        
        for supplier_id in supplier_ids:
            for target in target_users[:rules_per_supplier]:
                # Skip if target is the owner
                is_owner = False
                for uid, suppliers in self.context.user_supplier_mapping.items():
                    if supplier_id in suppliers and uid == target.id:
                        is_owner = True
                        break
                
                if is_owner:
                    continue
                
                key = f"{target.id}_{supplier_id}"
                if key in self._used_assignments:
                    continue
                
                data = {
                    "rule_ref_org": org_ids[0],
                    "rule_ref_provider": supplier_id,
                    "rule_ref_user": target.id,
                    "management_rule_code": random.choice(rule_codes),
                    "management_rule_status": random.choice(statuses),
                    "management_rule_expiry": (datetime.now() + timedelta(days=random.randint(7, 90))).isoformat(),
                    "management_rule_notes": f"Staff rule for supplier {supplier_id}"
                }
                
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/staff",
                        json=data,
                        headers=headers
                    )
                    if response.status_code == 201:
                        self.context.created_staff_rules.append(1)
                        self._used_assignments.add(key)
                        self.stats["staff_rules"] += 1
                        total += 1
                        print(f"   ✅ Rule: User {target.id} -> Supplier {supplier_id}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                await asyncio.sleep(0.1)
        
        print(f"✅ Created {total} staff rules")
        return total
    
    # ==================== INVOICES ====================
    
    async def create_invoices(self, user: TestUser, supplier_ids: List[int], count: int = 3) -> int:
        if not supplier_ids:
            return 0
        
        print(f"\n📄 Creating invoices for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return 0
        
        org_ids = self.context.user_org_mapping.get(user.id, [])
        if not org_ids:
            print("   ⚠️ No organisation found")
            return 0
        
        total = 0
        for supplier_id in supplier_ids[:3]:  # Limit to 3 suppliers
            for _ in range(count):
                data = generate_invoice_data(user.id, supplier_id, org_ids[0])
                
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/invoices",
                        json=data,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        inv_id = self.extract_id(response.json())
                        if inv_id > 0:
                            self.context.created_invoices.append(inv_id)
                            self.stats["invoices"] += 1
                            total += 1
                            print(f"   ✅ Invoice: {inv_id}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                await asyncio.sleep(0.1)
        
        print(f"✅ Created {total} invoices")
        return total
    
    # ==================== ORDERS ====================
    
    async def create_orders(self, user: TestUser, supplier_ids: List[int], count: int = 3) -> int:
        if not supplier_ids:
            return 0
        
        print(f"\n📋 Creating orders for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return 0
        
        org_ids = self.context.user_org_mapping.get(user.id, [])
        if not org_ids:
            print("   ⚠️ No organisation found")
            return 0
        
        total = 0
        for supplier_id in supplier_ids[:3]:  # Limit to 3 suppliers
            for _ in range(count):
                data = generate_order_data(user.id, supplier_id, org_ids[0])
                
                try:
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/orders",
                        json=data,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201]:
                        order_id = self.extract_id(response.json())
                        if order_id > 0:
                            self.context.created_orders.append(order_id)
                            self.stats["orders"] += 1
                            total += 1
                            print(f"   ✅ Order: {order_id}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                await asyncio.sleep(0.1)
        
        print(f"✅ Created {total} orders")
        return total
    
    # ==================== DELIVERIES ====================
    
    async def create_deliveries(self, user: TestUser, order_ids: List[int], count: int = 2) -> int:
        if not order_ids:
            return 0
        
        print(f"\n🚚 Creating deliveries for {user.username}...")
        
        headers = self.get_auth_headers(user)
        if not headers:
            print("   ❌ No auth token")
            return 0
        
        supplier_ids = self.context.user_supplier_mapping.get(user.id, [])
        if not supplier_ids:
            print("   ⚠️ No suppliers found")
            return 0
        
        total = 0
        for order_id in order_ids[:5]:  # Limit to 5 orders
            supplier_id = random.choice(supplier_ids)
            data = generate_delivery_data(order_id, supplier_id, user.id)
            
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/v1/deliveries",
                    json=data,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    delivery_id = self.extract_id(response.json())
                    if delivery_id > 0:
                        self.context.created_deliveries.append(delivery_id)
                        self.stats["deliveries"] += 1
                        total += 1
                        print(f"   ✅ Delivery: {delivery_id}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            await asyncio.sleep(0.1)
        
        print(f"✅ Created {total} deliveries")
        return total
    
    # ==================== MAIN RUNNER ====================
    
    async def run(self, skip_users: bool = False, skip_login: bool = False,
                  context_file: str = "test_context.json"):
        print("\n" + "="*60)
        print("🚀 GLUTTEX API TEST RUNNER - COMPREHENSIVE")
        print("="*60)
        print(f"📍 URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        # Load context
        if Path(context_file).exists():
            self.context.load(context_file)
            # Update stats from context
            self.stats["users"] = len(self.context.users)
            self.stats["organisations"] = len(self.context.created_organisations)
            self.stats["suppliers"] = len(self.context.created_suppliers)
            self.stats["products"] = len(self.context.created_products)
            self.stats["staff_rules"] = len(self.context.created_staff_rules)
            self.stats["invoices"] = len(self.context.created_invoices)
            self.stats["orders"] = len(self.context.created_orders)
            self.stats["deliveries"] = len(self.context.created_deliveries)
        
        # Create users
        if not skip_users and not self.context.users:
            await self.create_users(10)  # 10 users for better coverage
        else:
            print(f"\n📋 Using {len(self.context.users)} existing users")
        
        if not self.context.users:
            print("\n❌ No users available.")
            return
        
        # Login
        if not skip_login:
            await self.login_users()
        
        authenticated = [u for u in self.context.users if u.access_token]
        if not authenticated:
            print("\n⚠️ No authenticated users. Trying to create new users...")
            await self.create_users(3)
            await self.login_users()
            authenticated = [u for u in self.context.users if u.access_token]
        
        if not authenticated:
            print("\n❌ No authenticated users available")
            return
        
        self.test_user = authenticated[0]
        print(f"\n👤 Primary user: {self.test_user.username} (ID: {self.test_user.id})")
        print(f"   Roles: {', '.join(self.test_user.roles)}")
        
        # Provider users for staff rules
        providers = [u for u in authenticated if u.user_data.get('app_user_type') == 'provider']
        if not providers:
            providers = authenticated[:3] if len(authenticated) >= 3 else authenticated
        
        print("\n" + "="*60)
        print("🧪 Creating Test Data")
        print("="*60)
        
        # 1. Create organisations (3 per user)
        orgs = await self.create_organisations(self.test_user, count=3)
        
        # 2. Create suppliers (3 per organisation)
        suppliers = await self.create_suppliers(self.test_user, orgs, count_per_org=3)
        
        # 3. Create products (5 per supplier)
        products = await self.create_products(self.test_user, suppliers, count_per_supplier=5)
        
        # 4. Create staff rules (2 per supplier)
        if len(providers) > 1:
            rules = await self.create_staff_rules(self.test_user, suppliers, providers[:3], rules_per_supplier=2)
        
        # 5. Create invoices (3 per supplier)
        if suppliers:
            invoices = await self.create_invoices(self.test_user, suppliers, count=3)
        
        # 6. Create orders (3 per supplier)
        if suppliers:
            orders = await self.create_orders(self.test_user, suppliers, count=3)
        
        # 7. Create deliveries (2 per order)
        if self.context.created_orders:
            deliveries = await self.create_deliveries(self.test_user, self.context.created_orders, count=2)
        
        # Save
        self.context.save(context_file)
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        
        print(f"\n📈 Generated Data:")
        print(f"   👤 Users: {self.stats['users']}")
        print(f"   🔐 Authenticated: {len([u for u in self.context.users if u.access_token])}")
        print(f"   🏢 Organisations: {self.stats['organisations']}")
        print(f"   🏥 Suppliers: {self.stats['suppliers']}")
        print(f"   📦 Products: {self.stats['products']}")
        print(f"   👥 Staff Rules: {self.stats['staff_rules']}")
        print(f"   📄 Invoices: {self.stats['invoices']}")
        print(f"   📋 Orders: {self.stats['orders']}")
        print(f"   🚚 Deliveries: {self.stats['deliveries']}")
        
        print(f"\n📊 Distribution:")
        print(f"   Users with Orgs: {len(self.context.user_org_mapping)}")
        print(f"   Users with Suppliers: {len(self.context.user_supplier_mapping)}")
        print(f"   Staff Assignments: {len(self._used_assignments)}")
        
        # Role distribution
        if self.context.user_roles:
            role_counts = {}
            for roles in self.context.user_roles.values():
                for role in roles:
                    role_counts[role] = role_counts.get(role, 0) + 1
            print(f"\n👤 Role Distribution:")
            for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {role}: {count}")
        
        print("\n" + "="*60)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gluttex API Test Runner - Comprehensive")
    parser.add_argument("--url", default="http://localhost:9000")
    parser.add_argument("--skip-users", action="store_true")
    parser.add_argument("--skip-login", action="store_true")
    parser.add_argument("--context-file", default="test_context.json")
    parser.add_argument("--clear-context", action="store_true")
    
    args = parser.parse_args()
    
    if args.clear_context and Path(args.context_file).exists():
        Path(args.context_file).unlink()
        print(f"🗑️ Cleared context")
    
    async with TestRunner(args.url) as runner:
        await runner.run(
            skip_users=args.skip_users,
            skip_login=args.skip_login,
            context_file=args.context_file
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)