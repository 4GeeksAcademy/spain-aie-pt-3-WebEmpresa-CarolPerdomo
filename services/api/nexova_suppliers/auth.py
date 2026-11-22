"""
Authentication service for Nexova API.

Manages JWT token generation, password hashing, and user authentication.
"""
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from .config import get_setting

# SECRET_KEY es obligatorio desde el entorno
SECRET_KEY = get_setting("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "ERROR: SECRET_KEY must be set in environment variables. "
        "Export it before running the API: export SECRET_KEY='your-secret-key'"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_setting("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(get_setting("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", "30"))
if not 15 <= PASSWORD_RESET_TOKEN_EXPIRE_MINUTES <= 60:
    raise ValueError("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES must be between 15 and 60")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    @staticmethod
    def create_access_token(user_id: int, email: str, role: str = "user") -> str:
        """Create a JWT access token."""
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "token_type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_password_reset_token(user_id: int, email: str) -> tuple[str, str, int]:
        """Return a signed reset token, its one-time identifier, and expiry timestamp."""
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        token_id = secrets.token_urlsafe(24)
        payload = {
            "user_id": user_id,
            "email": email,
            "token_type": "password_reset",
            "jti": token_id,
            "iat": issued_at,
            "exp": expires_at,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM), token_id, int(expires_at.timestamp())

    @staticmethod
    def decode_password_reset_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.InvalidTokenError:
            return None
        if payload.get("token_type") != "password_reset" or not payload.get("jti"):
            return None
        return payload
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
