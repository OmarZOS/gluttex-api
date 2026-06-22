# storage/seed.py (main seed orchestrator)
"""
Database seeding module for DEV environment.
Populates the database with initial test data.
"""

from sqlalchemy import inspect
import logging
from typing import Dict, Any

import config
from storage.storage_broker import get_engine, session_scope, get, text
from storage.seeds.product_category import seed_product_categories
from storage.seeds.recipe_category import seed_recipe_categories
from storage.seeds.provider_type import seed_product_provider_types
from storage.seeds.provided_service_category import seed_service_categories
from storage.seeds.staff_role import seed_staff_roles
from storage.seeds.ingredient import seed_ingredients
from config import settings
from core import models

logger = logging.getLogger(__name__)


# ==================== Seed Functions ====================

def seed_database(
    with_icons: bool = False,
    with_quantifiers: bool = False
) -> Dict[str, Any]:
    """
    Run all seed functions.
    
    Args:
        with_icons: Whether to seed with icon URLs
        with_quantifiers: Whether to seed ingredients with quantifiers
        
    Returns:
        Dictionary with seeding results
    """
    logger.info("🌱 Starting database seeding...")
    
    results = {
        "product_categories": 0,
        "recipe_categories": 0,
        "product_provider_types": 0,
        "service_categories": 0,
        "staff_roles": 0,
        "ingredients": 0,
        "total": 0,
    }
    
    try:
        # Seed product categories
        logger.info("Seeding product categories...")
        results["product_categories"] = seed_product_categories()
        
        # Seed recipe categories
        logger.info("Seeding recipe categories...")
        results["recipe_categories"] = seed_recipe_categories(use_icons=with_icons)
        
        # Seed product provider types
        logger.info("Seeding product provider types...")
        results["product_provider_types"] = seed_product_provider_types(use_icons=with_icons)
        
        # Seed provided service categories
        logger.info("Seeding provided service categories...")
        results["service_categories"] = seed_service_categories()
        
        # Seed staff roles
        logger.info("Seeding staff roles...")
        results["staff_roles"] = seed_staff_roles()
        
        # Seed ingredients
        logger.info("Seeding ingredients...")
        results["ingredients"] = seed_ingredients(use_quantifiers=with_quantifiers)
        
        results["total"] = sum([
            results["product_categories"],
            results["recipe_categories"],
            results["product_provider_types"],
            results["service_categories"],
            results["staff_roles"],
            results["ingredients"],
        ])
        
        logger.info(f"✅ Seeding complete! Total records inserted: {results['total']}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise


def get_seed_status() -> Dict[str, Any]:
    """
    Get the current seeding status.
    
    Returns:
        Dictionary with seeding status information
    """
    try:
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        status = {
            "has_tables": bool(tables),
            # "tables": tables,
            "has_product_categories": False,
            "has_recipe_categories": False,
            "has_product_provider_types": False,
            "has_service_categories": False,
            "has_staff_roles": False,
            "has_ingredients": False,
            "product_category_count": 0,
            "recipe_category_count": 0,
            "product_provider_type_count": 0,
            "service_category_count": 0,
            "staff_role_count": 0,
            "ingredient_count": 0,
            "needs_seeding": True,
        }
        
        # Check each table
        table_checks = [
            ('product_category', 'has_product_categories', 'product_category_count'),
            ('recipe_category', 'has_recipe_categories', 'recipe_category_count'),
            ('product_provider_type', 'has_product_provider_types', 'product_provider_type_count'),
            ('provided_service_category', 'has_service_categories', 'service_category_count'),
            ('staff_role', 'has_staff_roles', 'staff_role_count'),
            ('ingredient', 'has_ingredients', 'ingredient_count'),
        ]
        
        for table_name, has_flag, count_field in table_checks:
            if table_name in tables:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    status[has_flag] = count > 0
                    status[count_field] = count
        
        # Determine if seeding is needed (any table is empty)
        status["needs_seeding"] = not all([
            status["has_product_categories"],
            status["has_recipe_categories"],
            status["has_product_provider_types"],
            status["has_service_categories"],
            status["has_staff_roles"],
            status["has_ingredients"],
        ])
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get seed status: {e}")
        return {
            "has_tables": False,
            "tables": [],
            "has_product_categories": False,
            "has_recipe_categories": False,
            "has_product_provider_types": False,
            "has_service_categories": False,
            "has_staff_roles": False,
            "has_ingredients": False,
            "product_category_count": 0,
            "recipe_category_count": 0,
            "product_provider_type_count": 0,
            "service_category_count": 0,
            "staff_role_count": 0,
            "ingredient_count": 0,
            "needs_seeding": True,
            "error": str(e)
        }


def needs_seeding() -> bool:
    """
    Check if the database needs seeding.
    
    Returns:
        True if database is empty or needs seeding, False otherwise
    """
    try:
        engine = get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # If no tables exist, we need seeding
        if not tables:
            logger.info("No tables found - seeding needed")
            return True
        
        # Check each table
        table_checks = [
            'product_category',
            'recipe_category',
            'product_provider_type',
            'provided_service_category',
            'staff_role',
            'ingredient',
        ]
        
        all_have_data = True
        for table_name in table_checks:
            if table_name in tables:
                with engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    if count == 0:
                        logger.info(f"Table '{table_name}' is empty - seeding needed")
                        all_have_data = False
                        break
            else:
                logger.info(f"Table '{table_name}' doesn't exist - seeding needed")
                all_have_data = False
                break
        
        if all_have_data:
            logger.info("All tables have data - no seeding needed")
        
        return not all_have_data
        
    except Exception as e:
        logger.warning(f"Failed to check seeding need: {e}")
        # If we can't check, assume seeding is needed
        return True


def seed_database_if_needed():
    """
    Seed the database with initial data if in DEV mode and seeding is needed.
    This function is meant to be called during application startup.
    """
    # Check if we're in DEV mode (DEBUG != "PRODUCTION")
    is_dev = settings.DEBUG != "PRODUCTION"
    if not is_dev:
        logger.info("Not in DEV mode - skipping database seeding")
        return
    
    try:
        # Check if seeding is needed
        if not needs_seeding():
            logger.info("Database already has seed data - skipping seeding")
            return
        
        logger.info("🌱 Starting database seeding in DEV mode...")
        
        # Run the seed
        seed_database()
        logger.info("✅ Database seeding completed successfully")
        
        # Log seed status
        status = get_seed_status()
        logger.info(f"📊 Seed status: {status}")
            
    except Exception as e:
        logger.error(f"❌ Failed to seed database: {e}")
        # Don't raise - let the application start anyway


# ==================== CLI Seeding Function ====================

def seed_database_cli():
    """
    Run database seeding from command line.
    Usage: python -m storage.seed
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed the database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force seeding even if data already exists"
    )
    parser.add_argument(
        "--with-icons",
        action="store_true",
        help="Seed with icon URLs (for categories and provider types)"
    )
    parser.add_argument(
        "--with-quantifiers",
        action="store_true",
        help="Seed ingredients with quantifiers"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all seeded tables before seeding"
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
    
    print("🌱 Starting database seeding...")
    
    try:
        if args.clear_all:
            print("Clearing all seeded tables...")
            with session_scope() as db:
                # Delete in reverse order of dependencies
                db.query(models.StaffRole).delete()
                db.query(models.ProvidedServiceCategory).delete()
                db.query(models.Ingredient).delete()
                db.query(models.RecipeCategory).delete()
                db.query(models.ProductProviderType).delete()
                db.query(models.ProductCategory).delete()
                db.commit()
            print("Cleared all seeded tables")
        elif args.force:
            print("Force seeding enabled - checking existing data...")
        
        results = seed_database(
            with_icons=args.with_icons,
            with_quantifiers=args.with_quantifiers
        )
        
        print(f"\n✅ Seeding complete!")
        print(f"   Product Categories: {results['product_categories']}")
        print(f"   Recipe Categories: {results['recipe_categories']}")
        print(f"   Product Provider Types: {results['product_provider_types']}")
        print(f"   Service Categories: {results['service_categories']}")
        print(f"   Staff Roles: {results['staff_roles']}")
        print(f"   Ingredients: {results['ingredients']}")
        print(f"   Total: {results['total']}")
        
        # Show status
        status = get_seed_status()
        print(f"\n📊 Database Status:")
        print(f"   Product Categories: {status['product_category_count']}")
        print(f"   Recipe Categories: {status['recipe_category_count']}")
        print(f"   Product Provider Types: {status['product_provider_type_count']}")
        print(f"   Service Categories: {status['service_category_count']}")
        print(f"   Staff Roles: {status['staff_role_count']}")
        print(f"   Ingredients: {status['ingredient_count']}")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        raise


# ==================== Module Export ====================

__all__ = [
    'seed_database',
    'seed_database_if_needed',
    'needs_seeding',
    'get_seed_status',
    'seed_database_cli',
]


# ==================== CLI Entry Point ====================

if __name__ == "__main__":
    seed_database_cli()