# routers/health_routers/health_router.py
from fastapi import APIRouter, Depends, status, Query
from typing import Optional, List
from core.api_models import Serology_API, Symptoms_API
from core.exception_handler import APIException
from core.messages import *
from services.medical_service import MedicalService

health_router = APIRouter()

def get_medical_service() -> MedicalService:
    return MedicalService()


# ==================== Serology Endpoints ====================

@health_router.get("/patient/serology/history/{patient_id}")
def get_serology_history_by_patient(
    patient_id: int,
    indicator_id: int = Query(..., description="Serology indicator ID"),
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Fetch the serology history of a patient.

    Args:
        patient_id (int): The patient's ID.
        indicator_id (int): The serology indicator ID.

    Returns:
        list: Serology history records.
    """
    try:
        return medical_service.get_serology_history(patient_id, indicator_id)
    except APIException:
        raise
    except Exception as e:
        raise APIException(
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=HEALTH_FETCH_FAILED,
            details=f"Couldn't fetch serology history: {str(e)}"
        )


@health_router.get("/serology/indicators")
def get_all_serology_indicators(
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Get all available serology indicators.
    
    Returns:
        List of serology indicators
    """
    return medical_service.get_all_serology_indicators()


@health_router.get("/serology/indicator/{indicator_id}")
def get_serology_indicator(
    indicator_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Get a specific serology indicator by ID.
    
    Args:
        indicator_id: The serology indicator ID
    """
    return medical_service.get_serology_indicator_by_id(indicator_id)


@health_router.get("/serology/{serology_id}")
def get_serology_record(
    serology_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Get a specific serology record by ID.
    
    Args:
        serology_id: The serology record ID
    """
    return medical_service.get_serology_by_id(serology_id)


@health_router.post("/patient/serology/add")
def add_serology_record(
    serology_record: Serology_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Insert a new serology record.

    Args:
        serology_record (Serology_API): The serology record details.

    Returns:
        dict: Success message with inserted data.
    """
    return medical_service.create_serology(serology_record)


@health_router.put("/patient/serology/update/{serology_id}")
def update_serology_record(
    serology_id: int,
    serology_record: Serology_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Update an existing serology record.

    Args:
        serology_id (int): The serology record ID.
        serology_record (Serology_API): Updated serology record details.

    Returns:
        dict: Success message with updated data.
    """
    return medical_service.update_serology(serology_id, serology_record)


@health_router.delete("/patient/serology/delete/{serology_id}")
def delete_serology_record(
    serology_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Delete a serology record.

    Args:
        serology_id (int): The ID of the serology record to delete.

    Returns:
        dict: Success message.
    """
    return medical_service.delete_serology(serology_id)


# ==================== Symptom Endpoints ====================

@health_router.get("/symptoms/all")
def get_all_symptoms(
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Retrieve all available symptoms.

    Returns:
        list: List of symptoms.
    """
    return medical_service.get_all_symptoms()


@health_router.get("/symptoms/{symptom_id}")
def get_symptom_by_id(
    symptom_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Retrieve a specific symptom by ID.

    Args:
        symptom_id: The symptom ID

    Returns:
        Symptom details
    """
    return medical_service.get_symptom_by_id(symptom_id)


@health_router.post("/patient/symptoms/add")
def add_symptom_occurrence(
    symptoms: Symptoms_API,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Add a new symptom occurrence for a patient.

    Args:
        symptoms (Symptoms_API): The symptom occurrence details.

    Returns:
        dict: Success message with inserted data.
    """
    return medical_service.create_symptoms_occurrence(symptoms)


@health_router.get("/patient/symptoms/history/{patient_id}")
def get_symptom_occurrence(
    patient_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Retrieve a patient's symptom occurrence history.

    Args:
        patient_id (int): The patient's ID.

    Returns:
        list: Symptom history records.
    """
    return medical_service.get_symptoms_history(patient_id)


@health_router.get("/patient/symptoms/occurrence/{occurrence_id}")
def get_symptom_occurrence_by_id(
    occurrence_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Retrieve a specific symptom occurrence by ID.

    Args:
        occurrence_id: The symptom occurrence ID

    Returns:
        Symptom occurrence details
    """
    return medical_service.get_symptoms_occurrence_by_id(occurrence_id)


@health_router.delete("/patient/symptoms/delete/{occurrence_id}")
def delete_symptom_occurrence(
    occurrence_id: int,
    medical_service: MedicalService = Depends(get_medical_service)
):
    """
    Delete a symptom occurrence record.

    Args:
        occurrence_id: The ID of the symptom occurrence to delete

    Returns:
        Success message
    """
    return medical_service.delete_symptoms_occurrence(occurrence_id)