# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALLOWED_ORIGINS
import auth, dependencies
from database import schemas, crud, models
from database.models import engine
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    openapi_url="/auth/openapi.json",  # Move OpenAPI to `/api/openapi.json`
    docs_url="/auth/docs",  # Keep Swagger UI at `/docs`
    redoc_url="/auth/redoc"  # Keep ReDoc at `/redoc`
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Adjust this for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    try:
        return crud.create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Couldn't create user: {str(e)}"
        )

@app.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(dependencies.get_db)
):
    """Authenticate user and generate access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={
            "sub": user.app_user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_of_birth": user.date_of_birth,
            "gender": user.gender,
            "roles": user.roles,
            "mfa_enabled": user.mfa_enabled,
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "app_user_id": str(user.app_user_id)
    }

@app.get("/auth/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    """Retrieve the currently logged-in user."""
    return current_user

@app.put("/auth/users/update-password/", response_model=schemas.UserResponse)
def update_user_password(
    user: schemas.UserUpdate, 
    db: Session = Depends(dependencies.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    """Update the password of the authenticated user."""
    return crud.change_user_password(db=db, user=user)
