from fastapi import APIRouter,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import Patient_API
from fastapi.responses import JSONResponse


health_router = APIRouter()

@health_router.get("/patient/serology/history/{patient_id}")
def getSerologyHistory(patient_id : int):
    try:
        res = JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(get_serology_history(patient_id)))
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't fetch patient/serology."}),
    )
    return res


@health_router.put("/patient/serology/add/{patient_id}")
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


