"""
User management routes for Nexova API.
Protected routes for user operations (read, update, delete).
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models import UserResponse, UserCreate, AdminUserCreate
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user, verify_owns_resource

router = APIRouter(prefix="/users", tags=["users"])
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: AdminUserCreate,
    db: SuppliersDB = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a user. Only administrators can create users."""

    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users"
    )

    new_user = db.create_user(
        email=user_data.email,
        password=user_data.password,
        role=user_data.role.value
    )

    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return UserResponse(
        id=new_user['id'],
        email=new_user['email'],
        role=new_user.get('role', 'user'),
        created_at=new_user['created_at']
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Get current authenticated user's information.
    Requires valid JWT token.
    """
    user = db.get_user_by_id(user_payload['user_id'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        role=user.get('role', 'user'),
        created_at=user['created_at']

)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Get a specific user's public information.
    Only the user themselves or admin can view full details.
    """
    # Users can only access their own data
    if user_payload['user_id'] != user_id:
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
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        role=user.get('role', 'user'),
        created_at=user['created_at']

)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    name: str = None,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Update user information (name only).
    Users can only update their own profile.
    """
    if user_payload['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this user"
        )
    
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updates = {}
    if name is not None:
        updates['name'] = name
    
    if updates:
        updated_user = db.update_user(user_id, **updates)
    else:
        updated_user = user
    
    return UserResponse(
        id=updated_user['id'],
        email=updated_user['email'],
     role=updated_user.get('role', 'user'),
        created_at=updated_user['created_at']
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Delete a user account.
    Users can only delete their own account.
    Also deletes associated profile data.
    """
    if user_payload['user_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this user"
        )
    
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete_user(user_id)
