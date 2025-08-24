
from core.exception_handler import APIException
from core.api_models import Location_API, Person_API
from core.messages import *
from core.models import BloodType, Location, Person, PersonDetails
from features.insertion import insert_or_complete_or_raise
from core.models import  Product
import storage.storage_broker as storage_broker


def fetch_person_blood_type_object(person_blood_type_id: str):
    record = storage_broker.get(BloodType,{BloodType.id_blood_type:person_blood_type_id},None,[])
    if record == []:
        raise APIException(status= HTTP_404_NOT_FOUND,code=BLOOD_TYPE_NOT_EXISTS,message=f"{BLOOD_TYPE_NOT_EXISTS}: {person_blood_type_id}")
    
    person_blood_type = BloodType(id_blood_type=record[0].id_blood_type,blood_type_desc=record[0].blood_type_desc)
    return person_blood_type

def fetch_person_blood_type(person_blood_type_id: str):
    return storage_broker.get(BloodType,{BloodType.id_blood_type:person_blood_type_id},None,[])

def fetch_person_details_object(person_details_id: str):
    record = storage_broker.get(PersonDetails,{PersonDetails.id_person_details:person_details_id},None,[])
        
    try:
        person_details = PersonDetails(id_person_details=record[0].id_person_details,
                                        person_first_name=record[0].person_first_name,
                                        person_last_name=record[0].person_last_name,
                                        person_birth_date=record[0].person_birth_date,
                                        person_gender=record[0].person_gender,
                                        person_nationality=record[0].person_nationality,)
        
    except :
        return None
    return person_details
def fetch_person_details(person_details_id: str):
    return storage_broker.get(PersonDetails,{PersonDetails.id_person_details:person_details_id},None,[])

def fetch_person_object(person_id: str):
    
    record = storage_broker.get(Person,{Person.id_person:person_id},None,[])
    if record == []:
        return None
    person = Person(id_person=record[0].id_person,
                person_details_id=record[0].person_details_id, 
                person_blood_type_id=record[0].person_blood_type_id, 
                person_location_id=record[0].person_location_id,
                )
    return person

def fetch_person(person_id: str):
    return storage_broker.get(Person,{Person.id_person:person_id},None,[Person.person_blood_type,Person.person_location,Person.person_details])

def fetch_only_person_by_id(person_id: str):
    records = storage_broker.get(Person
                                 ,{Person.id_person:person_id}
                                 ,None
                                 ,[
                                     
                                ])
    if records == []: return None
    return records[0] 
    

