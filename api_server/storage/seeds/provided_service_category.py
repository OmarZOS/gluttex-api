# storage/seeds/provided_service_category.py
"""
Provided service category seed module using the storage broker.

Each category is backed by a NamingContribution row carrying the
Arabic / French / English names. Seeding is idempotent: re-running
inserts nothing.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

# `en` is both the lookup anchor and the English name. Treat it as
# immutable once shipped — downstream lookups key on it.
#
# `description` is per-locale too. Where a translation isn't provided,
# `ar` / `fr` fall back to the English string so the row is never
# half-empty.
SEED_SERVICE_CATEGORIES: List[Dict[str, Any]] = [
    {
        "en": "Blood Testing",
        "ar": "تحاليل الدم",
        "fr": "Analyses sanguines",
        "icon_url": "https://example.com/icons/blood-test.svg",
        "avg_duration": Decimal("30.00"),
        "description_en": "Complete blood count, cholesterol, glucose, and other blood tests",
        "description_ar": "تعداد الدم الكامل والكوليسترول والجلوكوز وفحوصات دم أخرى",
        "description_fr": "Numération formule sanguine, cholestérol, glucose et autres analyses",
    },
    {
        "en": "Diagnostic Imaging",
        "ar": "التصوير التشخيصي",
        "fr": "Imagerie diagnostique",
        "icon_url": "https://example.com/icons/xray.svg",
        "avg_duration": Decimal("45.00"),
        "description_en": "X-rays, MRIs, CT scans, and ultrasound services",
        "description_ar": "الأشعة السينية والرنين المغناطيسي والتصوير المقطعي والموجات فوق الصوتية",
        "description_fr": "Radiographies, IRM, scanners et échographies",
    },
    {
        "en": "Vaccination",
        "ar": "التطعيم",
        "fr": "Vaccination",
        "icon_url": "https://example.com/icons/vaccine.svg",
        "avg_duration": Decimal("15.00"),
        "description_en": "Routine immunizations and travel vaccinations",
        "description_ar": "التحصينات الروتينية وتطعيمات السفر",
        "description_fr": "Vaccinations de routine et vaccins de voyage",
    },
    {
        "en": "Health Check-up",
        "ar": "الفحص الطبي الشامل",
        "fr": "Bilan de santé",
        "icon_url": "https://example.com/icons/stethoscope.svg",
        "avg_duration": Decimal("60.00"),
        "description_en": "Comprehensive annual physical examinations",
        "description_ar": "الفحوصات الجسدية السنوية الشاملة",
        "description_fr": "Examens physiques annuels complets",
    },
    {
        "en": "Dental Care",
        "ar": "العناية بالأسنان",
        "fr": "Soins dentaires",
        "icon_url": "https://example.com/icons/dental.svg",
        "avg_duration": Decimal("40.00"),
        "description_en": "Teeth cleaning, fillings, and basic dental procedures",
        "description_ar": "تنظيف الأسنان والحشوات والإجراءات الأساسية لطب الأسنان",
        "description_fr": "Nettoyage dentaire, plombages et procédures dentaires de base",
    },
    {
        "en": "Pathology Tests",
        "ar": "اختبارات علم الأمراض",
        "fr": "Examens pathologiques",
        "icon_url": "https://example.com/icons/microscope.svg",
        "avg_duration": Decimal("120.00"),
        "description_en": "Tissue biopsy analysis and histopathology",
        "description_ar": "تحليل خزعات الأنسجة وعلم الأنسجة المرضية",
        "description_fr": "Analyse de biopsies tissulaires et histopathologie",
    },
    {
        "en": "Urine Analysis",
        "ar": "تحليل البول",
        "fr": "Analyse d'urine",
        "icon_url": "https://example.com/icons/urine-test.svg",
        "avg_duration": Decimal("20.00"),
        "description_en": "Complete urinalysis and culture tests",
        "description_ar": "تحليل البول الكامل واختبارات الزراعة",
        "description_fr": "Analyse d'urine complète et cultures",
    },
    {
        "en": "Allergy Testing",
        "ar": "اختبارات الحساسية",
        "fr": "Tests d'allergie",
        "icon_url": "https://example.com/icons/allergy.svg",
        "avg_duration": Decimal("90.00"),
        "description_en": "Skin prick tests and allergen screening",
        "description_ar": "اختبارات وخز الجلد وفحص مسببات الحساسية",
        "description_fr": "Tests cutanés et dépistage des allergènes",
    },
    {
        "en": "Genetic Testing",
        "ar": "الفحوصات الجينية",
        "fr": "Tests génétiques",
        "icon_url": "https://example.com/icons/dna.svg",
        "avg_duration": Decimal("180.00"),
        "description_en": "DNA analysis and genetic screening services",
        "description_ar": "خدمات تحليل الحمض النووي والفحص الجيني",
        "description_fr": "Analyses ADN et services de dépistage génétique",
    },
    {
        "en": "Physiotherapy",
        "ar": "العلاج الطبيعي",
        "fr": "Physiothérapie",
        "icon_url": "https://example.com/icons/physical-therapy.svg",
        "avg_duration": Decimal("50.00"),
        "description_en": "Rehabilitation and physical therapy sessions",
        "description_ar": "جلسات إعادة التأهيل والعلاج الطبيعي",
        "description_fr": "Séances de rééducation et de physiothérapie",
    },
    {
        "en": "Nutrition Counseling",
        "ar": "الاستشارات الغذائية",
        "fr": "Conseil nutritionnel",
        "icon_url": "https://example.com/icons/nutrition.svg",
        "avg_duration": Decimal("45.00"),
        "description_en": "Diet planning and nutritional guidance",
        "description_ar": "تخطيط النظام الغذائي والإرشاد التغذوي",
        "description_fr": "Planification alimentaire et conseils nutritionnels",
    },
    {
        "en": "Mental Health Counseling",
        "ar": "استشارات الصحة النفسية",
        "fr": "Conseil en santé mentale",
        "icon_url": "https://example.com/icons/mental-health.svg",
        "avg_duration": Decimal("60.00"),
        "description_en": "Therapy and psychological counseling sessions",
        "description_ar": "جلسات العلاج والاستشارات النفسية",
        "description_fr": "Séances de thérapie et de conseil psychologique",
    },
    {
        "en": "Acupuncture",
        "ar": "الوخز بالإبر",
        "fr": "Acupuncture",
        "icon_url": "https://example.com/icons/acupuncture.svg",
        "avg_duration": Decimal("40.00"),
        "description_en": "Traditional acupuncture therapy sessions",
        "description_ar": "جلسات العلاج التقليدي بالوخز بالإبر",
        "description_fr": "Séances de thérapie traditionnelle par acupuncture",
    },
    {
        "en": "Prenatal Care",
        "ar": "رعاية ما قبل الولادة",
        "fr": "Soins prénatals",
        "icon_url": "https://example.com/icons/pregnancy.svg",
        "avg_duration": Decimal("30.00"),
        "description_en": "Pregnancy monitoring and prenatal check-ups",
        "description_ar": "متابعة الحمل والفحوصات قبل الولادة",
        "description_fr": "Suivi de grossesse et examens prénatals",
    },
    {
        "en": "Pediatric Care",
        "ar": "رعاية الأطفال",
        "fr": "Soins pédiatriques",
        "icon_url": "https://example.com/icons/baby-care.svg",
        "avg_duration": Decimal("25.00"),
        "description_en": "Child healthcare and development monitoring",
        "description_ar": "رعاية صحة الطفل ومتابعة النمو",
        "description_fr": "Soins de santé infantile et suivi du développement",
    },
    {
        "en": "Geriatric Care",
        "ar": "رعاية كبار السن",
        "fr": "Soins gériatriques",
        "icon_url": "https://example.com/icons/elderly-care.svg",
        "avg_duration": Decimal("40.00"),
        "description_en": "Elderly health monitoring and management",
        "description_ar": "متابعة وإدارة صحة كبار السن",
        "description_fr": "Suivi et gestion de la santé des personnes âgées",
    },
    {
        "en": "Sports Medicine",
        "ar": "الطب الرياضي",
        "fr": "Médecine du sport",
        "icon_url": "https://example.com/icons/sports-medicine.svg",
        "avg_duration": Decimal("50.00"),
        "description_en": "Injury assessment and sports-related healthcare",
        "description_ar": "تقييم الإصابات والرعاية الصحية المتعلقة بالرياضة",
        "description_fr": "Évaluation des blessures et soins liés au sport",
    },
    {
        "en": "First Aid Training",
        "ar": "تدريب الإسعافات الأولية",
        "fr": "Formation aux premiers secours",
        "icon_url": "https://example.com/icons/first-aid.svg",
        "avg_duration": Decimal("240.00"),
        "description_en": "CPR and emergency first aid certification",
        "description_ar": "شهادة الإنعاش القلبي الرئوي والإسعافات الأولية الطارئة",
        "description_fr": "Certification RCR et premiers secours d'urgence",
    },
    {
        "en": "Minor Surgery",
        "ar": "الجراحة البسيطة",
        "fr": "Chirurgie mineure",
        "icon_url": "https://example.com/icons/surgery.svg",
        "avg_duration": Decimal("75.00"),
        "description_en": "Outpatient minor surgical procedures",
        "description_ar": "الإجراءات الجراحية البسيطة للمرضى الخارجيين",
        "description_fr": "Interventions chirurgicales mineures en ambulatoire",
    },
    {
        "en": "Wound Care",
        "ar": "العناية بالجروح",
        "fr": "Soins des plaies",
        "icon_url": "https://example.com/icons/wound-care.svg",
        "avg_duration": Decimal("25.00"),
        "description_en": "Dressing changes and wound management",
        "description_ar": "تغيير الضمادات وإدارة الجروح",
        "description_fr": "Changement de pansements et gestion des plaies",
    },
    {
        "en": "IV Therapy",
        "ar": "العلاج الوريدي",
        "fr": "Thérapie intraveineuse",
        "icon_url": "https://example.com/icons/iv-therapy.svg",
        "avg_duration": Decimal("35.00"),
        "description_en": "Intravenous hydration and vitamin therapy",
        "description_ar": "الترطيب الوريدي والعلاج بالفيتامينات",
        "description_fr": "Hydratation intraveineuse et vitaminothérapie",
    },
]


# ==================== Helpers ====================

def _get_or_create_naming_contribution(
    *,
    name_en: str,
    name_ar: str,
    name_fr: str,
    icon_url: Optional[str] = None,
    contribution_type: str = "service",
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


def _get_or_create_service_category(
    *,
    name_en: str,
    naming_contribution_id: int,
    icon_url: Optional[str],
    avg_duration: Optional[Decimal],
    description: Optional[str],
) -> Optional[Any]:
    """
    Return the existing ProvidedServiceCategory for the given name, or
    insert a new one linked to `naming_contribution_id`.
    """
    existing = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": name_en},
    )
    if existing:
        return existing

    category = models.ProvidedServiceCategory(
        provided_service_category_name=name_en,
        provided_service_category_icon_url=icon_url,
        provided_service_category_avg_duration=avg_duration,
        provided_service_category_description=description,
        provided_service_category_naming_ref=naming_contribution_id,
    )
    result = insert_record(category)
    return result if result else None


def _pick_description(entry: Dict[str, Any], lang: str) -> Optional[str]:
    """
    Return the description for the given language, falling back to the
    English one when a translation isn't provided.
    """
    return entry.get(f"description_{lang}") or entry.get("description_en")


# ==================== Seeding Functions ====================

def seed_service_categories() -> int:
    """
    Seed provided service categories and their multilingual names.

    Returns:
        Number of categories inserted (existing rows are not counted).
    """
    count_inserted = 0

    for entry in SEED_SERVICE_CATEGORIES:
        name_en = entry["en"]

        contribution = _get_or_create_naming_contribution(
            name_en=name_en,
            name_ar=entry["ar"],
            name_fr=entry["fr"],
            icon_url=entry.get("icon_url"),
        )
        if contribution is None:
            logger.error(
                "Skipping service category %r: could not resolve naming "
                "contribution",
                name_en,
            )
            continue

        existing_category = get(
            table=models.ProvidedServiceCategory,
            conditions={"provided_service_category_name": name_en},
        )
        if existing_category:
            # Backfill the naming link, icon, and duration if missing.
            if (
                getattr(
                    existing_category,
                    "provided_service_category_naming_ref",
                    None,
                )
                is None
            ):
                existing_category.provided_service_category_naming_ref = (
                    contribution.id_naming_contribution
                )
                logger.debug(
                    "Backfilled naming ref for existing category %r",
                    name_en,
                )
            if (
                entry.get("icon_url")
                and not existing_category.provided_service_category_icon_url
            ):
                existing_category.provided_service_category_icon_url = entry[
                    "icon_url"
                ]
            if (
                entry.get("avg_duration") is not None
                and existing_category.provided_service_category_avg_duration
                is None
            ):
                existing_category.provided_service_category_avg_duration = (
                    entry["avg_duration"]
                )
            continue

        category = _get_or_create_service_category(
            name_en=name_en,
            naming_contribution_id=contribution.id_naming_contribution,
            icon_url=entry.get("icon_url"),
            avg_duration=entry.get("avg_duration"),
            description=_pick_description(entry, "en"),
        )
        if category:
            count_inserted += 1
            logger.debug("Seeded service category: %s", name_en)

    logger.info("Seeded %d new provided service categories", count_inserted)
    return count_inserted


def seed_service_category(category_data: Dict[str, Any]) -> bool:
    """
    Seed a single provided service category.

    `category_data` may carry `en` / `ar` / `fr` plus optional
    `icon_url`, `avg_duration`, and `description_{en,ar,fr}`. Falls
    back to the old `provided_service_category_*` keys for backward
    compatibility.

    Returns True if inserted, False if the category already existed.
    """
    name_en = (
        category_data.get("en")
        or category_data.get("provided_service_category_name")
    )
    if not name_en:
        logger.warning(
            "seed_service_category called with no name: %r", category_data
        )
        return False

    existing = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": name_en},
    )
    if existing:
        logger.debug("Service category already exists: %s", name_en)
        return False

    icon_url = category_data.get("icon_url") or category_data.get(
        "provided_service_category_icon_url"
    )
    avg_duration = category_data.get("avg_duration") or category_data.get(
        "provided_service_category_avg_duration"
    )

    contribution = _get_or_create_naming_contribution(
        name_en=name_en,
        name_ar=category_data.get("ar", name_en),
        name_fr=category_data.get("fr", name_en),
        icon_url=icon_url,
    )
    if contribution is None:
        logger.error("Could not create naming contribution for %r", name_en)
        return False

    category = _get_or_create_service_category(
        name_en=name_en,
        naming_contribution_id=contribution.id_naming_contribution,
        icon_url=icon_url,
        avg_duration=avg_duration,
        description=_pick_description(category_data, "en"),
    )
    if category:
        logger.debug("Seeded service category: %s", name_en)
        return True
    return False


def seed_service_categories_from_list(
    categories: List[Dict[str, Any]],
) -> int:
    """
    Seed provided service categories from a custom list.

    Each entry may carry `en` / `ar` / `fr` and optionally `icon_url`,
    `avg_duration`, and `description_{en,ar,fr}`. The English name is
    the lookup key. Falls back to the old `provided_service_category_*`
    keys for backward compatibility.

    Returns:
        Number of categories inserted.
    """
    count_inserted = 0

    for entry in categories:
        name_en = entry.get("en") or entry.get(
            "provided_service_category_name"
        )
        if not name_en:
            logger.warning("Skipping entry with no English name: %r", entry)
            continue

        icon_url = entry.get("icon_url") or entry.get(
            "provided_service_category_icon_url"
        )
        avg_duration = entry.get("avg_duration") or entry.get(
            "provided_service_category_avg_duration"
        )

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

        category = _get_or_create_service_category(
            name_en=name_en,
            naming_contribution_id=contribution.id_naming_contribution,
            icon_url=icon_url,
            avg_duration=avg_duration,
            description=_pick_description(entry, "en"),
        )
        if category:
            count_inserted += 1
            logger.debug("Seeded service category: %s", name_en)

    logger.info(
        "Seeded %d provided service categories from custom list",
        count_inserted,
    )
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_service_categories() -> List[Dict[str, Any]]:
    """
    Return every service category with its name and description in all
    three languages.

    The primary `name` field is the English name for backward
    compatibility with callers that only want one string.
    """
    with session_scope() as session:
        rows = (
            session.query(
                models.ProvidedServiceCategory,
                models.NamingContribution,
            )
            .outerjoin(
                models.NamingContribution,
                models.ProvidedServiceCategory.provided_service_category_naming_ref
                == models.NamingContribution.id_naming_contribution,
            )
            .all()
        )

        result: List[Dict[str, Any]] = []
        for category, naming in rows:
            result.append(
                {
                    "id": category.provided_service_category_id,
                    "name": category.provided_service_category_name,
                    "en": category.provided_service_category_name,
                    "ar": getattr(naming, "naming_contribution_ar", None)
                    if naming
                    else None,
                    "fr": getattr(naming, "naming_contribution_fr", None)
                    if naming
                    else None,
                    "icon_url": category.provided_service_category_icon_url,
                    "avg_duration": float(
                        category.provided_service_category_avg_duration
                    )
                    if category.provided_service_category_avg_duration
                    else None,
                    "description": category.provided_service_category_description,
                    "naming_ref": category.provided_service_category_naming_ref,
                }
            )
        return result


def service_category_exists(category_name: str) -> bool:
    """
    Check whether a service category with the given English name exists.
    """
    existing = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": category_name},
    )
    return bool(existing)


def get_service_category_by_name(
    category_name: str,
) -> Optional[models.ProvidedServiceCategory]:
    """
    Return a service category by its English name, or None.
    """
    result = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_name": category_name},
    )
    if not result:
        return None
    return result[0] if isinstance(result, list) else result


def get_service_category_by_id(
    category_id: int,
) -> Optional[models.ProvidedServiceCategory]:
    """
    Return a service category by its primary key, or None.
    """
    result = get(
        table=models.ProvidedServiceCategory,
        conditions={"provided_service_category_id": category_id},
    )
    if not result:
        return None
    return result[0] if isinstance(result, list) else result


def get_service_categories_by_duration(
    max_duration: int,
) -> List[models.ProvidedServiceCategory]:
    """
    Return service categories whose average duration is at or below
    `max_duration` minutes.
    """
    with session_scope() as session:
        return (
            session.query(models.ProvidedServiceCategory)
            .filter(
                models.ProvidedServiceCategory.provided_service_category_avg_duration
                <= max_duration
            )
            .all()
        )


def delete_all_service_categories() -> int:
    """
    Delete all provided service categories. Leaves the naming
    contributions in place, since other tables may reference them.

    Returns the number of categories deleted.
    """
    with session_scope() as session:
        count = session.query(models.ProvidedServiceCategory).delete()
        session.commit()
        logger.info("Deleted %d provided service categories", count)
        return count


def update_service_category_duration(
    category_name: str, avg_duration: Decimal
) -> bool:
    """
    Update the average duration for a service category.
    """
    with session_scope() as session:
        category = (
            session.query(models.ProvidedServiceCategory)
            .filter(
                models.ProvidedServiceCategory.provided_service_category_name
                == category_name
            )
            .first()
        )

        if not category:
            logger.warning("Service category not found: %s", category_name)
            return False

        category.provided_service_category_avg_duration = avg_duration
        session.commit()
        logger.debug(
            "Updated duration for service category: %s", category_name
        )
        return True


def update_service_category_icon(category_name: str, icon_url: str) -> bool:
    """
    Update the icon URL for a service category.
    """
    with session_scope() as session:
        category = (
            session.query(models.ProvidedServiceCategory)
            .filter(
                models.ProvidedServiceCategory.provided_service_category_name
                == category_name
            )
            .first()
        )

        if not category:
            logger.warning("Service category not found: %s", category_name)
            return False

        category.provided_service_category_icon_url = icon_url
        session.commit()
        logger.debug("Updated icon for service category: %s", category_name)
        return True


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding provided service categories."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed provided service categories"
    )
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing service categories before seeding",
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

    print("Starting provided service category seeding...")

    try:
        if args.delete_first:
            delete_all_service_categories()

        count = seed_service_categories()
        print(f"Successfully seeded {count} provided service categories")

        if count > 0:
            categories = get_all_seeded_service_categories()
            print("\nSeeded service categories:")
            for cat in categories:
                languages = " / ".join(
                    filter(None, [cat.get("en"), cat.get("fr"), cat.get("ar")])
                )
                duration = (
                    f"{cat['avg_duration']} min"
                    if cat["avg_duration"]
                    else "N/A"
                )
                icon_info = (
                    f" (icon: {cat['icon_url']})" if cat["icon_url"] else ""
                )
                print(
                    f"  - {languages} (ID: {cat['id']}, "
                    f"Duration: {duration}){icon_info}"
                )

    except Exception as e:
        print(f"Failed to seed provided service categories: {e}")
        raise


if __name__ == "__main__":
    main()