import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration
os.environ.setdefault("SECRET_KEY", "test-only-incident-key-longer-than-32-bytes")

from fastapi import FastAPI

from nexova_suppliers.database import SuppliersDB
from nexova_suppliers.dependencies import get_current_user, get_db
from nexova_suppliers.routes.incidents import router


async def asgi_request(app, method, path, body=None):
    parsed_path = urlsplit(path)
    path = parsed_path.path
    request_body = json.dumps(body).encode("utf-8") if body is not None else b""
    headers = [(b"host", b"testserver")]
    if body is not None:
        headers.extend([
            (b"content-type", b"application/json"),
            (b"content-length", str(len(request_body)).encode("ascii")),
        ])
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

    await app(
        {
            "type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1", "method": method, "scheme": "http",
            "path": path, "raw_path": path.encode("ascii"), "query_string": parsed_path.query.encode("ascii"),
            "root_path": "", "headers": headers, "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 80),
        },
        receive,
        send,
    )
    return response_status, json.loads(response_body) if response_body else None


def request(app, method, path, body=None):
    return asyncio.run(asgi_request(app, method, path, body))


@pytest.fixture
def client():
    db_path = Path(__file__).resolve().parents[1] / "data" / f"incidents-test-{uuid4().hex}.json"
    db = SuppliersDB(db_path)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: {"user_id": 1, "email": "operator@example.test"}
    try:
        yield app, db
    finally:
        app.dependency_overrides.clear()
        db.close()
        db_path.unlink(missing_ok=True)


def valid_incident(**updates):
    return {
        "title": "Incidencia de prueba",
        "description": "Descripción detallada para la incidencia.",
        "category": "technical_failure",
        "status": "open",
        "origin": "branch",
        "branch": "valencia_operations",
        **updates,
    }


def test_incident_lifecycle_filters_detail_and_summary(client):
    app, _db = client
    status, incident = request(app, "POST", "/api/incidents", valid_incident())
    assert status == 201
    assert incident["id"] > 0
    assert datetime.fromisoformat(incident["created_at"]).utcoffset().total_seconds() == 0
    assert incident["created_at"] == incident["updated_at"]

    status, filtered = request(app, "GET", "/api/incidents?origin=branch&branch=valencia_operations")
    assert status == 200
    assert [item["id"] for item in filtered] == [incident["id"]]
    assert request(app, "GET", f"/api/incidents/{incident['id']}")[1]["title"] == "Incidencia de prueba"
    assert request(app, "GET", "/api/incidents/9999")[0] == 404

    status, invalid_transition = request(app, "PATCH", f"/api/incidents/{incident['id']}/status", {"status": "resolved"})
    assert status == 400
    assert invalid_transition["detail"]["errors"][0]["field"] == "status"

    status, moved = request(app, "PATCH", f"/api/incidents/{incident['id']}/status", {"status": "in_progress"})
    assert status == 200
    status, resolved = request(app, "PATCH", f"/api/incidents/{incident['id']}/status", {"status": "resolved"})
    assert status == 200
    assert resolved["status"] == "resolved"
    assert request(app, "PATCH", f"/api/incidents/{incident['id']}/status", {"status": "discarded"})[0] == 400

    status, summary = request(app, "GET", "/api/incidents/summary")
    assert status == 200
    assert summary["total"] == 1
    assert summary["by_status"]["resolved"] == 1
    assert summary["by_category"]["technical_failure"] == 1
    assert summary["by_origin"]["branch"] == 1
    assert summary["by_branch"]["valencia_operations"] == 1


def test_create_returns_field_level_errors_and_empty_summary(client):
    app, _db = client
    status, invalid = request(app, "POST", "/api/incidents", valid_incident(title=" ", category="unknown"))
    assert status == 400
    errors = invalid["detail"]["errors"]
    assert {error["field"] for error in errors} == {"title", "category"}

    status, empty = request(app, "GET", "/api/incidents/summary")
    assert status == 200
    assert empty["total"] == 0
    assert all(value == 0 for counts in empty.values() if isinstance(counts, dict) for value in counts.values())


def test_invalid_filters_identify_the_filter_field(client):
    app, _db = client
    status, response = request(app, "GET", "/api/incidents?branch=not-a-branch")
    assert status == 400
    assert response["detail"]["errors"][0]["field"] == "branch"
