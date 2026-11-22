"""
User profile management routes for Nexova API.
Protected routes for profile operations (read and update).
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..models import ProfileResponse, ProfileCreate
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/me", response_model=ProfileResponse)
def get_own_profile(
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Get current user's profile.
    Requires valid JWT token.
    """
    profile = db.get_profile_by_user_id(user_payload['user_id'])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        id=profile['id'],
        user_id=profile['user_id'],
        name=profile.get('name'),
        phone=profile.get('phone'),
        address=profile.get('address'),
        specialization=profile.get('specialization'),
        experience_years=profile.get('experience_years'),
        created_at=profile['created_at'],
        updated_at=profile.get('updated_at')
)

@router.get("/{user_id}", response_model=ProfileResponse)
def get_user_profile(
    user_id: int,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Get a specific user's profile.
    Users can only view their own profile; use /profiles/me for authenticated user.
    """
    if user_payload['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this profile"
        )
    
    profile = db.get_profile_by_user_id(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        id=profile['id'],
        user_id=profile['user_id'],
        name=profile.get('name'),
        phone=profile.get('phone'),
        address=profile.get('address'),
        specialization=profile.get('specialization'),
        experience_years=profile.get('experience_years'),
        created_at=profile['created_at'],
        updated_at=profile.get('updated_at')
    )

@router.put("/me", response_model=ProfileResponse)
def update_own_profile(
    profile_data: ProfileCreate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Update current user's profile.
    Requires valid JWT token.
    """
    profile = db.get_profile_by_user_id(user_payload['user_id'])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update only provided fields
    updates = profile_data.model_dump(exclude_unset=True)
    updated_profile = db.update_profile(user_payload['user_id'], **updates)
    
    return ProfileResponse(
        id=updated_profile['id'],
        user_id=updated_profile['user_id'],
        name=updated_profile.get('name'),
        phone=updated_profile.get('phone'),
        address=updated_profile.get('address'),
        specialization=updated_profile.get('specialization'),
        experience_years=updated_profile.get('experience_years'),
        created_at=updated_profile['created_at'],
        updated_at=updated_profile.get('updated_at')
    )

@router.put("/{user_id}", response_model=ProfileResponse)
def update_user_profile(
    user_id: int,
    profile_data: ProfileCreate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Update a user's profile.
    Users can only update their own profile.
    """
    if user_payload['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this profile"
        )
    
    profile = db.get_profile_by_user_id(user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update only provided fields
    updates = profile_data.model_dump(exclude_unset=True)
    updated_profile = db.update_profile(user_id, **updates)
    
    return ProfileResponse(
        id=updated_profile['id'],
        user_id=updated_profile['user_id'],
        name=updated_profile.get('name'),
        phone=updated_profile.get('phone'),
        address=updated_profile.get('address'),
        specialization=updated_profile.get('specialization'),
        experience_years=updated_profile.get('experience_years'),
        created_at=updated_profile['created_at'],
        updated_at=updated_profile.get('updated_at')
    )
