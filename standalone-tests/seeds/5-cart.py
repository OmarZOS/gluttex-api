#!/usr/bin/env python3
"""
Test script for Cart endpoints (creation, retrieval, update, deletion).
Run with: python test_cart_endpoints.py

This test script loads context from test_context.json (created by test_runner.py)
to get authentication tokens and existing data.
"""

import asyncio
import httpx
import json
import sys
import uuid
import random
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# ============================================================================
# PYDANTIC MODELS FOR TEST DATA
# ============================================================================

class CartStatus(str, Enum):
    """Cart status enum matching database exactly"""
    OPEN = 'open'
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    PARTIAL = 'partial'
    CHECKOUT = 'checkout'
    ABANDONED = 'abandoned'
    
    @classmethod
    def get_valid_statuses(cls) -> List[str]:
        return [status.value for status in cls]
    
    @classmethod
    def get_random(cls) -> str:
        return random.choice(cls.get_valid_statuses())


class DeliveryShippingMethod(str, Enum):
    """Delivery shipping methods"""
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    PICKUP = "pickup"
    COURIER = "courier"
    SAME_DAY = "same_day"
    INTERNATIONAL = "international"
    
    @classmethod
    def get_random(cls) -> str:
        return random.choice([m.value for m in cls])


class DeliveryStatus(str, Enum):
    """Delivery status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETURNED = "returned"
    REFUNDED = "refunded"
    
    @classmethod
    def get_random(cls) -> str:
        return random.choice([s.value for s in cls])


# ============================================================================
# TEST DATA MODELS WITH VALIDATION
# ============================================================================

class OrderedItemTest(BaseModel):
    """Ordered item test data model with validation"""
    ordered_product_id: int = Field(..., gt=0, description="Product ID")
    ordered_quantity: int = Field(default=1, gt=0, le=100, description="Quantity ordered")
    applied_vat: float = Field(default=0.0, ge=0, le=100, description="VAT percentage")
    product_discount: float = Field(default=0.0, ge=0, le=100, description="Discount percentage")
    
    @field_validator('ordered_quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is positive and within limits"""
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 100:
            raise ValueError('Quantity cannot exceed 100')
        return v
    
    @field_validator('applied_vat', 'product_discount')
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage values are between 0 and 100"""
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v


class OrderedServiceTest(BaseModel):
    """Ordered service test data model with validation"""
    ordered_service_service_id: int = Field(..., gt=0, description="Service ID")
    ordered_service_quantity: int = Field(default=1, gt=0, le=50, description="Quantity")
    ordered_service_unit_price: float = Field(default=0.0, ge=0, description="Unit price")
    ordered_service_total_price: float = Field(default=0.0, ge=0, description="Total price")
    ordered_service_notes: Optional[str] = Field(default=None, max_length=500, description="Notes")
    ordered_service_scheduled_at: Optional[str] = Field(default=None, description="Scheduled datetime ISO format")
    
    @field_validator('ordered_service_quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        if v > 50:
            raise ValueError('Quantity cannot exceed 50')
        return v
    
    @field_validator('ordered_service_unit_price', 'ordered_service_total_price')
    @classmethod
    def validate_prices(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v
    
    @model_validator(mode='after')
    def validate_total_price(self) -> 'OrderedServiceTest':
        """Validate that total price equals unit price * quantity"""
        expected_total = self.ordered_service_unit_price * self.ordered_service_quantity
        if self.ordered_service_total_price > 0 and abs(self.ordered_service_total_price - expected_total) > 0.01:
            raise ValueError(
                f'Total price ({self.ordered_service_total_price}) does not match '
                f'unit price * quantity ({expected_total})'
            )
        return self


class CartTestData(BaseModel):
    """Cart test data model with validation"""
    cart_status: str = Field(default='open', description="Cart status")
    cart_total_amount: float = Field(default=0.0, ge=0, description="Total amount")
    cart_notes: Optional[str] = Field(default=None, max_length=65535, description="Notes")
    cart_due_date: Optional[str] = Field(default=None, description="Due date ISO format")
    
    @field_validator('cart_status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = CartStatus.get_valid_statuses()
        if v not in valid_statuses:
            raise ValueError(f'cart_status must be one of: {", ".join(valid_statuses)}')
        return v
    
    @field_validator('cart_total_amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v < 0:
            raise ValueError('cart_total_amount cannot be negative')
        return v
    
    @field_validator('cart_due_date')
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('cart_due_date must be a valid ISO date')
        return v


class DeliveryTestData(BaseModel):
    """Delivery test data model with validation"""
    delivery_address: str = Field(..., max_length=500, description="Delivery address")
    delivery_city: str = Field(..., max_length=100, description="City")
    delivery_postal_code: str = Field(..., max_length=20, description="Postal code")
    delivery_country: str = Field(..., max_length=100, description="Country")
    delivery_shipping_method: str = Field(default="standard", description="Shipping method")
    delivery_fee: float = Field(default=0.0, ge=0, description="Delivery fee")
    delivery_special_instructions: Optional[str] = Field(default=None, max_length=500, description="Special instructions")
    delivery_status: str = Field(default="pending", description="Delivery status")
    
    @field_validator('delivery_shipping_method')
    @classmethod
    def validate_shipping_method(cls, v: str) -> str:
        valid_methods = [m.value for m in DeliveryShippingMethod]
        if v not in valid_methods:
            raise ValueError(f'Invalid shipping method. Must be one of: {", ".join(valid_methods)}')
        return v
    
    @field_validator('delivery_status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = [s.value for s in DeliveryStatus]
        if v not in valid_statuses:
            raise ValueError(f'Invalid delivery status. Must be one of: {", ".join(valid_statuses)}')
        return v
    
    @field_validator('delivery_fee')
    @classmethod
    def validate_fee(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Delivery fee cannot be negative')
        return v


class PersonTestData(BaseModel):
    """Person test data model with validation"""
    id_person: int = Field(default=0, ge=0, description="Person ID")
    person_first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    person_last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    person_phone: Optional[str] = Field(default=None, max_length=20, description="Phone number")
    
    @field_validator('person_phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Basic phone validation - can be customized
            import re
            if not re.match(r'^\+?[\d\s\-()]+$', v):
                raise ValueError('Invalid phone number format')
        return v


class CreateCartRequest(BaseModel):
    """Complete cart creation request with validation"""
    provider_id: int = Field(..., gt=0, description="Provider ID")
    seller_user_id: int = Field(..., gt=0, description="Seller user ID")
    buyer_user_id: int = Field(..., gt=0, description="Buyer user ID")
    cart: CartTestData = Field(..., description="Cart data")
    ordered_items: List[OrderedItemTest] = Field(default_factory=list, description="Ordered items")
    ordered_services: List[OrderedServiceTest] = Field(default_factory=list, description="Ordered services")
    delivery: Optional[DeliveryTestData] = Field(default=None, description="Delivery data")
    client: Optional[PersonTestData] = Field(default=None, description="Client person data")
    
    @model_validator(mode='after')
    def validate_items_or_services(self) -> 'CreateCartRequest':
        """Validate that at least one item or service is provided"""
        if not self.ordered_items and not self.ordered_services:
            raise ValueError('At least one ordered item or service must be provided')
        return self
    
    @model_validator(mode='after')
    def validate_buyer_seller_match(self) -> 'CreateCartRequest':
        """Validate seller and buyer are different or same as needed"""
        # This is optional - you might want to allow buyer == seller
        # For now, just a warning
        if self.buyer_user_id == self.seller_user_id:
            # This is allowed, just note it
            pass
        return self


# ============================================================================
# DATA GENERATORS (Updated to use Pydantic models)
# ============================================================================

def generate_cart_data(
    provider_id: int = 0,
    seller_user_id: int = 0,
    buyer_user_id: int = 0
) -> Dict[str, Any]:
    """Generate random cart data with validation"""
    
    notes = [
        "Regular order",
        "Urgent delivery needed",
        "Special instructions for delivery",
        "Handle with care",
        "Fragile items included",
        "Please call before delivery"
    ]
    
    data = {
        "cart_status": CartStatus.get_random(),
        "cart_total_amount": round(random.uniform(10, 500), 2),
        "cart_notes": random.choice(notes),
        "cart_due_date": (datetime.now() + timedelta(days=random.randint(1, 30))).date().isoformat()
    }
    
    # Validate with Pydantic
    try:
        CartTestData(**data)
    except Exception as e:
        # Fallback to open status if validation fails
        data["cart_status"] = "open"
    
    return data


def generate_ordered_item(
    product_id: int = 0,
    quantity: int = 1
) -> Dict[str, Any]:
    """Generate ordered item data with validation"""
    
    data = {
        "ordered_product_id": product_id,
        "ordered_quantity": quantity,
        "applied_vat": random.choice([0.19, 0.10, 0.07, 0.0]),
        "product_discount": 0.0
    }
    
    # Validate with Pydantic
    try:
        OrderedItemTest(**data)
    except Exception as e:
        print(f"⚠️ Ordered item validation warning: {e}")
        # Use safe defaults
        data["ordered_quantity"] = max(1, min(quantity, 100))
        data["applied_vat"] = 0.0
        data["product_discount"] = 0.0
    
    return data


def generate_ordered_service(
    service_id: int = 0,
    quantity: int = 1
) -> Dict[str, Any]:
    """Generate ordered service data with validation"""
    
    unit_price = round(random.uniform(10, 200), 2)
    total_price = round(unit_price * quantity, 2)
    
    data = {
        "ordered_service_service_id": service_id,
        "ordered_service_quantity": quantity,
        "ordered_service_unit_price": unit_price,
        "ordered_service_total_price": total_price,
        "ordered_service_notes": f"Service order - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "ordered_service_scheduled_at": (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat()
    }
    
    # Validate with Pydantic
    try:
        OrderedServiceTest(**data)
    except Exception as e:
        print(f"⚠️ Ordered service validation warning: {e}")
        # Use safe defaults
        data["ordered_service_quantity"] = max(1, min(quantity, 50))
        data["ordered_service_unit_price"] = round(random.uniform(10, 100), 2)
        data["ordered_service_total_price"] = data["ordered_service_unit_price"] * data["ordered_service_quantity"]
        data["ordered_service_scheduled_at"] = None
    
    return data


def generate_delivery_data() -> Dict[str, Any]:
    """Generate delivery data with validation"""
    
    cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida"]
    
    data = {
        "delivery_address": f"{random.randint(1, 999)} Main St",
        "delivery_city": random.choice(cities),
        "delivery_postal_code": f"{random.randint(10000, 99999)}",
        "delivery_country": "Algeria",
        "delivery_shipping_method": DeliveryShippingMethod.get_random(),
        "delivery_fee": round(random.uniform(5.0, 50.0), 2),
        "delivery_special_instructions": f"Test delivery {uuid.uuid4().hex[:6]}",
        "delivery_status": DeliveryStatus.get_random()
    }
    
    # Validate with Pydantic
    try:
        DeliveryTestData(**data)
    except Exception as e:
        print(f"⚠️ Delivery validation warning: {e}")
        # Use safe defaults
        data["delivery_shipping_method"] = "standard"
        data["delivery_status"] = "pending"
        data["delivery_fee"] = 10.0
    
    return data


def generate_person_data() -> Dict[str, Any]:
    """Generate person data with validation"""
    
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    
    data = {
        "id_person": 0,
        "person_first_name": random.choice(first_names),
        "person_last_name": random.choice(last_names),
        "person_phone": f"+213-5{random.randint(10, 99)}{random.randint(10, 99)}{random.randint(10, 99)}"
    }
    
    # Validate with Pydantic
    try:
        PersonTestData(**data)
    except Exception as e:
        print(f"⚠️ Person data validation warning: {e}")
        data["person_phone"] = None
    
    return data


def generate_create_cart_request(
    provider_id: int,
    seller_user_id: int,
    product_id: int = 0,
    service_id: int = 0,
    include_delivery: bool = False,
    include_client: bool = False
) -> Dict[str, Any]:
    """Generate a complete cart creation request with validation"""
    
    request_data = {
        "provider_id": provider_id,
        "seller_user_id": seller_user_id,
        "buyer_user_id": seller_user_id,
        "cart": generate_cart_data(provider_id, seller_user_id),
        "ordered_items": [],
        "ordered_services": [],
        "delivery": None,
        "client": None
    }
    
    if product_id > 0:
        request_data["ordered_items"].append(generate_ordered_item(product_id, random.randint(1, 3)))
    
    if service_id > 0:
        request_data["ordered_services"].append(generate_ordered_service(service_id, random.randint(1, 2)))
    
    if include_delivery:
        request_data["delivery"] = generate_delivery_data()
    
    if include_client:
        request_data["client"] = generate_person_data()
    
    # Validate with Pydantic
    try:
        CreateCartRequest(**request_data)
    except Exception as e:
        print(f"⚠️ Create cart request validation warning: {e}")
        # Ensure at least one item
        if not request_data["ordered_items"] and not request_data["ordered_services"]:
            request_data["ordered_items"].append(generate_ordered_item(1, 1))
    
    return request_data


# ============================================================================
# TEST CONTEXT AND RUNNER (Rest remains similar but with improved validation)
# ============================================================================

@dataclass
class TestResult:
    """Test result container"""
    name: str
    passed: bool
    details: str = ""
    response: Any = None
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class TestUser:
    """Test user with authentication data"""
    id: int = 0
    username: str = ""
    email: str = ""
    password: str = ""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    def is_token_valid(self) -> bool:
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now() < self.token_expires_at


@dataclass
class TestContext:
    """Test context containing all fetched data"""
    users: List[TestUser] = field(default_factory=list)
    categories: List[Dict[str, Any]] = field(default_factory=list)
    providers: List[Dict[str, Any]] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    created_carts: List[Dict[str, Any]] = field(default_factory=list)
    created_products: List[int] = field(default_factory=list)
    created_suppliers: List[int] = field(default_factory=list)
    auth_token: Optional[str] = None
    
    @property
    def provider_ids(self) -> List[int]:
        ids = []
        for p in self.providers:
            pid = p.get('id_product_provider')
            if pid is None:
                pid = p.get('id')
            if pid and isinstance(pid, int) and pid > 0:
                ids.append(pid)
        return ids
    
    @property
    def product_ids(self) -> List[int]:
        ids = []
        for p in self.products:
            pid = p.get('id_product')
            if pid is None:
                pid = p.get('id')
            if pid and isinstance(pid, int) and pid > 0:
                ids.append(pid)
        return ids
    
    @property
    def service_ids(self) -> List[int]:
        ids = []
        for s in self.services:
            sid = s.get('provided_service_id')
            if sid is None:
                sid = s.get('id')
            if sid and isinstance(sid, int) and sid > 0:
                ids.append(sid)
        return ids
    
    @property
    def cart_ids(self) -> List[int]:
        ids = []
        for c in self.created_carts:
            cid = c.get('cart_id')
            if cid is None:
                cid = c.get('id')
            if cid and isinstance(cid, int) and cid > 0:
                ids.append(cid)
        return ids
    
    def get_random_provider_id(self) -> int:
        if not self.provider_ids:
            return 1
        return random.choice(self.provider_ids)
    
    def get_random_product_id(self) -> int:
        if not self.product_ids:
            return 0
        return random.choice(self.product_ids)
    
    def get_random_service_id(self) -> int:
        if not self.service_ids:
            return 0
        return random.choice(self.service_ids)
    
    def get_random_cart_id(self) -> int:
        if not self.cart_ids:
            return 0
        return random.choice(self.cart_ids)
    
    def get_provider_with_products(self) -> Tuple[int, List[int]]:
        """Get a provider that has products"""
        for provider in self.providers:
            pid = provider.get('id_product_provider', provider.get('id', 0))
            if pid > 0:
                products_for_provider = [
                    p for p in self.products 
                    if p.get('product_provider_id') == pid or p.get('product_provider_id') == int(pid)
                ]
                if products_for_provider:
                    product_ids = [
                        p.get('id_product', p.get('id', 0)) 
                        for p in products_for_provider 
                        if p.get('id_product', p.get('id', 0)) > 0
                    ]
                    if product_ids:
                        return pid, product_ids
        return 0, []
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers from the first user with a valid token"""
        for user in self.users:
            if user.is_token_valid():
                return {"Authorization": f"Bearer {user.access_token}"}
        
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        
        return {}
    
    def get_first_valid_token(self) -> Optional[str]:
        """Get the first valid access token"""
        for user in self.users:
            if user.is_token_valid():
                return user.access_token
        return self.auth_token
    
    def load_from_file(self, filename: str = "test_context.json") -> bool:
        """Load context from the main test runner's context file"""
        if not Path(filename).exists():
            return False
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load users
        user_data = data.get('users', [])
        for u in user_data:
            user = TestUser(
                id=u.get('id', 0),
                username=u.get('username', ''),
                email=u.get('email', ''),
                password=u.get('password', ''),
                access_token=u.get('access_token'),
                refresh_token=u.get('refresh_token')
            )
            expires_at = u.get('token_expires_at')
            if expires_at:
                try:
                    user.token_expires_at = datetime.fromisoformat(expires_at)
                except:
                    pass
            self.users.append(user)
        
        # Load other data
        self.created_products = data.get('created_products', [])
        self.created_suppliers = data.get('created_suppliers', [])
        
        # Set auth token from first user with token
        token = self.get_first_valid_token()
        if token:
            self.auth_token = token
        
        return True


