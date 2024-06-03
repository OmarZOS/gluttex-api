from fastapi import FastAPI,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.api_models import AppUser_API, Location_API, Person_API, Product_API, ProductImage_API, ProductProvider_API
from core.models import BloodType
from features.location.location_fetch import fetch_location
from features.location.location_insert import insert_location
from features.person.person_fetch import fetch_person_blood_type, fetch_person_details
from features.product.product_fetch import fetch_all_product, fetch_product_by_id, get_product_categories, get_products_by_category_id
from features.product.product_insert import insert_product
from features.person.person_insert import insert_person, insert_person_details
from features.supplier.supplier_fetch import fetch_supplier_by_id, fetch_supplier_categories, fetch_suppliers
from features.supplier.supplier_insert import insert_supplier
from features.user.user_delete import delete_user
from features.user.user_fetch import fetch_all_users, fetch_user_by_id
from features.user.user_insert import insert_user
from features.product.product_update import update_product
from features.product.product_delete import delete_product

from fastapi import FastAPI, File, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import UploadFile as StarletteUploadFile

class LargeFileMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request._max_body_size = 1024 * 1024 * 50  # Set maximum body size to 50 MB
        response = await call_next(request)
        return response


# ----------- App initialisation -------------------------------------

app = FastAPI()

# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}

# # Product related endpoints

@app.get("/Product/all")
def get_all_Products():
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content=jsonable_encoder(fetch_all_product()),
    )
    

@app.post("/product/{product_id}")
def update_Product(product_id: int,product: Product_API, image: ProductImage_API):
    
    try:
        res = update_product(product_id,product, image)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't update product."}),
    )
    return res

@app.put("/product/add")
def insert_Product(product: Product_API, image: ProductImage_API):
    
    try:
        res = insert_product(product, image)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert product."}),
    )
    return res

@app.put("/supplier/add")
def insert_User(supplier: ProductProvider_API,location:Location_API):
    try:
        res = insert_supplier(supplier,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert supplier."}),
    )
    return res

@app.get("/supplier/{supplier_id}")
def get_Supplier_by_id(supplier_id: int):
    try:
        res = fetch_supplier_by_id(supplier_id)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get supplier."}),
    )
    return res

@app.get("/Supplier/all")
def get_all_Suppliers():
    try:
        res = fetch_suppliers()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get suppliers."}),
    )
    return res

@app.get("/Supplier/Category/all")
def get_all_Supplier_categories():
    try:
        res = fetch_supplier_categories()
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't get supplier categories."}),
    )
    return res


@app.get("/product/{Product_id}")
def get_Product_by_id(Product_id: int):
    res = fetch_product_by_id(Product_id)
    return res


@app.delete("/Product/delete/{Product_id}")
def delete_Product_by_id(Product_id: int):
    res = delete_product(Product_id)
    return res

@app.get("/product/category/{category_id}")
def get_products_by_category(category_id: int):
    res = get_products_by_category_id(category_id)
    return res

@app.get("/product/Category/all")
def get_categories():
    res = get_product_categories()
    return res


# @app.post("/Product/insertion")
# def insert_Product(product: Product_API):
#     res = insert_product(product)
#     return res

# User related endpoints

@app.get("/appUser")
def get_all_Users():
    return fetch_all_users()

@app.get("/appUser/{user_id}")
def get_User_by_id(user_id: int):
    res = fetch_user_by_id(user_id)
    return res

@app.put("/appUser/add")
def insert_User(user: AppUser_API,person: Person_API=None,location: Location_API=None):
    """
    This function is responsible for inserting a new user into the system.

    Parameters:
    user (AppUser_API): The user object to be inserted.
    person (Person_API, optional): The person object associated with the user. Defaults to None.
    location (Location_API, optional): The location object associated with the user. Defaults to None.

    Returns:
    JSONResponse: A JSON response object containing the result of the insertion operation.
                 If successful, the response will contain the inserted user's details.
                 If an error occurs, the response will contain an error message.

    Raises:
    Exception: If any error occurs during the insertion process.
    """
    try:
        res = insert_user(user,person,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert user."}),
    )
    return res


@app.delete("/appUser/delete")
def delete_User(user: AppUser_API):
    try:
        res = delete_user(user)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't delete user."}),
    )
    return res


# @app.get("/person")
# def get_all_persons():
#     return fetch_all_persons()

# @app.get("/person/{person_id}")
# def get_person_by_id(person_id: int):
#     res = fetch_person_by_id(person_id)
#     return res

# @app.post("/appUser/add/{user_id}")
# def update_User(User: AppUser_API):
#     res = update_user(User)
#     return res

# @app.post("/appUser/delete/{user_id}")
# def delete_AppUser(AppUser: AppUser_API):
#     res = delete_appUser(AppUser)
#     return res



# /product/delete
# /supplier/delete