import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
from uuid import uuid4

os.environ.setdefault("SECRET_KEY", "test-only-auth-http-key-longer-than-32-bytes")

from fastapi import FastAPI
import pytest

from nexova_suppliers.auth import AuthService
from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.dependencies import get_db
from nexova_suppliers.models import RoleEnum, Supplier, SupplierCreate
from nexova_suppliers.routes import auth, profiles, suppliers, users
from nexova_suppliers.auth import ALGORITHM, SECRET_KEY


def build_app(db: SuppliersDB) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_db] = lambda: db
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(profiles.router)
    app.include_router(suppliers.router)
    return app


async def asgi_request(app, method, path, token=None, body=None):
    parsed_url = urlsplit(path)
    path = parsed_url.path
    request_body = json.dumps(body).encode("utf-8") if body is not None else b""
    headers = [(b"host", b"testserver")]
    if body is not None:
        headers.extend([
            (b"content-type", b"application/json"),
            (b"content-length", str(len(request_body)).encode("ascii")),
        ])
    if token:
        headers.append((b"authorization", f"Bearer {token}".encode("ascii")))

    sent_request = False
    response_status = None
    response_body = bytearray()

    async def receive():
        nonlocal sent_request
        if not sent_request:
            sent_request = True
            return {"type": "http.request", "body": request_body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message):
        nonlocal response_status
        if message["type"] == "http.response.start":
            response_status = message["status"]
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    raw_path = path.encode("ascii")
    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": raw_path,
            "query_string": parsed_url.query.encode("ascii"),
            "root_path": "",
            "headers": headers,
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 80),
        },
        receive,
        send,
    )
    parsed_body = json.loads(response_body) if response_body else None
    return response_status, parsed_body


def request(app, method, path, token=None, body=None):
    return asyncio.run(asgi_request(app, method, path, token=token, body=body))


@pytest.fixture
def api():
    db_path = Path(__file__).resolve().parents[1] / "data" / f"api-test-{uuid4().hex}.json"
    db = SuppliersDB(db_path)
    try:
        yield build_app(db), db
    finally:
        db.close()
        db_path.unlink(missing_ok=True)


def test_roles_include_admin_manager_and_user():
    assert {role.value for role in RoleEnum} == {"admin", "manager", "user"}


def test_supplier_contract_validation_filters_and_system_timestamps(api):
    assert set(SupplierCreate.model_fields) == {
        "name", "country", "categories", "monthly_rate", "currency", "status",
        "contract_renewal_date", "contact_email", "notes",
    }
    assert set(Supplier.model_fields) == set(SupplierCreate.model_fields) | {"id", "updated_at"}
    app, db = api
    user = db.create_user("supplier-contract@example.com", "secure-password")
    token = AuthService.create_access_token(user["id"], user["email"])
    valid = {
        "name": "Example Spain Supplier", "country": "Spain", "categories": ["job_boards"],
        "monthly_rate": 100, "currency": "EUR", "status": "active",
    }

    assert request(app, "POST", "/suppliers", token=token, body={**valid, "status": "pending"})[0] == 422
    assert request(app, "POST", "/suppliers", token=token, body={**valid, "monthly_rate": "not-a-number"})[0] == 422
    assert request(app, "POST", "/suppliers", token=token, body={**valid, "currency": "USD"})[0] == 422
    assert request(app, "POST", "/suppliers", token=token, body={**valid, "categories": []})[0] == 422
    assert request(app, "POST", "/suppliers", token=token, body={**valid, "updated_at": "2000-01-01T00:00:00"})[0] == 422

    status_code, created = request(app, "POST", "/suppliers", token=token, body=valid)
    assert status_code == 201
    assert created["id"] > 0
    created_timestamp = created["updated_at"]
    assert created_timestamp and created_timestamp != "2000-01-01T00:00:00"

    status_code, other_supplier = request(app, "POST", "/suppliers", token=token, body={
        **valid, "name": "Example USA Supplier", "country": "USA",
        "categories": ["ats_software"], "monthly_rate": 200, "currency": "USD",
    })
    assert status_code == 201
    assert [item["name"] for item in request(app, "GET", "/suppliers?country=Spain", token=token)[1]] == [created["name"]]
    assert [item["name"] for item in request(app, "GET", "/suppliers?category=job_boards", token=token)[1]] == [created["name"]]
    assert [item["name"] for item in request(app, "GET", "/suppliers?country=Spain&category=job_boards", token=token)[1]] == [created["name"]]
    assert request(app, "GET", "/suppliers?country=Canada", token=token)[0] == 422
    assert request(app, "GET", "/suppliers?category=invalid", token=token)[0] == 422

    assert request(app, "PATCH", f"/suppliers/{created['id']}/rate", token=token, body={"monthly_rate": -1})[0] == 422
    status_code, rated = request(app, "PATCH", f"/suppliers/{created['id']}/rate", token=token, body={"monthly_rate": 150})
    assert status_code == 200 and rated["monthly_rate"] == 150
    assert rated["updated_at"] != created_timestamp
    assert request(app, "PATCH", f"/suppliers/{created['id']}/status", token=token, body={"status": "paused"})[0] == 422
    status_code, suspended = request(app, "PATCH", f"/suppliers/{created['id']}/status", token=token, body={"status": "suspended"})
    assert status_code == 200 and suspended["status"] == "suspended"
    assert suspended["updated_at"] == rated["updated_at"]
    assert request(app, "GET", "/suppliers/99999", token=token)[0] == 404
    assert request(app, "DELETE", "/suppliers/99999", token=token)[0] == 404


