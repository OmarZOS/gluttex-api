# repositories/medical_repository.py (complete)
from typing import Optional, List
from core.models.models import Patient, Serology, SerologyIndicator, Symptom, SymptomsOccurence, PresentedSymptom
import storage.storage_broker as storage_broker

class MedicalRepository:
    """Repository for medical/health-related database operations"""
    
    # ==================== Patient Operations ====================
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        records = storage_broker.get(Patient, {Patient.id_patient: patient_id}, [])
        return records[0] if records else None
    
    # ==================== Serology Operations ====================
    
    def get_serology_by_id(self, serology_id: int) -> Optional[Serology]:
        """Get serology record by ID"""
        records = storage_broker.get(Serology, {Serology.id_serology: serology_id}, [])
        return records[0] if records else None
    
    def get_serology_history(self, patient_id: int, indicator_id: int) -> List[Serology]:
        """Get serology history for a patient and indicator"""
        return storage_broker.get(
            Serology,
            {
                Serology.patient_id: patient_id,
                Serology.indicator_id: indicator_id
            },
            []
        )
    
    def get_serology_by_indicator_and_date(
        self,
        patient_id: int,
        indicator_id: int,
        date_time: str
    ) -> List[Serology]:
        """Get serology record by indicator and date"""
        return storage_broker.get(
            Serology,
            {
                Serology.patient_id: patient_id,
                Serology.indicator_id: indicator_id,
                Serology.serology_date: date_time
            },
            []
        )
    
    def get_serology_indicator_by_id(self, indicator_id: int) -> Optional[SerologyIndicator]:
        """Get serology indicator by ID"""
        records = storage_broker.get(
            SerologyIndicator,
            {SerologyIndicator.id_serology_indicator: indicator_id},
            []
        )
        return records[0] if records else None
    
    def get_all_serology_indicators(self) -> List[SerologyIndicator]:
        """Get all serology indicators"""
        return storage_broker.get(SerologyIndicator, {}, [])
    
    def create_serology(self, serology: Serology) -> Serology:
        """Create a serology record"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(serology)
    
    def update_serology(self, serology: Serology) -> Serology:
        """Update a serology record"""
        from features.insertion import update_record_in_api
        return update_record_in_api(serology)
    
    def delete_serology(self, serology: Serology) -> bool:
        """Delete a serology record"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(serology)
    
    # ==================== Symptom Operations ====================
    
    def get_all_symptoms(self) -> List[Symptom]:
        """Get all symptoms"""
        return storage_broker.get(Symptom, {}, [])
    
    def get_symptom_by_id(self, symptom_id: int) -> Optional[Symptom]:
        """Get symptom by ID"""
        records = storage_broker.get(Symptom, {Symptom.id_symptom: symptom_id}, [])
        return records[0] if records else None
    
    def get_symptoms_history(self, patient_id: int) -> List[SymptomsOccurence]:
        """Get symptoms history for a patient"""
        return storage_broker.get(
            SymptomsOccurence,
            {SymptomsOccurence.symptoms_occurence_ref_patient: patient_id},
            [],
            [SymptomsOccurence.presented_symptom]
        )
    
    def get_symptoms_occurrence_by_id(self, occurrence_id: int) -> Optional[SymptomsOccurence]:
        """Get symptoms occurrence by ID"""
        records = storage_broker.get(
            SymptomsOccurence,
            {SymptomsOccurence.id_symptoms_occurence: occurrence_id},
            [],
            [SymptomsOccurence.presented_symptom]
        )
        return records[0] if records else None
    
    def create_symptoms_occurrence(self, occurrence: SymptomsOccurence) -> SymptomsOccurence:
        """Create a symptoms occurrence record"""
        from features.insertion import insert_or_complete_or_raise
        return insert_or_complete_or_raise(occurrence)
    
    def update_symptoms_occurrence(self, occurrence: SymptomsOccurence) -> SymptomsOccurence:
        """Update a symptoms occurrence record"""
        from features.insertion import update_record_in_api
        return update_record_in_api(occurrence)
    
    def delete_symptoms_occurrence(self, occurrence: SymptomsOccurence) -> bool:
        """Delete a symptoms occurrence record"""
        from features.insertion import delete_record_from_api
        return delete_record_from_api(occurrence)