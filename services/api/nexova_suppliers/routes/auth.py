"""
Authentication routes for Nexova API.
Handles user registration, login, and token generation.
"""
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status, Depends
from ..models import (UserCreate, LoginRequest, TokenResponse, UserResponse,
                      ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest)
from ..auth import AuthService
from ..database import SuppliersDB
from ..dependencies import get_db, get_current_user
from ..email_service import EmailDeliveryError, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
RESET_TOKEN_TTL_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_TTL_MINUTES", "30"))
if not 15 <= RESET_TOKEN_TTL_MINUTES <= 60:
    raise ValueError("PASSWORD_RESET_TOKEN_TTL_MINUTES must be between 15 and 60")
GENERIC_RESET_MESSAGE = "Si el correo está registrado, recibirás un enlace para restablecer la contraseña."


def get_client_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


def deliver_password_reset_email(email: str, reset_url: str) -> None:
    try:
        send_password_reset_email(email, reset_url)
    except EmailDeliveryError as exc:
        # The provider detail is sanitized; never log the user's address, token, or API key.
        logger.warning("Password reset email delivery failed: %s", exc)

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


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(payload: ForgotPasswordRequest, http_request: Request, background_tasks: BackgroundTasks, db: SuppliersDB = Depends(get_db)):
    """Send a single-use reset link without revealing whether the email exists."""
    user = db.get_user_by_email(payload.email)
    db.record_password_audit("reset_requested", get_client_ip(http_request), user['id'] if user else None)
    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
        db.create_password_reset_token(user['id'], hashlib.sha256(token.encode()).hexdigest(), expires_at)
        reset_page = os.getenv("PASSWORD_RESET_URL", "http://localhost:3001/reset-password")
        reset_url = f"{reset_page}?token={quote(token)}"
        background_tasks.add_task(deliver_password_reset_email, user['email'], reset_url)
    return {"message": GENERIC_RESET_MESSAGE}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, http_request: Request, db: SuppliersDB = Depends(get_db)):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    user_id = db.get_password_reset_token_user_id(token_hash)
    if not db.password_reset_token_is_valid(token_hash, datetime.now(timezone.utc)):
        db.record_password_audit("reset_rejected", get_client_ip(http_request), user_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace de restablecimiento no es válido, ha caducado o ya fue utilizado.")
    password_hash = AuthService.hash_password(payload.new_password)
    if not db.consume_password_reset_token(token_hash, password_hash, datetime.now(timezone.utc)):
        db.record_password_audit("reset_rejected", get_client_ip(http_request), user_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace de restablecimiento no es válido, ha caducado o ya fue utilizado.")
    db.record_password_audit("reset_completed", get_client_ip(http_request), user_id)
    return {"message": "Contraseña restablecida correctamente."}


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    http_request: Request,
    current_user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    user = db.get_user_by_id(current_user['user_id'])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    if not AuthService.verify_password(request.current_password, user['password']):
        db.record_password_audit("password_change_rejected", get_client_ip(http_request), user['id'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña actual es incorrecta.")
    if not db.update_password(user['id'], AuthService.hash_password(request.new_password)):
        db.record_password_audit("password_change_rejected", get_client_ip(http_request), user['id'])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo actualizar la contraseña.")
    db.record_password_audit("password_changed", get_client_ip(http_request), user['id'])
    return {"message": "Contraseña cambiada correctamente."}


@router.get("/me")
def get_my_account(
    current_user: dict = Depends(get_current_user),
    db: SuppliersDB = Depends(get_db),
):
    user = db.get_user_by_id(current_user['user_id'])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    profile = db.get_profile_by_user_id(user['id'])
    if profile:
        profile = {key: value for key, value in profile.items() if key not in {'id', 'user_id'}}
    return {"id": user['id'], "email": user['email'], "role": user.get('role', 'user'), "profile": profile}

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
