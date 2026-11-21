"""
Dependency functions for FastAPI route protection and user context.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .auth import AuthService
from .database import SuppliersDB

security = HTTPBearer()
db_instance = None

def set_db(db: SuppliersDB):
    """Set the global database instance."""
    global db_instance
    db_instance = db

def get_db() -> SuppliersDB:
    """Get the database instance."""
    if db_instance is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not initialized"
        )
    return db_instance

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extract and validate the current user from JWT token.
    Returns the decoded token payload with user_id and email.
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def verify_owns_resource(user_payload: dict = Depends(get_current_user), resource_user_id: int = None):
    """
    Verify that the current user owns the resource.
    Pass resource_user_id as a path parameter.
    """
    if user_payload.get("user_id") != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return user_payload
