# storage/seeds/iproduct.py
"""
Iproduct (External/Imported Product) seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import random

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

# Common product categories (these should exist in product_category table)
# Category IDs: 1=Baked Goods, 2=Spreads, 3=Cereals, 4=Pasta, 5=Snacks, 
# 6=Beverages, 7=Desserts, 8=Frozen Foods, 9=Flours & Baking, 10=Canned Goods

SEED_IPRODUCTS = [
    # Baked Goods (category_id: 1)
    {
        "iproduct_name": "Whole Wheat Bread",
        "iproduct_barcode": "8901234567890",
        "iproduct_brand": "HealthyLife",
        "iproduct_estimated_price": 2.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 1,
        "iproduct_image_url": "https://example.com/images/whole_wheat_bread.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.95,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Artisan Sourdough",
        "iproduct_barcode": "8901234567891",
        "iproduct_brand": "Baker's Delight",
        "iproduct_estimated_price": 4.50,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 1,
        "iproduct_image_url": "https://example.com/images/sourdough.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.92,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Gluten-Free Bread",
        "iproduct_barcode": "8901234567892",
        "iproduct_brand": "FreeLife",
        "iproduct_estimated_price": 5.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 1,
        "iproduct_image_url": "https://example.com/images/gluten_free_bread.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.88,
        "iproduct_model_name": "gpt-4"
    },
    
    # Spreads (category_id: 2)
    {
        "iproduct_name": "Organic Peanut Butter",
        "iproduct_barcode": "8901234567893",
        "iproduct_brand": "NutriSpread",
        "iproduct_estimated_price": 3.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 2,
        "iproduct_image_url": "https://example.com/images/peanut_butter.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.94,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Strawberry Jam",
        "iproduct_barcode": "8901234567894",
        "iproduct_brand": "FruitSpread",
        "iproduct_estimated_price": 2.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 2,
        "iproduct_image_url": "https://example.com/images/strawberry_jam.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.91,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Honey Spread",
        "iproduct_barcode": "8901234567895",
        "iproduct_brand": "PureHoney",
        "iproduct_estimated_price": 6.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 2,
        "iproduct_image_url": "https://example.com/images/honey.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.96,
        "iproduct_model_name": "gpt-4"
    },
    
    # Cereals (category_id: 3)
    {
        "iproduct_name": "Oatmeal Cereal",
        "iproduct_barcode": "8901234567896",
        "iproduct_brand": "MorningOats",
        "iproduct_estimated_price": 3.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 3,
        "iproduct_image_url": "https://example.com/images/oatmeal.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.93,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Corn Flakes",
        "iproduct_barcode": "8901234567897",
        "iproduct_brand": "CrispyCorn",
        "iproduct_estimated_price": 2.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 3,
        "iproduct_image_url": "https://example.com/images/corn_flakes.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.90,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Gluten-Free Granola",
        "iproduct_barcode": "8901234567898",
        "iproduct_brand": "GranolaHealth",
        "iproduct_estimated_price": 4.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 3,
        "iproduct_image_url": "https://example.com/images/granola.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.87,
        "iproduct_model_name": "gpt-4"
    },
    
    # Pasta (category_id: 4)
    {
        "iproduct_name": "Spaghetti Pasta",
        "iproduct_barcode": "8901234567899",
        "iproduct_brand": "PastaItalia",
        "iproduct_estimated_price": 1.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 4,
        "iproduct_image_url": "https://example.com/images/spaghetti.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.95,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Gluten-Free Pasta",
        "iproduct_barcode": "8901234567900",
        "iproduct_brand": "FreePasta",
        "iproduct_estimated_price": 3.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 4,
        "iproduct_image_url": "https://example.com/images/gluten_free_pasta.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.89,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Lasagna Sheets",
        "iproduct_barcode": "8901234567901",
        "iproduct_brand": "PastaItalia",
        "iproduct_estimated_price": 2.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 4,
        "iproduct_image_url": "https://example.com/images/lasagna.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.92,
        "iproduct_model_name": "gpt-4"
    },
    
    # Snacks (category_id: 5)
    {
        "iproduct_name": "Potato Chips",
        "iproduct_barcode": "8901234567902",
        "iproduct_brand": "CrispySnack",
        "iproduct_estimated_price": 1.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 5,
        "iproduct_image_url": "https://example.com/images/potato_chips.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.94,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Gluten-Free Crackers",
        "iproduct_barcode": "8901234567903",
        "iproduct_brand": "FreeSnack",
        "iproduct_estimated_price": 3.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 5,
        "iproduct_image_url": "https://example.com/images/crackers.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.88,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Trail Mix",
        "iproduct_barcode": "8901234567904",
        "iproduct_brand": "NutriMix",
        "iproduct_estimated_price": 4.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 5,
        "iproduct_image_url": "https://example.com/images/trail_mix.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.91,
        "iproduct_model_name": "gpt-4"
    },
    
    # Beverages (category_id: 6)
    {
        "iproduct_name": "Orange Juice",
        "iproduct_barcode": "8901234567905",
        "iproduct_brand": "FreshSqueeze",
        "iproduct_estimated_price": 2.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 6,
        "iproduct_image_url": "https://example.com/images/orange_juice.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.96,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Almond Milk",
        "iproduct_barcode": "8901234567906",
        "iproduct_brand": "PlantMilk",
        "iproduct_estimated_price": 3.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 6,
        "iproduct_image_url": "https://example.com/images/almond_milk.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.93,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Green Tea",
        "iproduct_barcode": "8901234567907",
        "iproduct_brand": "TeaLeaf",
        "iproduct_estimated_price": 2.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 6,
        "iproduct_image_url": "https://example.com/images/green_tea.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.97,
        "iproduct_model_name": "gpt-4"
    },
    
    # Desserts (category_id: 7)
    {
        "iproduct_name": "Chocolate Brownie",
        "iproduct_barcode": "8901234567908",
        "iproduct_brand": "SweetTreat",
        "iproduct_estimated_price": 2.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 7,
        "iproduct_image_url": "https://example.com/images/brownie.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.94,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Gluten-Free Cookies",
        "iproduct_barcode": "8901234567909",
        "iproduct_brand": "FreeCookie",
        "iproduct_estimated_price": 4.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 7,
        "iproduct_image_url": "https://example.com/images/gluten_free_cookies.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.89,
        "iproduct_model_name": "gpt-4"
    },
    
    # Frozen Foods (category_id: 8)
    {
        "iproduct_name": "Frozen Vegetables Mix",
        "iproduct_barcode": "8901234567910",
        "iproduct_brand": "FrostFresh",
        "iproduct_estimated_price": 3.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 8,
        "iproduct_image_url": "https://example.com/images/frozen_veg.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.95,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Frozen Pizza",
        "iproduct_barcode": "8901234567911",
        "iproduct_brand": "PizzaFast",
        "iproduct_estimated_price": 5.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 8,
        "iproduct_image_url": "https://example.com/images/frozen_pizza.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.92,
        "iproduct_model_name": "gpt-4"
    },
    
    # Flours & Baking (category_id: 9)
    {
        "iproduct_name": "All-Purpose Flour",
        "iproduct_barcode": "8901234567912",
        "iproduct_brand": "BakeMaster",
        "iproduct_estimated_price": 1.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "contains_gluten",
        "iproduct_category_id": 9,
        "iproduct_image_url": "https://example.com/images/flour.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.96,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Almond Flour",
        "iproduct_barcode": "8901234567913",
        "iproduct_brand": "NutriFlour",
        "iproduct_estimated_price": 7.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 9,
        "iproduct_image_url": "https://example.com/images/almond_flour.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.90,
        "iproduct_model_name": "gpt-4"
    },
    
    # Canned & Packaged Goods (category_id: 10)
    {
        "iproduct_name": "Canned Tomatoes",
        "iproduct_barcode": "8901234567914",
        "iproduct_brand": "CanFresh",
        "iproduct_estimated_price": 1.49,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 10,
        "iproduct_image_url": "https://example.com/images/canned_tomatoes.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.95,
        "iproduct_model_name": "gpt-4"
    },
    {
        "iproduct_name": "Canned Beans",
        "iproduct_barcode": "8901234567915",
        "iproduct_brand": "BeanGood",
        "iproduct_estimated_price": 1.99,
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": "gluten_free",
        "iproduct_category_id": 10,
        "iproduct_image_url": "https://example.com/images/canned_beans.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": 0.94,
        "iproduct_model_name": "gpt-4"
    },
]


# ==================== Additional Data Generators ====================

def generate_random_iproduct_data(category_id: int = None) -> Dict[str, Any]:
    """
    Generate random iproduct data for testing.
    
    Args:
        category_id: Optional category ID to assign
        
    Returns:
        Dictionary with random iproduct data
    """
    names = [
        "Organic Quinoa", "Chia Seeds", "Coconut Oil", "Olive Oil", 
        "Maple Syrup", "Vanilla Extract", "Cocoa Powder", "Protein Powder",
        "Coconut Flour", "Tapioca Starch", "Xanthan Gum", "Psyllium Husk"
    ]
    brands = [
        "HealthyLife", "NutriFood", "PureOrganic", "WholeFoods", 
        "NaturalChoice", "GreenGarden", "FarmFresh", "OrganicHarvest"
    ]
    gluten_statuses = ["gluten_free", "contains_gluten", "may_contain_gluten", "unknown"]
    
    return {
        "iproduct_name": random.choice(names),
        "iproduct_barcode": str(random.randint(1000000000000, 9999999999999)),
        "iproduct_brand": random.choice(brands),
        "iproduct_estimated_price": round(random.uniform(1.99, 29.99), 2),
        "iproduct_price_currency": "DZD",
        "iproduct_gluten_status": random.choice(gluten_statuses),
        "iproduct_category_id": category_id or random.randint(1, 10),
        "iproduct_image_url": f"https://example.com/images/product_{random.randint(1000, 9999)}.jpg",
        "iproduct_info_source": "openai",
        "iproduct_info_confidence": round(random.uniform(0.75, 0.99), 2),
        "iproduct_model_name": "gpt-4"
    }


# ==================== Seeding Functions ====================

def seed_iproducts() -> int:
    """
    Seed iproducts using the storage broker's insert_record function.
    
    Returns:
        Number of iproducts inserted
    """
    count_inserted = 0
    
    for product_data in SEED_IPRODUCTS:
        # Check if product already exists by barcode
        existing = get(
            table=models.Iproduct,
            conditions={"iproduct_barcode": product_data["iproduct_barcode"]}
        )
        
        if not existing:
            # Create iproduct instance
            iproduct = models.Iproduct(
                iproduct_name=product_data["iproduct_name"],
                iproduct_barcode=product_data["iproduct_barcode"],
                iproduct_brand=product_data["iproduct_brand"],
                iproduct_estimated_price=Decimal(str(product_data["iproduct_estimated_price"])),
                iproduct_price_currency=product_data["iproduct_price_currency"],
                iproduct_gluten_status=product_data["iproduct_gluten_status"],
                iproduct_category_id=product_data["iproduct_category_id"],
                iproduct_image_url=product_data["iproduct_image_url"],
                iproduct_info_source=product_data["iproduct_info_source"],
                iproduct_info_confidence=Decimal(str(product_data["iproduct_info_confidence"])),
                iproduct_model_name=product_data["iproduct_model_name"],
                iproduct_naming_ref=None,  # Set if you have naming_contribution references
                iproduct_last_price_update=datetime.now(),
                iproduct_created_at=datetime.now(),
                iproduct_last_update=datetime.now(),
            )
            # Insert using broker
            result = insert_record(iproduct)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded iproduct: {product_data['iproduct_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} iproducts")
    return count_inserted


def seed_random_iproducts(count: int = 10) -> int:
    """
    Seed random iproducts.
    
    Args:
        count: Number of random iproducts to generate and seed
        
    Returns:
        Number of iproducts inserted
    """
    count_inserted = 0
    
    for _ in range(count):
        product_data = generate_random_iproduct_data()
        
        # Check if product already exists by barcode
        existing = get(
            table=models.Iproduct,
            conditions={"iproduct_barcode": product_data["iproduct_barcode"]}
        )
        
        if not existing:
            iproduct = models.Iproduct(
                iproduct_name=product_data["iproduct_name"],
                iproduct_barcode=product_data["iproduct_barcode"],
                iproduct_brand=product_data["iproduct_brand"],
                iproduct_estimated_price=Decimal(str(product_data["iproduct_estimated_price"])),
                iproduct_price_currency=product_data["iproduct_price_currency"],
                iproduct_gluten_status=product_data["iproduct_gluten_status"],
                iproduct_category_id=product_data["iproduct_category_id"],
                iproduct_image_url=product_data["iproduct_image_url"],
                iproduct_info_source=product_data["iproduct_info_source"],
                iproduct_info_confidence=Decimal(str(product_data["iproduct_info_confidence"])),
                iproduct_model_name=product_data["iproduct_model_name"],
                iproduct_naming_ref=None,
                iproduct_last_price_update=datetime.now(),
                iproduct_created_at=datetime.now(),
                iproduct_last_update=datetime.now(),
            )
            result = insert_record(iproduct)
            if result:
                count_inserted += 1
    
    logger.info(f"✅ Seeded {count_inserted} random iproducts")
    return count_inserted


def seed_iproduct(product_data: Dict[str, Any]) -> bool:
    """
    Seed a single iproduct.
    
    Args:
        product_data: Product data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.Iproduct,
        conditions={"iproduct_barcode": product_data.get("iproduct_barcode")}
    )
    
    if existing:
        logger.debug(f"Iproduct already exists: {product_data.get('iproduct_name')}")
        return False
    
    iproduct = models.Iproduct(
        iproduct_name=product_data.get("iproduct_name"),
        iproduct_barcode=product_data.get("iproduct_barcode"),
        iproduct_brand=product_data.get("iproduct_brand"),
        iproduct_estimated_price=Decimal(str(product_data.get("iproduct_estimated_price", 0.00))),
        iproduct_price_currency=product_data.get("iproduct_price_currency", "DZD"),
        iproduct_gluten_status=product_data.get("iproduct_gluten_status", "unknown"),
        iproduct_category_id=product_data.get("iproduct_category_id"),
        iproduct_image_url=product_data.get("iproduct_image_url"),
        iproduct_info_source=product_data.get("iproduct_info_source"),
        iproduct_info_confidence=Decimal(str(product_data.get("iproduct_info_confidence", 0.00))),
        iproduct_model_name=product_data.get("iproduct_model_name"),
        iproduct_naming_ref=product_data.get("iproduct_naming_ref"),
        iproduct_last_price_update=product_data.get("iproduct_last_price_update", datetime.now()),
        iproduct_created_at=product_data.get("iproduct_created_at", datetime.now()),
        iproduct_last_update=product_data.get("iproduct_last_update", datetime.now()),
    )
    result = insert_record(iproduct)
    if result:
        logger.debug(f"Seeded iproduct: {product_data.get('iproduct_name')}")
    return bool(result)


