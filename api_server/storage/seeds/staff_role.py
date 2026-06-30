# storage/seeds/staff_role.py
"""
Staff role seed module using the storage broker.
"""

import logging
from typing import Dict, Any, List, Optional

from storage.storage_broker import insert_record, get, session_scope
from core.models import models

logger = logging.getLogger(__name__)


# ==================== Seed Data ====================

SEED_STAFF_ROLES = [
    # Medical Doctors (Reference General Medical Consultation - id: 1)
    {"staff_role_name": "General Practitioner", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/doctor.svg"},
    {"staff_role_name": "Family Physician", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/doctor.svg"},
    {"staff_role_name": "Specialist Doctor", "staff_role_service_category_ref": 2, "staff_role_icon_url": "icons/staff/specialist.svg"},
    {"staff_role_name": "Consultant", "staff_role_service_category_ref": 2, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    
    # Surgeons (Reference Surgery - id: 4)
    {"staff_role_name": "General Surgeon", "staff_role_service_category_ref": 4, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    {"staff_role_name": "Cardiothoracic Surgeon", "staff_role_service_category_ref": 4, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    {"staff_role_name": "Neurosurgeon", "staff_role_service_category_ref": 4, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    {"staff_role_name": "Orthopedic Surgeon", "staff_role_service_category_ref": 4, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    {"staff_role_name": "Plastic Surgeon", "staff_role_service_category_ref": 4, "staff_role_icon_url": "icons/staff/surgeon.svg"},
    
    # Dental Staff (Reference Dental Services - id: 5)
    {"staff_role_name": "General Dentist", "staff_role_service_category_ref": 5, "staff_role_icon_url": "icons/staff/dentist.svg"},
    {"staff_role_name": "Orthodontist", "staff_role_service_category_ref": 5, "staff_role_icon_url": "icons/staff/dentist.svg"},
    {"staff_role_name": "Oral Surgeon", "staff_role_service_category_ref": 5, "staff_role_icon_url": "icons/staff/dentist.svg"},
    {"staff_role_name": "Dental Hygienist", "staff_role_service_category_ref": 5, "staff_role_icon_url": "icons/staff/dental_hygienist.svg"},
    {"staff_role_name": "Dental Assistant", "staff_role_service_category_ref": 5, "staff_role_icon_url": "icons/staff/dental_assistant.svg"},
    
    # Orthopedic Staff (Reference Orthopedic Services - id: 6)
    {"staff_role_name": "Orthopedic Surgeon", "staff_role_service_category_ref": 6, "staff_role_icon_url": "icons/staff/orthopedic.svg"},
    {"staff_role_name": "Sports Medicine Specialist", "staff_role_service_category_ref": 6, "staff_role_icon_url": "icons/staff/orthopedic.svg"},
    {"staff_role_name": "Physical Therapist", "staff_role_service_category_ref": 6, "staff_role_icon_url": "icons/staff/physical_therapist.svg"},
    
    # Dermatology Staff (Reference Dermatology - id: 7)
    {"staff_role_name": "Dermatologist", "staff_role_service_category_ref": 7, "staff_role_icon_url": "icons/staff/dermatologist.svg"},
    {"staff_role_name": "Cosmetic Dermatologist", "staff_role_service_category_ref": 7, "staff_role_icon_url": "icons/staff/dermatologist.svg"},
    
    # Ophthalmology Staff (Reference Ophthalmology - id: 8)
    {"staff_role_name": "Ophthalmologist", "staff_role_service_category_ref": 8, "staff_role_icon_url": "icons/staff/ophthalmologist.svg"},
    {"staff_role_name": "Optometrist", "staff_role_service_category_ref": 8, "staff_role_icon_url": "icons/staff/optometrist.svg"},
    
    # Cardiology Staff (Reference Cardiology - id: 9)
    {"staff_role_name": "Interventional Cardiologist", "staff_role_service_category_ref": 9, "staff_role_icon_url": "icons/staff/cardiologist.svg"},
    {"staff_role_name": "Cardiac Surgeon", "staff_role_service_category_ref": 9, "staff_role_icon_url": "icons/staff/cardiologist.svg"},
    {"staff_role_name": "Cardiovascular Technician", "staff_role_service_category_ref": 9, "staff_role_icon_url": "icons/staff/cardiologist.svg"},
    
    # Neurology Staff (Reference Neurology - id: 10)
    {"staff_role_name": "Neurologist", "staff_role_service_category_ref": 10, "staff_role_icon_url": "icons/staff/neurologist.svg"},
    {"staff_role_name": "Neurosurgeon", "staff_role_service_category_ref": 10, "staff_role_icon_url": "icons/staff/neurologist.svg"},
    
    # Gynecology Staff (Reference Gynecology & Obstetrics - id: 11)
    {"staff_role_name": "Gynecologist", "staff_role_service_category_ref": 11, "staff_role_icon_url": "icons/staff/gynecologist.svg"},
    {"staff_role_name": "Obstetrician", "staff_role_service_category_ref": 11, "staff_role_icon_url": "icons/staff/gynecologist.svg"},
    {"staff_role_name": "Midwife", "staff_role_service_category_ref": 11, "staff_role_icon_url": "icons/staff/midwife.svg"},
    
    # Pediatric Staff (Reference Pediatrics - id: 12)
    {"staff_role_name": "Pediatrician", "staff_role_service_category_ref": 12, "staff_role_icon_url": "icons/staff/pediatrician.svg"},
    {"staff_role_name": "Neonatologist", "staff_role_service_category_ref": 12, "staff_role_icon_url": "icons/staff/pediatrician.svg"},
    
    # Laboratory Staff (Reference Laboratory Tests - id: 13)
    {"staff_role_name": "Lab Technician", "staff_role_service_category_ref": 13, "staff_role_icon_url": "icons/staff/lab_technician.svg"},
    {"staff_role_name": "Pathologist", "staff_role_service_category_ref": 13, "staff_role_icon_url": "icons/staff/pathologist.svg"},
    
    # Radiology Staff (Reference Radiology & Imaging - id: 14)
    {"staff_role_name": "Radiologist", "staff_role_service_category_ref": 14, "staff_role_icon_url": "icons/staff/radiologist.svg"},
    {"staff_role_name": "Radiology Technician", "staff_role_service_category_ref": 14, "staff_role_icon_url": "icons/staff/radiology_technician.svg"},
    {"staff_role_name": "Ultrasound Technician", "staff_role_service_category_ref": 14, "staff_role_icon_url": "icons/staff/ultrasound_technician.svg"},
    
    # Physical Therapy Staff (Reference Physiotherapy - id: 16)
    {"staff_role_name": "Physical Therapist", "staff_role_service_category_ref": 16, "staff_role_icon_url": "icons/staff/physical_therapist.svg"},
    {"staff_role_name": "Physical Therapy Assistant", "staff_role_service_category_ref": 16, "staff_role_icon_url": "icons/staff/physical_therapist.svg"},
    
    # Mental Health Staff (Reference Psychological Services - id: 19)
    {"staff_role_name": "Clinical Psychologist", "staff_role_service_category_ref": 19, "staff_role_icon_url": "icons/staff/psychologist.svg"},
    {"staff_role_name": "Psychiatrist", "staff_role_service_category_ref": 19, "staff_role_icon_url": "icons/staff/psychiatrist.svg"},
    
    # Support Staff (General)
    {"staff_role_name": "Registered Nurse", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/nurse.svg"},
    {"staff_role_name": "Licensed Practical Nurse", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/nurse.svg"},
    {"staff_role_name": "Nurse Practitioner", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/nurse.svg"},
    {"staff_role_name": "Medical Assistant", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/medical_assistant.svg"},
    {"staff_role_name": "Pharmacist", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/pharmacist.svg"},
    {"staff_role_name": "Pharmacy Technician", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/pharmacist.svg"},
    {"staff_role_name": "Medical Administrator", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/administrator.svg"},
    {"staff_role_name": "Medical Receptionist", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/receptionist.svg"},
    
    # Emergency & Critical Care Staff (Reference Emergency Care - id: 3)
    {"staff_role_name": "Emergency Physician", "staff_role_service_category_ref": 3, "staff_role_icon_url": "icons/staff/emergency_doctor.svg"},
    {"staff_role_name": "Paramedic", "staff_role_service_category_ref": 3, "staff_role_icon_url": "icons/staff/paramedic.svg"},
    {"staff_role_name": "Emergency Nurse", "staff_role_service_category_ref": 3, "staff_role_icon_url": "icons/staff/emergency_nurse.svg"},
    {"staff_role_name": "Critical Care Nurse", "staff_role_service_category_ref": 3, "staff_role_icon_url": "icons/staff/critical_care_nurse.svg"},
    
    # Nutrition Staff (Reference Nutrition & Dietetics - id: 21)
    {"staff_role_name": "Clinical Nutritionist", "staff_role_service_category_ref": 21, "staff_role_icon_url": "icons/staff/nutritionist.svg"},
    {"staff_role_name": "Registered Dietitian", "staff_role_service_category_ref": 21, "staff_role_icon_url": "icons/staff/dietitian.svg"},
    
    # Healthcare Support
    {"staff_role_name": "Caregiver", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/caregiver.svg"},
    {"staff_role_name": "Home Health Aide", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/home_health_aide.svg"},
    {"staff_role_name": "Medical Social Worker", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/medical_social_worker.svg"},
    {"staff_role_name": "Health Coach", "staff_role_service_category_ref": 1, "staff_role_icon_url": "icons/staff/health_coach.svg"},
]


# ==================== Seeding Functions ====================

def seed_staff_roles() -> int:
    """
    Seed staff roles using the storage broker's insert_record function.
    
    Returns:
        Number of staff roles inserted
    """
    count_inserted = 0
    
    for role_data in SEED_STAFF_ROLES:
        # Check if role already exists
        existing = get(
            table=models.StaffRole,
            conditions={
                "staff_role_name": role_data["staff_role_name"],
                "staff_role_service_category_ref": role_data["staff_role_service_category_ref"]
            }
        )
        
        if not existing:
            # Create role instance
            role = models.StaffRole(
                staff_role_name=role_data["staff_role_name"],
                staff_role_service_category_ref=role_data["staff_role_service_category_ref"],
                staff_role_icon_url=role_data["staff_role_icon_url"],
                staff_role_naming_ref=None,  # Set if you have naming_contribution references
            )
            # Insert using broker
            result = insert_record(role)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded staff role: {role_data['staff_role_name']}")
    
    logger.info(f"✅ Seeded {count_inserted} staff roles")
    return count_inserted


def seed_staff_role(role_data: Dict[str, Any]) -> bool:
    """
    Seed a single staff role.
    
    Args:
        role_data: Role data dictionary
        
    Returns:
        True if inserted, False if already exists
    """
    existing = get(
        table=models.StaffRole,
        conditions={
            "staff_role_name": role_data.get("staff_role_name"),
            "staff_role_service_category_ref": role_data.get("staff_role_service_category_ref")
        }
    )
    
    if existing:
        logger.debug(f"Staff role already exists: {role_data.get('staff_role_name')}")
        return False
    
    role = models.StaffRole(
        staff_role_name=role_data.get("staff_role_name"),
        staff_role_service_category_ref=role_data.get("staff_role_service_category_ref"),
        staff_role_icon_url=role_data.get("staff_role_icon_url"),
        staff_role_naming_ref=role_data.get("staff_role_naming_ref"),
    )
    result = insert_record(role)
    if result:
        logger.debug(f"Seeded staff role: {role_data.get('staff_role_name')}")
    return bool(result)


def seed_staff_roles_from_list(roles: List[Dict[str, Any]]) -> int:
    """
    Seed staff roles from a custom list.
    
    Args:
        roles: List of role dictionaries
        
    Returns:
        Number of roles inserted
    """
    count_inserted = 0
    
    for role_data in roles:
        # Check if role already exists
        existing = get(
            table=models.StaffRole,
            conditions={
                "staff_role_name": role_data.get("staff_role_name"),
                "staff_role_service_category_ref": role_data.get("staff_role_service_category_ref")
            }
        )
        
        if not existing:
            role = models.StaffRole(
                staff_role_name=role_data.get("staff_role_name"),
                staff_role_service_category_ref=role_data.get("staff_role_service_category_ref"),
                staff_role_icon_url=role_data.get("staff_role_icon_url"),
                staff_role_naming_ref=role_data.get("staff_role_naming_ref"),
            )
            result = insert_record(role)
            if result:
                count_inserted += 1
                logger.debug(f"Seeded staff role: {role_data.get('staff_role_name')}")
    
    logger.info(f"✅ Seeded {count_inserted} staff roles from custom list")
    return count_inserted


# ==================== Utility Functions ====================

def get_all_seeded_staff_roles() -> List[Dict[str, Any]]:
    """
    Get all seeded staff roles from the database.
    
    Returns:
        List of role dictionaries
    """
    with session_scope() as session:
        roles = session.query(models.StaffRole).all()
        return [
            {
                "id": role.id_staff_role,
                "name": role.staff_role_name,
                "service_category_ref": role.staff_role_service_category_ref,
                "icon_url": role.staff_role_icon_url,
                "naming_ref": role.staff_role_naming_ref,
            }
            for role in roles
        ]


def get_staff_roles_by_service_category(category_id: int) -> List[models.StaffRole]:
    """
    Get all staff roles for a specific service category.
    
    Args:
        category_id: Service category ID
        
    Returns:
        List of StaffRole instances
    """
    with session_scope() as session:
        return session.query(models.StaffRole).filter(
            models.StaffRole.staff_role_service_category_ref == category_id
        ).all()


def staff_role_exists(role_name: str, category_id: int) -> bool:
    """
    Check if a staff role already exists for a category.
    
    Args:
        role_name: Name of the role
        category_id: Service category ID
        
    Returns:
        True if exists, False otherwise
    """
    existing = get(
        table=models.StaffRole,
        conditions={
            "staff_role_name": role_name,
            "staff_role_service_category_ref": category_id
        }
    )
    return bool(existing)


def get_staff_role_by_name(role_name: str) -> Optional[models.StaffRole]:
    """
    Get a staff role by name.
    
    Args:
        role_name: Name of the role
        
    Returns:
        StaffRole instance or None
    """
    result = get(
        table=models.StaffRole,
        conditions={"staff_role_name": role_name}
    )
    return result[0] if result else None


def get_staff_role_by_id(role_id: int) -> Optional[models.StaffRole]:
    """
    Get a staff role by ID.
    
    Args:
        role_id: ID of the role
        
    Returns:
        StaffRole instance or None
    """
    result = get(
        table=models.StaffRole,
        conditions={"id_staff_role": role_id}
    )
    return result[0] if result else None


def delete_all_staff_roles() -> int:
    """
    Delete all staff roles from the database.
    
    Returns:
        Number of roles deleted
    """
    with session_scope() as session:
        count = session.query(models.StaffRole).delete()
        session.commit()
        logger.info(f"🗑️ Deleted {count} staff roles")
        return count


def update_staff_role_icon(role_name: str, icon_url: str) -> bool:
    """
    Update the icon URL for a staff role.
    
    Args:
        role_name: Name of the role
        icon_url: New icon URL
        
    Returns:
        True if updated, False if not found
    """
    with session_scope() as session:
        role = session.query(models.StaffRole).filter(
            models.StaffRole.staff_role_name == role_name
        ).first()
        
        if not role:
            logger.warning(f"Staff role not found: {role_name}")
            return False
        
        role.staff_role_icon_url = icon_url
        session.commit()
        logger.debug(f"Updated icon for staff role: {role_name}")
        return True


def get_staff_roles_by_category_name(category_name: str) -> List[Dict[str, Any]]:
    """
    Get all staff roles for a service category by its name.
    
    Args:
        category_name: Service category name
        
    Returns:
        List of role dictionaries
    """
    from core.models import models
    
    with session_scope() as session:
        # First get the category ID
        category = session.query(models.ProvidedServiceCategory).filter(
            models.ProvidedServiceCategory.provided_service_category_name == category_name
        ).first()
        
        if not category:
            logger.warning(f"Service category not found: {category_name}")
            return []
        
        # Then get all roles for that category
        roles = session.query(models.StaffRole).filter(
            models.StaffRole.staff_role_service_category_ref == category.provided_service_category_id
        ).all()
        
        return [
            {
                "id": role.id_staff_role,
                "name": role.staff_role_name,
                "icon_url": role.staff_role_icon_url,
            }
            for role in roles
        ]


# ==================== Main Execution ====================

def main():
    """Main entry point for seeding staff roles."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed staff roles")
    parser.add_argument(
        "--delete-first",
        action="store_true",
        help="Delete all existing staff roles before seeding"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--category",
        "-c",
        type=int,
        help="Only seed roles for a specific category ID"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    print("🌱 Starting staff role seeding...")
    
    try:
        if args.delete_first:
            delete_all_staff_roles()
        
        count = seed_staff_roles()
        print(f"✅ Successfully seeded {count} staff roles")
        
        # Show seeded roles grouped by category
        if count > 0:
            roles = get_all_seeded_staff_roles()
            print("\n📋 Seeded staff roles:")
            
            # Group by category
            from collections import defaultdict
            grouped = defaultdict(list)
            for role in roles:
                grouped[role['service_category_ref']].append(role)
            
            for category_id, role_list in sorted(grouped.items()):
                print(f"\n  Category ID: {category_id}")
                for role in role_list:
                    print(f"    - {role['name']} (ID: {role['id']})")
        
    except Exception as e:
        print(f"❌ Failed to seed staff roles: {e}")
        raise


if __name__ == "__main__":
    main()