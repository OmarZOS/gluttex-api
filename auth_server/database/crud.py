# app/crud.py
from sqlalchemy.orm import Session
from database.crypt import generate_salt, hash_with_salt
import database.models as models 
import database.schemas as schemas 
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.AppUser).filter(models.AppUser.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.AppUser).filter(models.AppUser.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.AppUser).filter(models.AppUser.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    salt = generate_salt()
    hashed_password = hash_with_salt(user.password, salt)
    db_user = models.AppUser(
        username = user.username,
        email = user.email,
        app_user_id = user.app_user_id,
        phone_number = user.phone_number,
        hashed_password = hashed_password,
        password_salt = salt,
        first_name = user.first_name,
        last_name = user.last_name,
        date_of_birth = user.date_of_birth,
        gender = user.gender,
        profile_picture = user.profile_picture,
        roles = user.roles,
        last_login = datetime.datetime.now(),
        login_count = str(user.login_count),
        failed_login_attempts = str(user.failed_login_attempts),
        account_locked = False,
        mfa_enabled = False,
        created_at = datetime.datetime.now(),
        updated_at = datetime.datetime.now(),
        deleted_at = None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_object(db: Session, user):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def change_user_password(db: Session, user:schemas.UserUpdate):
    db_user = get_user_by_username(db, user.username)
    db_user.password_salt = generate_salt()
    db_user.hashed_password = hash_with_salt(user.new_password, db_user.password_salt)
    return update_user_object(db,user)

def change_username(db: Session, user:schemas.UserUpdate):
    db_user = get_user_by_username(db, user.username)
    db_user.username = user.new_username
    return update_user_object(db,user)




