#!/usr/bin/env python3
"""
Bulk Data Creator for Gluttex - Creates Carts and Processes Payments
Run with: python bulk_data_creator.py

This script:
1. Fetches existing products, services, and providers
2. Creates carts with products and services
3. Processes payments for carts using their invoices
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
import time
import argparse


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
    wallet_id: Optional[int] = None
    person_id: Optional[int] = None


@dataclass
class BulkContext:
    users: List[TestUser] = field(default_factory=list)
    products: List[Dict[str, Any]] = field(default_factory=list)
    services: List[Dict[str, Any]] = field(default_factory=list)
    providers: List[Dict[str, Any]] = field(default_factory=list)
    created_carts: List[int] = field(default_factory=list)
    created_invoices: List[int] = field(default_factory=list)
    created_payments: List[int] = field(default_factory=list)
    auth_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    @property
    def product_ids(self) -> List[int]:
        ids = []
        for p in self.products:
            pid = p.get('id_product') or p.get('id')
            if pid and isinstance(pid, int) and pid > 0:
                ids.append(pid)
        return ids
    
    @property
    def service_ids(self) -> List[int]:
        ids = []
        for s in self.services:
            sid = s.get('provided_service_id') or s.get('id')
            if sid and isinstance(sid, int) and sid > 0:
                ids.append(sid)
        return ids
    
    @property
    def provider_ids(self) -> List[int]:
        ids = []
        for p in self.providers:
            pid = p.get('id_product_provider') or p.get('id')
            if pid and isinstance(pid, int) and pid > 0:
                ids.append(pid)
        return ids
    
    def is_token_valid(self) -> bool:
        if not self.auth_token:
            return False
        if not self.token_expires_at:
            return True
        return datetime.now() < self.token_expires_at


# ============================================================================
# TEST CONTEXT LOADER
# ============================================================================

def load_context(context_file: str = "test_context.json") -> BulkContext:
    context = BulkContext()
    
    if not Path(context_file).exists():
        print(f"⚠️ Context file {context_file} not found")
        return context
    
    with open(context_file, 'r') as f:
        data = json.load(f)
    
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
        context.users.append(user)
    
    for user in context.users:
        if user.access_token:
            context.auth_token = user.access_token
            context.token_expires_at = user.token_expires_at
            break
    
    print(f"📂 Loaded context from {context_file}")
    print(f"   👤 Users: {len(context.users)}")
    
    if context.auth_token:
        if context.is_token_valid():
            print(f"   🔐 Token valid until: {context.token_expires_at}")
        else:
            print(f"   ⚠️ Token expired at: {context.token_expires_at}")
    
    return context


# ============================================================================
# DATA GENERATORS
# ============================================================================

def generate_cart_data(provider_id: int, seller_id: int, product_ids: List[int], service_ids: List[int]) -> Dict[str, Any]:
    cart_data = {
        "provider_id": provider_id,
        "seller_user_id": seller_id,
        "buyer_user_id": seller_id,
        "cart": {
            "cart_status": "open",
            "cart_total_amount": 0,
            "cart_notes": f"Bulk cart - {datetime.now().isoformat()}",
            "cart_due_date": (datetime.now() + timedelta(days=30)).date().isoformat()
        },
        "ordered_items": [],
        "ordered_services": [],
        "delivery": None,
        "client": None
    }
    
    if product_ids:
        num_products = random.randint(1, min(3, len(product_ids)))
        selected_products = random.sample(product_ids, num_products)
        
        for product_id in selected_products:
            cart_data["ordered_items"].append({
                "ordered_product_id": product_id,
                "ordered_quantity": random.randint(1, 3),
                "unit_price": round(random.uniform(5, 100), 2),
                "applied_vat": round(random.uniform(0, 19), 2),
                "product_discount": round(random.uniform(0, 10), 2)
            })
    
    if service_ids:
        num_services = random.randint(0, min(2, len(service_ids)))
        selected_services = random.sample(service_ids, num_services) if num_services > 0 else []
        
        for service_id in selected_services:
            unit_price = round(random.uniform(50, 300), 2)
            quantity = random.randint(1, 2)
            cart_data["ordered_services"].append({
                "ordered_service_service_id": service_id,
                "ordered_service_quantity": quantity,
                "ordered_service_unit_price": unit_price,
                "ordered_service_total_price": unit_price * quantity,
                "ordered_service_notes": f"Bulk service - {uuid.uuid4().hex[:6]}",
                "ordered_service_scheduled_at": (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat()
            })
    
    if random.random() > 0.5:
        cities = ["Algiers", "Oran", "Constantine", "Annaba", "Blida"]
        streets = ["Main St", "Rue Didouche Mourad", "Avenue du 1er Novembre"]
        cart_data["delivery"] = {
            "delivery_address": f"{random.randint(1, 999)} {random.choice(streets)}",
            "delivery_city": random.choice(cities),
            "delivery_postal_code": f"{random.randint(10000, 99999)}",
            "delivery_country": "Algeria",
            "delivery_shipping_method": random.choice(["standard", "express", "same_day"]),
            "delivery_fee": round(random.uniform(5, 50), 2),
            "delivery_special_instructions": f"Bulk delivery {uuid.uuid4().hex[:4]}",
            "delivery_status": "pending"
        }
    
    return cart_data


def generate_payment_data(invoice_id: int, amount: float) -> Dict[str, Any]:
    methods = ["cash", "card", "bank_transfer", "mobile_money", "wallet"]
    return {
        "payment_invoice_id": invoice_id,
        "payment_amount": amount,
        "payment_method": random.choice(methods),
        "payment_status": "completed",
        "payment_reference": f"PAY-{uuid.uuid4().hex[:8].upper()}",
        "payment_notes": f"Bulk payment for invoice {invoice_id}",
        "payment_type": "payment"
    }


# ============================================================================
# BULK DATA CREATOR
# ============================================================================

class BulkDataCreator:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.client = None
        self.context = BulkContext()
        self.stats = {
            "carts_created": 0,
            "invoices_created": 0,
            "payments_created": 0,
            "errors": 0
        }
        self._token_refreshed = False
    
    async def __aenter__(self):
        limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
        timeout = httpx.Timeout(30.0, connect=5.0)
        self.client = httpx.AsyncClient(timeout=timeout, verify=False, limits=limits)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def get_auth_headers(self) -> Dict[str, str]:
        if self.context.auth_token:
            return {"Authorization": f"Bearer {self.context.auth_token}"}
        return {}
    
    def print_status(self, message: str, emoji: str = "ℹ️"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
    
    # ==================== Authentication ====================
    
    async def ensure_valid_token(self) -> bool:
        if self.context.is_token_valid():
            return True
        
        if self.context.users:
            for user in self.context.users:
                if user.username and user.password:
                    self.print_status(f"🔐 Token expired, logging in as {user.username}...", "🔐")
                    if await self.login_user(user.username, user.password):
                        self._token_refreshed = True
                        return True
        
        self.print_status("❌ No valid authentication token available", "❌")
        return False
    
    async def login_user(self, username: str, password: str) -> bool:
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/authentication/token",
                json={
                    "app_user_name": username,
                    "app_user_password": password
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                access_token = result.get('access_token')
                if access_token:
                    self.context.auth_token = access_token
                    expires_in = result.get('expires_in', 3600)
                    self.context.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                    
                    for user in self.context.users:
                        if user.username == username:
                            user.access_token = access_token
                            user.token_expires_at = self.context.token_expires_at
                            break
                    
                    self.print_status(f"✅ Login successful, token valid until {self.context.token_expires_at.strftime('%H:%M:%S')}", "✅")
                    return True
            else:
                self.print_status(f"❌ Login failed: {response.status_code}", "❌")
                return False
        except Exception as e:
            self.print_status(f"❌ Login error: {e}", "❌")
            return False
    
    # ==================== Fetch Existing Data ====================
    
    async def fetch_providers(self) -> bool:
        self.print_status("📋 Fetching providers...", "📋")
        
        if not await self.ensure_valid_token():
            return False
        
        headers = self.get_auth_headers()
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/suppliers",
                params={"offset": 0, "limit": 100},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.context.providers = data
                elif isinstance(data, dict):
                    self.context.providers = data.get("data", data.get("items", []))
                else:
                    self.context.providers = []
                
                self.print_status(f"✅ Found {len(self.context.providers)} providers", "✅")
                for prov in self.context.providers[:3]:
                    pid = prov.get('id_product_provider', prov.get('id', 'N/A'))
                    name = prov.get('provider_name', prov.get('name', 'Unknown'))
                    print(f"      - ID: {pid}, Name: {name}")
                return True
            else:
                self.print_status(f"❌ Failed to fetch providers: {response.status_code}", "❌")
                return False
        except Exception as e:
            self.print_status(f"❌ Error fetching providers: {e}", "❌")
            return False
    
    async def fetch_products(self, provider_id: int) -> bool:
        self.print_status(f"📦 Fetching products for provider {provider_id}...", "📦")
        
        if not await self.ensure_valid_token():
            return False
        
        headers = self.get_auth_headers()
        user_id = self.context.users[0].id if self.context.users else 0
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/products/{user_id}/{provider_id}/0/0/50",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.context.products = data
                elif isinstance(data, dict):
                    self.context.products = data.get("data", data.get("items", []))
                else:
                    self.context.products = []
                
                self.print_status(f"✅ Found {len(self.context.products)} products", "✅")
                for prod in self.context.products[:3]:
                    pid = prod.get('id_product', prod.get('id', 'N/A'))
                    name = prod.get('product_name', 'Unknown')
                    qty = prod.get('product_quantity', 0)
                    print(f"      - ID: {pid}, Name: {name}, Qty: {qty}")
                return True
            else:
                self.print_status(f"❌ Failed to fetch products: {response.status_code}", "❌")
                return False
        except Exception as e:
            self.print_status(f"❌ Error fetching products: {e}", "❌")
            return False
    
    async def fetch_services(self, provider_id: int) -> bool:
        self.print_status(f"📋 Fetching services for provider {provider_id}...", "📋")
        
        if not await self.ensure_valid_token():
            return False
        
        headers = self.get_auth_headers()
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/business/services/provider/{provider_id}",
                params={"offset": 0, "limit": 50, "active_only": True},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.context.services = data
                elif isinstance(data, dict):
                    self.context.services = data.get("data", data.get("items", []))
                else:
                    self.context.services = []
                
                self.print_status(f"✅ Found {len(self.context.services)} services", "✅")
                for service in self.context.services[:3]:
                    sid = service.get('provided_service_id', service.get('id', 'N/A'))
                    name = service.get('provided_service_name', 'Unknown')
                    is_active = service.get('provided_service_is_active', False)
                    print(f"      - ID: {sid}, Name: {name}, Active: {is_active}")
                return True
            else:
                self.print_status(f"❌ Failed to fetch services: {response.status_code}", "❌")
                return False
        except Exception as e:
            self.print_status(f"❌ Error fetching services: {e}", "❌")
            return False
    
    async def fetch_all_data(self) -> bool:
        print("\n" + "="*50)
        print("📊 FETCHING EXISTING DATA")
        print("="*50)
        
        if not await self.ensure_valid_token():
            self.print_status("❌ Cannot authenticate", "❌")
            return False
        
        if not await self.fetch_providers():
            self.print_status("⚠️ Failed to fetch providers", "⚠️")
            return False
        
        if not self.context.provider_ids:
            self.print_status("⚠️ No providers found", "⚠️")
            return False
        
        provider_id = self.context.provider_ids[0]
        self.print_status(f"Using provider ID: {provider_id}", "🏢")
        
        await self.fetch_products(provider_id)
        await self.fetch_services(provider_id)
        
        if not self.context.product_ids and not self.context.service_ids:
            self.print_status("⚠️ No products or services found", "⚠️")
            return False
        
        return True
    
    # ==================== Cart Creation ====================
    
    async def create_cart(self, provider_id: int, seller_id: int,
                          product_ids: List[int], service_ids: List[int]) -> Optional[Dict[str, Any]]:
        if not await self.ensure_valid_token():
            return None
        
        headers = self.get_auth_headers()
        
        cart_data = generate_cart_data(provider_id, seller_id, product_ids, service_ids)
        
        if not cart_data["ordered_items"] and not cart_data["ordered_services"]:
            return None
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/business/carts",
                json=cart_data,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                
                if 'data' in result:
                    cart_data_result = result['data']
                else:
                    cart_data_result = result
                
                cart_id = cart_data_result.get('cart_id', 0)
                invoice_id = cart_data_result.get('cart_invoice', 0)
                total_amount = cart_data_result.get('total_amount', 0)
                
                if cart_id:
                    self.stats["carts_created"] += 1
                    self.context.created_carts.append(cart_id)
                    
                    if invoice_id and invoice_id > 0:
                        self.stats["invoices_created"] += 1
                        self.context.created_invoices.append(invoice_id)
                        self.print_status(f"✅ Cart {cart_id} created with invoice {invoice_id}", "🛒")
                    else:
                        self.print_status(f"⚠️ Cart {cart_id} created but no invoice ID returned", "⚠️")
                    
                    return {
                        "cart_id": cart_id,
                        "invoice_id": invoice_id,
                        "total_amount": total_amount
                    }
            return None
        except Exception as e:
            self.print_status(f"❌ Error creating cart: {e}", "❌")
            return None
    
    async def create_carts_bulk(self, provider_id: int, seller_id: int,
                                product_ids: List[int], service_ids: List[int],
                                count: int = 10) -> List[Dict[str, Any]]:
        if not product_ids and not service_ids:
            self.print_status("⚠️ No products or services available for carts", "⚠️")
            return []
        
        self.print_status(f"🛒 Creating {count} carts...", "🛒")
        
        tasks = []
        for _ in range(count):
            task = self.create_cart(provider_id, seller_id, product_ids, service_ids)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        cart_details = []
        for result in results:
            if isinstance(result, dict) and result.get('cart_id'):
                cart_details.append(result)
            elif isinstance(result, Exception):
                self.stats["errors"] += 1
        
        self.print_status(f"✅ Created {len(cart_details)} carts", "✅")
        return cart_details
    
    # ==================== Payment Processing ====================
    
    async def get_cart_with_invoice(self, cart_id: int) -> Optional[Dict[str, Any]]:
        """Fetch cart details to get the invoice ID"""
        headers = self.get_auth_headers()
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/business/carts/{cart_id}?eager_load=true",
                headers=headers
            )
            
            if response.status_code == 200:
                cart_data = response.json()
                if 'data' in cart_data:
                    cart_data = cart_data['data']
                
                invoice_id = cart_data.get('cart_invoice', 0)
                total_amount = cart_data.get('total_amount', 0)
                status = cart_data.get('cart_status', 'open')
                
                return {
                    "cart_id": cart_id,
                    "invoice_id": invoice_id,
                    "total_amount": total_amount,
                    "status": status
                }
            return None
        except Exception as e:
            self.print_status(f"❌ Error fetching cart {cart_id}: {e}", "❌")
            return None
    
    async def process_cart_payment(self, cart_detail: Dict[str, Any]) -> bool:
        if not await self.ensure_valid_token():
            return False
        
        headers = self.get_auth_headers()
        cart_id = cart_detail.get('cart_id')
        invoice_id = cart_detail.get('invoice_id')
        total_amount = cart_detail.get('total_amount', 0)
        
        # If no invoice_id or total_amount is 0, fetch cart details
        if not invoice_id or invoice_id == 0 or total_amount == 0:
            self.print_status(f"🔍 Fetching cart {cart_id} details...", "🔍")
            cart_info = await self.get_cart_with_invoice(cart_id)
            
            if not cart_info:
                self.print_status(f"❌ Failed to fetch cart {cart_id}", "❌")
                return False
            
            invoice_id = cart_info.get('invoice_id', 0)
            total_amount = cart_info.get('total_amount', 0)
            
            if invoice_id and invoice_id > 0:
                self.print_status(f"✅ Found invoice {invoice_id} for cart {cart_id} (total: {total_amount})", "📄")
                if invoice_id not in self.context.created_invoices:
                    self.context.created_invoices.append(invoice_id)
            else:
                self.print_status(f"⚠️ Cart {cart_id} has no invoice", "⚠️")
                return False
        
        if not invoice_id or invoice_id == 0:
            self.print_status(f"⚠️ Cart {cart_id} has no invoice", "⚠️")
            return False
        
        if total_amount <= 0:
            self.print_status(f"⚠️ Cart {cart_id} has zero total amount ({total_amount})", "⚠️")
            return False
        
        try:
            # Create payment - CORRECT ENDPOINT AND DATA
            payment_methods = ["cash", "card", "bank_transfer", "mobile_money", "wallet"]
            payment_data = {
                "payment_invoice_id": invoice_id,
                "payment_amount": total_amount,
                "payment_method": random.choice(payment_methods),
                # "payment_status": "PAID",  # Set to completed directly
                "payment_reference": f"PAY-{uuid.uuid4().hex[:8].upper()}",
                "payment_notes": f"Bulk payment for invoice {invoice_id} from cart {cart_id}",
            }
            
            self.print_status(f"💳 Creating payment for invoice {invoice_id} (amount: {total_amount})", "💳")
            self.print_status(f"📝 Payment data: {json.dumps(payment_data, indent=2)}", "📝")
            
            # CORRECT ENDPOINT: /api/v1/business/payments (not /api/v1/finance/payments)
            payment_response = await self.client.post(
                f"{self.base_url}/api/v1/business/payments",
                json=payment_data,
                headers=headers
            )
            
            if payment_response.status_code == 201:
                payment_result = payment_response.json()
                payment_id = payment_result.get('payment_id', payment_result.get('id', 0))
                if payment_id:
                    self.stats["payments_created"] += 1
                    self.context.created_payments.append(payment_id)
                    self.print_status(f"✅ Payment {payment_id} created for invoice {invoice_id}", "💳")
                    return True
                else:
                    self.print_status(f"⚠️ Payment created but no ID returned", "⚠️")
                    return False
            else:
                error_msg = payment_response.text[:300] if payment_response.text else "No response"
                self.print_status(f"❌ Payment failed ({payment_response.status_code}): {error_msg}", "❌")
                return False
        except Exception as e:
            self.print_status(f"❌ Error processing payment: {e}", "❌")
            return False

    
    async def process_payments_bulk(self, cart_details: List[Dict[str, Any]]) -> int:
        if not cart_details:
            return 0
        
        self.print_status(f"💳 Processing payments for {len(cart_details)} carts...", "💳")
        
        tasks = []
        for cart_detail in cart_details:
            task = self.process_cart_payment(cart_detail)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in results if r is True)
        self.print_status(f"✅ Processed {successful} payments", "✅")
        return successful
    
    # ==================== Main Runner ====================
    
    async def run(self, context_file: str = "test_context.json",
                  carts: int = 10):
        print("\n" + "="*70)
        print("🚀 BULK DATA CREATOR - Carts & Payments (Using Existing Data)")
        print("="*70)
        print(f"📍 Base URL: {self.base_url}")
        print(f"🛒 Carts to create: {carts}")
        print("="*70)
        
        self.context = load_context(context_file)
        
        if not await self.ensure_valid_token():
            self.print_status("❌ No authentication token available", "❌")
            return
        
        if not await self.fetch_all_data():
            self.print_status("❌ Failed to fetch required data", "❌")
            return
        
        start_time = time.time()
        
        product_ids = self.context.product_ids
        service_ids = self.context.service_ids
        provider_id = self.context.provider_ids[0] if self.context.provider_ids else 1
        seller_id = self.context.users[0].id if self.context.users else 0
        
        self.print_status(f"📦 Products available: {len(product_ids)}", "📦")
        self.print_status(f"📋 Services available: {len(service_ids)}", "📋")
        self.print_status(f"🏢 Provider ID: {provider_id}", "🏢")
        self.print_status(f"👤 Seller ID: {seller_id}", "👤")
        
        cart_details = await self.create_carts_bulk(provider_id, seller_id, product_ids, service_ids, carts)
        
        if cart_details:
            await self.process_payments_bulk(cart_details)
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*70)
        print("📊 BULK DATA CREATION SUMMARY")
        print("="*70)
        print(f"✅ Carts created: {self.stats['carts_created']}")
        print(f"✅ Invoices created: {self.stats['invoices_created']}")
        print(f"✅ Payments created: {self.stats['payments_created']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print(f"⏱️ Total time: {elapsed:.2f}s")
        
        if self.context.created_carts:
            print(f"\n🛒 Cart IDs: {self.context.created_carts[:10]}{'...' if len(self.context.created_carts) > 10 else ''}")
        if self.context.created_invoices:
            print(f"📄 Invoice IDs: {self.context.created_invoices[:10]}{'...' if len(self.context.created_invoices) > 10 else ''}")
        if self.context.created_payments:
            print(f"💳 Payment IDs: {self.context.created_payments[:10]}{'...' if len(self.context.created_payments) > 10 else ''}")
        
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Bulk Data Creator for Gluttex")
    parser.add_argument("--url", default="http://localhost:9000", help="Base URL")
    parser.add_argument("--context-file", default="test_context.json", help="Context file")
    parser.add_argument("--carts", type=int, default=10, help="Number of carts to create")
    
    args = parser.parse_args()
    
    async with BulkDataCreator(args.url) as creator:
        await creator.run(
            context_file=args.context_file,
            carts=args.carts
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)