import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from tinydb import TinyDB, Query
from tinydb.operations import delete
from services.core.config import settings
from services.core.security import hash_password, verify_password
from services.core.models import UserRole


class Database:
    """TinyDB wrapper for user and profile management"""
    
    def __init__(self):
        self.db = TinyDB(settings.DATABASE_URL)
        self.users_table = self.db.table("users")
        self.profiles_table = self.db.table("profiles")
    
    # ============ USER OPERATIONS ============
    
    def create_user(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.USER
    ) -> Dict[str, Any]:
        """Create a new user with hashed password"""
        user_id = str(uuid.uuid4())
        hashed_pwd = hash_password(password)
        
        user_doc = {
            "id": user_id,
            "email": email,
            "hashed_password": hashed_pwd,
            "is_active": True,
            "role": role.value,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.users_table.insert(user_doc)
        return user_doc
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        User = Query()
        result = self.users_table.get(User.id == user_id)
        return result
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by email"""
        User = Query()
        result = self.users_table.get(User.email == email)
        return result
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        return self.users_table.all()
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user fields"""
        User = Query()
        
        # Only allow updating specific fields
        allowed_fields = {"email", "role", "is_active"}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        result = self.users_table.update(update_data, User.id == user_id)
        return len(result) > 0
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user and their associated profile"""
        User = Query()
        
        # Delete the profile first
        self._delete_profile_by_user_id(user_id)
        
        # Delete the user
        result = self.users_table.remove(User.id == user_id)
        return len(result) > 0
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user by email and password"""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.get("is_active"):
            return None
        
        if not verify_password(password, user.get("hashed_password", "")):
            return None
        
        return user
    
    # ============ PROFILE OPERATIONS ============
    
    def create_profile(
        self,
        user_id: str,
        name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a profile for a user"""
        profile_id = str(uuid.uuid4())
        
        profile_doc = {
            "id": profile_id,
            "user_id": user_id,
            "name": name,
            "phone": phone,
            "address": address
        }
        
        self.profiles_table.insert(profile_doc)
        return profile_doc
    
    def get_profile_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a profile by user ID"""
        Profile = Query()
        result = self.profiles_table.get(Profile.user_id == user_id)
        return result
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a profile by ID"""
        Profile = Query()
        result = self.profiles_table.get(Profile.id == profile_id)
        return result
    
    def update_profile(self, profile_id: str, **kwargs) -> bool:
        """Update profile fields"""
        Profile = Query()
        
        # Only allow updating specific fields
        allowed_fields = {"name", "phone", "address"}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        result = self.profiles_table.update(update_data, Profile.id == profile_id)
        return len(result) > 0
    
    def _delete_profile_by_user_id(self, user_id: str) -> bool:
        """Delete a profile by user ID"""
        Profile = Query()
        result = self.profiles_table.remove(Profile.user_id == user_id)
        return len(result) > 0
    
    def close(self):
        """Close the database connection"""
        self.db.close()


# Global database instance
db_instance = Database()


def get_database() -> Database:
    """Get the database instance"""
    return db_instance
