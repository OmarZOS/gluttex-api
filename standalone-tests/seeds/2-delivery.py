#!/usr/bin/env python3
"""
Delivery Updater Script
Fetches deliveries by provider and updates delivery details with address and tracking info.
Uses users from the test context file.
Run with: python update_deliveries.py
"""

import asyncio
import httpx
import json
import sys
import random
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import argparse


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for the delivery updater"""
    BASE_URL = "http://localhost:9000"
    DEFAULT_PROVIDER_ID = 1  # Provider ID from test data
    CONTEXT_FILE = "test_context.json"  # Use the main test context file
    
    # Delivery statuses matching the database enum
    DELIVERY_STATUSES = [
        "pending", "processing", "confirmed", "shipped", 
        "in_transit", "out_for_delivery", "delivered", 
        "failed", "cancelled", "returned", "refunded"
    ]
    
    # Shipping methods matching the database enum
    SHIPPING_METHODS = ["standard", "express", "overnight", "pickup", "courier", "same_day", "international"]
    
    # Status flow for delivery lifecycle
    STATUS_FLOW = ["processing", "confirmed", "shipped", "in_transit", "out_for_delivery", "delivered"]
    
    # Terminal statuses (skip these)
    TERMINAL_STATUSES = ["delivered", "cancelled", "returned", "refunded", "failed"]


# ============================================================================
# LOCATION GENERATOR
# ============================================================================

class LocationGenerator:
    """Generate random location data for deliveries matching Location_API"""
    
    CITIES = [
        "Algiers", "Oran", "Constantine", "Annaba", "Blida", 
        "Setif", "Tizi Ouzou", "Bejaia", "Batna", "Sidi Bel Abbes",
        "Biskra", "Tebessa", "El Oued", "Ghardaia", "Tamanrasset"
    ]
    STREETS = [
        "Main St", "Didouche Mourad", "1er Novembre", 
        "Larbi Ben Mhidi", "Krim Belkacem", 
        "Freres Bouadou", "Independance",
        "Ali Khodja", "Colonel Amirouche", "Emir Abdelkader",
        "Liberte", "Ben Boulaid", "Mohamed Khider"
    ]
    COUNTRIES = ["DZ", "FR", "US", "CA", "DE", "GB", "IT", "ES", "MA", "TN"]
    
    @classmethod
    def _get_city_coordinates(cls, city: str) -> tuple:
        """Get approximate coordinates for a city"""
        coords = {
            "Algiers": (36.7538, 3.0588),
            "Oran": (35.6969, -0.6331),
            "Constantine": (36.3650, 6.6147),
            "Annaba": (36.9020, 7.7557),
            "Blida": (36.4700, 2.8277),
            "Setif": (36.1911, 5.4137),
            "Tizi Ouzou": (36.7111, 4.0458),
            "Bejaia": (36.7558, 5.0843),
            "Batna": (35.5550, 6.1741),
            "Sidi Bel Abbes": (35.1937, -0.6322),
            "Biskra": (34.8500, 5.7333),
            "Tebessa": (35.4042, 8.1242),
            "El Oued": (33.3667, 6.8500),
            "Ghardaia": (32.4833, 3.6667),
            "Tamanrasset": (22.7850, 5.5228)
        }
        return coords.get(city, (36.7538, 3.0588))
    
    @classmethod
    def generate_location(cls, location_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete Location_API structure"""
        city = random.choice(cls.CITIES)
        country = random.choice(cls.COUNTRIES)
        lat, lon = cls._get_city_coordinates(city)
        
        # Add slight random offset
        lat += random.uniform(-0.02, 0.02)
        lon += random.uniform(-0.02, 0.02)
        
        # Ensure street name is not too long (max 255 chars)
        street = f"{random.randint(1, 999)} {random.choice(cls.STREETS)}"
        if len(street) > 200:
            street = street[:200]
        
        return {
            "id_location": 0,
            "location_latitude": round(lat, 6),
            "location_longitude": round(lon, 6),
            "location_name": location_name or random.choice(["Home", "Work", "Clinic", "Office", "Shop", "Warehouse", "Distribution Center"]),
            "location_address_id": 0,
            "id_address": 0,
            "address_street": street,
            "address_city": city,
            "address_postal_code": f"{random.randint(1000, 9999)}",
            "address_country": country
        }
    
    @classmethod
    def generate_tracking_location(cls, step: int, total_steps: int = 6) -> Dict[str, Any]:
        """Generate a tracking location based on progress through the delivery"""
        progress = step / total_steps
        
        # Start from a random city and move toward destination
        if step == 0:
            city = random.choice(["Algiers", "Oran", "Constantine"])
            location_name = "Distribution Center"
        else:
            city = random.choice(cls.CITIES)
            location_name = f"Tracking Point {step}"
        
        lat, lon = cls._get_city_coordinates(city)
        
        # Add random offset based on progress (closer to destination = less random)
        offset = 0.02 * (1 - progress)
        lat += random.uniform(-offset, offset)
        lon += random.uniform(-offset, offset)
        
        # Ensure street name is not too long (max 255 chars)
        street = f"TP{step} - {random.randint(1, 999)} {random.choice(cls.STREETS)}"
        if len(street) > 200:
            street = street[:200]
        
        return {
            "id_location": 0,
            "location_latitude": round(lat, 6),
            "location_longitude": round(lon, 6),
            "location_name": location_name,
            "location_address_id": 0,
            "id_address": 0,
            "address_street": street,
            "address_city": city,
            "address_postal_code": f"{random.randint(1000, 9999)}",
            "address_country": random.choice(cls.COUNTRIES)
        }


