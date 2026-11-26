import os
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-user-update-key-longer-than-32-bytes")

from fastapi import HTTPException
from pydantic import ValidationError
import pytest

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.models import UserUpdate
from nexova_suppliers.routes.users import update_user


@pytest.fixture
def database():
    db_path = Path(__file__).resolve().parents[1] / "data" / f"user-update-test-{uuid4().hex}.json"
    db = SuppliersDB(db_path)
    try:
        yield db, db_path
    finally:
        db.close()
        db_path.unlink(missing_ok=True)


def test_owner_email_update_persists_after_database_reopen(database):
    db, db_path = database
    user = db.create_user("before@example.com", "password123")

    response = update_user(
        user["id"], UserUpdate(email="after@example.com"),
        {"user_id": user["id"], "role": "user"}, db,
    )

    assert response.email == "after@example.com"
    db.close()

    reopened = SuppliersDB(db_path)
    try:
        persisted_user = reopened.get_user_by_id(user["id"])
        assert persisted_user["email"] == "after@example.com"
    finally:
        reopened.close()


def test_non_admin_cannot_change_role(database):
    db, _ = database
    user = db.create_user("member@example.com", "password123")

    with pytest.raises(HTTPException) as error:
        update_user(
            user["id"], UserUpdate(role="admin"),
            {"user_id": user["id"], "role": "user"}, db,
        )

    assert error.value.status_code == 403
    assert db.get_user_by_id(user["id"])["role"] == "user"


def test_admin_can_change_another_users_role(database):
    db, _ = database
    admin = db.create_user("admin@example.com", "password123", role="admin")
    member = db.create_user("member@example.com", "password123")

    response = update_user(
        member["id"], UserUpdate(role="admin"),
        {"user_id": admin["id"], "role": "admin"}, db,
    )

    assert response.role == "admin"
    assert db.get_user_by_id(member["id"])["role"] == "admin"


def test_profile_name_is_not_accepted_as_user_field(database):
    db, _ = database
    user = db.create_user("profile@example.com", "password123")

    with pytest.raises(ValidationError):
        UserUpdate(name="Name belongs to Profile")
    assert db.get_profile_by_user_id(user["id"])["name"] is None
