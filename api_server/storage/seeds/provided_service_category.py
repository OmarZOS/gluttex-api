# storage/seeds/provided_service_category.py
"""
Provided service category seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_SERVICE_CATEGORIES = [
    {
        "provided_service_category_name": "Blood Testing",
        "provided_service_category_icon_url": "https://example.com/icons/blood-test.svg",
        "provided_service_category_avg_duration": Decimal("30.00"),
        "provided_service_category_description": "Complete blood count, cholesterol, glucose, and other blood tests"
    },
    {
        "provided_service_category_name": "Diagnostic Imaging",
        "provided_service_category_icon_url": "https://example.com/icons/xray.svg",
        "provided_service_category_avg_duration": Decimal("45.00"),
        "provided_service_category_description": "X-rays, MRIs, CT scans, and ultrasound services"
    },
    {
        "provided_service_category_name": "Vaccination",
        "provided_service_category_icon_url": "https://example.com/icons/vaccine.svg",
        "provided_service_category_avg_duration": Decimal("15.00"),
        "provided_service_category_description": "Routine immunizations and travel vaccinations"
    },
    {
        "provided_service_category_name": "Health Check-up",
        "provided_service_category_icon_url": "https://example.com/icons/stethoscope.svg",
        "provided_service_category_avg_duration": Decimal("60.00"),
        "provided_service_category_description": "Comprehensive annual physical examinations"
    },
    {
        "provided_service_category_name": "Dental Care",
        "provided_service_category_icon_url": "https://example.com/icons/dental.svg",
        "provided_service_category_avg_duration": Decimal("40.00"),
        "provided_service_category_description": "Teeth cleaning, fillings, and basic dental procedures"
    },
    {
        "provided_service_category_name": "Pathology Tests",
        "provided_service_category_icon_url": "https://example.com/icons/microscope.svg",
        "provided_service_category_avg_duration": Decimal("120.00"),
        "provided_service_category_description": "Tissue biopsy analysis and histopathology"
    },
    {
        "provided_service_category_name": "Urine Analysis",
        "provided_service_category_icon_url": "https://example.com/icons/urine-test.svg",
        "provided_service_category_avg_duration": Decimal("20.00"),
        "provided_service_category_description": "Complete urinalysis and culture tests"
    },
    {
        "provided_service_category_name": "Allergy Testing",
        "provided_service_category_icon_url": "https://example.com/icons/allergy.svg",
        "provided_service_category_avg_duration": Decimal("90.00"),
        "provided_service_category_description": "Skin prick tests and allergen screening"
    },
    {
        "provided_service_category_name": "Genetic Testing",
        "provided_service_category_icon_url": "https://example.com/icons/dna.svg",
        "provided_service_category_avg_duration": Decimal("180.00"),
        "provided_service_category_description": "DNA analysis and genetic screening services"
    },
    {
        "provided_service_category_name": "Physiotherapy",
        "provided_service_category_icon_url": "https://example.com/icons/physical-therapy.svg",
        "provided_service_category_avg_duration": Decimal("50.00"),
        "provided_service_category_description": "Rehabilitation and physical therapy sessions"
    },
    {
        "provided_service_category_name": "Nutrition Counseling",
        "provided_service_category_icon_url": "https://example.com/icons/nutrition.svg",
        "provided_service_category_avg_duration": Decimal("45.00"),
        "provided_service_category_description": "Diet planning and nutritional guidance"
    },
    {
        "provided_service_category_name": "Mental Health Counseling",
        "provided_service_category_icon_url": "https://example.com/icons/mental-health.svg",
        "provided_service_category_avg_duration": Decimal("60.00"),
        "provided_service_category_description": "Therapy and psychological counseling sessions"
    },
    {
        "provided_service_category_name": "Acupuncture",
        "provided_service_category_icon_url": "https://example.com/icons/acupuncture.svg",
        "provided_service_category_avg_duration": Decimal("40.00"),
        "provided_service_category_description": "Traditional acupuncture therapy sessions"
    },
    {
        "provided_service_category_name": "Prenatal Care",
        "provided_service_category_icon_url": "https://example.com/icons/pregnancy.svg",
        "provided_service_category_avg_duration": Decimal("30.00"),
        "provided_service_category_description": "Pregnancy monitoring and prenatal check-ups"
    },
    {
        "provided_service_category_name": "Pediatric Care",
        "provided_service_category_icon_url": "https://example.com/icons/baby-care.svg",
        "provided_service_category_avg_duration": Decimal("25.00"),
        "provided_service_category_description": "Child healthcare and development monitoring"
    },
    {
        "provided_service_category_name": "Geriatric Care",
        "provided_service_category_icon_url": "https://example.com/icons/elderly-care.svg",
        "provided_service_category_avg_duration": Decimal("40.00"),
        "provided_service_category_description": "Elderly health monitoring and management"
    },
    {
        "provided_service_category_name": "Sports Medicine",
        "provided_service_category_icon_url": "https://example.com/icons/sports-medicine.svg",
        "provided_service_category_avg_duration": Decimal("50.00"),
        "provided_service_category_description": "Injury assessment and sports-related healthcare"
    },
    {
        "provided_service_category_name": "First Aid Training",
        "provided_service_category_icon_url": "https://example.com/icons/first-aid.svg",
        "provided_service_category_avg_duration": Decimal("240.00"),
        "provided_service_category_description": "CPR and emergency first aid certification"
    },
    {
        "provided_service_category_name": "Minor Surgery",
        "provided_service_category_icon_url": "https://example.com/icons/surgery.svg",
        "provided_service_category_avg_duration": Decimal("75.00"),
        "provided_service_category_description": "Outpatient minor surgical procedures"
    },
    {
        "provided_service_category_name": "Wound Care",
        "provided_service_category_icon_url": "https://example.com/icons/wound-care.svg",
        "provided_service_category_avg_duration": Decimal("25.00"),
        "provided_service_category_description": "Dressing changes and wound management"
    },
    {
        "provided_service_category_name": "IV Therapy",
        "provided_service_category_icon_url": "https://example.com/icons/iv-therapy.svg",
        "provided_service_category_avg_duration": Decimal("35.00"),
        "provided_service_category_description": "Intravenous hydration and vitamin therapy"
    },
]


# ==================== Seeding Functions ====================

def seed_service_categories() -> int:
    """
    Seed provided service categories using the storage broker's insert_record function.
    
    Returns:
        Number of service categories inserted
    """
    count_inserted = 0
    
    for category_data in SEED_SERVICE_CATEGORIES:
        # Check if category already exists
        existing = get(
            table=models.ProvidedServiceCategory,
            conditions={
                "provided_service_category_name": category_data["provided_service_category_name"]
            }
        )
        
        if not existing:
            # Create category instance
            category = models.ProvidedServiceCategory(
                provided_service_category_name=category_data["provided_service_category_name"],
                provided_service_category_icon_url=category_data["provided_service_category_icon_url"],
                provided_service_category_avg_duration=category_data["provided_service_category_avg_duration"],
                provided_service_category_description=category_data["provided_service_category_description"],
                provided_service_category_naming_ref=None,  # Set if you have naming_contribution references
            )
            # Insert using broker
            result = insert_record(category)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded service category: {category_data['provided_service_category_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} provided service categories")
    return count_inserted


def seed_service_category(category_data: Dict[str, Any]) -> bool:
    """
    Seed a single provided service category.
    
    Args:
        category_data: Category data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.ProvidedServiceCategory,
        conditions={
            "provided_service_category_name": category_data.get("provided_service_category_name")
        }
    )
    
    if existing:
        logger.debug(f"Service category already exists: {category_data.get('provided_service_category_name')}")
        return False
    
    category = models.ProvidedServiceCategory(
        provided_service_category_name=category_data.get("provided_service_category_name"),
        provided_service_category_icon_url=category_data.get("provided_service_category_icon_url"),
        provided_service_category_avg_duration=category_data.get("provided_service_category_avg_duration"),
        provided_service_category_description=category_data.get("provided_service_category_description"),
        provided_service_category_naming_ref=category_data.get("provided_service_category_naming_ref"),
    )
    result = insert_record(category)
    if result:
        logger.debug(f"Seeded service category: {category_data.get('provided_service_category_name')}")
    return bool(result)


