# storage/seeds/product_provider_type.py
"""
Product provider type seed module using the storage broker.

Each provider type is backed by a NamingContribution row carrying the
Arabic / French / English names. Seeding is idempotent: re-running
inserts nothing.
"""

import logging
from typing import Any, Dict, List, Optional

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

# `en` is both the lookup anchor and the English name. Treat it as
# immutable once shipped — downstream lookups key on it.
SEED_PROVIDER_TYPES: List[Dict[str, str]] = [
    {
        "ar": "مطعم",
        "fr": "Restaurant",
        "en": "Restaurant",
    },
    {
        "ar": "مخبزة",
        "fr": "Boulangerie",
        "en": "Bakery",
    },
    {
        "ar": "مصنع",
        "fr": "Usine",
        "en": "Factory",
    },
    {
        "ar": "سوبر ماركت",
        "fr": "Supermarché",
        "en": "Supermarket",
    },
    {
        "ar": "بقالة",
        "fr": "Épicerie",
        "en": "Grocery Store",
    },
    {
        "ar": "موزّع",
        "fr": "Distributeur",
        "en": "Distributor",
    },
]


# Optional: icon URLs keyed by English name. Kept separate from the
# translation data so translations and icons can be edited independently.
SEED_PROVIDER_TYPE_ICONS: Dict[str, str] = {
    "Restaurant": "https://example.com/icons/restaurant.png",
    "Bakery": "https://example.com/icons/bakery.png",
    "Factory": "https://example.com/icons/factory.png",
    "Supermarket": "https://example.com/icons/supermarket.png",
    "Grocery Store": "https://example.com/icons/grocery.png",
    "Distributor": "https://example.com/icons/distributor.png",
}


# ==================== Helpers ====================

