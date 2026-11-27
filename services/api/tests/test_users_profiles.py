"""Unit tests for user and profile route logic; no HTTP/ASGI client is used."""

import os
from pathlib import Path
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-resource-unit-key-with-more-than-32-chars")

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.models import AdminUserCreate, ProfileCreate, RoleEnum, UserUpdate
from nexova_suppliers.routes import profiles, users


@pytest.fixture
def db():
    path = Path(__file__).resolve().parents[1] / "data" / f"resource-unit-{uuid4().hex}.json"
    database = SuppliersDB(path)
    try:
        yield database
    finally:
        database.close()
        path.unlink(missing_ok=True)


@pytest.fixture
def admin(db):
    user = db.create_user("admin@example.com", "secure-password", role="admin")
    return {"user_id": user["id"], "role": "admin"}


def test_create_user_admin_success_duplicate_and_non_admin_failure(db, admin):
    created = users.create_user(
        AdminUserCreate(email="created@example.com", password="secure-password", role=RoleEnum.MANAGER),
        db,
        admin,
    )
    assert created.email == "created@example.com"
    assert created.role == "manager"
    assert "password" not in created.model_dump()

    with pytest.raises(HTTPException) as duplicate:
        users.create_user(AdminUserCreate(email="created@example.com", password="secure-password"), db, admin)
    assert duplicate.value.status_code == 400

    with pytest.raises(HTTPException) as forbidden:
        users.create_user(
            AdminUserCreate(email="forbidden@example.com", password="secure-password"),
            db,
            {"user_id": created.id, "role": "user"},
        )
    assert forbidden.value.status_code == 403


def test_list_users_admin_success_and_non_admin_failure(db, admin):
    assert len(users.list_users(db, admin)) == 1
    user = db.create_user("member@example.com", "secure-password")

    result = users.list_users(db, admin)

    assert len(result) == 2
    assert all("password" not in record for record in result)
    assert any(record["id"] == user["id"] for record in result)
    with pytest.raises(HTTPException) as forbidden:
        users.list_users(db, {"user_id": user["id"], "role": "user"})
    assert forbidden.value.status_code == 403


def test_get_current_user_info_success_and_missing_account(db):
    user = db.create_user("current@example.com", "secure-password")
    result = users.get_current_user_info({"user_id": user["id"]}, db)
    assert result.email == user["email"]
    assert result.role == "user"

    with pytest.raises(HTTPException) as missing:
        users.get_current_user_info({"user_id": 9999}, db)
    assert missing.value.status_code == 404


def test_get_user_own_resource_cross_user_and_missing_cases(db):
    owner = db.create_user("owner@example.com", "secure-password")
    other = db.create_user("other@example.com", "secure-password")
    assert users.get_user(owner["id"], {"user_id": owner["id"]}, db).email == owner["email"]

    with pytest.raises(HTTPException) as forbidden:
        users.get_user(other["id"], {"user_id": owner["id"]}, db)
    assert forbidden.value.status_code == 403
    with pytest.raises(HTTPException) as missing:
        users.get_user(9999, {"user_id": 9999}, db)
    assert missing.value.status_code == 404


def test_update_user_owner_admin_boundary_conflict_and_failure(db, admin):
    owner = db.create_user("owner@example.com", "secure-password")
    other = db.create_user("other@example.com", "secure-password")
    owner_payload = {"user_id": owner["id"], "role": "user"}

    changed = users.update_user(owner["id"], UserUpdate(email="owner-new@example.com"), owner_payload, db)
    assert changed.email == "owner-new@example.com"

    promoted = users.update_user(owner["id"], UserUpdate(role=RoleEnum.MANAGER), admin, db)
    assert promoted.role == "manager"

    cases = [
        (other["id"], UserUpdate(email="no-access@example.com"), owner_payload, 403),
        (owner["id"], UserUpdate(role=RoleEnum.ADMIN), owner_payload, 403),
        (owner["id"], UserUpdate(), owner_payload, 422),
        (owner["id"], UserUpdate(email=other["email"]), admin, 409),
        (9999, UserUpdate(email="missing@example.com"), {"user_id": 9999, "role": "user"}, 404),
    ]
    for user_id, update, actor, status_code in cases:
        with pytest.raises(HTTPException) as error:
            users.update_user(user_id, update, actor, db)
        assert error.value.status_code == status_code

    with pytest.raises(ValidationError):
        UserUpdate(extra_field="not-allowed")


