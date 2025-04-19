from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core.exception_handler import API_Resolution
from routers.product_router import product_router
from routers.supplier_router import supplier_router
from routers.user_router import app_user_router
from routers.recipe_router import recipe_router
from routers.health_router import health_router
from routers.auth_router import auth_router
from routers.business_router import business_router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    OperationalError,
    ProgrammingError,
    DatabaseError,
    InternalError,
    InterfaceError,
    StatementError,
    SQLAlchemyError
)
# ----------- App initialisation -------------------------------------

app = FastAPI(
    openapi_url="/api/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/api/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/api/redoc"  # Keep ReDoc at `/redoc`
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request,  exc: Exception):
    # Default error response
    resolution = API_Resolution()
    
    resolution.status_code = 500
    resolution.error_code = "INTERNAL_SERVER_ERROR"
    resolution.message = "An unexpected error occurred."

    # Special handling for known exceptions
    # Inside your exception handler
    if isinstance(exc, HTTPException):
        resolution.status_code = exc.resolution.status_code
        resolution.error_code = "HTTP_EXCEPTION"
        resolution.message = exc.detaresolution.il
    elif isinstance(exc, IntegrityError):
        resolution.status_code = 409
        resolution.error_code = "INTEGRITY_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, DataError):
        resolution.status_code = 400
        resolution.error_code = "DATA_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, OperationalError):
        resolution.status_code = 500
        resolution.error_code = "OPERATIONAL_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, ProgrammingError):
        resolution.status_code = 500
        resolution.error_code = "PROGRAMMING_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, DatabaseError):
        resolution.status_code = 500
        resolution.error_code = "DATABASE_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, InternalError):
        resolution.status_code = 500
        resolution.error_code = "INTERNAL_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, InterfaceError):
        resolution.status_code = 500
        resolution.error_code = "INTERFACE_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, StatementError):
        resolution.status_code = 400
        resolution.error_code = "STATEMENT_ERROR"
        resolution.message = str(exc.orig)
    elif isinstance(exc, SQLAlchemyError):
        resolution.status_code = 500
        resolution.error_code = "SQLALCHEMY_ERROR"
        resolution.message = str(exc)

    return JSONResponse(
        status_code=resolution.status_code,
        content={
            "error_code": resolution.error_code,
            "message": resolution.message,
            "path": request.url.path,
        },
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
