from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from core.api_models import Serology_API, Symptoms_API

from features.health.fetch_serology import get_serology_history
from features.health.insert_serology import insert_serology
from features.health.update_serology import update_serology
from features.health.delete_serology import delete_serology
from features.health.symptoms_fetch import get_symptoms, get_symptoms_history
from features.health.symptoms_insert import insert_symptoms

health_router = APIRouter()


@health_router.get("/patient/serology/history/{patient_id}")
def get_serology_history_by_patient(patient_id: int, indicator_id: int):
    """
    Fetch the serology history of a patient.

    Args:
        patient_id (int): The patient's ID.
        indicator_id (int): The serology indicator ID.

    Returns:
        list: Serology history records.
    """
    try:
        return get_serology_history(patient_id, indicator_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch serology history: {str(e)}"
        )


@health_router.put("/patient/serology/add/")
def add_serology_record(serology_record: Serology_API):
    """
    Insert a new serology record.

    Args:
        serology_record (Serology_API): The serology record details.

    Returns:
        dict: Success message with inserted data.
    """
    try:
        return insert_serology(serology_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert serology record: {str(e)}"
        )


@health_router.post("/patient/serology/update/{serology_id}")
def update_serology_record(serology_id: int, serology_record: Serology_API):
    """
    Update an existing serology record.

    Args:
        serology_id (int): The serology record ID.
        serology_record (Serology_API): Updated serology record details.

    Returns:
        dict: Success message with updated data.
    """
    try:
        return update_serology(serology_id, serology_record)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't update serology record: {str(e)}"
        )


@health_router.delete("/patient/serology/delete/{serology_id}")
def delete_serology_record(serology_id: int):
    """
    Delete a serology record.

    Args:
        serology_id (int): The ID of the serology record to delete.

    Returns:
        dict: Success message.
    """
    try:
        return delete_serology(serology_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't delete serology record: {str(e)}"
        )


# -------------------------------------------------------------------------

@health_router.get("/symptoms/all")
def get_all_symptoms():
    """
    Retrieve all available symptoms.

    Returns:
        list: List of symptoms.
    """
    try:
        return get_symptoms()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch symptoms: {str(e)}"
        )


@health_router.put("/patient/symptoms/add/")
def add_symptom_occurrence(symptoms: Symptoms_API):
    """
    Add a new symptom occurrence for a patient.

    Args:
        symptoms (Symptoms_API): The symptom occurrence details.

    Returns:
        dict: Success message with inserted data.
    """
    try:
        return insert_symptoms(symptoms)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't insert symptom occurrence: {str(e)}"
        )


@health_router.get("/patient/symptoms/get/{patient_id}")
def get_symptom_occurrence(patient_id: int):
    """
    Retrieve a patient's symptom occurrence history.

    Args:
        patient_id (int): The patient's ID.

    Returns:
        list: Symptom history records.
    """
    try:
        return get_symptoms_history(patient_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Couldn't fetch symptom occurrence history: {str(e)}"
        )