# ============================================================================
# DELIVERY UPDATER
# ============================================================================

class DeliveryUpdater:
    """Updates delivery details for orders with address and tracking"""
    
    def __init__(self, base_url: str = Config.BASE_URL):
        self.base_url = base_url
        self.client = None
        self.auth_token = None
        self.user_id = None
        self.provider_id = Config.DEFAULT_PROVIDER_ID
        self.context_users = []
        self.stats = {
            "deliveries_found": 0,
            "deliveries_updated": 0,
            "deliveries_failed": 0,
            "status_transitions": 0,
            "deliveries_skipped": 0,
            "locations_created": 0,
            "tracking_updates": 0,
            "addresses_created": 0,
            "addresses_failed": 0
        }
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def print_status(self, message: str, emoji: str = "ℹ️"):
        """Print status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {emoji} {message}")
    
    def load_context_users(self) -> bool:
        """Load users from the test context file"""
        context_file = Config.CONTEXT_FILE
        
        if not Path(context_file).exists():
            self.print_status(f"Context file {context_file} not found", "❌")
            return False
        
        try:
            with open(context_file, 'r') as f:
                data = json.load(f)
            
            self.context_users = data.get('users', [])
            self.print_status(f"Loaded {len(self.context_users)} users from context", "📂")
            
            if self.context_users:
                for i, user in enumerate(self.context_users[:3]):
                    self.print_status(f"  User {i+1}: {user.get('username')} (ID: {user.get('id')})", "👤")
                if len(self.context_users) > 3:
                    self.print_status(f"  ... and {len(self.context_users) - 3} more", "👤")
            
            return True
            
        except Exception as e:
            self.print_status(f"Error loading context: {e}", "❌")
            return False
    
    async def login_with_context_user(self, user_index: int = 0) -> bool:
        """Login using a user from the context"""
        if not self.context_users:
            self.print_status("No context users available", "❌")
            return False
        
        if user_index >= len(self.context_users):
            self.print_status(f"User index {user_index} out of range", "❌")
            return False
        
        user = self.context_users[user_index]
        username = user.get('username')
        password = user.get('password')
        
        self.print_status(f"Logging in as '{username}' (ID: {user.get('id')})", "🔐")
        
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
                self.auth_token = result.get('access_token')
                self.user_id = user.get('id')
                self.print_status(f"✅ Login successful as {username}", "✅")
                return True
            else:
                self.print_status(f"Login failed: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.print_status(f"Login error: {e}", "❌")
            return False
    
    async def get_deliveries_by_provider(self, provider_id: int) -> List[Dict]:
        """Get all deliveries for a provider"""
        self.print_status(f"Fetching deliveries for provider {provider_id}", "📦")
        
        if not self.auth_token:
            return []
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/business/delivery",
                params={
                    "provider_id": provider_id, 
                    "offset": 0, 
                    "limit": 100
                },
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    deliveries = result
                elif isinstance(result, dict):
                    deliveries = result.get('data', result.get('items', []))
                else:
                    deliveries = []
                
                self.stats["deliveries_found"] = len(deliveries)
                self.print_status(f"Found {len(deliveries)} deliveries", "📦")
                
                # Show first few deliveries
                for i, delivery in enumerate(deliveries[:5]):
                    self.print_status(f"  Delivery {i+1}: ID={delivery.get('id_delivery')}, Status={delivery.get('delivery_status')}", "📋")
                if len(deliveries) > 5:
                    self.print_status(f"  ... and {len(deliveries) - 5} more", "📋")
                
                return deliveries
            else:
                self.print_status(f"Failed to fetch deliveries: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return []
                
        except Exception as e:
            self.print_status(f"Error fetching deliveries: {e}", "❌")
            return []
    
    async def get_delivery_by_id(self, delivery_id: int) -> Optional[Dict]:
        """Get delivery details by ID"""
        if not self.auth_token:
            return None
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/business/delivery/{delivery_id}",
                params={"eager_load": True},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            self.print_status(f"Error getting delivery {delivery_id}: {e}", "⚠️")
            return None
    
    async def update_delivery_details(self, delivery_id: int, details: Dict[str, Any]) -> bool:
        """Update delivery details using PUT endpoint"""
        self.print_status(f"Updating delivery {delivery_id} with details", "✏️")
        
        if not self.auth_token:
            return False
        
        try:
            response = await self.client.put(
                f"{self.base_url}/api/v1/business/delivery/{delivery_id}",
                json=details,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                self.stats["deliveries_updated"] += 1
                self.print_status(f"✅ Delivery {delivery_id} updated successfully", "✅")
                return True
            else:
                self.stats["deliveries_failed"] += 1
                self.print_status(f"❌ Failed to update delivery {delivery_id}: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.stats["deliveries_failed"] += 1
            self.print_status(f"❌ Error updating delivery {delivery_id}: {e}", "❌")
            return False
    
    async def update_delivery_status(self, delivery_id: int, status: str) -> bool:
        """Update delivery status"""
        self.print_status(f"Updating delivery {delivery_id} status to '{status}'", "🔄")
        
        if not self.auth_token:
            return False
        
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/business/delivery/{delivery_id}/status",
                params={"status": status},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                self.stats["status_transitions"] += 1
                self.print_status(f"✅ Delivery {delivery_id} status updated to '{status}'", "✅")
                return True
            else:
                self.print_status(f"❌ Failed to update status: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Error updating status: {e}", "❌")
            return False
    
    async def update_delivery_tracking(self, delivery_id: int, current_address_id: int) -> bool:
        """Update delivery tracking location by address ID"""
        self.print_status(f"Updating delivery {delivery_id} tracking to address {current_address_id}", "📍")
        
        if not self.auth_token:
            return False
        
        try:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/business/delivery/{delivery_id}/tracking",
                params={"current_address_id": current_address_id},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                self.stats["tracking_updates"] += 1
                self.print_status(f"✅ Delivery {delivery_id} tracking updated", "📍")
                return True
            else:
                self.print_status(f"❌ Failed to update tracking: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Error updating tracking: {e}", "❌")
            return False
    
    def generate_delivery_update_payload(self, delivery: Dict) -> Dict[str, Any]:
        """Generate the full delivery update payload with locations"""
        
        # Generate locations using Location_API structure
        destination_location = LocationGenerator.generate_location("Destination")
        
        # Base delivery details
        payload = {
            "delivery_package_count": str(random.randint(1, 5)),
            "delivery_total_weight": round(random.uniform(0.5, 50.0), 1),
            "delivery_cargo_dimensions": f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}",
            "delivery_goods_description": f"Package containing {random.choice(['medical supplies', 'pharmaceuticals', 'equipment', 'documents', 'samples'])}",
            "hs_code": f"{random.randint(1000000000, 9999999999)}",
            "delivery_merchant_name": f"Merchant_{uuid.uuid4().hex[:4]}",
            "delivery_shipping_method": random.choice(Config.SHIPPING_METHODS),
            "delivery_special_instructions": random.choice([
                "Leave at reception desk",
                "Call 30 minutes before arrival",
                "Package requires signature",
                "Fragile - handle with care",
                "Temperature sensitive",
                "Deliver between 9am-5pm",
                "Ring the doorbell twice",
                "Leave with security guard",
                "Do not leave outside"
            ]),
            "delivery_fee": round(random.uniform(0, 50), 2),
            # Add destination address fields
            "delivery_address": destination_location.get("address_street"),
            "delivery_city": destination_location.get("address_city"),
            "delivery_postal_code": destination_location.get("address_postal_code"),
            "delivery_country": destination_location.get("address_country"),
            "delivery_latitude": destination_location.get("location_latitude"),
            "delivery_longitude": destination_location.get("location_longitude"),
            "delivery_location_name": destination_location.get("location_name")
        }
        
        # Preserve existing fields
        preserve_fields = [
            'recipient_person', 'recipient_provider', 'delivery_source_type',
            'delivery_source_id', 'delivery_invoice_ref', 'delivery_provider_id',
            'delivery_broker_id', 'delivery_address_id', 'delivery_current_address_id'
        ]
        for field in preserve_fields:
            if delivery.get(field):
                payload[field] = delivery.get(field)
        
        return payload
    
    async def create_tracking_address(self, location: Dict[str, Any]) -> Optional[int]:
        """Create a tracking address and return its ID"""
        self.print_status(f"Creating tracking address...", "📍")
        
        if not self.auth_token:
            return None
        
        # Build address data matching the Location_API structure
        address_data = {
            "address_street": location.get("address_street"),
            "address_city": location.get("address_city"),
            "address_postal_code": location.get("address_postal_code"),
            "address_country": location.get("address_country"),
            "location_latitude": location.get("location_latitude"),
            "location_longitude": location.get("location_longitude"),
            "location_name": location.get("location_name")
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/addresses",
                json=address_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 201:
                result = response.json()
                address_id = result.get('id_address')
                if address_id:
                    self.stats["addresses_created"] += 1
                    self.print_status(f"✅ Tracking address created: {address_id}", "📍")
                    return address_id
                else:
                    self.stats["addresses_failed"] += 1
                    self.print_status(f"⚠️ Tracking address created but no ID returned", "⚠️")
                    return None
            else:
                self.stats["addresses_failed"] += 1
                self.print_status(f"❌ Failed to create tracking address: {response.status_code}", "❌")
                print(f"   Response: {response.text[:200]}")
                return None
                
        except Exception as e:
            self.stats["addresses_failed"] += 1
            self.print_status(f"❌ Error creating tracking address: {e}", "❌")
            return None
    
    async def process_delivery(self, delivery: Dict) -> bool:
        """
        Process a single delivery:
        1. Update delivery details with destination address (PUT)
        2. Update delivery status through lifecycle (PATCH)
        3. Create tracking addresses and update tracking at each step
        """
        delivery_id = delivery.get('id_delivery')
        if not delivery_id:
            return False
        
        current_status = delivery.get('delivery_status', 'pending')
        
        # Skip terminal statuses
        if current_status in Config.TERMINAL_STATUSES:
            self.print_status(f"Skipping delivery {delivery_id} - already {current_status}", "⏭️")
            self.stats["deliveries_skipped"] += 1
            return False
        
        self.print_status(f"\n🔧 Processing delivery {delivery_id}", "🔧")
        print(f"   Current status: {current_status}")
        
        # Step 1: Generate and update delivery details with locations
        payload = self.generate_delivery_update_payload(delivery)
        
        print(f"   📍 Destination: {payload.get('delivery_address')}, {payload.get('delivery_city')}")
        
        success = await self.update_delivery_details(delivery_id, payload)
        
        if not success:
            self.stats["deliveries_failed"] += 1
            return False
        
        self.stats["locations_created"] += 1
        
        # Step 2: Update delivery status through lifecycle with tracking
        try:
            start_index = Config.STATUS_FLOW.index(current_status) + 1
        except ValueError:
            start_index = 0
        
        for step_index, status in enumerate(Config.STATUS_FLOW[start_index:]):
            # Update status first
            result = await self.update_delivery_status(delivery_id, status)
            if not result:
                self.print_status(f"Failed to transition to {status}", "❌")
                break
            
            # Only create tracking address and update tracking if not delivered
            if status != 'delivered' and status not in ['cancelled', 'returned']:
                # Generate new current location for this step
                new_location = LocationGenerator.generate_tracking_location(
                    start_index + step_index + 1, 
                    len(Config.STATUS_FLOW)
                )
                
                # Create tracking address and update delivery
                new_tracking_id = await self.create_tracking_address(new_location)
                if new_tracking_id:
                    await self.update_delivery_tracking(delivery_id, new_tracking_id)
                    print(f"   📍 Updated tracking to step {start_index + step_index + 1}")
            
            await asyncio.sleep(0.3)  # Small delay between updates
        
        return True
    
    async def process_all_deliveries_for_provider(self, provider_id: int, limit: int = 20):
        """Process all deliveries for a provider"""
        self.provider_id = provider_id
        self.print_status(f"\n🚀 Processing deliveries for provider {provider_id}", "🚀")
        print("="*70)
        
        # Get all deliveries for the provider
        deliveries = await self.get_deliveries_by_provider(provider_id)
        
        if not deliveries:
            self.print_status("No deliveries found to process", "ℹ️")
            return
        
        # Process each delivery
        processed_count = 0
        for i, delivery in enumerate(deliveries):
            if processed_count >= limit:
                break
            
            print(f"\n📦 Processing delivery {processed_count + 1}/{min(len(deliveries), limit)}")
            print(f"   ID: {delivery.get('id_delivery')}")
            print(f"   Current status: {delivery.get('delivery_status')}")
            
            success = await self.process_delivery(delivery)
            if success:
                processed_count += 1
            
            # Small delay between processing deliveries
            await asyncio.sleep(0.5)
        
        # Print statistics
        self.print_stats()
    
    def print_stats(self):
        """Print processing statistics"""
        print("\n" + "="*70)
        print("📊 PROCESSING STATISTICS")
        print("="*70)
        print(f"   👤 User ID: {self.user_id}")
        print(f"   📦 Deliveries found: {self.stats['deliveries_found']}")
        print(f"   ✅ Deliveries updated: {self.stats['deliveries_updated']}")
        print(f"   ❌ Deliveries failed: {self.stats['deliveries_failed']}")
        print(f"   ⏭️ Deliveries skipped: {self.stats['deliveries_skipped']}")
        print(f"   🔄 Status transitions: {self.stats['status_transitions']}")
        print(f"   📍 Locations created: {self.stats['locations_created']}")
        print(f"   📍 Tracking updates: {self.stats['tracking_updates']}")
        print(f"   📍 Addresses created: {self.stats['addresses_created']}")
        print(f"   📍 Addresses failed: {self.stats['addresses_failed']}")
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Update delivery details for orders with addresses and tracking")
    parser.add_argument("--url", default=Config.BASE_URL, help="Base URL of the API")
    parser.add_argument("--provider", type=int, default=Config.DEFAULT_PROVIDER_ID, 
                       help="Provider ID to process")
    parser.add_argument("--user-index", type=int, default=0, 
                       help="Index of user from context file to use (default: 0)")
    parser.add_argument("--limit", type=int, default=20, 
                       help="Maximum number of deliveries to process")
    parser.add_argument("--context-file", default=Config.CONTEXT_FILE, 
                       help="Context file to load users from")
    
    args = parser.parse_args()
    
    # Update config
    Config.CONTEXT_FILE = args.context_file
    Config.DEFAULT_PROVIDER_ID = args.provider
    
    print("\n" + "="*70)
    print("🚚 DELIVERY UPDATER SERVICE (with Addresses & Tracking)")
    print("="*70)
    print(f"📍 Base URL: {args.url}")
    print(f"🏢 Provider: {args.provider}")
    print(f"📊 Limit: {args.limit}")
    print(f"📂 Context: {args.context_file}")
    print("="*70)
    
    async with DeliveryUpdater(args.url) as updater:
        # Load users from context
        if not updater.load_context_users():
            print("\n❌ Failed to load context users. Exiting.")
            return
        
        if not updater.context_users:
            print("\n❌ No users found in context. Exiting.")
            return
        
        # Login with the specified user
        if not await updater.login_with_context_user(args.user_index):
            print(f"\n❌ Failed to login with user index {args.user_index}. Exiting.")
            return
        
        # Process deliveries
        await updater.process_all_deliveries_for_provider(args.provider, args.limit)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)