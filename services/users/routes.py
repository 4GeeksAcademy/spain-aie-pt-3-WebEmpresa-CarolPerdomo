from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from services.core.models import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithProfile,
    ProfileResponse,
    UserRole,
)
from services.core.database import Database, get_database
from services.auth.dependencies import get_current_user, get_current_admin_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserWithProfile, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Database = Depends(get_database)
) -> UserWithProfile:
    """
    Register a new user.
    
    - Creates a User with role 'user' by default
    - If profile fields are provided, creates the associated Profile
    - Password is hashed before storing
    
    Args:
        user_data: Email, password, and optional profile fields
        db: Database instance
    
    Returns:
        UserWithProfile with created user and profile
    
    Raises:
        HTTPException(400): If email is already registered
    """
    # Check if email already exists
    existing_user = db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with default role 'user'
    user = db.create_user(
        email=user_data.email,
        password=user_data.password,
        role=UserRole.USER
    )
    
    # Create profile if profile data is provided
    profile = None
    if user_data.name:
        profile = db.create_profile(
            user_id=user["id"],
            name=user_data.name,
            phone=user_data.phone,
            address=user_data.address
        )
    
    # Build response
    profile_response = None
    if profile:
        profile_response = ProfileResponse(
            id=profile["id"],
            user_id=profile["user_id"],
            name=profile["name"],
            phone=profile.get("phone"),
            address=profile.get("address")
        )
    
    return UserWithProfile(
        id=user["id"],
        email=user["email"],
        is_active=user["is_active"],
        role=user["role"],
        created_at=user["created_at"],
        profile=profile_response
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> List[UserResponse]:
    """
    List all users.
    
    Protected endpoint - requires authentication.
    
    Returns:
        List of users (without passwords)
    """
    users = db.get_all_users()
    return [
        UserResponse(
            id=user["id"],
            email=user["email"],
            is_active=user["is_active"],
            role=user["role"],
            created_at=user["created_at"]
        )
        for user in users
    ]


@router.get("/{user_id}", response_model=UserWithProfile)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> UserWithProfile:
    """
    Get a user by ID.
    
    Protected endpoint - requires authentication.
    Regular users can only view their own profile;
    admins can view any user.
    
    Args:
        user_id: ID of the user to retrieve
        current_user: Authenticated user
        db: Database instance
    
    Returns:
        UserWithProfile with user and associated profile
    
    Raises:
        HTTPException(403): If not allowed to view
        HTTPException(404): If user not found
    """
    # Check permissions
    if current_user["id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user"
        )
    
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get associated profile
    profile = db.get_profile_by_user_id(user_id)
    
    profile_response = None
    if profile:
        profile_response = ProfileResponse(
            id=profile["id"],
            user_id=profile["user_id"],
            name=profile["name"],
            phone=profile.get("phone"),
            address=profile.get("address")
        )
    
    return UserWithProfile(
        id=user["id"],
        email=user["email"],
        is_active=user["is_active"],
        role=user["role"],
        created_at=user["created_at"],
        profile=profile_response
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> UserResponse:
    """
    Update user credentials (email and/or role).
    
    Protected endpoint - requires authentication.
    - Regular users can only update their own email
    - Only admins can change user roles
    
    Args:
        user_id: ID of the user to update
        user_data: Fields to update (email, role)
        current_user: Authenticated user
        db: Database instance
    
    Returns:
        Updated UserResponse
    
    Raises:
        HTTPException(403): If not allowed to update
        HTTPException(404): If user not found
        HTTPException(400): If email already exists
    """
    # Check if user exists
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    is_admin = current_user["role"] == "admin"
    is_own_account = current_user["id"] == user_id
    
    if not is_admin and not is_own_account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user"
        )
    
    # Validate role change permissions
    if user_data.role and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change user roles"
        )
    
    # Check if email is unique (if changing email)
    if user_data.email and user_data.email != user["email"]:
        existing = db.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Build update data
    update_data = {}
    if user_data.email:
        update_data["email"] = user_data.email
    if user_data.role:
        update_data["role"] = user_data.role.value
    
    # Perform update
    success = db.update_user(user_id, **update_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Return updated user
    updated_user = db.get_user_by_id(user_id)
    
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        is_active=updated_user["is_active"],
        role=updated_user["role"],
        created_at=updated_user["created_at"]
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Delete a user and their associated profile.
    
    Protected endpoint - requires authentication.
    - Regular users can only delete their own account
    - Only admins can delete any user
    
    Args:
        user_id: ID of the user to delete
        current_user: Authenticated user
        db: Database instance
    
    Raises:
        HTTPException(403): If not allowed to delete
        HTTPException(404): If user not found
    """
    # Check if user exists
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check permissions
    is_admin = current_user["role"] == "admin"
    is_own_account = current_user["id"] == user_id
    
    if not is_admin and not is_own_account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this user"
        )
    
    # Delete user (and associated profile)
    success = db.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete user"
        )
    
    return None
