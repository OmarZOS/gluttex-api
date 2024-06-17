
from core.models import Patient, Symptom, SymptomsOccurence
import storage.storage_broker as storage_broker


def get_symptoms():
    """Returns the symptoms related to the celiac disease."""
    return storage_broker.get(Symptom,{},[])


def get_symptoms_history(patient_id):
    """Returns the patient history of presented symptoms."""
    return storage_broker.get(SymptomsOccurence
                              ,{SymptomsOccurence.symptoms_occurence_ref_patient:patient_id}
                              ,[]
                              ,[SymptomsOccurence.presented_symptom])

def get_symptom_by_id(symptom_id):
    """Returns the patient history of presented symptoms."""
    return storage_broker.get(Symptom
                              ,{Symptom.id_symptom:symptom_id}
                              ,[])
