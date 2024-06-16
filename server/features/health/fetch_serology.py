
import storage.storage_broker as storage_broker





def get_diagnosis(id_patients):
    return storage_broker.get(Diagnosis,{Diagnosis.id_patients:id_patients},[])


