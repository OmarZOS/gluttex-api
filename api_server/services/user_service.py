import logging
import datetime
from typing import Optional
from core.api_models import AppUser_API, Person_API, Location_API, AppUserUpdate_API
from core.exception_handler import APIException
from core.messages import *
from core.models import AppUser
from repositories.user_repository import UserRepository
from repositories.person_repository import PersonRepository
from repositories.location_repository import LocationRepository
from services.auth_service import AuthService
from services.person_service import PersonService

logger = logging.getLogger("FastAPIApp")

class UserService:
    """Service for user-related business logic"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.person_repo = PersonRepository()
        self.location_repo = LocationRepository()
        self.auth_service = AuthService()
        self.person_service = PersonService()
    
    def get_all_users(self):
        """Get all users"""
        return self.user_repo.get_all()
    
    def get_user_by_id(self, user_id: int, full: bool = False):
        """Get user by ID with optional full details"""
        user = self.user_repo.get_by_id(user_id, eager_load=full)
        if not user:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=APPUSER_NOT_EXISTS,
                details=f"{APPUSER_NOT_EXISTS}: {user_id}"
            )
        return user
    
    async def create_user(
        self,
        user_data: AppUser_API,
        person_data: Optional[Person_API] = None,
        location_data: Optional[Location_API] = None,
        provider: Optional[str] = None
    ):
        """Create a new user"""
        
        # Check if user already exists
        if self.user_repo.get_by_name(user_data.app_user_name):
            raise APIException(
                status=HTTP_409_CONFLICT,
                code=APPUSER_ALREADY_EXISTS,
                details=f"User '{user_data.app_user_name}' already exists."
            )
        
        # Validate user type
        user_type = self.user_repo.get_user_type(user_data.app_user_type_id)
        if not user_type:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=APPUSERTYPE_NOT_EXISTS,
                details=f"Invalid user type ID: {user_data.app_user_type_id}"
            )
        
        # Build AppUser object
        now = datetime.datetime.now()
        app_user = AppUser(
            app_user_name=user_data.app_user_name,
            app_user_password="",
            app_user_preferences=user_data.app_user_preferences,
            app_user_image_url=user_data.app_user_image_url,
            app_user_type_id=user_type.id_app_user_type,
            app_user_email=user_data.app_user_email,
            app_user_last_active=str(now),
            app_user_last_updated=str(now),
            app_user_creation=str(now),
        )
        
        # Attach Person if provided
        if person_data:
            existing_person = self.person_repo.get_by_id(person_data.id_person)
            if existing_person:
                app_user.app_user_person_id = existing_person.id_person
            else:
                app_user.app_user_person = self.person_service.generate_person_object(person_data, location_data)
        
        # Save AppUser record
        try:
            user = self.user_repo.create(app_user)
        except Exception as e:
            logger.error(f"Failed to insert AppUser: {e}")
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=USER_INSERT_FAILED,
                details=f"Failed to insert AppUser: {e}"
            )
        
        # Handle authentication for non-OAuth users
        if provider and provider.lower() == "google":
            logger.info(f"Skipping auth creation for OAuth provider '{provider}'")
            return user
        
        # Create auth record for regular users
        user_auth_data = {
            "username": user.app_user_name,
            "app_user_id": user.id_app_user,
            "password": user_data.app_user_password,
        }
        
        try:
            logger.info(f"Creating auth record for user '{user.app_user_name}'")
            user_auth_record = await self.auth_service.create_user_auth(user_auth_data)
            self.update_user_password(user, user_auth_record["hashed_password"])
        except APIException as e:
            logger.error(f"Failed to create/update auth record: {e}")
            if e.status == HTTP_417_EXPECTATION_FAILED:
                self.user_repo.delete(user)
            raise APIException(
                status=HTTP_410_GONE,
                code=USER_AUTH_CREATION_FAILED,
                details=str(e)
            )
        
        return user
    
    def update_user(
        self,
        user_data: AppUser_API,
        person_data: Person_API,
        location_data: Location_API
    ):
        """Update user information"""
        
        user = self.get_user_by_id(user_data.id_app_user)
        
        # Update person information
        person = self.person_service.refresh_or_insert_person(person_data, location_data)
        
        # Validate user type
        user_type = self.user_repo.get_user_type(user_data.app_user_type_id)
        if not user_type:
            raise APIException(
                status=HTTP_400_BAD_REQUEST,
                code=APPUSERTYPE_NOT_EXISTS,
                details=f"{APPUSERTYPE_NOT_EXISTS}: {user_data.app_user_type_id}"
            )
        
        # Update allowed fields
        updatable_fields = [
            "app_user_preferences",
            "app_user_last_active",
            "app_user_image_url",
            "app_user_email",
            "app_user_type_id",
        ]
        
        for field in updatable_fields:
            if hasattr(user_data, field):
                setattr(user, field, getattr(user_data, field))
        
        user.app_user_person_id = person.id_person
        user.app_user_last_updated = datetime.datetime.now()
        
        try:
            return self.user_repo.update(user)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=USER_UPDATE_FAILED,
                message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",
                details=str(e)
            )
    
    def update_user_password(self, user_record, hashed_password: str):
        """Update user's password hash"""
        user = self.get_user_by_id(user_record.id_app_user)
        user.app_user_password = hashed_password
        
        try:
            return self.user_repo.update(user)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=USER_UPDATE_FAILED,
                message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",
                details=str(e)
            )
    
    def update_user_image_url(self, user_record, image_url: str):
        """Update user's image URL"""
        user = self.get_user_by_id(user_record.id_app_user)
        user.app_user_image_url = image_url
        
        try:
            return self.user_repo.update(user)
        except Exception as e:
            raise APIException(
                status=HTTP_417_EXPECTATION_FAILED,
                code=USER_UPDATE_FAILED,
                message=f"{USER_UPDATE_FAILED}: {user.id_app_user}",
                details=str(e)
            )
    
    def delete_user(self, user_data: AppUser_API):
        """Delete a user"""
        user = self.get_user_by_id(user_data.id_app_user)
        return self.user_repo.delete(user)
    
    async def update_user_password_with_auth(
        self,
        user_data: AppUserUpdate_API,
        token: str
    ):
        """Update password with authentication server sync"""
        
        user_update = {
            "app_user_id": user_data.id_app_user,
            "username": user_data.username,
            "new_username": user_data.username,
            "new_password": user_data.new_password
        }
        
        try:
            auth_response = await self.auth_service.update_password(user_update, token)
            new_password_hash = auth_response.get("hashed_password")
            return self.update_user_password(user_data, new_password_hash)
        except APIException as e:
            raise APIException(
                status=e.status,
                code=e.code,
                message=e.message
            )