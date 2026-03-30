# app/main.py
from datetime import datetime 
import logging
from core.exception_handler import APIException
from core.messages import *
from fastapi import FastAPI, Depends,  Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALLOWED_ORIGINS
import auth, dependencies
from database import schemas, crud, models
from database.models import engine
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta,timezone
from prometheus_client import make_asgi_app

# Create database tables
models.Base.metadata.create_all(bind=engine)


# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    openapi_url="/auth/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/auth/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/auth/redoc"  # Keep ReDoc at `/redoc`
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If it's a known APIException
    if isinstance(exc, APIException):
        resolution = schemas.API_Resolution(
            status=exc.status,
            error_code=exc.code,
            message=str(exc.message),
        )
        return JSONResponse(
            status_code=exc.status,
            content=resolution.dict(),
        )
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    # If it's an unexpected internal error
    resolution = schemas.API_Resolution(
        status=status_code,
        error_code=INTERNAL_SERVER_ERROR,
        message=str(exc),
    )
    return JSONResponse(
        status_code=status_code,
        content=resolution.dict(),
    )

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Adjust this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/metrics", make_asgi_app())

@app.post("/auth/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise APIException(status_code=HTTP_409_CONFLICT,code=USERNAME_ALREADY_REGISTERED)
    
    try:
        return crud.create_user(db=db, user=user)
    except Exception as e:
        raise APIException(
            status_code=HTTP_417_EXPECTATION_FAILED,
            details=f"Couldn't create user: {str(e)}"
        )

@app.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(dependencies.get_db)
):
    """Authenticate user and generate access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise APIException(
            status=HTTP_401_UNAUTHORIZED,
            code=AUTH_UNAUTHORIZED,
            # headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={
            "sub": str(user.app_user_id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth,
            "gender": user.gender,
            "roles": user.roles,
            "mfa_enabled": user.mfa_enabled,
        },
        expires_delta=access_token_expires
    )
    iat = datetime.now(timezone.utc)

    expire = iat + access_token_expires  # default expiry

    return {
        "access_token": access_token,
        "iat": iat, 
        "expires_at": expire,
        "iss": "gluttex-auth-server",
        "token_type": "bearer",
        "app_user_id": str(user.app_user_id)
    }

@app.get("/auth/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    """Retrieve the currently logged-in user."""
    return current_user

@app.post("/auth/users/update-password/", response_model=schemas.UserResponse)
def update_user_password(
    user: schemas.UserUpdate, 
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """Update the password of the authenticated user."""
    logger.info(f"{user.username}; {user.new_password}")
    return crud.change_user_password(db=db, user=user)

# In server.py, update the delete_user endpoint:
@app.delete("/auth/users/delete", response_model=schemas.UserResponse)
def delete_user(
        user: schemas.UserUpdate, 
        db: Session = Depends(dependencies.get_db)
    ):
    """Deletion of the authenticated user."""
    logger.info(f"{user.username}; {user.new_password}")
    # Get the user first to return full response
    db_user = crud.get_user(db, user.app_user_id)
    if not db_user:
        raise APIException(
            status_code=HTTP_404_NOT_FOUND,
            code=USER_NOT_FOUND,
            message=f"User not found: {user.username}"
        )
    
    # Store user data for response
    user_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "app_user_id": db_user.app_user_id,
        "hashed_password": db_user.hashed_password,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "phone_number": db_user.phone_number,
        "date_of_birth": db_user.date_of_birth,
        "gender": db_user.gender,
        "roles": db_user.roles,
        "login_count": str(db_user.login_count) if db_user.login_count else "0",
        "failed_login_attempts": str(db_user.failed_login_attempts) if db_user.failed_login_attempts else "0",
        "account_locked": db_user.account_locked,
        "mfa_enabled": db_user.mfa_enabled,
        "last_login": db_user.last_login,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "profile_picture": db_user.profile_picture
    }
    
    # Delete the user
    result = crud.delete_user(db=db, user=user)
    
    # Return the stored user data
    return user_data


