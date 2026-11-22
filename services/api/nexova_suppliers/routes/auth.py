"""
Authentication routes for Nexova API.
Handles user registration, login, and token generation.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
import logging
from urllib.parse import quote
from ..models import (
    UserCreate, LoginRequest, TokenResponse, UserResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
)
from ..auth import AuthService
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user
from ..config import get_setting
from ..email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

RESET_REQUEST_MESSAGE = "Si esa dirección está registrada, recibirás un enlace en breve."
INVALID_RESET_MESSAGE = "El enlace de restablecimiento no es válido o ha expirado."

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: SuppliersDB = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **name**: Optional; if not provided, a default name is generated
    - Public registration always creates the account with the 'user' role.
    
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


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    request: ForgotPasswordRequest,
    db: SuppliersDB = Depends(get_db),
):
    """Always respond with the same confirmation to prevent email enumeration."""
    try:
        user = db.get_user_by_email(str(request.email))
        if user:
            token, token_id, expires_at = AuthService.create_password_reset_token(
                user['id'], user['email']
            )
            db.create_password_reset_token(user['id'], token_id, expires_at)
            base_url = get_setting("FRONTEND_BASE_URL", "http://localhost:3001").rstrip("/")
            reset_url = f"{base_url}/reset-password?token={quote(token, safe='')}"
            send_password_reset_email(user['email'], reset_url)
    except Exception:
        # Never log the address, reset token, provider response, or API key.
        logger.warning("Password reset email could not be issued")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": RESET_REQUEST_MESSAGE},
    )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    request: ResetPasswordRequest,
    db: SuppliersDB = Depends(get_db),
):
    claims = AuthService.decode_password_reset_token(request.token)
    if not claims:
        raise HTTPException(status_code=400, detail=INVALID_RESET_MESSAGE)

    user = db.get_user_by_id(claims.get('user_id'))
    if not user or user.get('email') != claims.get('email'):
        raise HTTPException(status_code=400, detail=INVALID_RESET_MESSAGE)

    if not db.consume_password_reset_token(
        user['id'], claims['jti'], int(claims['exp'])
    ):
        raise HTTPException(status_code=400, detail=INVALID_RESET_MESSAGE)

    if not db.update_password(user['id'], request.new_password):
        raise HTTPException(status_code=400, detail=INVALID_RESET_MESSAGE)

    return {"message": "Tu contraseña se actualizó correctamente."}


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    request: ChangePasswordRequest,
    user_payload: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    user = db.get_user_by_id(user_payload['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La sesión ya no es válida.",
        )
    if not AuthService.verify_password(request.current_password, user['password']):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    db.update_password(user['id'], request.new_password)
    return {"message": "Tu contraseña se actualizó correctamente."}
