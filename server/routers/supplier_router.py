from fastapi import status,APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import  Location_API, ProductProvider_API
from features.supplier.supplier_fetch import fetch_supplier_by_id, fetch_supplier_categories, fetch_suppliers
from features.supplier.supplier_insert import insert_supplier



supplier_router = APIRouter()



@supplier_router.put("/supplier/add")
def insert_User(supplier: ProductProvider_API,location:Location_API):
    try:
        res = insert_supplier(supplier,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert supplier."}),
    )
    return res

@supplier_router.get("/supplier/{supplier_id}")
def get_Supplier_by_id(supplier_id: int):
    try:
        res = fetch_supplier_by_id(supplier_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get supplier."}),
    )
    return res

@supplier_router.get("/Supplier/all")
def get_all_Suppliers():
    try:
        res = fetch_suppliers()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get suppliers."}),
    )
    return res

@supplier_router.get("/Supplier/Category/all")
def get_all_Supplier_categories():
    try:
        res = fetch_supplier_categories()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get supplier categories."}),
    )
    return res