
from core.models import Patient, Serology, SerologyIndicator
import storage.storage_broker as storage_broker


def get_patient_by_id(id_patient):
    return storage_broker.get(Patient,{Patient.id_patient:id_patient},[])

def get_serology_history(id_patient,indicator_id):
    return storage_broker.get(Serology,{Serology.patient_id:id_patient,Serology.indicator_id:indicator_id},[])

def fetch_serology_by_indicator_and_date(id_patient,indicator_id,date_time):
    return storage_broker.get(Serology,{Serology.patient_id:id_patient
                                        ,Serology.indicator_id:indicator_id
                                        ,Serology.serology_date:date_time
                                        }
                                        ,[])
def fetch_serology_indicator_by_id(indicator_id):
    return storage_broker.get(SerologyIndicator,{SerologyIndicator.id_serology_indicator:indicator_id
                                        }
                                        ,[])
def fetch_serology_by_id(serology_id):
    return storage_broker.get(Serology,{Serology.id_serology:serology_id
                                        }
                                        ,[])