def test_password_reset_and_change_password_are_secure_and_persistent(api, monkeypatch):
    app, db = api
    user = db.create_user("reset@example.com", "old-password")
    sent = []
    monkeypatch.setattr(auth, "send_password_reset_email", lambda address, url: sent.append((address, url)))

    missing_status, missing_body = request(app, "POST", "/auth/forgot-password", body={"email": "unknown@example.com"})
    existing_status, existing_body = request(app, "POST", "/auth/forgot-password", body={"email": "reset@example.com"})
    assert missing_status == existing_status == 200
    assert missing_body == existing_body
    assert len(sent) == 1 and sent[0][0] == "reset@example.com"

    from urllib.parse import parse_qs, urlparse
    reset_token = parse_qs(urlparse(sent[0][1]).query)["token"][0]
    assert AuthService.decode_password_reset_token(reset_token)["user_id"] == user["id"]
    assert request(app, "POST", "/auth/reset-password", body={"token": "invalid", "new_password": "new-password"})[0] == 400

    expired_token = AuthService.create_password_reset_token(user["id"], user["email"])[0]
    expired_claims = AuthService.decode_password_reset_token(expired_token)
    expired_claims["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    import jwt
    expired_token = jwt.encode(expired_claims, SECRET_KEY, algorithm=ALGORITHM)
    assert request(app, "POST", "/auth/reset-password", body={"token": expired_token, "new_password": "new-password"})[0] == 400

    session_token = AuthService.create_access_token(user["id"], user["email"])
    assert request(app, "POST", "/auth/change-password", body={"current_password": "old-password", "new_password": "new-password"})[0] == 401
    assert request(app, "POST", "/auth/change-password", token=session_token, body={"current_password": "wrong", "new_password": "new-password"})[0] == 400
    assert request(app, "POST", "/auth/change-password", token=session_token, body={"current_password": "old-password", "new_password": "changed-password"})[0] == 200
    assert AuthService.verify_password("changed-password", db.get_user_by_id(user["id"])["password"])
    assert request(app, "POST", "/auth/reset-password", body={"token": reset_token, "new_password": "reset-password"})[0] == 400

    request(app, "POST", "/auth/forgot-password", body={"email": "reset@example.com"})
    reset_token = parse_qs(urlparse(sent[-1][1]).query)["token"][0]
    assert request(app, "POST", "/auth/reset-password", body={"token": reset_token, "new_password": "reset-password"})[0] == 200
    assert request(app, "POST", "/auth/reset-password", body={"token": reset_token, "new_password": "second-use-password"})[0] == 400
    assert AuthService.verify_password("reset-password", db.get_user_by_id(user["id"])["password"])


def test_auth_and_protected_routes_work_with_bearer_tokens(api):
    app, db = api
    owner = db.create_user("owner@example.com", "secure-password")
    other = db.create_user("other@example.com", "other-password")
    owner_record = db.get_user_by_id(owner["id"])
    assert owner_record["password"] != "secure-password"
    assert AuthService.verify_password("secure-password", owner_record["password"])

    protected_requests = [
        ("POST", "/users/", {"email": "new@example.com", "password": "password123"}),
        ("GET", "/users/", None),
        ("GET", "/users/me", None),
        ("GET", f"/users/{owner['id']}", None),
        ("PUT", f"/users/{owner['id']}", {"email": "changed@example.com"}),
        ("DELETE", f"/users/{owner['id']}", None),
        ("GET", "/profiles/me", None),
        ("GET", f"/profiles/{owner['id']}", None),
        ("PUT", "/profiles/me", {"name": "Profile Name"}),
        ("PUT", f"/profiles/{owner['id']}", {"phone": "555-0100"}),
        ("POST", "/suppliers", {
            "name": "Example Supplier", "country": "Spain", "categories": ["job_boards"],
            "monthly_rate": 1, "currency": "EUR", "status": "active",
        }),
        ("GET", "/suppliers", None),
        ("GET", "/suppliers/1", None),
        ("PATCH", "/suppliers/1/rate", {"monthly_rate": 2}),
        ("PATCH", "/suppliers/1/status", {"status": "suspended"}),
        ("DELETE", "/suppliers/1", None),
    ]
    for method, path, body in protected_requests:
        status_code, _ = request(app, method, path, body=body)
        assert status_code == 401, f"{method} {path} without token returned {status_code}"

    status_code, login = request(
        app, "POST", "/auth/login",
        body={"email": "owner@example.com", "password": "secure-password"},
    )
    assert status_code == 200
    owner_token = login["access_token"]
    assert AuthService.decode_token(owner_token)["user_id"] == owner["id"]
    assert request(
        app, "POST", "/auth/login",
        body={"email": "owner@example.com", "password": "wrong-password"},
    )[0] == 401

    status_code, current_user = request(app, "GET", "/users/me", token=owner_token)
    assert status_code == 200
    assert current_user["id"] == owner["id"]
    assert "password" not in current_user
    assert request(app, "GET", f"/users/{owner['id']}", token=owner_token)[0] == 200

    status_code, updated_profile = request(
        app, "PUT", "/profiles/me", token=owner_token,
        body={"name": "Example Profile", "phone": "555-0100", "address": "Example Address"},
    )
    assert status_code == 200
    assert updated_profile["name"] == "Example Profile"
    assert updated_profile["phone"] == "555-0100"
    assert updated_profile["address"] == "Example Address"
    owner_record = db.get_user_by_id(owner["id"])
    assert all(field not in owner_record for field in ("name", "phone", "address"))

    supplier_body = {
        "name": "Example Supplier", "country": "Spain", "categories": ["job_boards"],
        "monthly_rate": 1, "currency": "EUR", "status": "active",
    }
    status_code, created_supplier = request(
        app, "POST", "/suppliers", token=owner_token, body=supplier_body,
    )
    assert status_code == 201
    supplier_id = created_supplier["id"]
    assert request(app, "GET", "/suppliers", token=owner_token)[0] == 200
    assert request(app, "GET", f"/suppliers/{supplier_id}", token=owner_token)[0] == 200
    status_code, updated_rate = request(
        app, "PATCH", f"/suppliers/{supplier_id}/rate", token=owner_token,
        body={"monthly_rate": 2},
    )
    assert status_code == 200
    assert updated_rate["monthly_rate"] == 2
    status_code, updated_status = request(
        app, "PATCH", f"/suppliers/{supplier_id}/status", token=owner_token,
        body={"status": "suspended"},
    )
    assert status_code == 200
    assert updated_status["status"] == "suspended"
    assert request(app, "DELETE", f"/suppliers/{supplier_id}", token=owner_token)[0] == 204
    assert request(app, "GET", f"/profiles/{other['id']}", token=owner_token)[0] == 403
    assert request(app, "PUT", f"/profiles/{other['id']}", token=owner_token, body={"name": "Other"})[0] == 403
    assert request(app, "GET", f"/users/{other['id']}", token=owner_token)[0] == 403
    assert request(app, "PUT", f"/users/{other['id']}", token=owner_token, body={"email": "new-other@example.com"})[0] == 403
    assert request(app, "PUT", f"/users/{owner['id']}", token=owner_token, body={"role": "manager"})[0] == 403
    assert request(app, "GET", "/users/", token=owner_token)[0] == 403

    status_code, registered_user = request(
        app, "POST", "/auth/register",
        body={"email": "registered@example.com", "password": "password123"},
    )
    assert status_code == 200
    assert registered_user["user"]["role"] == "user"
    assert AuthService.decode_token(registered_user["access_token"])["user_id"] == registered_user["user"]["id"]
    assert db.get_profile_by_user_id(registered_user["user"]["id"])["user_id"] == registered_user["user"]["id"]

    admin = db.create_user("admin@example.com", "admin-password", role="admin")
    admin_token = AuthService.create_access_token(admin["id"], admin["email"], admin["role"])
    status_code, listed_users = request(app, "GET", "/users/", token=admin_token)
    assert status_code == 200
    assert len(listed_users) == 4
    assert all("password" not in user for user in listed_users)

    status_code, created_user = request(
        app, "POST", "/users/", token=admin_token,
        body={"email": "created@example.com", "password": "password123"},
    )
    assert status_code == 201
    assert created_user["role"] == "user"
    assert db.get_profile_by_user_id(created_user["id"])["user_id"] == created_user["id"]

    status_code, manager_user = request(
        app, "POST", "/users/", token=admin_token,
        body={"email": "manager@example.com", "password": "password123", "role": "manager"},
    )
    assert status_code == 201
    assert manager_user["role"] == "manager"

    status_code, promoted_user = request(
        app, "PUT", f"/users/{created_user['id']}", token=admin_token,
        body={"role": "manager"},
    )
    assert status_code == 200
    assert promoted_user["role"] == "manager"

    status_code, created_login = request(
        app, "POST", "/auth/login",
        body={"email": "created@example.com", "password": "password123"},
    )
    assert status_code == 200
    created_token = created_login["access_token"]
    assert request(app, "GET", f"/users/{created_user['id']}", token=created_token)[0] == 200
    assert request(app, "DELETE", f"/users/{created_user['id']}", token=created_token)[0] == 204
    assert db.get_user_by_id(created_user["id"]) is None
    assert db.get_profile_by_user_id(created_user["id"]) is None

    assert request(
        app, "POST", "/auth/register",
        body={"email": "registration@example.com", "password": "password123", "role": "admin"},
    )[0] == 422
