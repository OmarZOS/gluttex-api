from fastapi import FastAPI,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from server.core.api_models import AppUser_API, Location_API, Person_API, Product_API, ProductImage_API, ProductProvider_API
from server.core.models import BloodType
from server.features.location.location_fetch import fetch_location
from server.features.location.location_insert import insert_location
from server.features.person.person_fetch import fetch_person_blood_type, fetch_person_details
from server.features.product.product_fetch import fetch_all_product, fetch_product_by_id, get_product_categories, get_products_by_category_id
from server.features.product.product_insert import insert_product
from server.features.person.person_insert import insert_person, insert_person_details
from server.features.supplier.supplier_insert import insert_supplier
from server.features.user.user_fetch import fetch_all_users, fetch_user_by_id
from server.features.user.user_insert import insert_user

# ----------- App initialisation -------------------------------------

app = FastAPI()

# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}

# # Product related endpoints

@app.get("/Product/all")
def get_all_Products():
    return fetch_all_product()

@app.put("/product/add")
def insert_User(product: Product_API, image: ProductImage_API):
    
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

@app.get("/product/{Product_id}")
def get_Product_by_id(Product_id: int):
    res = fetch_product_by_id(Product_id)
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
    try:
        res = insert_user(user,person,location)
    except Exception as e:
        res = JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content=jsonable_encoder({"detail": str(e), "Error": "Couldn't insert user."}),
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



# /appUser/delete
# /appUser
# /product/delete
# /product
# /supplier/delete
# /supplier