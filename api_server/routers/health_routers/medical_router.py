# routers/medical_router.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from core.api_models import Serology_API, Symptoms_API
from core.exception_handler import APIException
from core.messages import *
from services.medical_service import MedicalService

medical_router = APIRouter()

def get_medical_service() -> MedicalService:
    return MedicalService()

# ==================== Serology Endpoints ====================

@medical_router.post("/serology")
def create_serology(
    serology: Serology_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Create a new serology record"""
    return medical_service.create_serology(serology)

@medical_router.get("/serology/{serology_id}")
def get_serology(
    serology_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get serology record by ID"""
    return medical_service.get_serology_by_id(serology_id)

@medical_router.get("/serology/patient/{patient_id}/indicator/{indicator_id}")
def get_serology_history(
    patient_id: int,
    indicator_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get serology history for a patient and indicator"""
    return medical_service.get_serology_history(patient_id, indicator_id)

@medical_router.get("/serology/indicators")
def get_serology_indicators(
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get all serology indicators"""
    return medical_service.get_all_serology_indicators()

@medical_router.get("/serology/indicator/{indicator_id}")
def get_serology_indicator(
    indicator_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get serology indicator by ID"""
    return medical_service.get_serology_indicator_by_id(indicator_id)

@medical_router.put("/serology/{serology_id}")
def update_serology(
    serology_id: int,
    serology: Serology_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Update a serology record"""
    return medical_service.update_serology(serology_id, serology)

@medical_router.delete("/serology/{serology_id}")
def delete_serology(
    serology_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Delete a serology record"""
    return medical_service.delete_serology(serology_id)

# ==================== Symptom Endpoints ====================

@medical_router.get("/symptoms")
def get_all_symptoms(
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get all symptoms"""
    return medical_service.get_all_symptoms()

@medical_router.get("/symptoms/{symptom_id}")
def get_symptom(
    symptom_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get symptom by ID"""
    return medical_service.get_symptom_by_id(symptom_id)

@medical_router.get("/symptoms/patient/{patient_id}/history")
def get_symptoms_history(
    patient_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get symptoms history for a patient"""
    return medical_service.get_symptoms_history(patient_id)

@medical_router.post("/symptoms")
def create_symptoms_occurrence(
    symptoms: Symptoms_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Create a new symptoms occurrence record"""
    return medical_service.create_symptoms_occurrence(symptoms)

@medical_router.get("/symptoms/occurrence/{occurrence_id}")
def get_symptoms_occurrence(
    occurrence_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Get symptoms occurrence by ID"""
    return medical_service.get_symptoms_occurrence_by_id(occurrence_id)

@medical_router.delete("/symptoms/occurrence/{occurrence_id}")
def delete_symptoms_occurrence(
    occurrence_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """Delete a symptoms occurrence record"""
    return medical_service.delete_symptoms_occurrence(occurrence_id)