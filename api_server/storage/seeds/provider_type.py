# storage/seeds/product_provider_type.py
"""
Product provider type seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List, Optional

from storage.storage_broker import insert_record, get, session_scope
from core import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_PROVIDER_TYPES = [
    {"product_provider_type_name": "Restaurant"},
    {"product_provider_type_name": "Bakery"},
    {"product_provider_type_name": "Factory"},
    {"product_provider_type_name": "Supermarket"},
    {"product_provider_type_name": "Grocery Store"},
    {"product_provider_type_name": "Distributor"},
]

# Optional: Provider types with icon URLs
SEED_PROVIDER_TYPES_WITH_ICONS = [
    {"product_provider_type_name": "Restaurant", "product_provider_type_icon_url": "https://example.com/icons/restaurant.png"},
    {"product_provider_type_name": "Bakery", "product_provider_type_icon_url": "https://example.com/icons/bakery.png"},
    {"product_provider_type_name": "Factory", "product_provider_type_icon_url": "https://example.com/icons/factory.png"},
    {"product_provider_type_name": "Supermarket", "product_provider_type_icon_url": "https://example.com/icons/supermarket.png"},
    {"product_provider_type_name": "Grocery Store", "product_provider_type_icon_url": "https://example.com/icons/grocery.png"},
    {"product_provider_type_name": "Distributor", "product_provider_type_icon_url": "https://example.com/icons/distributor.png"},
]


# ==================== Seeding Functions ====================

def seed_product_provider_types(use_icons: bool = False) -> int:
    """
    Seed product provider types using the storage broker's insert_record function.
    
    Args:
        use_icons: If True, use the version with icon URLs
        
    Returns:
        Number of provider types inserted
    """
    provider_types_data = SEED_PROVIDER_TYPES_WITH_ICONS if use_icons else SEED_PROVIDER_TYPES
    count_inserted = 0
    
    for provider_type_data in provider_types_data:
        # Check if provider type already exists
        existing = get(
            table=models.ProductProviderType,
            conditions={"product_provider_type_name": provider_type_data["product_provider_type_name"]}
        )
        
        if not existing:
            # Create provider type instance
            provider_type = models.ProductProviderType(
                product_provider_type_name=provider_type_data["product_provider_type_name"],
                product_provider_type_icon_url=provider_type_data.get("product_provider_type_icon_url"),
                product_provider_type_naming_ref=None,  # Set if you have naming_contribution references
            )
            # Insert using broker
            result = insert_record(provider_type)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded product provider type: {provider_type_data['product_provider_type_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} product provider types")
    return count_inserted


def seed_product_provider_type(provider_type_data: Dict[str, Any]) -> bool:
    """
    Seed a single product provider type.
    
    Args:
        provider_type_data: Provider type data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": provider_type_data.get("product_provider_type_name")}
    )
    
    if existing:
        logger.debug(f"Provider type already exists: {provider_type_data.get('product_provider_type_name')}")
        return False
    
    provider_type = models.ProductProviderType(
        product_provider_type_name=provider_type_data.get("product_provider_type_name"),
        product_provider_type_icon_url=provider_type_data.get("product_provider_type_icon_url"),
        product_provider_type_naming_ref=provider_type_data.get("product_provider_type_naming_ref"),
    )
    result = insert_record(provider_type)
    if result:
        logger.debug(f"Seeded product provider type: {provider_type_data.get('product_provider_type_name')}")
    return bool(result)


def seed_product_provider_types_from_list(provider_types: List[Dict[str, Any]]) -> int:
    """
    Seed product provider types from a custom list.
    
    Args:
        provider_types: List of provider type dictionaries
        
    Returns:
        Number of provider types inserted
    """
    count_inserted = 0
    
    for provider_type_data in provider_types:
        # Check if provider type already exists
        existing = get(
            table=models.ProductProviderType,
            conditions={"product_provider_type_name": provider_type_data.get("product_provider_type_name")}
        )
        
        if not existing:
            provider_type = models.ProductProviderType(
                product_provider_type_name=provider_type_data.get("product_provider_type_name"),
                product_provider_type_icon_url=provider_type_data.get("product_provider_type_icon_url"),
                product_provider_type_naming_ref=provider_type_data.get("product_provider_type_naming_ref"),
            )
            result = insert_record(provider_type)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded product provider type: {provider_type_data.get('product_provider_type_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} product provider types from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_provider_types() -> List[Dict[str, Any]]:
    """
    Get all seeded provider types from the database.
    
    Returns:
        List of provider type dictionaries
    """
    with session_scope() as session:
        provider_types = session.query(models.ProductProviderType).all()
        return [
            {
                "id": pt.id_product_provider_type,
                "name": pt.product_provider_type_name,
                "icon_url": pt.product_provider_type_icon_url,
                "naming_ref": pt.product_provider_type_naming_ref,
            }
            for pt in provider_types
        ]


def provider_type_exists(provider_type_name: str) -> bool:
    """
    Check if a provider type already exists in the database.
    
    Args:
        provider_type_name: Name of the provider type to check
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": provider_type_name}
    )
    return bool(existing)


def get_provider_type_by_name(provider_type_name: str) -> Optional[models.ProductProviderType]:
    """
    Get a provider type by name.
    
    Args:
        provider_type_name: Name of the provider type
        
    Returns:
        ProductProviderType instance or None
    """
    result = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": provider_type_name}
    )
    return result[0] if result else None


def get_provider_type_by_id(provider_type_id: int) -> Optional[models.ProductProviderType]:
    """
    Get a provider type by ID.
    
    Args:
        provider_type_id: ID of the provider type
        
    Returns:
        ProductProviderType instance or None
    """
    result = get(
        table=models.ProductProviderType,
        conditions={"id_product_provider_type": provider_type_id}
    )
    return result[0] if result else None


def delete_all_product_provider_types() -> int:
    """
    Delete all product provider types from the database.
    
    Returns:
        Number of provider types deleted
    """
    with session_scope() as session:
        count = session.query(models.ProductProviderType).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} product provider types")
        return count


def update_provider_type_icon(provider_type_name: str, icon_url: str) -> bool:
    """
    Update the icon URL for a provider type.
    
    Args:
        provider_type_name: Name of the provider type
        icon_url: New icon URL
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        provider_type = session.query(models.ProductProviderType).filter(
            models.ProductProviderType.product_provider_type_name == provider_type_name
        ).first()
        
        if not provider_type:
            logger.warning(f"Provider type not found: {provider_type_name}")
            return False
        
        provider_type.product_provider_type_icon_url = icon_url
        session.commit()
        logger.debug(f"Updated icon for provider type: {provider_type_name}")
        return True


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding product provider types."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed product provider types")
    parser.add_argument(
        "--with-icons", 
        action="store_true",
        help="Use provider types with icon URLs"
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing provider types before seeding"
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
    
    print("🌱 Starting product provider type seeding...")
    
    try:
        if args.delete_first:
            delete_all_product_provider_types()
        
        count = seed_product_provider_types(use_icons=args.with_icons)
        print(f"✅ Successfully seeded {count} product provider types")
        
        # Show seeded provider types
        if count > 0:
            provider_types = get_all_seeded_provider_types()
            print("\n📋 Seeded provider types:")
            for pt in provider_types:
                icon_info = f" (icon: {pt['icon_url']})" if pt['icon_url'] else ""
                print(f"  - {pt['name']} (ID: {pt['id']}){icon_info}")
        
    except Exception as e:
        print(f"❌ Failed to seed product provider types: {e}")
        raise


if __name__ == "__main__":
    main()