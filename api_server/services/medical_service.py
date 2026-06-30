# services/medical_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.models.api_models import Serology_API, Symptoms_API
from core.exceptions.handler import APIException
from core.messages import *
from core.models.models import Serology, SerologyIndicator, Symptom, SymptomsOccurence, PresentedSymptom
from repositories.medical_repository import MedicalRepository

class MedicalService:
    """Service for medical/health-related operations"""
    
    def __init__(self):
        self.medical_repo = MedicalRepository()
    
    # ==================== Serology Operations ====================
    
    def _build_serology_model(self, serology_data: Serology_API) -> Serology:
        """Build Serology model from API data"""
        return Serology(
            indicator_id=serology_data.serology_indicator_id,
            serology_date=serology_data.serology_date,
            patient_id=serology_data.id_patient,
            indicator_value=serology_data.serology_indicator_value
        )
    
    def get_serology_by_id(self, serology_id: int) -> Serology:
        """Get serology record by ID"""
        serology = self.medical_repo.get_serology_by_id(serology_id)
        if not serology:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SEROLOGY_NOT_EXISTS,
                message=SEROLOGY_NOT_EXISTS,
                details=f"Serology record {serology_id} not found"
            )
        return serology
    
    def get_serology_history(self, patient_id: int, indicator_id: int) -> List[Serology]:
        """Get serology history for a patient"""
        patient = self.medical_repo.get_patient_by_id(patient_id)
        if not patient:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PATIENT_NOT_EXISTS,
                message=PATIENT_NOT_EXISTS,
                details=f"Patient {patient_id} not found"
            )
        
        return self.medical_repo.get_serology_history(patient_id, indicator_id)
    
    def get_serology_indicator_by_id(self, indicator_id: int) -> SerologyIndicator:
        """Get serology indicator by ID"""
        indicator = self.medical_repo.get_serology_indicator_by_id(indicator_id)
        if not indicator:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SEROLOGY_INDICATOR_NOT_EXISTS,
                message=SEROLOGY_INDICATOR_NOT_EXISTS,
                details=f"Serology indicator {indicator_id} not found"
            )
        return indicator
    
    def get_all_serology_indicators(self) -> List[SerologyIndicator]:
        """Get all serology indicators"""
        return self.medical_repo.get_all_serology_indicators()
    
    def create_serology(self, serology_data: Serology_API) -> Serology:
        """Create a new serology record"""
        
        # Check if serology already exists for this date
        existing = self.medical_repo.get_serology_by_indicator_and_date(
            serology_data.id_patient,
            serology_data.serology_indicator_id,
            serology_data.serology_date
        )
        
        if existing:
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=SEROLOGY_ALREADY_EXISTS,
                message=SEROLOGY_ALREADY_EXISTS,
                details=f"Serology record already exists for date {serology_data.serology_date}"
            )
        
        # Validate indicator exists
        indicator = self.get_serology_indicator_by_id(serology_data.serology_indicator_id)
        
        # Validate patient exists
        patient = self.medical_repo.get_patient_by_id(serology_data.id_patient)
        if not patient:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PATIENT_NOT_EXISTS,
                message=PATIENT_NOT_EXISTS,
                details=f"Patient {serology_data.id_patient} not found"
            )
        
        # Build and create serology
        serology = self._build_serology_model(serology_data)
        
        try:
            return self.medical_repo.create_serology(serology)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SEROLOGY_INSERT_FAILED,
                details=f"Failed to create serology record: {str(e)}"
            )
    
    def update_serology(self, serology_id: int, serology_data: Serology_API) -> Serology:
        """Update an existing serology record"""
        
        # Get existing serology
        serology = self.get_serology_by_id(serology_id)
        
        # Update fields
        serology.serology_date = serology_data.serology_date
        serology.indicator_value = serology_data.serology_indicator_value
        
        try:
            return self.medical_repo.update_serology(serology)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SEROLOGY_UPDATE_FAILED,
                details=f"Failed to update serology record: {str(e)}"
            )
    
    def delete_serology(self, serology_id: int) -> Dict[str, Any]:
        """Delete a serology record"""
        
        serology = self.get_serology_by_id(serology_id)
        success = self.medical_repo.delete_serology(serology)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=HEALTH_DELETE_FAILED,
                details=f"Failed to delete serology record {serology_id}"
            )
        
        return {
            "message": "Serology record deleted successfully",
            "serology_id": serology_id
        }
    
    # ==================== Symptom Operations ====================
    
    def get_all_symptoms(self) -> List[Symptom]:
        """Get all symptoms"""
        return self.medical_repo.get_all_symptoms()
    
    def get_symptom_by_id(self, symptom_id: int) -> Symptom:
        """Get symptom by ID"""
        symptom = self.medical_repo.get_symptom_by_id(symptom_id)
        if not symptom:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SYMPTOM_NOT_EXISTS,
                details=f"Symptom {symptom_id} not found"
            )
        return symptom
    
    def get_symptoms_history(self, patient_id: int) -> List[SymptomsOccurence]:
        """Get symptoms history for a patient"""
        patient = self.medical_repo.get_patient_by_id(patient_id)
        if not patient:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PATIENT_NOT_EXISTS,
                message=PATIENT_NOT_EXISTS,
                details=f"Patient {patient_id} not found"
            )
        
        return self.medical_repo.get_symptoms_history(patient_id)
    
    def create_symptoms_occurrence(self, symptoms_data: Symptoms_API) -> SymptomsOccurence:
        """Create a new symptoms occurrence record"""
        
        # Validate patient exists
        patient = self.medical_repo.get_patient_by_id(symptoms_data.id_patient)
        if not patient:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PATIENT_NOT_EXISTS,
                message=PATIENT_NOT_EXISTS,
                details=f"Patient {symptoms_data.id_patient} not found"
            )
        
        # Create symptoms occurrence
        occurrence = SymptomsOccurence(
            symptoms_occurence_reason=symptoms_data.symptoms_occurence_reason,
            reason_date=symptoms_data.reason_date,
            symptoms_occurence_ref_patient=symptoms_data.id_patient,
            symptoms_occurence_submission_time=datetime.now(),
        )
        
        # Add presented symptoms
        presented_symptoms = []
        for symptom_ref in symptoms_data.symptom_ids:
            symptom = self.medical_repo.get_symptom_by_id(symptom_ref)
            if symptom:
                presented_symptoms.append(
                    PresentedSymptom(presented_symptom_ref_symptom=symptom_ref)
                )
        
        if not presented_symptoms:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=SYMPTOM_INSERT_FAILED,
                details="No valid symptoms provided"
            )
        
        occurrence.presented_symptom = presented_symptoms
        
        try:
            return self.medical_repo.create_symptoms_occurrence(occurrence)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=SYMPTOM_INSERT_FAILED,
                details=f"Failed to create symptoms record: {str(e)}"
            )
    
    def get_symptoms_occurrence_by_id(self, occurrence_id: int) -> SymptomsOccurence:
        """Get symptoms occurrence by ID"""
        occurrence = self.medical_repo.get_symptoms_occurrence_by_id(occurrence_id)
        if not occurrence:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=SYMPTOM_OCCURRENCE_NOT_EXISTS,
                details=f"Symptoms occurrence {occurrence_id} not found"
            )
        return occurrence
    
    def delete_symptoms_occurrence(self, occurrence_id: int) -> Dict[str, Any]:
        """Delete a symptoms occurrence record"""
        
        occurrence = self.get_symptoms_occurrence_by_id(occurrence_id)
        success = self.medical_repo.delete_symptoms_occurrence(occurrence)
        
        if not success:
            raise APIException(
                status=HTTP_500_INTERNAL_SERVER_ERROR,
                code=HEALTH_DELETE_FAILED,
                details=f"Failed to delete symptoms occurrence {occurrence_id}"
            )
        
        return {
            "message": "Symptoms occurrence deleted successfully",
            "occurrence_id": occurrence_id
        }