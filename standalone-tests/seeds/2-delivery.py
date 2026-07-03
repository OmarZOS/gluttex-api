#!/usr/bin/env python3
"""
Delivery Updater Script
Fetches deliveries by provider and updates delivery details.
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
# DELIVERY UPDATER
# ============================================================================

class DeliveryUpdater:
    """Updates delivery details for orders"""
    
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
            "deliveries_skipped": 0
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
    
    def generate_random_delivery_details(self) -> Dict[str, Any]:
        """Generate random delivery details matching the Delivery_API model"""
        return {
            "delivery_package_count": random.randint(1, 5),
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
                "Ring the doorbell twice"
            ]),
            "delivery_fee": round(random.uniform(0, 50), 2)
        }
    
    async def process_delivery(self, delivery: Dict) -> bool:
        """
        Process a single delivery:
        1. Update delivery details (PUT)
        2. Update delivery status through lifecycle (PATCH)
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
        
        # Step 1: Generate and update delivery details
        details = self.generate_random_delivery_details()
        
        # Preserve existing fields if they exist
        if delivery.get('delivery_address_id'):
            details['delivery_address_id'] = delivery.get('delivery_address_id')
        if delivery.get('delivery_current_address_id'):
            details['delivery_current_address_id'] = delivery.get('delivery_current_address_id')
        if delivery.get('recipient_person'):
            details['recipient_person'] = delivery.get('recipient_person')
        if delivery.get('recipient_provider'):
            details['recipient_provider'] = delivery.get('recipient_provider')
        if delivery.get('delivery_source_type'):
            details['delivery_source_type'] = delivery.get('delivery_source_type')
        if delivery.get('delivery_source_id'):
            details['delivery_source_id'] = delivery.get('delivery_source_id')
        if delivery.get('delivery_invoice_ref'):
            details['delivery_invoice_ref'] = delivery.get('delivery_invoice_ref')
        if delivery.get('delivery_provider_id'):
            details['delivery_provider_id'] = delivery.get('delivery_provider_id')
        
        success = await self.update_delivery_details(delivery_id, details)
        
        if not success:
            self.stats["deliveries_failed"] += 1
            return False
        
        # Step 2: Update delivery status through lifecycle
        # Find where to start in the status flow
        try:
            start_index = Config.STATUS_FLOW.index(current_status) + 1
        except ValueError:
            start_index = 0
        
        for status in Config.STATUS_FLOW[start_index:]:
            result = await self.update_delivery_status(delivery_id, status)
            if not result:
                self.print_status(f"Failed to transition to {status}", "❌")
                break
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
        print("="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Update delivery details for orders")
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
    print("🚚 DELIVERY UPDATER SERVICE")
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