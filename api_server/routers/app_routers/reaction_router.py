# routers/reaction_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from core.api_models import ReactionBase
from services.reaction_service import ReactionService
from constants import ReactionType

reaction_router = APIRouter()

def get_reaction_service() -> ReactionService:
    return ReactionService()

@reaction_router.post("/")
def handle_reaction(
    reaction: ReactionBase,
    reaction_service: ReactionService = Depends(get_reaction_service)
):
    """
    Create or update a reaction.
    """
    return reaction_service.handle_reaction(reaction)

@reaction_router.get("/user/{user_id}/target/{target_type}/{target_id}")
def get_user_reaction(
    user_id: int,
    target_type: str,
    target_id: int,
    reaction_service: ReactionService = Depends(get_reaction_service)
):
    """
    Get a user's reaction on a specific target.
    """
    try:
        reaction_type = ReactionType(target_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reaction type: {target_type}"
        )
    
    reaction = reaction_service.get_user_reaction_on_target(
        user_id, target_id, reaction_type
    )
    
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    return reaction

@reaction_router.delete("/user/{user_id}/target/{target_type}/{target_id}")
def delete_user_reaction(
    user_id: int,
    target_type: str,
    target_id: int,
    reaction_service: ReactionService = Depends(get_reaction_service)
):
    """
    Delete a user's reaction on a target.
    """
    try:
        reaction_type = ReactionType(target_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reaction type: {target_type}"
        )
    
    success = reaction_service.delete_user_reaction(user_id, target_id, reaction_type)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    return {"message": "Reaction deleted successfully"}

