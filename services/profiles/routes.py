from fastapi import APIRouter, Depends, HTTPException, status
from services.core.models import ProfileResponse, ProfileUpdate
from services.core.database import Database, get_database
from services.auth.dependencies import get_current_user


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
async def get_profile_me(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> ProfileResponse:
    """
    Get the authenticated user's profile.
    
    Protected endpoint - requires authentication.
    
    Returns:
        ProfileResponse with user's profile data
    
    Raises:
        HTTPException(401): If user is not authenticated
        HTTPException(404): If profile not found
    """
    profile = db.get_profile_by_user_id(current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        id=profile["id"],
        user_id=profile["user_id"],
        name=profile["name"],
        phone=profile.get("phone"),
        address=profile.get("address")
    )


@router.put("/me", response_model=ProfileResponse)
async def update_profile_me(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> ProfileResponse:
    """
    Update the authenticated user's profile.
    
    Protected endpoint - requires authentication.
    Users can only update their own profile.
    
    Args:
        profile_data: Fields to update (name, phone, address)
        current_user: Authenticated user
        db: Database instance
    
    Returns:
        Updated ProfileResponse
    
    Raises:
        HTTPException(401): If user is not authenticated
        HTTPException(404): If profile not found
        HTTPException(400): If no fields to update
    """
    profile = db.get_profile_by_user_id(current_user["id"])
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Build update data
    update_data = {}
    if profile_data.name is not None:
        update_data["name"] = profile_data.name
    if profile_data.phone is not None:
        update_data["phone"] = profile_data.phone
    if profile_data.address is not None:
        update_data["address"] = profile_data.address
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Perform update
    success = db.update_profile(profile["id"], **update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    # Return updated profile
    updated_profile = db.get_profile_by_id(profile["id"])
    
    return ProfileResponse(
        id=updated_profile["id"],
        user_id=updated_profile["user_id"],
        name=updated_profile["name"],
        phone=updated_profile.get("phone"),
        address=updated_profile.get("address")
    )
