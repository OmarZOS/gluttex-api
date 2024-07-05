from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import Patient_API, Serology_API, Symptoms_API
from features.health.fetch_serology import get_serology_history
from features.health.insert_serology import insert_serology
from features.health.update_serology import update_serology
from features.health.delete_serology import delete_serology
from features.health.symptoms_fetch import get_symptoms, get_symptoms_history
from features.health.symptoms_insert import insert_symptoms



health_router = APIRouter()

@health_router.get("/patient/serology/history/{patient_id}")
def Get_Serology_History(patient_id : int,indicator_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_serology_history(patient_id,indicator_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch patient/serology."}),
    )
    return res


@health_router.put("/patient/serology/add/")
def Add_Serology_Record(serology_record : Serology_API):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(insert_serology(serology_record)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert serology record."}),
    )
    return res

@health_router.post("/patient/serology/update/{serology_id}")
def update_Serology_Record(serology_id:int,serology_record : Serology_API):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(update_serology(serology_id,serology_record)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't update serology record."}),
    )
    return res

@health_router.delete("/patient/serology/delete/{serology_id}")
def Delete_Serology_Record(serology_id:int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(delete_serology(serology_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete serology record."}),
    )
    return res

# -------------------------------------------------------------------------

@health_router.get("/symptoms/all")
def Get_Symptoms():
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(get_symptoms()))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch symptoms."}),
    )
    return res

@health_router.put("/patient/symptoms/add/")
def Add_Symptom_Occurence(symptoms:Symptoms_API):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(insert_symptoms(symptoms)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert serology record."}),
    )
    return res

@health_router.get("/patient/symptoms/get/{patient_id}")
def Get_Symptom_Occurence(patient_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_symptoms_history(patient_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert serology record."}),
    )
    return res


