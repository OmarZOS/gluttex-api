from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# from core.exception_handler import API_Resolution
from constants import SECRET_KEY
from core.api_models import API_Resolution
from core.exception_handler import APIException
from routers.business_routers.product_router import product_router
from routers.business_routers.supplier_router import supplier_router
from routers.app_routers.user_router import app_user_router
from routers.health_routers.recipe_router import recipe_router
from routers.health_routers.health_router import health_router
from routers.app_routers.auth_router import auth_router
from routers.app_routers.notification_router import notification_router
from routers.business_routers.staff_router import staff_router
from routers.business_routers.document_router import document_router

from routers.business_routers.business_router import business_router
from routers.search_router import search_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
# ----------- App initialisation -------------------------------------

app = FastAPI(
    openapi_url="/api/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/api/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/api/redoc"  # Keep ReDoc at `/redoc`
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If it's a known APIException
    if isinstance(exc, APIException):
        resolution = API_Resolution(
            status=exc.status,
            error_code=exc.code,
            message=str(exc.details),
        )
        return JSONResponse(
            status_code=exc.status,
            content=resolution.dict(),
        )

    # If it's an unexpected internal error
    resolution = API_Resolution(
        status=500,
        error_code="INTERNAL_SERVER_ERROR",
        message=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content=resolution.dict(),
    )

# 1. Add SessionMiddleware FIRST (before any other middleware or routers)
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=3600,
    same_site="lax",
    https_only=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,prefix="/api")
app.include_router(supplier_router,prefix="/api") # , dependencies=[Depends(verify_token)]
app.include_router(product_router,prefix="/api") # , dependencies=[Depends(verify_token)]
app.include_router(recipe_router,prefix="/api") # , dependencies=[Depends(verify_token)]
app.include_router(health_router,prefix="/api") # , dependencies=[Depends(verify_token)]
app.include_router(app_user_router,prefix="/api")
app.include_router(business_router,prefix="/api")
app.include_router(search_router,prefix="/api")
app.include_router(staff_router,prefix="/api")
app.include_router(notification_router,prefix="/api")
app.include_router(document_router,prefix="/api")

# ------------- Standard endpoints -----------------------------------------------

@app.get("/api")
def home():
    return {'data': 'Hello from the other side'}
