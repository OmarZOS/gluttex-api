# storage/seeds/product_category.py
"""
Product category seed module using the storage broker.

Each category is backed by a NamingContribution row carrying the
Arabic / French / English names. Seeding is idempotent: re-running
inserts nothing.
"""

import logging
from typing import Any, Dict, Optional

from storage.storage_broker import insert_record, get
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

# `key` is the lookup anchor and the English name. It is used to find an
# existing contribution on re-runs, so treat it as immutable once shipped.
SEED_PRODUCT_CATEGORIES = [
    {
        "key": "Baked Goods",
        "ar": "المخبوزات",
        "fr": "Produits de boulangerie",
        "en": "Baked Goods",
    },
    {
        "key": "Spreads",
        "ar": "المربى والدهون القابلة للدهن",
        "fr": "Pâtes à tartiner",
        "en": "Spreads",
    },
    {
        "key": "Cereals",
        "ar": "الحبوب",
        "fr": "Céréales",
        "en": "Cereals",
    },
    {
        "key": "Pasta",
        "ar": "المعكرونة",
        "fr": "Pâtes alimentaires",
        "en": "Pasta",
    },
    {
        "key": "Snacks",
        "ar": "الوجبات الخفيفة",
        "fr": "En-cas",
        "en": "Snacks",
    },
    {
        "key": "Beverages",
        "ar": "المشروبات",
        "fr": "Boissons",
        "en": "Beverages",
    },
    {
        "key": "Desserts",
        "ar": "الحلويات",
        "fr": "Desserts",
        "en": "Desserts",
    },
    {
        "key": "Frozen Foods",
        "ar": "الأطعمة المجمدة",
        "fr": "Produits surgelés",
        "en": "Frozen Foods",
    },
    {
        "key": "Flours & Baking Ingredients",
        "ar": "الطحين ومكونات الخبز",
        "fr": "Farines et ingrédients de boulangerie",
        "en": "Flours & Baking Ingredients",
    },
    {
        "key": "Canned & Packaged Goods",
        "ar": "المعلبات والأغذية المعبأة",
        "fr": "Conserves et produits emballés",
        "en": "Canned & Packaged Goods",
    },
]


# ==================== Helpers ====================

def _get_or_create_naming_contribution(
    *,
    name_en: str,
    name_ar: str,
    name_fr: str,
    contribution_type: str = "product",
) -> Optional[Any]:
    """
    Return the existing NamingContribution for the given English name,
    or insert a new one. Returns the contribution row (with its id
    populated) on success, None on failure.

    The English name is used as the natural key, since
    `naming_contribution_en` is what downstream lookups key on. If your
    schema enforces uniqueness elsewhere, adjust accordingly.
    """
    existing = get(
        table=models.NamingContribution,
        conditions={"naming_contribution_en": name_en},
    )
    if existing:
        return existing

    contribution = models.NamingContribution(
        naming_contribution_en=name_en,
        naming_contribution_ar=name_ar,
        naming_contribution_fr=name_fr,
        naming_contribution_status="APP_TRANSLATED",
        naming_contribution_type=contribution_type,
        naming_contribution_icon_url=None,
        naming_contribution_by=None,
        naming_contribution_app_version=None,
    )
    result = insert_record(contribution)
    return result if result else None


def _get_or_create_product_category(
    *,
    name_en: str,
    naming_contribution_id: int,
) -> Optional[Any]:
    """
    Return the existing ProductCategory for the given name, or insert a
    new one linked to `naming_contribution_id`.
    """
    existing = get(
        table=models.ProductCategory,
        conditions={"product_category_name": name_en},
    )
    if existing:
        return existing

    category = models.ProductCategory(
        product_category_name=name_en,
        product_category_icon=None,
        product_category_naming_ref=naming_contribution_id,
    )
    result = insert_record(category)
    return result if result else None


# ==================== Seeding Function ====================

def seed_product_categories() -> int:
    """
    Seed product categories and their multilingual names.

    Returns:
        Number of product categories inserted (existing rows are not
        counted).
    """
    count_inserted = 0

    for entry in SEED_PRODUCT_CATEGORIES:
        name_en = entry["en"]

        contribution = _get_or_create_naming_contribution(
            name_en=name_en,
            name_ar=entry["ar"],
            name_fr=entry["fr"],
        )
        if contribution is None:
            logger.error(
                "Skipping category %r: could not resolve naming contribution",
                name_en,
            )
            continue

        existing_category = get(
            table=models.ProductCategory,
            conditions={"product_category_name": name_en},
        )
        if existing_category:
            # Backfill the naming link if the row predates this seed.
            if (
                getattr(existing_category, "product_category_naming_ref", None)
                is None
            ):
                existing_category.product_category_naming_ref = (
                    contribution.id_naming_contribution
                )
                logger.debug(
                    "Backfilled naming ref for existing category %r",
                    name_en,
                )
            continue

        category = _get_or_create_product_category(
            name_en=name_en,
            naming_contribution_id=contribution.id_naming_contribution,
        )
        if category:
            count_inserted += 1
            logger.debug("Seeded product category: %s", name_en)

    logger.info("Seeded %d new product categories", count_inserted)
    return count_inserted


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding product categories."""
    print("Starting product category seeding...")

    try:
        count = seed_product_categories()
        print(f"Successfully seeded {count} product categories")
    except Exception as e:
        print(f"Failed to seed product categories: {e}")
        raise


if __name__ == "__main__":
    main()