"""Unit tests for authentication behavior without exercising HTTP serialization."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-auth-unit-key-with-more-than-32-characters")

import jwt
import pytest
from fastapi import BackgroundTasks, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from starlette.requests import Request

from nexova_suppliers.auth import ALGORITHM, SECRET_KEY, AuthService
from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.dependencies import get_current_user
from nexova_suppliers.models import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    UserCreate,
)
from nexova_suppliers.routes import auth


@pytest.fixture
def db():
    path = Path(__file__).resolve().parents[1] / "data" / f"auth-unit-{uuid4().hex}.json"
    database = SuppliersDB(path)
    try:
        yield database
    finally:
        database.close()
        path.unlink(missing_ok=True)


def make_request(client_ip="198.51.100.20") -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/auth/unit-test",
            "raw_path": b"/auth/unit-test",
            "query_string": b"",
            "headers": [],
            "client": (client_ip, 4321) if client_ip else None,
            "server": ("testserver", 80),
        }
    )


def issue_reset_link(monkeypatch, db, email="person@example.com"):
    sent = []
    monkeypatch.setattr(auth, "send_password_reset_email", lambda recipient, url: sent.append((recipient, url)))
    tasks = BackgroundTasks()
    result = auth.forgot_password(ForgotPasswordRequest(email=email), make_request(), tasks, db)
    for task in tasks.tasks:
        task.func(*task.args)
    return result, tasks, sent


def test_register_creates_hashed_user_profile_and_access_token(db):
    response = auth.register(UserCreate(email="new@example.com", password="safe-password"), db)

    user = db.get_user_by_email("new@example.com")
    assert response.user.id == user["id"]
    assert response.user.role == "user"
    assert user["password"] != "safe-password"
    assert AuthService.verify_password("safe-password", user["password"])
    assert db.get_profile_by_user_id(user["id"]) is not None
    assert AuthService.decode_token(response.access_token)["user_id"] == user["id"]


def test_register_accepts_password_at_minimum_length_and_rejects_empty(db):
    created = auth.register(UserCreate(email="minimum@example.com", password="12345678"), db)

    assert AuthService.verify_password("12345678", db.get_user_by_id(created.user.id)["password"])
    with pytest.raises(ValidationError):
        UserCreate(email="empty@example.com", password="")


def test_register_rejects_duplicate_email(db):
    db.create_user("duplicate@example.com", "safe-password")

    with pytest.raises(HTTPException) as error:
        auth.register(UserCreate(email="duplicate@example.com", password="another-password"), db)

    assert error.value.status_code == 400
    assert error.value.detail == "Email already registered"


def test_login_returns_access_token_for_valid_credentials(db):
    user = db.create_user("login@example.com", "safe-password")

    response = auth.login(LoginRequest(email="login@example.com", password="safe-password"), db)

    claims = AuthService.decode_token(response.access_token)
    assert claims["user_id"] == user["id"]
    assert claims["email"] == user["email"]
    assert response.user.role == "user"


@pytest.mark.parametrize(
    "credentials",
    [
        LoginRequest(email="login@example.com", password="wrong-password"),
        LoginRequest(email="missing@example.com", password="safe-password"),
    ],
)
def test_login_rejects_wrong_or_unknown_credentials(db, credentials):
    db.create_user("login@example.com", "safe-password")

    with pytest.raises(HTTPException) as error:
        auth.login(credentials, db)

    assert error.value.status_code == 401


def test_login_defaults_legacy_account_role_to_user(db):
    from nexova_suppliers.auth import AuthService

    user_id = db.users_table.insert(
        {
            "email": "legacy@example.com",
            "password": AuthService.hash_password("safe-password"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    response = auth.login(LoginRequest(email="legacy@example.com", password="safe-password"), db)

    assert response.user.id == user_id
    assert response.user.role == "user"


def test_forgot_password_schedules_email_and_persists_only_token_hash(db, monkeypatch):
    user = db.create_user("person@example.com", "safe-password")

    response, tasks, sent = issue_reset_link(monkeypatch, db)

    assert response["message"] == auth.GENERIC_RESET_MESSAGE
    assert len(tasks.tasks) == 1
    assert len(sent) == 1  # The unit test executes the queued callback after testing scheduling.
    recipient, reset_url = tasks.tasks[0].args
    assert recipient == user["email"]
    token = parse_qs(urlparse(reset_url).query)["token"][0]
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    assert db.get_password_reset_token_user_id(token_hash) == user["id"]
    assert all(record["token_hash"] != token for record in db.password_reset_tokens_table.all())


def test_forgot_password_unknown_email_returns_same_confirmation(db, monkeypatch):
    _, tasks, _ = issue_reset_link(monkeypatch, db, email="unknown@example.com")

    assert not tasks.tasks
    assert auth.forgot_password(
        ForgotPasswordRequest(email="unknown@example.com"), make_request(), BackgroundTasks(), db
    )["message"] == auth.GENERIC_RESET_MESSAGE


def test_forgot_password_reports_database_lookup_failure_without_leaking_details(db, monkeypatch, caplog):
    monkeypatch.setattr(db, "get_user_by_email", lambda _email: (_ for _ in ()).throw(RuntimeError("private detail")))

    with pytest.raises(HTTPException) as error:
        auth.forgot_password(
            ForgotPasswordRequest(email="person@example.com"), make_request(), BackgroundTasks(), db
        )

    assert error.value.status_code == 503
    assert "private detail" not in caplog.text


def test_reset_password_consumes_valid_token_and_changes_password(db, monkeypatch):
    user = db.create_user("reset@example.com", "old-password")
    _, _, sent = issue_reset_link(monkeypatch, db, "reset@example.com")
    token = parse_qs(urlparse(sent[0][1]).query)["token"][0]

    result = auth.reset_password(ResetPasswordRequest(token=token, new_password="new-password"), make_request(), db)

    assert result["message"] == "Contraseña restablecida correctamente."
    assert AuthService.verify_password("new-password", db.get_user_by_id(user["id"])["password"])
    assert not db.password_reset_token_is_valid(hashlib.sha256(token.encode()).hexdigest(), datetime.now(timezone.utc))


def test_reset_password_rejects_expired_and_reused_tokens(db, monkeypatch):
    user = db.create_user("reset@example.com", "old-password")
    expired = secrets.token_urlsafe(32)
    db.create_password_reset_token(
        user["id"], hashlib.sha256(expired.encode()).hexdigest(), datetime.now(timezone.utc) - timedelta(seconds=1)
    )
    with pytest.raises(HTTPException) as expired_error:
        auth.reset_password(ResetPasswordRequest(token=expired, new_password="new-password"), make_request(), db)
    assert expired_error.value.status_code == 400

    _, _, sent = issue_reset_link(monkeypatch, db, "reset@example.com")
    valid = parse_qs(urlparse(sent[0][1]).query)["token"][0]
    auth.reset_password(ResetPasswordRequest(token=valid, new_password="new-password"), make_request(), db)
    with pytest.raises(HTTPException) as reused_error:
        auth.reset_password(ResetPasswordRequest(token=valid, new_password="again-password"), make_request(), db)
    assert reused_error.value.status_code == 400


def test_reset_password_rejects_unknown_token(db):
    with pytest.raises(HTTPException) as error:
        auth.reset_password(
            ResetPasswordRequest(token=secrets.token_urlsafe(32), new_password="new-password"), make_request(), db
        )

    assert error.value.status_code == 400


def test_change_password_accepts_minimum_length_and_invalidates_reset_link(db):
    user = db.create_user("change@example.com", "old-password")
    token_hash = hashlib.sha256("pending-reset-token".encode()).hexdigest()
    db.create_password_reset_token(user["id"], token_hash, datetime.now(timezone.utc) + timedelta(minutes=5))
    current_user = AuthService.decode_token(AuthService.create_access_token(user["id"], user["email"]))

    result = auth.change_password(
        ChangePasswordRequest(current_password="old-password", new_password="12345678"),
        make_request(), current_user, db,
    )

    assert result["message"] == "Contraseña cambiada correctamente."
    assert AuthService.verify_password("12345678", db.get_user_by_id(user["id"])["password"])
    assert not db.password_reset_token_is_valid(token_hash, datetime.now(timezone.utc))


def test_change_password_rejects_wrong_current_password(db):
    user = db.create_user("change@example.com", "old-password")
    current_user = {"user_id": user["id"]}

    with pytest.raises(HTTPException) as error:
        auth.change_password(
            ChangePasswordRequest(current_password="wrong-password", new_password="new-password"),
            make_request(), current_user, db,
        )

    assert error.value.status_code == 400
    assert AuthService.verify_password("old-password", db.get_user_by_id(user["id"])["password"])


def test_change_password_rejects_deleted_user(db):
    with pytest.raises(HTTPException) as error:
        auth.change_password(
            ChangePasswordRequest(current_password="old-password", new_password="new-password"),
            make_request(), {"user_id": 999}, db,
        )

    assert error.value.status_code == 401


def test_get_my_account_returns_account_and_sanitized_profile(db):
    user = db.create_user("me@example.com", "safe-password")
    db.update_profile(user["id"], name="Example Person", phone="+34 600 000 000")

    result = auth.get_my_account({"user_id": user["id"], "role": "user"}, db)

    assert result["id"] == user["id"]
    assert result["profile"]["name"] == "Example Person"
    assert "id" not in result["profile"]
    assert "user_id" not in result["profile"]
    assert "password" not in result


def test_get_my_account_handles_missing_profile(db, monkeypatch):
    user = db.create_user("me@example.com", "safe-password")
    monkeypatch.setattr(db, "get_profile_by_user_id", lambda _user_id: None)

    result = auth.get_my_account({"user_id": user["id"]}, db)

    assert result["profile"] is None


def test_get_my_account_rejects_deleted_user(db):
    with pytest.raises(HTTPException) as error:
        auth.get_my_account({"user_id": 999}, db)

    assert error.value.status_code == 404


def test_access_token_decoder_accepts_valid_and_rejects_expired_or_invalid_tokens():
    valid = AuthService.create_access_token(7, "token@example.com")
    expired = jwt.encode(
        {"user_id": 7, "email": "token@example.com", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    assert AuthService.decode_token(valid)["user_id"] == 7
    assert AuthService.decode_token(expired) is None
    assert AuthService.decode_token("not-a-token") is None


def test_current_user_dependency_rejects_reset_tokens_and_expired_access_tokens():
    expired = jwt.encode(
        {"user_id": 7, "email": "token@example.com", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    reset_token, _, _ = AuthService.create_password_reset_token(7, "token@example.com")

    for token in (expired, reset_token, "invalid"):
        with pytest.raises(HTTPException) as error:
            import asyncio

            asyncio.run(get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)))
        assert error.value.status_code == 401


def test_current_user_dependency_accepts_valid_access_token():
    import asyncio

    token = AuthService.create_access_token(12, "valid@example.com", "manager")

    payload = asyncio.run(get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)))

    assert payload["user_id"] == 12
    assert payload["role"] == "manager"