def _get_or_create_naming_contribution(
    *,
    name_en: str,
    name_ar: str,
    name_fr: str,
    icon_url: Optional[str] = None,
    contribution_type: str = "provider",
) -> Optional[Any]:
    """
    Return the existing NamingContribution for the given English name,
    or insert a new one. Returns the contribution row (with its id
    populated) on success, None on failure.
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
        naming_contribution_icon_url=icon_url,
        naming_contribution_by=None,
        naming_contribution_app_version=None,
    )
    result = insert_record(contribution)
    return result if result else None


def _get_or_create_provider_type(
    *,
    name_en: str,
    naming_contribution_id: int,
    icon_url: Optional[str] = None,
) -> Optional[Any]:
    """
    Return the existing ProductProviderType for the given name, or
    insert a new one linked to `naming_contribution_id`.
    """
    existing = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": name_en},
    )
    if existing:
        return existing

    provider_type = models.ProductProviderType(
        product_provider_type_name=name_en,
        product_provider_type_icon_url=icon_url,
        product_provider_type_naming_ref=naming_contribution_id,
    )
    result = insert_record(provider_type)
    return result if result else None


# ==================== Seeding Functions ====================

def seed_product_provider_types(use_icons: bool = False) -> int:
    """
    Seed product provider types and their multilingual names.

    Args:
        use_icons: If True, attach the icon URLs from
            SEED_PROVIDER_TYPE_ICONS to both the naming contribution
            and the provider type.

    Returns:
        Number of provider types inserted (existing rows are not
        counted).
    """
    count_inserted = 0

    for entry in SEED_PROVIDER_TYPES:
        name_en = entry["en"]
        icon_url = SEED_PROVIDER_TYPE_ICONS.get(name_en) if use_icons else None

        contribution = _get_or_create_naming_contribution(
            name_en=name_en,
            name_ar=entry["ar"],
            name_fr=entry["fr"],
            icon_url=icon_url,
        )
        if contribution is None:
            logger.error(
                "Skipping provider type %r: could not resolve naming "
                "contribution",
                name_en,
            )
            continue

        existing_type = get(
            table=models.ProductProviderType,
            conditions={"product_provider_type_name": name_en},
        )
        if existing_type:
            # Backfill the naming link and icon if they're missing.
            if (
                getattr(existing_type, "product_provider_type_naming_ref", None)
                is None
            ):
                existing_type.product_provider_type_naming_ref = (
                    contribution.id_naming_contribution
                )
                logger.debug(
                    "Backfilled naming ref for existing provider type %r",
                    name_en,
                )
            if icon_url and not existing_type.product_provider_type_icon_url:
                existing_type.product_provider_type_icon_url = icon_url
            continue

        provider_type = _get_or_create_provider_type(
            name_en=name_en,
            naming_contribution_id=contribution.id_naming_contribution,
            icon_url=icon_url,
        )
        if provider_type:
            count_inserted += 1
            logger.debug("Seeded product provider type: %s", name_en)

    logger.info("Seeded %d new product provider types", count_inserted)
    return count_inserted


def seed_product_provider_type(provider_type_data: Dict[str, Any]) -> bool:
    """
    Seed a single product provider type.

    `provider_type_data` may carry `en` / `ar` / `fr` and optionally
    `product_provider_type_icon_url`. Falls back to
    `product_provider_type_name` as the English name for backward
    compatibility with the old shape.

    Returns True if inserted, False if the provider type already
    existed.
    """
    name_en = provider_type_data.get("en") or provider_type_data.get(
        "product_provider_type_name"
    )
    if not name_en:
        logger.warning(
            "seed_product_provider_type called with no name: %r",
            provider_type_data,
        )
        return False

    existing = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": name_en},
    )
    if existing:
        logger.debug("Provider type already exists: %s", name_en)
        return False

    icon_url = provider_type_data.get("product_provider_type_icon_url")

    contribution = _get_or_create_naming_contribution(
        name_en=name_en,
        name_ar=provider_type_data.get("ar", name_en),
        name_fr=provider_type_data.get("fr", name_en),
        icon_url=icon_url,
    )
    if contribution is None:
        logger.error("Could not create naming contribution for %r", name_en)
        return False

    provider_type = _get_or_create_provider_type(
        name_en=name_en,
        naming_contribution_id=contribution.id_naming_contribution,
        icon_url=icon_url,
    )
    if provider_type:
        logger.debug("Seeded product provider type: %s", name_en)
        return True
    return False


def seed_product_provider_types_from_list(
    provider_types: List[Dict[str, Any]],
) -> int:
    """
    Seed product provider types from a custom list.

    Each entry may carry `en` / `ar` / `fr` for the naming
    contribution, and optionally `product_provider_type_icon_url`. The
    English name is the lookup key. Falls back to
    `product_provider_type_name` for backward compatibility.

    Returns:
        Number of provider types inserted.
    """
    count_inserted = 0

    for entry in provider_types:
        name_en = entry.get("en") or entry.get("product_provider_type_name")
        if not name_en:
            logger.warning("Skipping entry with no English name: %r", entry)
            continue

        icon_url = entry.get("product_provider_type_icon_url")

        contribution = _get_or_create_naming_contribution(
            name_en=name_en,
            name_ar=entry.get("ar", name_en),
            name_fr=entry.get("fr", name_en),
            icon_url=icon_url,
        )
        if contribution is None:
            logger.error(
                "Skipping %r: could not resolve naming contribution",
                name_en,
            )
            continue

        provider_type = _get_or_create_provider_type(
            name_en=name_en,
            naming_contribution_id=contribution.id_naming_contribution,
            icon_url=icon_url,
        )
        if provider_type:
            count_inserted += 1
            logger.debug("Seeded product provider type: %s", name_en)

    logger.info(
        "Seeded %d product provider types from custom list", count_inserted
    )
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_provider_types() -> List[Dict[str, Any]]:
    """
    Return every provider type with its name in all three languages.

    The primary `name` field is the English name for backward
    compatibility with callers that only want one string.
    """
    with session_scope() as session:
        rows = (
            session.query(
                models.ProductProviderType,
                models.NamingContribution,
            )
            .outerjoin(
                models.NamingContribution,
                models.ProductProviderType.product_provider_type_naming_ref
                == models.NamingContribution.id_naming_contribution,
            )
            .all()
        )

        result: List[Dict[str, Any]] = []
        for provider_type, naming in rows:
            result.append(
                {
                    "id": provider_type.id_product_provider_type,
                    "name": provider_type.product_provider_type_name,
                    "en": provider_type.product_provider_type_name,
                    "ar": getattr(naming, "naming_contribution_ar", None)
                    if naming
                    else None,
                    "fr": getattr(naming, "naming_contribution_fr", None)
                    if naming
                    else None,
                    "icon_url": provider_type.product_provider_type_icon_url,
                    "naming_ref": provider_type.product_provider_type_naming_ref,
                }
            )
        return result


def provider_type_exists(provider_type_name: str) -> bool:
    """
    Check whether a provider type with the given English name exists.
    """
    existing = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": provider_type_name},
    )
    return bool(existing)


def get_provider_type_by_name(
    provider_type_name: str,
) -> Optional[models.ProductProviderType]:
    """
    Return a provider type by its English name, or None.
    """
    result = get(
        table=models.ProductProviderType,
        conditions={"product_provider_type_name": provider_type_name},
    )
    if not result:
        return None
    # `get` may return a list; normalise to a single row.
    return result[0] if isinstance(result, list) else result


def get_provider_type_by_id(
    provider_type_id: int,
) -> Optional[models.ProductProviderType]:
    """
    Return a provider type by its primary key, or None.
    """
    result = get(
        table=models.ProductProviderType,
        conditions={"id_product_provider_type": provider_type_id},
    )
    if not result:
        return None
    return result[0] if isinstance(result, list) else result


def delete_all_product_provider_types() -> int:
    """
    Delete all product provider types. Leaves the naming contributions
    in place, since other tables may reference them.

    Returns the number of provider types deleted.
    """
    with session_scope() as session:
        count = session.query(models.ProductProviderType).delete()
        session.commit()
        logger.info("Deleted %d product provider types", count)
        return count


def update_provider_type_icon(
    provider_type_name: str, icon_url: str
) -> bool:
    """
    Update the icon URL for a provider type.
    """
    with session_scope() as session:
        provider_type = (
            session.query(models.ProductProviderType)
            .filter(
                models.ProductProviderType.product_provider_type_name
                == provider_type_name
            )
            .first()
        )

        if not provider_type:
            logger.warning("Provider type not found: %s", provider_type_name)
            return False

        provider_type.product_provider_type_icon_url = icon_url
        session.commit()
        logger.debug("Updated icon for provider type: %s", provider_type_name)
        return True


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding product provider types."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed product provider types")
    parser.add_argument(
        "--with-icons",
        action="store_true",
        help="Attach icon URLs to naming contributions and provider types",
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing provider types before seeding",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    print("Starting product provider type seeding...")

    try:
        if args.delete_first:
            delete_all_product_provider_types()

        count = seed_product_provider_types(use_icons=args.with_icons)
        print(f"Successfully seeded {count} product provider types")

        if count > 0:
            provider_types = get_all_seeded_provider_types()
            print("\nSeeded provider types:")
            for pt in provider_types:
                languages = " / ".join(
                    filter(None, [pt.get("en"), pt.get("fr"), pt.get("ar")])
                )
                icon_info = (
                    f" (icon: {pt['icon_url']})" if pt["icon_url"] else ""
                )
                print(f"  - {languages} (ID: {pt['id']}){icon_info}")

    except Exception as e:
        print(f"Failed to seed product provider types: {e}")
        raise


if __name__ == "__main__":
    main()