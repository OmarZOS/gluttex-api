# services/social_service.py
from typing import Optional
from core.api_models import ReactionBase
from core.exceptions.handler import APIException
from core.messages import *
from services.reaction_service import ReactionService
from repositories.person_repository import PersonRepository  # You'll need to create this

class SocialService:
    """Service for social/reaction operations"""
    
    def __init__(self):
        self.reaction_service = ReactionService()
        self.person_repo = PersonRepository()
    
    def get_person_by_id(self, person_id: int):
        """Get person by ID with full details"""
        # Using repository instead of direct fetch function
        person = self.person_repo.get_person_by_id(person_id)
        if not person:
            raise APIException(
                status=HTTP_404_NOT_FOUND,
                code=PERSON_FETCH_NOT_FOUND,
                details=f"{PERSON_FETCH_NOT_FOUND}: {person_id}"
            )
        
        # If you need full details with nested relationships
        # You might want to implement a get_full_person_by_id method in the repository
        return person
    
    def handle_reaction(self, reaction: ReactionBase):
        """Handle user reactions"""
        # Using the reaction service instead of the old handle_reaction function
        return self.reaction_service.handle_reaction(reaction)