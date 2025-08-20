from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# from core.exception_handler import API_Resolution
from core.api_models import API_Resolution
from core.exception_handler import APIException
from routers.product_router import product_router
from routers.supplier_router import supplier_router
from routers.user_router import app_user_router
from routers.recipe_router import recipe_router
from routers.health_router import health_router
from routers.auth_router import auth_router
from routers.business_router import business_router
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

# ------------- Standard endpoints -----------------------------------------------

@app.get("/api")
def home():
    return {'data': 'Hello from the other side'}
