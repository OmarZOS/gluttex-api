# storage/seeds/product_category.py
"""
Product category seed module using the storage broker.
"""

import logging
from typing import Dict, Any

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_PRODUCT_CATEGORIES = [
    {"product_category_name": "Baked Goods"},
    {"product_category_name": "Spreads"},
    {"product_category_name": "Cereals"},
    {"product_category_name": "Pasta"},
    {"product_category_name": "Snacks"},
    {"product_category_name": "Beverages"},
    {"product_category_name": "Desserts"},
    {"product_category_name": "Frozen Foods"},
    {"product_category_name": "Flours & Baking Ingredients"},
    {"product_category_name": "Canned & Packaged Goods"},
]


# ==================== Seeding Function ====================

def seed_product_categories() -> int:
    """
    Seed product categories using the storage broker's insert_record function.
    
    Returns:
        Number of categories inserted
    """
    count_inserted = 0
    
    for category_data in SEED_PRODUCT_CATEGORIES:
        # Check if category already exists using get
        existing = get(
            table=models.ProductCategory,
            conditions={"product_category_name": category_data["product_category_name"]}
        )
        
        if not existing:
            # Create category instance
            category = models.ProductCategory(
                product_category_name=category_data["product_category_name"],
                product_category_icon=None,
                product_category_naming_ref=None,
            )
            # Insert using broker
            result = insert_record(category)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded product category: {category_data['product_category_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} product categories")
    return count_inserted


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding product categories."""
    print("🌱 Starting product category seeding...")
    
    try:
        count = seed_product_categories()
        print(f"✅ Successfully seeded {count} product categories")
    except Exception as e:
        print(f"❌ Failed to seed product categories: {e}")
        raise


if __name__ == "__main__":
    main()