# routers/person_router.py
from fastapi import APIRouter, Depends, Query
from typing import Optional
from core.api_models import Person_API, Location_API
from services.person_service import PersonService

person_router = APIRouter()

def get_person_service() -> PersonService:
    return PersonService()

@person_router.get("/{person_id}")
def get_person(
    person_id: str,
    full: bool = Query(False, description="Include all related data"),
    person_service: PersonService = Depends(get_person_service)
):
    """Get person by ID"""
    return person_service.get_person_by_id(person_id, full)

@person_router.post("/")
def create_or_update_person(
    person: Person_API,
    location: Location_API,
    person_service: PersonService = Depends(get_person_service)
):
    """Create or update a person"""
    return person_service.refresh_or_insert_person(person, location)

@person_router.delete("/{person_id}")
def delete_person(
    person_id: str,
    person_service: PersonService = Depends(get_person_service)
):
    """Delete a person"""
    return person_service.delete_person(person_id)

@person_router.get("/blood-types/all")
def get_blood_types(
    person_service: PersonService = Depends(get_person_service)
):
    """Get all blood types"""
    return person_service.get_all_blood_types()

@person_router.get("/blood-type/{blood_type_id}")
def get_blood_type(
    blood_type_id: str,
    person_service: PersonService = Depends(get_person_service)
):
    """Get blood type by ID"""
    return person_service.get_blood_type_by_id(blood_type_id)