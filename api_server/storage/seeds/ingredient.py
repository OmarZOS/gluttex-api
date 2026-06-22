# storage/seeds/ingredient.py
"""
Ingredient seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List, Optional

from storage.storage_broker import insert_record, get, session_scope
from core import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_INGREDIENTS = [
    # Grains
    {"ingredient_name": "Wheat"},
    {"ingredient_name": "Barley"},
    {"ingredient_name": "Rye"},
    {"ingredient_name": "Oats"},
    {"ingredient_name": "Corn"},
    {"ingredient_name": "Rice"},
    {"ingredient_name": "Soy"},
    {"ingredient_name": "Buckwheat"},
    
    # Dairy
    {"ingredient_name": "Milk"},
    {"ingredient_name": "Butter"},
    {"ingredient_name": "Margarine"},
    
    # Proteins
    {"ingredient_name": "Egg"},
    {"ingredient_name": "Peanuts"},
    {"ingredient_name": "Tree Nuts"},
    {"ingredient_name": "Fish"},
    {"ingredient_name": "Shellfish"},
    {"ingredient_name": "Lentils"},
    {"ingredient_name": "Chickpeas"},
    {"ingredient_name": "Lupin"},
    
    # Nuts & Seeds
    {"ingredient_name": "Almond"},
    {"ingredient_name": "Coconut"},
    {"ingredient_name": "Sunflower Seeds"},
    {"ingredient_name": "Pumpkin Seeds"},
    {"ingredient_name": "Sesame Seeds"},
    
    # Vegetables
    {"ingredient_name": "Potato"},
    {"ingredient_name": "Sweet Potato"},
    {"ingredient_name": "Ginger"},
    {"ingredient_name": "Garlic"},
    {"ingredient_name": "Onion"},
    {"ingredient_name": "Leek"},
    {"ingredient_name": "Shallot"},
    {"ingredient_name": "Scallion"},
    {"ingredient_name": "Chive"},
    {"ingredient_name": "Parsley"},
    {"ingredient_name": "Cilantro"},
    {"ingredient_name": "Basil"},
    {"ingredient_name": "Oregano"},
    {"ingredient_name": "Thyme"},
    {"ingredient_name": "Rosemary"},
    {"ingredient_name": "Sage"},
    {"ingredient_name": "Mint"},
    {"ingredient_name": "Lemongrass"},
    {"ingredient_name": "Lavender"},
    
    # Spices
    {"ingredient_name": "Fennel"},
    {"ingredient_name": "Cumin"},
    {"ingredient_name": "Paprika"},
    {"ingredient_name": "Chili Pepper"},
    {"ingredient_name": "Black Pepper"},
    {"ingredient_name": "White Pepper"},
    {"ingredient_name": "Green Pepper"},
    {"ingredient_name": "Red Pepper"},
    {"ingredient_name": "Cinnamon"},
    {"ingredient_name": "Allspice"},
    {"ingredient_name": "Mustard"},
    
    # Oils & Fats
    {"ingredient_name": "Vegetable Oil"},
    
    # Baking Ingredients
    {"ingredient_name": "Baking Powder"},
    {"ingredient_name": "Baking Soda"},
    {"ingredient_name": "Cornstarch"},
    {"ingredient_name": "All-Purpose Flour"},
    {"ingredient_name": "Pastry Flour"},
    {"ingredient_name": "Self-Rising Flour"},
    
    # Other
    {"ingredient_name": "Gelatin"},
]

# Optional: Ingredients with specific quantifiers
SEED_INGREDIENTS_WITH_QUANTIFIERS = [
    {"ingredient_name": "Wheat", "ingredient_quantifier": "g"},
    {"ingredient_name": "Barley", "ingredient_quantifier": "g"},
    {"ingredient_name": "Rye", "ingredient_quantifier": "g"},
    {"ingredient_name": "Oats", "ingredient_quantifier": "g"},
    {"ingredient_name": "Corn", "ingredient_quantifier": "g"},
    {"ingredient_name": "Rice", "ingredient_quantifier": "g"},
    {"ingredient_name": "Soy", "ingredient_quantifier": "g"},
    {"ingredient_name": "Buckwheat", "ingredient_quantifier": "g"},
    {"ingredient_name": "Milk", "ingredient_quantifier": "mL"},
    {"ingredient_name": "Butter", "ingredient_quantifier": "g"},
    {"ingredient_name": "Margarine", "ingredient_quantifier": "g"},
    {"ingredient_name": "Egg", "ingredient_quantifier": "pc"},
    {"ingredient_name": "Peanuts", "ingredient_quantifier": "g"},
    {"ingredient_name": "Tree Nuts", "ingredient_quantifier": "g"},
    {"ingredient_name": "Fish", "ingredient_quantifier": "g"},
    {"ingredient_name": "Shellfish", "ingredient_quantifier": "g"},
    {"ingredient_name": "Lentils", "ingredient_quantifier": "g"},
    {"ingredient_name": "Chickpeas", "ingredient_quantifier": "g"},
    {"ingredient_name": "Lupin", "ingredient_quantifier": "g"},
    {"ingredient_name": "Almond", "ingredient_quantifier": "g"},
    {"ingredient_name": "Coconut", "ingredient_quantifier": "g"},
    {"ingredient_name": "Sunflower Seeds", "ingredient_quantifier": "g"},
    {"ingredient_name": "Pumpkin Seeds", "ingredient_quantifier": "g"},
    {"ingredient_name": "Sesame Seeds", "ingredient_quantifier": "g"},
    {"ingredient_name": "Potato", "ingredient_quantifier": "g"},
    {"ingredient_name": "Sweet Potato", "ingredient_quantifier": "g"},
    {"ingredient_name": "Ginger", "ingredient_quantifier": "g"},
    {"ingredient_name": "Garlic", "ingredient_quantifier": "g"},
    {"ingredient_name": "Onion", "ingredient_quantifier": "g"},
    {"ingredient_name": "Leek", "ingredient_quantifier": "g"},
    {"ingredient_name": "Shallot", "ingredient_quantifier": "g"},
    {"ingredient_name": "Scallion", "ingredient_quantifier": "g"},
    {"ingredient_name": "Chive", "ingredient_quantifier": "g"},
    {"ingredient_name": "Parsley", "ingredient_quantifier": "g"},
    {"ingredient_name": "Cilantro", "ingredient_quantifier": "g"},
    {"ingredient_name": "Basil", "ingredient_quantifier": "g"},
    {"ingredient_name": "Oregano", "ingredient_quantifier": "g"},
    {"ingredient_name": "Thyme", "ingredient_quantifier": "g"},
    {"ingredient_name": "Rosemary", "ingredient_quantifier": "g"},
    {"ingredient_name": "Sage", "ingredient_quantifier": "g"},
    {"ingredient_name": "Mint", "ingredient_quantifier": "g"},
    {"ingredient_name": "Lemongrass", "ingredient_quantifier": "g"},
    {"ingredient_name": "Lavender", "ingredient_quantifier": "g"},
    {"ingredient_name": "Fennel", "ingredient_quantifier": "g"},
    {"ingredient_name": "Cumin", "ingredient_quantifier": "g"},
    {"ingredient_name": "Paprika", "ingredient_quantifier": "g"},
    {"ingredient_name": "Chili Pepper", "ingredient_quantifier": "g"},
    {"ingredient_name": "Black Pepper", "ingredient_quantifier": "g"},
    {"ingredient_name": "White Pepper", "ingredient_quantifier": "g"},
    {"ingredient_name": "Green Pepper", "ingredient_quantifier": "g"},
    {"ingredient_name": "Red Pepper", "ingredient_quantifier": "g"},
    {"ingredient_name": "Cinnamon", "ingredient_quantifier": "g"},
    {"ingredient_name": "Allspice", "ingredient_quantifier": "g"},
    {"ingredient_name": "Mustard", "ingredient_quantifier": "g"},
    {"ingredient_name": "Vegetable Oil", "ingredient_quantifier": "mL"},
    {"ingredient_name": "Baking Powder", "ingredient_quantifier": "g"},
    {"ingredient_name": "Baking Soda", "ingredient_quantifier": "g"},
    {"ingredient_name": "Cornstarch", "ingredient_quantifier": "g"},
    {"ingredient_name": "All-Purpose Flour", "ingredient_quantifier": "g"},
    {"ingredient_name": "Pastry Flour", "ingredient_quantifier": "g"},
    {"ingredient_name": "Self-Rising Flour", "ingredient_quantifier": "g"},
    {"ingredient_name": "Gelatin", "ingredient_quantifier": "g"},
]


# ==================== Seeding Functions ====================

def seed_ingredients(use_quantifiers: bool = False) -> int:
    """
    Seed ingredients using the storage broker's insert_record function.
    
    Args:
        use_quantifiers: If True, use the version with quantifiers
        
    Returns:
        Number of ingredients inserted
    """
    ingredients_data = SEED_INGREDIENTS_WITH_QUANTIFIERS if use_quantifiers else SEED_INGREDIENTS
    count_inserted = 0
    
    for ingredient_data in ingredients_data:
        # Check if ingredient already exists
        existing = get(
            table=models.Ingredient,
            conditions={"ingredient_name": ingredient_data["ingredient_name"]}
        )
        
        if not existing:
            # Create ingredient instance
            ingredient = models.Ingredient(
                ingredient_name=ingredient_data["ingredient_name"],
                ingredient_quantifier=ingredient_data.get("ingredient_quantifier", "pc"),
                ingredient_icon_url=ingredient_data.get("ingredient_icon_url"),
                ingredient_naming_contribution=ingredient_data.get("ingredient_naming_contribution"),
            )
            # Insert using broker
            result = insert_record(ingredient)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded ingredient: {ingredient_data['ingredient_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} ingredients")
    return count_inserted


def seed_ingredient(ingredient_data: Dict[str, Any]) -> bool:
    """
    Seed a single ingredient.
    
    Args:
        ingredient_data: Ingredient data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.Ingredient,
        conditions={"ingredient_name": ingredient_data.get("ingredient_name")}
    )
    
    if existing:
        logger.debug(f"Ingredient already exists: {ingredient_data.get('ingredient_name')}")
        return False
    
    ingredient = models.Ingredient(
        ingredient_name=ingredient_data.get("ingredient_name"),
        ingredient_quantifier=ingredient_data.get("ingredient_quantifier", "pc"),
        ingredient_icon_url=ingredient_data.get("ingredient_icon_url"),
        ingredient_naming_contribution=ingredient_data.get("ingredient_naming_contribution"),
    )
    result = insert_record(ingredient)
    if result:
        logger.debug(f"Seeded ingredient: {ingredient_data.get('ingredient_name')}")
    return bool(result)