# ============================================================================
# TEST RUNNER (Simplified - Only showing the key methods)
# ============================================================================

class CartTester:
    """Test runner for cart endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client: Optional[httpx.AsyncClient] = None
        self.context = TestContext()
        self.results: List[TestResult] = []
        self.context_file = "test_context.json"
        self.test_provider_id = 0
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    # ==================== HTTP Helpers ====================
    
    async def _get(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.get(
                f"{self.base_url}{path}", 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _post(self, path: str, json_data: Dict) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.post(
                f"{self.base_url}{path}", 
                json=json_data,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _patch(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.patch(
                f"{self.base_url}{path}", 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def _delete(self, path: str, params: Optional[Dict] = None) -> Tuple[int, Any]:
        try:
            headers = self.context.get_auth_headers()
            response = await self.client.delete(
                f"{self.base_url}{path}", 
                params=params,
                headers=headers
            )
            data = response.json() if response.text else None
            return response.status_code, data
        except Exception as e:
            return 500, {"error": str(e)}
    
    # ==================== Context Loading ====================
    
    async def load_context(self) -> bool:
        """Load context from file"""
        loaded = self.context.load_from_file(self.context_file)
        if loaded:
            print(f"\n📂 Loaded context from {self.context_file}")
            print(f"   👤 Users: {len(self.context.users)}")
            print(f"   🏥 Suppliers: {len(self.context.created_suppliers)}")
            print(f"   📦 Products: {len(self.context.created_products)}")
            
            token = self.context.get_first_valid_token()
            if token:
                print(f"   🔐 Valid authentication token found")
            else:
                print(f"   ⚠️ No valid authentication token found")
        return loaded
    
    async def fetch_providers(self) -> bool:
        """Fetch providers/suppliers"""
        print("\n📋 Fetching providers...")
        status, data = await self._get("/api/v1/suppliers", {"offset": 0, "limit": 100})
        
        if status != 200:
            print(f"   ❌ Failed to fetch providers: {status}")
            return False
        
        if isinstance(data, list):
            self.context.providers = data
        elif isinstance(data, dict):
            self.context.providers = data.get("data", data.get("items", []))
        else:
            self.context.providers = []
        
        print(f"   ✅ Found {len(self.context.providers)} providers")
        for prov in self.context.providers[:3]:
            pid = prov.get('id_product_provider', prov.get('id', 'N/A'))
            name = prov.get('provider_name', prov.get('name', 'Unknown'))
            print(f"      - ID: {pid}, Name: {name}")
        
        return True
    
    async def fetch_products(self, provider_id: int) -> bool:
        """Fetch products for a provider"""
        print(f"\n📋 Fetching products for provider {provider_id}...")
        
        user_id = self.context.users[0].id if self.context.users else 0
        
        status, data = await self._get(
            f"/api/v1/products/{user_id}/{provider_id}/0/0/50",
            {}
        )
        
        if status != 200:
            print(f"   ❌ Failed to fetch products: {status}")
            return False
        
        if isinstance(data, list):
            self.context.products = data
        elif isinstance(data, dict):
            self.context.products = data.get("data", data.get("items", []))
        else:
            self.context.products = []
        
        print(f"   ✅ Found {len(self.context.products)} products")
        for prod in self.context.products[:3]:
            pid = prod.get('id_product', prod.get('id', 'N/A'))
            name = prod.get('product_name', 'Unknown')
            qty = prod.get('product_quantity', 0)
            print(f"      - ID: {pid}, Name: {name}, Qty: {qty}")
        
        return True
    
    async def fetch_services(self, provider_id: int) -> bool:
        """Fetch services for a provider"""
        print(f"\n📋 Fetching services for provider {provider_id}...")
        
        status, data = await self._get(
            f"/api/v1/business/services/provider/{provider_id}",
            {"offset": 0, "limit": 50, "active_only": True}
        )
        
        if status != 200:
            print(f"   ❌ Failed to fetch services: {status}")
            return False
        
        if isinstance(data, list):
            self.context.services = data
        elif isinstance(data, dict):
            self.context.services = data.get("data", data.get("items", []))
        else:
            self.context.services = []
        
        print(f"   ✅ Found {len(self.context.services)} services")
        for service in self.context.services[:3]:
            sid = service.get('provided_service_id', service.get('id', 'N/A'))
            name = service.get('provided_service_name', 'Unknown')
            is_active = service.get('provided_service_is_active', False)
            print(f"      - ID: {sid}, Name: {name}, Active: {is_active}")
        
        return True
    
    async def fetch_all_data(self) -> bool:
        """Fetch all required data"""
        print("\n" + "="*50)
        print("📊 FETCHING EXISTING DATA")
        print("="*50)
        
        prov_ok = await self.fetch_providers()
        
        if not prov_ok or not self.context.provider_ids:
            print("\n⚠️  No providers found! Please seed providers first.")
            print("   Using fallback provider ID: 1")
            self.context.providers = [{"id_product_provider": 1, "provider_name": "Fallback Provider"}]
        
        self.test_provider_id = self.context.get_random_provider_id()
        
        provider_with_products, _ = self.context.get_provider_with_products()
        if provider_with_products > 0:
            self.test_provider_id = provider_with_products
        
        if self.test_provider_id:
            await self.fetch_products(self.test_provider_id)
            await self.fetch_services(self.test_provider_id)
        
        if not self.context.product_ids:
            print(f"\n⚠️  No products found for provider {self.test_provider_id}. Trying all providers...")
            for provider in self.context.providers:
                pid = provider.get('id_product_provider', provider.get('id', 0))
                if pid > 0:
                    await self.fetch_products(pid)
                    if self.context.product_ids:
                        self.test_provider_id = pid
                        break
        
        return True
    
    # ==================== Test Methods ====================
    
    def _add_result(self, name: str, passed: bool, details: str = "", response: Any = None):
        result = TestResult(name=name, passed=passed, details=details, response=response)
        self.results.append(result)
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"     {details}")
    
    def _extract_cart_id(self, data: Dict) -> int:
        """Extract cart ID from response data"""
        if not data:
            return 0
        
        if 'data' in data and isinstance(data['data'], dict):
            return data['data'].get('cart_id', 0)
        
        for key in ['cart_id', 'id', 'id_cart']:
            if key in data:
                return data[key]
        
        return 0
    
    def _extract_response_data(self, data: Dict) -> Dict:
        """Extract data from response wrapper"""
        if not data:
            return {}
        
        if 'data' in data and isinstance(data['data'], dict):
            return data['data']
        
        return data
    
    # ==================== Test Cases ====================
    
    async def test_create_cart_with_product(self) -> bool:
        """Test creating a cart with a product"""
        print("\n📦 Test: Create Cart with Product")
        
        # Find a provider with products
        provider_id, product_ids = self.context.get_provider_with_products()
        
        if not provider_id or not product_ids:
            provider_id = self.test_provider_id
            product_ids = self.context.product_ids
            if not product_ids:
                self._add_result("Create Cart with Product", False, "No product ID available")
                return False
        
        product_id = random.choice(product_ids) if product_ids else 0
        if not product_id:
            self._add_result("Create Cart with Product", False, "No product ID available")
            return False
        
        seller_id = self.context.users[0].id if self.context.users else 0
        if not seller_id:
            self._add_result("Create Cart with Product", False, "No seller ID available")
            return False
        
        # Generate validated request data
        request_data = generate_create_cart_request(
            provider_id=provider_id,
            seller_user_id=seller_id,
            product_id=product_id,
            service_id=0,
            include_delivery=False,
            include_client=False
        )
        
        # Validate request with Pydantic
        try:
            validated_request = CreateCartRequest(**request_data)
            request_data = validated_request.model_dump()
        except Exception as e:
            self._add_result("Create Cart with Product", False, f"Request validation failed: {e}")
            return False
        
        print(f"   Provider: {provider_id}, Seller: {seller_id}")
        print(f"   Product: {product_id}, Qty: {request_data['ordered_items'][0]['ordered_quantity']}")
        
        status, data = await self._post("/api/v1/business/carts", request_data)
        
        passed = status == 201
        if passed and data:
            cart_data_response = self._extract_response_data(data)
            cart_id = cart_data_response.get('cart_id', 0)
            if cart_id:
                self.context.created_carts.append(cart_data_response)
                details = f"Cart {cart_id} created"
            else:
                details = "Cart created but ID extraction failed"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Cart with Product", passed, details)
        return passed
    
    async def test_create_cart_with_service(self) -> bool:
        """Test creating a cart with a service"""
        print("\n📦 Test: Create Cart with Service")
        
        provider_id = self.test_provider_id or self.context.get_random_provider_id()
        service_id = self.context.get_random_service_id()
        
        if not provider_id:
            self._add_result("Create Cart with Service", False, "No provider ID available")
            return False
        
        if not service_id:
            self._add_result("Create Cart with Service", False, "No service ID available")
            return False
        
        seller_id = self.context.users[0].id if self.context.users else 0
        if not seller_id:
            self._add_result("Create Cart with Service", False, "No seller ID available")
            return False
        
        # Generate validated request data
        request_data = generate_create_cart_request(
            provider_id=provider_id,
            seller_user_id=seller_id,
            product_id=0,
            service_id=service_id,
            include_delivery=False,
            include_client=False
        )
        
        # Validate request with Pydantic
        try:
            validated_request = CreateCartRequest(**request_data)
            request_data = validated_request.model_dump()
        except Exception as e:
            self._add_result("Create Cart with Service", False, f"Request validation failed: {e}")
            return False
        
        print(f"   Provider: {provider_id}, Seller: {seller_id}")
        print(f"   Service: {service_id}, Qty: {request_data['ordered_services'][0]['ordered_service_quantity']}")
        
        status, data = await self._post("/api/v1/business/carts", request_data)
        
        passed = status == 201
        if passed and data:
            cart_data_response = self._extract_response_data(data)
            cart_id = cart_data_response.get('cart_id', 0)
            if cart_id:
                self.context.created_carts.append(cart_data_response)
                details = f"Cart {cart_id} created"
            else:
                details = "Cart created but ID extraction failed"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Cart with Service", passed, details)
        return passed
    
    async def test_create_cart_with_both(self) -> bool:
        """Test creating a cart with both product and service"""
        print("\n📦 Test: Create Cart with Product and Service")
        
        provider_id, product_ids = self.context.get_provider_with_products()
        if not provider_id or not product_ids:
            provider_id = self.test_provider_id
            product_ids = self.context.product_ids
        
        product_id = random.choice(product_ids) if product_ids else 0
        service_id = self.context.get_random_service_id()
        
        if not provider_id:
            self._add_result("Create Cart with Both", False, "No provider ID available")
            return False
        
        if not product_id or not service_id:
            self._add_result("Create Cart with Both", False, "Product or Service ID missing")
            return False
        
        seller_id = self.context.users[0].id if self.context.users else 0
        if not seller_id:
            self._add_result("Create Cart with Both", False, "No seller ID available")
            return False
        
        # Generate validated request data
        request_data = generate_create_cart_request(
            provider_id=provider_id,
            seller_user_id=seller_id,
            product_id=product_id,
            service_id=service_id,
            include_delivery=False,
            include_client=False
        )
        
        # Validate request with Pydantic
        try:
            validated_request = CreateCartRequest(**request_data)
            request_data = validated_request.model_dump()
        except Exception as e:
            self._add_result("Create Cart with Both", False, f"Request validation failed: {e}")
            return False
        
        print(f"   Product: {product_id}, Service: {service_id}")
        
        status, data = await self._post("/api/v1/business/carts", request_data)
        
        passed = status == 201
        if passed and data:
            cart_data_response = self._extract_response_data(data)
            cart_id = cart_data_response.get('cart_id', 0)
            if cart_id:
                self.context.created_carts.append(cart_data_response)
                details = f"Cart {cart_id} created"
            else:
                details = "Cart created but ID extraction failed"
        else:
            details = f"Status: {status}"
            if data and isinstance(data, dict):
                details += f" - {data.get('message', data.get('detail', ''))}"
        
        self._add_result("Create Cart with Both", passed, details)
        return passed
    
    # ==================== Main Runner ====================
    
    async def run_all_tests(self) -> None:
        """Run all test suites"""
        print("\n" + "="*70)
        print("🚀 CART ENDPOINT TESTS (with Pydantic Validation)")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Load context from main test runner
        await self.load_context()
        
        # Fetch data
        if not await self.fetch_all_data():
            print("\n⚠️  Failed to fetch required data. Some tests may fail.")
        
        # Check authentication
        if not self.context.get_auth_headers():
            print("\n⚠️  No authentication headers available. Tests may fail with 401.")
            print("   Run test_runner.py first to get authentication tokens.")
        
        print("\n" + "="*70)
        print("📝 RUNNING TESTS WITH VALIDATION")
        print("="*70)
        
        # Creation tests
        await self.test_create_cart_with_product()
        await self.test_create_cart_with_service()
        await self.test_create_cart_with_both()
        
        self._print_summary()
    
    def _print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"  {status} {result.name}")
            if result.details:
                print(f"     {result.details}")
        
        print("="*70)
        print(f"📈 Total: {total} tests | ✅ Passed: {passed} | ❌ Failed: {failed}")
        print(f"🛒 Carts Created: {len(self.context.created_carts)}")
        print(f"📦 Products Found: {len(self.context.products)}")
        print(f"📋 Services Found: {len(self.context.services)}")
        print(f"🏥 Providers Found: {len(self.context.providers)}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed.")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test cart endpoints with validation")
    parser.add_argument(
        "--url",
        default="http://localhost:9000",
        help="Base URL of the API server (default: http://localhost:9000)"
    )
    parser.add_argument(
        "--provider-id",
        type=int,
        help="Use specific provider ID for all tests"
    )
    parser.add_argument(
        "--context-file",
        default="test_context.json",
        help="Context file to load (default: test_context.json)"
    )
    
    args = parser.parse_args()
    
    async with CartTester(args.url) as tester:
        tester.context_file = args.context_file
        
        if args.provider_id:
            tester.test_provider_id = args.provider_id
            tester.context.providers = [{"id_product_provider": args.provider_id, "provider_name": "Custom"}]
        
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)