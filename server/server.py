from fastapi import FastAPI, Depends, HTTPException, Request
# from starlette.middleware.sessions import SessionMiddleware
from constants import SECRET_KEY

from routers.product_router import product_router
from routers.supplier_router import supplier_router
from routers.user_router import app_user_router
from routers.recipe_router import recipe_router
from routers.health_router import health_router
from routers.auth_router import auth_router


# ----------- App initialisation -------------------------------------

app = FastAPI()

app.include_router(auth_router)
app.include_router(supplier_router)
app.include_router(product_router)
app.include_router(recipe_router)
app.include_router(health_router)
# app.include_router(app_user_router)

# ------------- Standard endpoints -----------------------------------------------

@app.get("/")
def home():
    return {'data': 'Hello from the other side'}