def seed_ingredients_from_list(ingredients: List[Dict[str, Any]]) -> int:
    """
    Seed ingredients from a custom list.
    
    Args:
        ingredients: List of ingredient dictionaries
        
    Returns:
        Number of ingredients inserted
    """
    count_inserted = 0
    
    for ingredient_data in ingredients:
        # Check if ingredient already exists
        existing = get(
            table=models.Ingredient,
            conditions={"ingredient_name": ingredient_data.get("ingredient_name")}
        )
        
        if not existing:
            ingredient = models.Ingredient(
                ingredient_name=ingredient_data.get("ingredient_name"),
                ingredient_quantifier=ingredient_data.get("ingredient_quantifier", "pc"),
                ingredient_icon_url=ingredient_data.get("ingredient_icon_url"),
                ingredient_naming_contribution=ingredient_data.get("ingredient_naming_contribution"),
            )
            result = insert_record(ingredient)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded ingredient: {ingredient_data.get('ingredient_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} ingredients from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_ingredients() -> List[Dict[str, Any]]:
    """
    Get all seeded ingredients from the database.
    
    Returns:
        List of ingredient dictionaries
    """
    with session_scope() as session:
        ingredients = session.query(models.Ingredient).all()
        return [
            {
                "id": ing.id_ingredient,
                "name": ing.ingredient_name,
                "quantifier": ing.ingredient_quantifier,
                "icon_url": ing.ingredient_icon_url,
                "naming_contribution": ing.ingredient_naming_contribution,
            }
            for ing in ingredients
        ]


def ingredient_exists(ingredient_name: str) -> bool:
    """
    Check if an ingredient already exists in the database.
    
    Args:
        ingredient_name: Name of the ingredient to check
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.Ingredient,
        conditions={"ingredient_name": ingredient_name}
    )
    return bool(existing)


def get_ingredient_by_name(ingredient_name: str) -> Optional[models.Ingredient]:
    """
    Get an ingredient by name.
    
    Args:
        ingredient_name: Name of the ingredient
        
    Returns:
        Ingredient instance or None
    """
    result = get(
        table=models.Ingredient,
        conditions={"ingredient_name": ingredient_name}
    )
    return result[0] if result else None


def get_ingredient_by_id(ingredient_id: int) -> Optional[models.Ingredient]:
    """
    Get an ingredient by ID.
    
    Args:
        ingredient_id: ID of the ingredient
        
    Returns:
        Ingredient instance or None
    """
    result = get(
        table=models.Ingredient,
        conditions={"id_ingredient": ingredient_id}
    )
    return result[0] if result else None


def get_ingredients_by_quantifier(quantifier: str) -> List[models.Ingredient]:
    """
    Get ingredients by quantifier.
    
    Args:
        quantifier: Quantifier type (e.g., 'g', 'kg', 'mL', 'pc')
        
    Returns:
        List of Ingredient instances
    """
    with session_scope() as session:
        return session.query(models.Ingredient).filter(
            models.Ingredient.ingredient_quantifier == quantifier
        ).all()


def search_ingredients(query: str, limit: int = 20) -> List[models.Ingredient]:
    """
    Search ingredients by name.
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        List of Ingredient instances
    """
    with session_scope() as session:
        return session.query(models.Ingredient).filter(
            models.Ingredient.ingredient_name.ilike(f"%{query}%")
        ).limit(limit).all()


def delete_all_ingredients() -> int:
    """
    Delete all ingredients from the database.
    
    Returns:
        Number of ingredients deleted
    """
    with session_scope() as session:
        count = session.query(models.Ingredient).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} ingredients")
        return count


def update_ingredient_quantifier(ingredient_name: str, quantifier: str) -> bool:
    """
    Update the quantifier for an ingredient.
    
    Args:
        ingredient_name: Name of the ingredient
        quantifier: New quantifier
        
    Returns:
        True if updated, False if not found
    """
    valid_quantifiers = ['g', 'kg', 'mg', 'L', 'mL', 'pc', 'pkg', 'box', 'bag', 'slice', 'cup']
    if quantifier not in valid_quantifiers:
        logger.warning(f"Invalid quantifier: {quantifier}. Must be one of {valid_quantifiers}")
        return False
    
    with session_scope() as session:
        ingredient = session.query(models.Ingredient).filter(
            models.Ingredient.ingredient_name == ingredient_name
        ).first()
        
        if not ingredient:
            logger.warning(f"Ingredient not found: {ingredient_name}")
            return False
        
        ingredient.ingredient_quantifier = quantifier
        session.commit()
        logger.debug(f"Updated quantifier for ingredient: {ingredient_name} -> {quantifier}")
        return True


def update_ingredient_icon(ingredient_name: str, icon_url: str) -> bool:
    """
    Update the icon URL for an ingredient.
    
    Args:
        ingredient_name: Name of the ingredient
        icon_url: New icon URL
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        ingredient = session.query(models.Ingredient).filter(
            models.Ingredient.ingredient_name == ingredient_name
        ).first()
        
        if not ingredient:
            logger.warning(f"Ingredient not found: {ingredient_name}")
            return False
        
        ingredient.ingredient_icon_url = icon_url
        session.commit()
        logger.debug(f"Updated icon for ingredient: {ingredient_name}")
        return True


def get_ingredients_starting_with(prefix: str) -> List[models.Ingredient]:
    """
    Get ingredients that start with a specific prefix.
    
    Args:
        prefix: Prefix to search for
        
    Returns:
        List of Ingredient instances
    """
    with session_scope() as session:
        return session.query(models.Ingredient).filter(
            models.Ingredient.ingredient_name.startswith(prefix)
        ).all()


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding ingredients."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed ingredients")
    parser.add_argument(
        "--with-quantifiers",
        action="store_true",
        help="Use ingredients with quantifiers"
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing ingredients before seeding"
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
    
    print("🌱 Starting ingredient seeding...")
    
    try:
        if args.delete_first:
            delete_all_ingredients()
        
        count = seed_ingredients(use_quantifiers=args.with_quantifiers)
        print(f"✅ Successfully seeded {count} ingredients")
        
        # Show seeded ingredients
        if count > 0:
            ingredients = get_all_seeded_ingredients()
            print(f"\n📋 Seeded {len(ingredients)} ingredients:")
            
            # Group by first letter
            from collections import defaultdict
            grouped = defaultdict(list)
            for ing in ingredients:
                first_letter = ing['name'][0].upper() if ing['name'] else '#'
                grouped[first_letter].append(ing)
            
            for letter, ing_list in sorted(grouped.items()):
                print(f"\n  [{letter}]")
                for ing in sorted(ing_list, key=lambda x: x['name']):
                    quantifier_info = f" (Quantifier: {ing['quantifier']})" if ing['quantifier'] else ""
                    print(f"    - {ing['name']} (ID: {ing['id']}){quantifier_info}")
        
    except Exception as e:
        print(f"❌ Failed to seed ingredients: {e}")
        raise


if __name__ == "__main__":
    main()