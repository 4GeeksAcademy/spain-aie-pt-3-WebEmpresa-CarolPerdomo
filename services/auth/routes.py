from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from services.core.models import (
    LoginRequest,
    LoginResponse,
    MeResponse,
    ProfileResponse,
)
from services.core.security import create_access_token
from services.core.config import settings
from services.core.database import Database, get_database
from services.auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Database = Depends(get_database)
) -> LoginResponse:
    """
    Authenticate a user with email and password.
    
    Returns a JWT access token if credentials are valid.
    
    Args:
        credentials: Email and password
        db: Database instance
    
    Returns:
        LoginResponse with access_token
    
    Raises:
        HTTPException(401): If credentials are invalid
    """
    user = db.authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=MeResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
) -> MeResponse:
    """
    Get the authenticated user's email, role, and profile.
    
    Returns:
        MeResponse with user info and associated profile
    
    Raises:
        HTTPException(401): If user is not authenticated
    """
    profile = db.get_profile_by_user_id(current_user["id"])
    
    profile_response = None
    if profile:
        profile_response = ProfileResponse(
            id=profile["id"],
            user_id=profile["user_id"],
            name=profile["name"],
            phone=profile.get("phone"),
            address=profile.get("address")
        )
    
    return MeResponse(
        email=current_user["email"],
        role=current_user["role"],
        profile=profile_response
    )