def seed_service_categories_from_list(categories: List[Dict[str, Any]]) -> int:
    """
    Seed provided service categories from a custom list.
    
    Args:
        categories: List of category dictionaries
        
    Returns:
        Number of categories inserted
    """
    count_inserted = 0
    
    for category_data in categories:
        # Check if category already exists
        existing = get(
            table=models.ProvidedServiceCategory,
            conditions={
                "provided_service_category_name": category_data.get("provided_service_category_name")
            }
        )
        
        if not existing:
            category = models.ProvidedServiceCategory(
                provided_service_category_name=category_data.get("provided_service_category_name"),
                provided_service_category_icon_url=category_data.get("provided_service_category_icon_url"),
                provided_service_category_avg_duration=category_data.get("provided_service_category_avg_duration"),
                provided_service_category_description=category_data.get("provided_service_category_description"),
                provided_service_category_naming_ref=category_data.get("provided_service_category_naming_ref"),
            )
            result = insert_record(category)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded service category: {category_data.get('provided_service_category_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} provided service categories from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_service_categories() -> List[Dict[str, Any]]:
    """
    Get all seeded service categories from the database.
    
    Returns:
        List of category dictionaries
    """
    with session_scope() as session:
        categories = session.query(models.ProvidedServiceCategory).all()
        return [
            {
                "id": cat.provided_service_category_id,
                "name": cat.provided_service_category_name,
                "icon_url": cat.provided_service_category_icon_url,
                "avg_duration": float(cat.provided_service_category_avg_duration) if cat.provided_service_category_avg_duration else None,
                "description": cat.provided_service_category_description,
                "naming_ref": cat.provided_service_category_naming_ref,
            }
            for cat in categories
        ]


def service_category_exists(category_name: str) -> bool:
    """
    Check if a service category already exists in the database.
    
    Args:
        category_name: Name of the category to check
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": category_name}
    )
    return bool(existing)


def get_service_category_by_name(category_name: str) -> Optional[models.ProvidedServiceCategory]:
    """
    Get a service category by name.
    
    Args:
        category_name: Name of the category
        
    Returns:
        ProvidedServiceCategory instance or None
    """
    result = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": category_name}
    )
    return result[0] if result else None


def get_service_category_by_id(category_id: int) -> Optional[models.ProvidedServiceCategory]:
    """
    Get a service category by ID.
    
    Args:
        category_id: ID of the category
        
    Returns:
        ProvidedServiceCategory instance or None
    """
    result = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_id": category_id}
    )
    return result[0] if result else None


def get_service_categories_by_duration(max_duration: int) -> List[models.ProvidedServiceCategory]:
    """
    Get service categories with average duration less than or equal to max_duration.
    
    Args:
        max_duration: Maximum average duration in minutes
        
    Returns:
        List of ProvidedServiceCategory instances
    """
    with session_scope() as session:
        return session.query(models.ProvidedServiceCategory).filter(
            models.ProvidedServiceCategory.provided_service_category_avg_duration <= max_duration
        ).all()


def delete_all_service_categories() -> int:
    """
    Delete all provided service categories from the database.
    
    Returns:
        Number of categories deleted
    """
    with session_scope() as session:
        count = session.query(models.ProvidedServiceCategory).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} provided service categories")
        return count


def update_service_category_duration(category_name: str, avg_duration: Decimal) -> bool:
    """
    Update the average duration for a service category.
    
    Args:
        category_name: Name of the category
        avg_duration: New average duration in minutes
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        category = session.query(models.ProvidedServiceCategory).filter(
            models.ProvidedServiceCategory.provided_service_category_name == category_name
        ).first()
        
        if not category:
            logger.warning(f"Service category not found: {category_name}")
            return False
        
        category.provided_service_category_avg_duration = avg_duration
        session.commit()
        logger.debug(f"Updated duration for service category: {category_name}")
        return True


def update_service_category_icon(category_name: str, icon_url: str) -> bool:
    """
    Update the icon URL for a service category.
    
    Args:
        category_name: Name of the category
        icon_url: New icon URL
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        category = session.query(models.ProvidedServiceCategory).filter(
            models.ProvidedServiceCategory.provided_service_category_name == category_name
        ).first()
        
        if not category:
            logger.warning(f"Service category not found: {category_name}")
            return False
        
        category.provided_service_category_icon_url = icon_url
        session.commit()
        logger.debug(f"Updated icon for service category: {category_name}")
        return True


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding provided service categories."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed provided service categories")
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing service categories before seeding"
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
    
    print("🌱 Starting provided service category seeding...")
    
    try:
        if args.delete_first:
            delete_all_service_categories()
        
        count = seed_service_categories()
        print(f"✅ Successfully seeded {count} provided service categories")
        
        # Show seeded categories
        if count > 0:
            categories = get_all_seeded_service_categories()
            print("\n📋 Seeded service categories:")
            for cat in categories:
                duration = f"{cat['avg_duration']} min" if cat['avg_duration'] else "N/A"
                icon_info = f" (icon: {cat['icon_url']})" if cat['icon_url'] else ""
                print(f"  - {cat['name']} (ID: {cat['id']}, Duration: {duration}){icon_info}")
        
    except Exception as e:
        print(f"❌ Failed to seed provided service categories: {e}")
        raise


if __name__ == "__main__":
    main()