def seed_iproducts_from_list(products: List[Dict[str, Any]]) -> int:
    """
    Seed iproducts from a custom list.
    
    Args:
        products: List of product dictionaries
        
    Returns:
        Number of products inserted
    """
    count_inserted = 0
    
    for product_data in products:
        # Check if product already exists by barcode
        existing = get(
            table=models.Iproduct,
            conditions={"iproduct_barcode": product_data.get("iproduct_barcode")}
        )
        
        if not existing:
            iproduct = models.Iproduct(
                iproduct_name=product_data.get("iproduct_name"),
                iproduct_barcode=product_data.get("iproduct_barcode"),
                iproduct_brand=product_data.get("iproduct_brand"),
                iproduct_estimated_price=Decimal(str(product_data.get("iproduct_estimated_price", 0.00))),
                iproduct_price_currency=product_data.get("iproduct_price_currency", "DZD"),
                iproduct_gluten_status=product_data.get("iproduct_gluten_status", "unknown"),
                iproduct_category_id=product_data.get("iproduct_category_id"),
                iproduct_image_url=product_data.get("iproduct_image_url"),
                iproduct_info_source=product_data.get("iproduct_info_source"),
                iproduct_info_confidence=Decimal(str(product_data.get("iproduct_info_confidence", 0.00))),
                iproduct_model_name=product_data.get("iproduct_model_name"),
                iproduct_naming_ref=product_data.get("iproduct_naming_ref"),
                iproduct_last_price_update=product_data.get("iproduct_last_price_update", datetime.now()),
                iproduct_created_at=product_data.get("iproduct_created_at", datetime.now()),
                iproduct_last_update=product_data.get("iproduct_last_update", datetime.now()),
            )
            result = insert_record(iproduct)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded iproduct: {product_data.get('iproduct_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} iproducts from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_iproducts() -> List[Dict[str, Any]]:
    """
    Get all seeded iproducts from the database.
    
    Returns:
        List of product dictionaries
    """
    with session_scope() as session:
        products = session.query(models.Iproduct).all()
        return [
            {
                "id": p.id_iproduct,
                "name": p.iproduct_name,
                "barcode": p.iproduct_barcode,
                "brand": p.iproduct_brand,
                "price": float(p.iproduct_estimated_price) if p.iproduct_estimated_price else 0,
                "currency": p.iproduct_price_currency,
                "gluten_status": p.iproduct_gluten_status,
                "category_id": p.iproduct_category_id,
                "image_url": p.iproduct_image_url,
            }
            for p in products
        ]


def iproduct_exists(barcode: str) -> bool:
    """
    Check if an iproduct already exists in the database.
    
    Args:
        barcode: Product barcode to check
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.Iproduct,
        conditions={"iproduct_barcode": barcode}
    )
    return bool(existing)


def get_iproduct_by_barcode(barcode: str) -> Optional[models.Iproduct]:
    """
    Get an iproduct by barcode.
    
    Args:
        barcode: Product barcode
        
    Returns:
        Iproduct instance or None
    """
    result = get(
        table=models.Iproduct,
        conditions={"iproduct_barcode": barcode}
    )
    return result[0] if result else None


def get_iproduct_by_id(product_id: int) -> Optional[models.Iproduct]:
    """
    Get an iproduct by ID.
    
    Args:
        product_id: Product ID
        
    Returns:
        Iproduct instance or None
    """
    result = get(
        table=models.Iproduct,
        conditions={"id_iproduct": product_id}
    )
    return result[0] if result else None


def get_iproducts_by_category(category_id: int) -> List[models.Iproduct]:
    """
    Get all iproducts in a category.
    
    Args:
        category_id: Category ID
        
    Returns:
        List of Iproduct instances
    """
    with session_scope() as session:
        return session.query(models.Iproduct).filter(
            models.Iproduct.iproduct_category_id == category_id
        ).all()


def get_iproducts_by_gluten_status(gluten_status: str) -> List[models.Iproduct]:
    """
    Get iproducts by gluten status.
    
    Args:
        gluten_status: Gluten status ('gluten_free', 'contains_gluten', 'may_contain_gluten', 'unknown')
        
    Returns:
        List of Iproduct instances
    """
    with session_scope() as session:
        return session.query(models.Iproduct).filter(
            models.Iproduct.iproduct_gluten_status == gluten_status
        ).all()


def delete_all_iproducts() -> int:
    """
    Delete all iproducts from the database.
    
    Returns:
        Number of products deleted
    """
    with session_scope() as session:
        count = session.query(models.Iproduct).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} iproducts")
        return count


def update_iproduct_price(barcode: str, new_price: float) -> bool:
    """
    Update the price of an iproduct.
    
    Args:
        barcode: Product barcode
        new_price: New price
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        product = session.query(models.Iproduct).filter(
            models.Iproduct.iproduct_barcode == barcode
        ).first()
        
        if not product:
            logger.warning(f"Iproduct not found with barcode: {barcode}")
            return False
        
        product.iproduct_estimated_price = Decimal(str(new_price))
        product.iproduct_last_price_update = datetime.now()
        session.commit()
        logger.debug(f"Updated price for product: {barcode} -> {new_price}")
        return True


def update_iproduct_image(barcode: str, image_url: str) -> bool:
    """
    Update the image URL of an iproduct.
    
    Args:
        barcode: Product barcode
        image_url: New image URL
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        product = session.query(models.Iproduct).filter(
            models.Iproduct.iproduct_barcode == barcode
        ).first()
        
        if not product:
            logger.warning(f"Iproduct not found with barcode: {barcode}")
            return False
        
        product.iproduct_image_url = image_url
        session.commit()
        logger.debug(f"Updated image for product: {barcode}")
        return True


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding iproducts."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed iproducts (external/imported products)")
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing iproducts before seeding"
    )
    parser.add_argument(
        "--random",
        type=int,
        default=0,
        help="Generate and seed random iproducts (specify count)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    print("🌱 Starting iproduct seeding...")
    
    try:
        if args.delete_first:
            delete_all_iproducts()
        
        count = 0
        
        if args.random > 0:
            count = seed_random_iproducts(args.random)
            print(f"✅ Successfully seeded {count} random iproducts")
        else:
            count = seed_iproducts()
            print(f"✅ Successfully seeded {count} iproducts")
        
        # Show seeded iproducts
        if count > 0:
            products = get_all_seeded_iproducts()
            print(f"\n📋 Seeded {len(products)} iproducts:")
            
            # Group by category
            from collections import defaultdict
            grouped = defaultdict(list)
            for p in products:
                grouped[p['category_id']].append(p)
            
            for category_id, product_list in sorted(grouped.items()):
                print(f"\n  Category ID: {category_id}")
                for p in product_list[:5]:  # Show first 5 per category
                    print(f"    - {p['name']} (ID: {p['id']}, Price: {p['price']} {p['currency']})")
                if len(product_list) > 5:
                    print(f"      ... and {len(product_list) - 5} more")
        
    except Exception as e:
        print(f"❌ Failed to seed iproducts: {e}")
        raise


if __name__ == "__main__":
    main()