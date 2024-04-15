from fastapi import FastAPI
from core.api_models import OrderMed_API, Payment_API, Product_API, ProductSupplier_API, User_API
from features.product.product_fetch import fetch_all_product, fetch_product_by_id, fetch_products_by_category
from features.product.product_insert import insert_product
from features.user.user_fetch import fetch_all_users, fetch_user_by_id
from features.user.user_insert import insert_user

# ----------- App initialisation -------------------------------------

app = FastAPI()

# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}

# Product related endpoints

@app.get("/Product/all")
def get_all_Products():
    return fetch_all_product()

@app.get("/Product/{Product_id}")
def get_Product_by_id(Product_id: int):
    res = fetch_product_by_id(Product_id)
    return res

@app.get("/Product/Category/{Category_id}")
def get_Category_by_id(Category_id: int):
    res = fetch_products_by_category(Category_id)
    return res

@app.post("/Product/insertion")
def insert_Product(product: Product_API):
    res = insert_product(product)
    return res

# User related endpoints

@app.get("/User/all")
def get_all_Users():
    return fetch_all_users()

@app.get("/User/{User_id}")
def get_User_by_id(User_id: int):
    res = fetch_user_by_id(User_id)
    return res

@app.post("/User/insertion")
def insert_User(User: User_API):
    res = insert_user(User)
    return res

