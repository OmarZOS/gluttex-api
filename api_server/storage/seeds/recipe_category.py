# storage/seeds/recipe_category.py
"""
Recipe category seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List

from storage.storage_broker import insert_record, get, session_scope
from core import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_RECIPE_CATEGORIES = [
    {"recipe_category_name": "Appetizers & Snacks"},
    {"recipe_category_name": "Soups & Stews"},
    {"recipe_category_name": "Salads"},
    {"recipe_category_name": "Main Courses"},
    {"recipe_category_name": "Side Dishes"},
    {"recipe_category_name": "Pasta & Noodles"},
    {"recipe_category_name": "Casseroles"},
    {"recipe_category_name": "Breakfast & Brunch"},
    {"recipe_category_name": "Breads & Baking"},
    {"recipe_category_name": "Desserts"},
    {"recipe_category_name": "Drinks & Beverages"},
    {"recipe_category_name": "Sauces & Condiments"},
    {"recipe_category_name": "International Cuisine"},
    {"recipe_category_name": "Healthy & Special Diets"},
    {"recipe_category_name": "Holiday & Seasonal"},
    {"recipe_category_name": "Kids & Family"},
    {"recipe_category_name": "Slow Cooker & Instant Pot"},
    {"recipe_category_name": "Quick & Easy"},
    {"recipe_category_name": "One-Pan Recipes"},
    {"recipe_category_name": "Grilling & BBQ"},
]

# Optional: Categories with icon URLs
SEED_RECIPE_CATEGORIES_WITH_ICONS = [
    {"recipe_category_name": "Appetizers & Snacks", "recipe_category_icon_url": "https://example.com/icons/appetizers.png"},
    {"recipe_category_name": "Soups & Stews", "recipe_category_icon_url": "https://example.com/icons/soups.png"},
    {"recipe_category_name": "Salads", "recipe_category_icon_url": "https://example.com/icons/salads.png"},
    {"recipe_category_name": "Main Courses", "recipe_category_icon_url": "https://example.com/icons/main-courses.png"},
    {"recipe_category_name": "Desserts", "recipe_category_icon_url": "https://example.com/icons/desserts.png"},
    # ... add more as needed
]


# ==================== Seeding Function ====================

def seed_recipe_categories(use_icons: bool = False) -> int:
    """
    Seed recipe categories using the storage broker's insert_record function.
    
    Args:
        use_icons: If True, use the version with icon URLs
        
    Returns:
        Number of categories inserted
    """
    categories_data = SEED_RECIPE_CATEGORIES_WITH_ICONS if use_icons else SEED_RECIPE_CATEGORIES
    count_inserted = 0
    
    for category_data in categories_data:
        # Check if category already exists using get
        existing = get(
            table=models.RecipeCategory,
            conditions={"recipe_category_name": category_data["recipe_category_name"]}
        )
        
        if not existing:
            # Create category instance
            category = models.RecipeCategory(
                recipe_category_name=category_data["recipe_category_name"],
                recipe_category_icon_url=category_data.get("recipe_category_icon_url"),
                recipe_category_naming=None,  # Set if you have naming_contribution references
            )
            # Insert using broker
            result = insert_record(category)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded recipe category: {category_data['recipe_category_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} recipe categories")
    return count_inserted


def seed_recipe_categories_from_list(categories: List[Dict[str, Any]]) -> int:
    """
    Seed recipe categories from a custom list.
    
    Args:
        categories: List of category dictionaries
        
    Returns:
        Number of categories inserted
    """
    count_inserted = 0
    
    for category_data in categories:
        # Check if category already exists
        existing = get(
            table=models.RecipeCategory,
            conditions={"recipe_category_name": category_data.get("recipe_category_name")}
        )
        
        if not existing:
            category = models.RecipeCategory(
                recipe_category_name=category_data.get("recipe_category_name"),
                recipe_category_icon_url=category_data.get("recipe_category_icon_url"),
                recipe_category_naming=category_data.get("recipe_category_naming"),
            )
            result = insert_record(category)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded recipe category: {category_data.get('recipe_category_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} recipe categories from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_categories() -> List[Dict[str, Any]]:
    """
    Get all seeded categories from the database.
    
    Returns:
        List of category dictionaries
    """
    with session_scope() as session:
        categories = session.query(models.RecipeCategory).all()
        return [
            {
                "id": cat.id_recipe_category,
                "name": cat.recipe_category_name,
                "icon_url": cat.recipe_category_icon_url,
            }
            for cat in categories
        ]


def category_exists(category_name: str) -> bool:
    """
    Check if a category already exists in the database.
    
    Args:
        category_name: Name of the category to check
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.RecipeCategory,
        conditions={"recipe_category_name": category_name}
    )
    return bool(existing)


def seed_recipe_category(category_data: Dict[str, Any]) -> bool:
    """
    Seed a single recipe category.
    
    Args:
        category_data: Category data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.RecipeCategory,
        conditions={"recipe_category_name": category_data.get("recipe_category_name")}
    )
    
    if existing:
        logger.debug(f"Category already exists: {category_data.get('recipe_category_name')}")
        return False
    
    category = models.RecipeCategory(
        recipe_category_name=category_data.get("recipe_category_name"),
        recipe_category_icon_url=category_data.get("recipe_category_icon_url"),
        recipe_category_naming=category_data.get("recipe_category_naming"),
    )
    result = insert_record(category)
    if result:
        logger.debug(f"Seeded recipe category: {category_data.get('recipe_category_name')}")
    return bool(result)


def delete_all_recipe_categories() -> int:
    """
    Delete all recipe categories from the database.
    
    Returns:
        Number of categories deleted
    """
    with session_scope() as session:
        count = session.query(models.RecipeCategory).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} recipe categories")
        return count


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding recipe categories."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed recipe categories")
    parser.add_argument(
        "--with-icons", 
        action="store_true",
        help="Use categories with icon URLs"
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing categories before seeding"
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
    
    print("🌱 Starting recipe category seeding...")
    
    try:
        if args.delete_first:
            delete_all_recipe_categories()
        
        count = seed_recipe_categories(use_icons=args.with_icons)
        print(f"✅ Successfully seeded {count} recipe categories")
        
        # Show seeded categories
        if count > 0:
            categories = get_all_seeded_categories()
            print("\n📋 Seeded categories:")
            for cat in categories:
                print(f"  - {cat['name']} (ID: {cat['id']})")
        
    except Exception as e:
        print(f"❌ Failed to seed recipe categories: {e}")
        raise


if __name__ == "__main__":
    main()