"""
Authentication routes for Nexova API.
Handles user registration, login, and token generation.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..models import UserCreate, LoginRequest, TokenResponse, UserResponse
from ..auth import AuthService
from ..database import SuppliersDB
from ..dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: SuppliersDB = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **name**: Optional; if not provided, a default name is generated
    - **role**: Optional; defaults to 'user'. Accepts: admin, manager, user
    
    Returns access token and user info.
    """
    # Create user (this also creates their Profile automatically)
    new_user = db.create_user(
    email=user_data.email,
    password=user_data.password
)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate token with role
    access_token = AuthService.create_access_token(new_user['id'], new_user['email'], new_user['role'])
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user['id'],
            email=new_user['email'],
            role=new_user['role'],
            created_at=new_user['created_at']
        )
    )

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: SuppliersDB = Depends(get_db)):
    """
    Login with email and password.
    
    Returns access token and user info.
    """
    user = db.get_user_by_email(credentials.email)
    
    if not user or not AuthService.verify_password(credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token with role
    access_token = AuthService.create_access_token(user['id'], user['email'], user.get('role', 'user'))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
        id=user['id'],
        email=user['email'],
        role=user.get('role', 'user'),
        created_at=user['created_at']
)
    )
