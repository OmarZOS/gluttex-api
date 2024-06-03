from fastapi import FastAPI
from routers.product_router import product_router
from routers.supplier_router import supplier_router
from routers.user_router import app_user_router
from routers.recipe_router import recipe_router


# ----------- App initialisation -------------------------------------

app = FastAPI()

app.include_router(supplier_router)
app.include_router(product_router)
app.include_router(app_user_router)
app.include_router(recipe_router)

# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}



# @app.post("/Product/insertion")
# def insert_Product(product: Product_API):
#     res = insert_product(product)
#     return res

# User related endpoints


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