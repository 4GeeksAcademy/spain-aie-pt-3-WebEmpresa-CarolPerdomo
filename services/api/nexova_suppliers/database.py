from tinydb import TinyDB, Query
from pathlib import Path
from datetime import datetime
from .models import Supplier, SupplierCreate, CategoryEnum, StatusEnum
from .auth import AuthService

DB_PATH = Path("data") / "suppliers.json"
DB_PATH.parent.mkdir(exist_ok=True)

class SuppliersDB:
    def __init__(self, db_path=DB_PATH):
        self.db = TinyDB(str(db_path))
        self.suppliers_table = self.db.table('suppliers')
        self.users_table = self.db.table('users')
        self.profiles_table = self.db.table('profiles')

    # ============ User Operations ============
    
    def _add_id_to_result(self, result_or_list):
        """Add doc_id as 'id' field to results."""
        if isinstance(result_or_list, list):
            return [
                {**item, 'id': item.doc_id} if hasattr(item, 'doc_id') else item
                for item in result_or_list
            ]
        elif result_or_list and hasattr(result_or_list, 'doc_id'):
            result_dict = dict(result_or_list)
            result_dict['id'] = result_or_list.doc_id
            return result_dict
        return result_or_list
    
    def create_user(self, email: str, password: str, role: str = "user"):
        # Check if email already exists
        User = Query()
        if self.users_table.search(User.email == email):
            return None  # Email already exists
        
        hashed_password = AuthService.hash_password(password)
        new_user = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'created_at': datetime.utcnow().isoformat()
        }
        user_id = self.users_table.insert(new_user)
        new_user['id'] = user_id
        
        # Auto-create profile for the user
        self._create_default_profile(user_id)
        
        return new_user
    
    def _create_default_profile(self, user_id: int) -> dict:
        """Create a default profile for a user."""
        new_profile = {
            'user_id': user_id,
            'name': None,
            'phone': None,
            'address': None,
            'specialization': None,
            'experience_years': None,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': None
        }
        profile_id = self.profiles_table.insert(new_profile)
        new_profile['id'] = profile_id
        return new_profile
    
    def get_user_by_email(self, email: str) -> dict:
        """Get user by email."""
        User = Query()
        result = self.users_table.search(User.email == email)
        return self._add_id_to_result(result[0]) if result else None
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID."""
        result = self.users_table.get(doc_id=user_id)
        return self._add_id_to_result(result) if result else None
    
    def get_all_users(self) -> list:
        """Get all users (without passwords for security)."""
        users = self.users_table.all()
        users_with_id = self._add_id_to_result(users)
        return [{k: v for k, v in u.items() if k != 'password'} for u in users_with_id]
    
    def update_user(self, user_id: int, **kwargs) -> dict:
        """Update user fields (excluding password)."""
        allowed_fields = {'email', 'role'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return self.get_user_by_id(user_id)
        
        self.users_table.update(updates, doc_ids=[user_id])
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user and their profile."""
        # Delete associated profiles
        Profile = Query()
        self.profiles_table.remove(Profile.user_id == user_id)
        # Delete user
        return bool(self.users_table.remove(doc_ids=[user_id]))
    
    # ============ Profile Operations ============
    
    def get_profile_by_user_id(self, user_id: int) -> dict:
        """Get profile by user ID."""
        Profile = Query()
        result = self.profiles_table.search(Profile.user_id == user_id)
        return self._add_id_to_result(result[0]) if result else None
    
    def update_profile(self, user_id: int, **kwargs) -> dict:
        """Update user's profile."""
        allowed_fields = {'name', 'phone', 'address', 'specialization', 'experience_years'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        updates['updated_at'] = datetime.utcnow().isoformat()
        
        Profile = Query()
        self.profiles_table.update(updates, (Profile.user_id == user_id))
        return self.get_profile_by_user_id(user_id)
    
    # ============ Supplier Operations (unchanged) ============

    def create_supplier(self, supplier_data: SupplierCreate) -> dict:
        new_supplier = supplier_data.model_dump()
        new_supplier['updated_at'] = datetime.now().isoformat()
        doc_id = self.suppliers_table.insert(new_supplier)
        new_supplier['id'] = doc_id
        return new_supplier

    def get_all_suppliers(self, country: str = None, category: str = None) -> list:
        results = self.suppliers_table.all()
        
        if country:
            results = [s for s in results if s.get('country') == country]
        
        if category:
            results = [s for s in results if category in s.get('categories', [])]
        
        return results

    def get_supplier_by_id(self, supplier_id: int) -> dict:
        return self.suppliers_table.get(doc_id=supplier_id)

    def update_rate(self, supplier_id: int, new_rate: float) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update({'monthly_rate': new_rate, 'updated_at': datetime.now().isoformat()}, doc_ids=[supplier_id])
        return self.get_supplier_by_id(supplier_id)

    def update_status(self, supplier_id: int, new_status: str) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update({'status': new_status}, doc_ids=[supplier_id])
        return self.get_supplier_by_id(supplier_id)

    def delete_supplier(self, supplier_id: int) -> bool:
        return bool(self.suppliers_table.remove(doc_ids=[supplier_id]))

    def close(self):
        self.db.close()
