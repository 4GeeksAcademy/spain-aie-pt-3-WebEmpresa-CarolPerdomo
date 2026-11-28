import os
from tinydb import TinyDB, Query
from pathlib import Path
from datetime import datetime, timezone
from threading import RLock
from typing import Optional
from uuid import uuid4
from .models import (
    Supplier, SupplierCreate, CategoryEnum, StatusEnum,
    IncidentCreate, IncidentStatusEnum, IncidentCategoryEnum,
    IncidentOriginEnum, IncidentBranchEnum,
)

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "suppliers.json"
DB_PATH = Path(os.environ.get("NEXOVA_DB_PATH", str(DEFAULT_DB_PATH))).expanduser().resolve()
DB_PATH.parent.mkdir(exist_ok=True)

class SuppliersDB:
    def __init__(self, db_path=DB_PATH):
        self.db = TinyDB(str(db_path))
        self.suppliers_table = self.db.table('suppliers')
        self.incidents_table = self.db.table('incidents')
        self.incident_imports_table = self.db.table('incident_imports')
        self.users_table = self.db.table('users')
        self.profiles_table = self.db.table('profiles')
        self.password_reset_tokens_table = self.db.table('password_reset_tokens')
        self.password_audit_table = self.db.table('password_audit')
        self._password_lock = RLock()
        self._user_uuid_lock = RLock()

    @staticmethod
    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_utc(value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

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
        from .auth import AuthService

        # Check if email already exists
        User = Query()
        if self.users_table.search(User.email == email):
            return None  # Email already exists
        
        hashed_password = AuthService.hash_password(password)
        new_user = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'uuid': str(uuid4()),
            'created_at': self._utc_now().isoformat()
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
            'created_at': self._utc_now().isoformat(),
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

    def get_or_create_user_uuid(self, user_id: int) -> Optional[str]:
        """Return a stable UUID for a TinyDB user, migrating older records lazily."""
        with self._user_uuid_lock:
            user = self.users_table.get(doc_id=user_id)
            if not user:
                return None
            user_uuid = user.get('uuid')
            if not user_uuid:
                user_uuid = str(uuid4())
                self.users_table.update({'uuid': user_uuid}, doc_ids=[user_id])
            return user_uuid
    
    def get_all_users(self) -> list:
        """Get all users (without passwords for security)."""
        users = self.users_table.all()
        users_with_id = self._add_id_to_result(users)
        return [{k: v for k, v in u.items() if k != 'password'} for u in users_with_id]
    
    def update_user(self, user_id: int, **kwargs) -> Optional[dict]:
        """Update email or role, preserving unique email addresses."""
        allowed_fields = {'email', 'role'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return self.get_user_by_id(user_id)

        if 'email' in updates:
            existing_user = self.get_user_by_email(updates['email'])
            if existing_user and existing_user['id'] != user_id:
                return None
        
        self.users_table.update(updates, doc_ids=[user_id])
        return self.get_user_by_id(user_id)

    def create_password_reset_token(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        """Keep only a hash of the reset token and invalidate older links."""
        with self._password_lock:
            Token = Query()
            self.password_reset_tokens_table.update(
                {'used_at': self._utc_now().isoformat()},
                (Token.user_id == user_id) & (Token.used_at == None),
            )
            self.password_reset_tokens_table.insert({
                'user_id': user_id,
                'token_hash': token_hash,
                'created_at': self._utc_now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'used_at': None,
            })

    def consume_password_reset_token(self, token_hash: str, password_hash: str, now: datetime) -> bool:
        """Atomically validate a token, change the password, and consume it."""
        with self._password_lock:
            Token = Query()
            matches = self.password_reset_tokens_table.search(Token.token_hash == token_hash)
            if not matches:
                return False
            record = matches[0]
            if record.get('used_at') or self._parse_utc(record['expires_at']) <= self._parse_utc(now.isoformat()):
                return False
            user_id = record['user_id']
            if not self.get_user_by_id(user_id):
                return False
            self.users_table.update({'password': password_hash}, doc_ids=[user_id])
            self.password_reset_tokens_table.update(
                {'used_at': now.isoformat()},
                (Token.user_id == user_id) & (Token.used_at == None),
            )
            return True

    def password_reset_token_is_valid(self, token_hash: str, now: datetime) -> bool:
        with self._password_lock:
            Token = Query()
            matches = self.password_reset_tokens_table.search(Token.token_hash == token_hash)
            if not matches:
                return False
            record = matches[0]
            return not record.get('used_at') and self._parse_utc(record['expires_at']) > self._parse_utc(now.isoformat()) and bool(self.get_user_by_id(record['user_id']))

    def get_password_reset_token_user_id(self, token_hash: str) -> Optional[int]:
        Token = Query()
        record = self.password_reset_tokens_table.get(Token.token_hash == token_hash)
        return record.get('user_id') if record else None

    def record_password_audit(self, event: str, client_ip: Optional[str], user_id: Optional[int] = None) -> None:
        self.password_audit_table.insert({
            'event': event,
            'user_id': user_id,
            'timestamp': self._utc_now().isoformat(),
            'client_ip': client_ip,
        })

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Change a user's password and invalidate any outstanding reset links."""
        with self._password_lock:
            if not self.get_user_by_id(user_id):
                return False
            self.users_table.update({'password': password_hash}, doc_ids=[user_id])
            Token = Query()
            self.password_reset_tokens_table.update(
                {'used_at': self._utc_now().isoformat()},
                (Token.user_id == user_id) & (Token.used_at == None),
            )
            return True
    
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
        updates['updated_at'] = self._utc_now().isoformat()
        
        Profile = Query()
        self.profiles_table.update(updates, (Profile.user_id == user_id))
        return self.get_profile_by_user_id(user_id)
    
    # ============ Supplier Operations (unchanged) ============

    def create_supplier(self, supplier_data: SupplierCreate) -> dict:
        new_supplier = supplier_data.model_dump()
        new_supplier['updated_at'] = datetime.now(timezone.utc).isoformat()
        doc_id = self.suppliers_table.insert(new_supplier)
        new_supplier['id'] = doc_id
        return new_supplier

    def get_all_suppliers(self, country: str = None, category: str = None) -> list:
        results = self._add_id_to_result(self.suppliers_table.all())
        
        if country:
            results = [s for s in results if s.get('country') == country]
        
        if category:
            results = [s for s in results if category in s.get('categories', [])]
        
        return results

    def get_supplier_by_id(self, supplier_id: int) -> dict:
        return self._add_id_to_result(self.suppliers_table.get(doc_id=supplier_id))

    def update_rate(self, supplier_id: int, new_rate: float) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update(
            {'monthly_rate': new_rate, 'updated_at': datetime.now(timezone.utc).isoformat()},
            doc_ids=[supplier_id],
        )
        return self.get_supplier_by_id(supplier_id)

    def update_status(self, supplier_id: int, new_status: str) -> dict:
        supplier = self.get_supplier_by_id(supplier_id)
        if not supplier:
            return None
        
        self.suppliers_table.update({'status': new_status}, doc_ids=[supplier_id])
        return self.get_supplier_by_id(supplier_id)

    def delete_supplier(self, supplier_id: int) -> bool:
        return bool(self.suppliers_table.remove(doc_ids=[supplier_id]))

    # ============ Incident Operations ============

    def create_incident(self, incident_data: IncidentCreate, created_at: Optional[str] = None) -> dict:
        now = created_at or self._utc_now().isoformat()
        new_incident = incident_data.model_dump(mode="json")
        new_incident.update({"created_at": now, "updated_at": now})
        doc_id = self.incidents_table.insert(new_incident)
        return {**new_incident, "id": doc_id}

    def get_incident_by_id(self, incident_id: int) -> Optional[dict]:
        incident = self.incidents_table.get(doc_id=incident_id)
        return {**incident, "id": incident.doc_id} if incident else None

    def get_all_incidents(
        self,
        status: Optional[str] = None,
        origin: Optional[str] = None,
        branch: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list:
        incidents = [
            {**incident, "id": incident.doc_id}
            for incident in self.incidents_table.all()
        ]
        filters = {"status": status, "origin": origin, "branch": branch, "category": category}
        return [item for item in incidents if all(value is None or item.get(key) == value for key, value in filters.items())]

    def update_incident_status(self, incident_id: int, status: str) -> Optional[dict]:
        incident = self.get_incident_by_id(incident_id)
        if not incident:
            return None
        self.incidents_table.update(
            {"status": status, "updated_at": self._utc_now().isoformat()},
            doc_ids=[incident_id],
        )
        return self.get_incident_by_id(incident_id)

    def get_incident_summary(self) -> dict:
        incidents = self.incidents_table.all()
        def count_by(field: str, allowed_values) -> dict:
            return {
                value.value: sum(1 for incident in incidents if incident.get(field) == value.value)
                for value in allowed_values
            }
        return {
            "total": len(incidents),
            "by_status": count_by("status", IncidentStatusEnum),
            "by_category": count_by("category", IncidentCategoryEnum),
            "by_origin": count_by("origin", IncidentOriginEnum),
            "by_branch": count_by("branch", IncidentBranchEnum),
        }

    def has_incident_import(self, source_key: str) -> bool:
        return self.incident_imports_table.contains(Query().source_key == source_key)

    def record_incident_import(self, source_key: str, incident_id: int) -> None:
        self.incident_imports_table.insert({"source_key": source_key, "incident_id": incident_id})

    def close(self):
        self.db.close()
