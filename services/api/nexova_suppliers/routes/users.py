"""
User management routes for Nexova API.
Protected routes for user operations (read, update, delete).
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..models import UserResponse, UserCreate, UserUpdate, AdminUserCreate
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user

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

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: SuppliersDB = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List account details without password hashes; admins only."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can list users"
        )

    return db.get_all_users()

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
    user_update: UserUpdate,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db)
):
    """
    Update account fields. Owners can update their email; admins can also
    update another user's email and change roles. Profile fields are managed
    through /profiles.
    """
    is_admin = user_payload.get('role') == 'admin'
    if user_payload['user_id'] != user_id and not is_admin:
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

    updates = user_update.model_dump(exclude_unset=True)
    if not updates or any(value is None for value in updates.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide a non-null email or role to update"
        )

    if 'role' in updates and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can change user roles"
        )

    if 'role' in updates:
        updates['role'] = updates['role'].value

    updated_user = db.update_user(user_id, **updates)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )
    
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
