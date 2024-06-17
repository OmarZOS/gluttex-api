from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import Patient_API, Serology_API
from fastapi.responses import JSONResponse
from features.health.fetch_serology import get_serology_history
from features.health.insert_serology import insert_serology
from features.health.update_serology import update_serology
from features.health.delete_serology import delete_serology



health_router = APIRouter()

@health_router.get("/patient/serology/history/{patient_id}")
def getSerologyHistory(patient_id : int,indicator_id : int):
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
def addSerologyRecord(serology_record : Serology_API):
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
def updateSerologyRecord(serology_id:int,serology_record : Serology_API):
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
def deleteSerologyRecord(serology_id:int):
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

@health_router.get("/patient/symptoms")
def getSymptoms():
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_symptoms()))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch patient/serology."}),
    )
    return res

@health_router.put("/patient/symptoms/add/{patient_id}")
def addSerologyRecord(patient_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(add_serology_record(patient_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert serology record."}),
    )
    return res