def test_delete_user_owner_success_and_access_failures(db):
    user = db.create_user("delete@example.com", "secure-password")
    other = db.create_user("other@example.com", "secure-password")
    payload = {"user_id": user["id"]}

    assert users.delete_user(user["id"], payload, db) is None
    assert db.get_user_by_id(user["id"]) is None
    assert db.get_profile_by_user_id(user["id"]) is None

    with pytest.raises(HTTPException) as forbidden:
        users.delete_user(other["id"], payload, db)
    assert forbidden.value.status_code == 403
    with pytest.raises(HTTPException) as missing:
        users.delete_user(user["id"], payload, db)
    assert missing.value.status_code == 404


def test_get_own_profile_success_and_missing_case(db, monkeypatch):
    user = db.create_user("profile@example.com", "secure-password")
    assert profiles.get_own_profile({"user_id": user["id"]}, db).name is None

    monkeypatch.setattr(db, "get_profile_by_user_id", lambda _user_id: None)
    with pytest.raises(HTTPException) as missing:
        profiles.get_own_profile({"user_id": user["id"]}, db)
    assert missing.value.status_code == 404


def test_get_user_profile_owner_cross_user_and_missing_cases(db, monkeypatch):
    owner = db.create_user("owner-profile@example.com", "secure-password")
    other = db.create_user("other-profile@example.com", "secure-password")
    assert profiles.get_user_profile(owner["id"], {"user_id": owner["id"]}, db).user_id == owner["id"]

    with pytest.raises(HTTPException) as forbidden:
        profiles.get_user_profile(other["id"], {"user_id": owner["id"]}, db)
    assert forbidden.value.status_code == 403
    monkeypatch.setattr(db, "get_profile_by_user_id", lambda _user_id: None)
    with pytest.raises(HTTPException) as missing:
        profiles.get_user_profile(owner["id"], {"user_id": owner["id"]}, db)
    assert missing.value.status_code == 404


def test_update_own_profile_success_boundary_and_missing_case(db, monkeypatch):
    user = db.create_user("update-profile@example.com", "secure-password")
    result = profiles.update_own_profile(
        ProfileCreate(name="Example Person", experience_years=0), {"user_id": user["id"]}, db
    )
    assert result.name == "Example Person"
    assert result.experience_years == 0
    with pytest.raises(ValidationError):
        ProfileCreate(experience_years=-1)

    monkeypatch.setattr(db, "get_profile_by_user_id", lambda _user_id: None)
    with pytest.raises(HTTPException) as missing:
        profiles.update_own_profile(ProfileCreate(name="Changed"), {"user_id": user["id"]}, db)
    assert missing.value.status_code == 404


def test_update_user_profile_owner_cross_user_and_missing_cases(db, monkeypatch):
    owner = db.create_user("owner-update@example.com", "secure-password")
    other = db.create_user("other-update@example.com", "secure-password")
    result = profiles.update_user_profile(
        owner["id"], ProfileCreate(phone="+34 600 000 000"), {"user_id": owner["id"]}, db
    )
    assert result.phone == "+34 600 000 000"

    with pytest.raises(HTTPException) as forbidden:
        profiles.update_user_profile(other["id"], ProfileCreate(name="No access"), {"user_id": owner["id"]}, db)
    assert forbidden.value.status_code == 403
    monkeypatch.setattr(db, "get_profile_by_user_id", lambda _user_id: None)
    with pytest.raises(HTTPException) as missing:
        profiles.update_user_profile(owner["id"], ProfileCreate(name="Missing"), {"user_id": owner["id"]}, db)
    assert missing.value.status_code == 404
