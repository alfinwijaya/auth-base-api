"""
Tests for the /audit-logs/* endpoints.

Covers: create logs, query logs by user/module/date range, and verifies that mutating requests to audit-logs are restricted.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient


AUDIT_LOGS_URL = "/audit-logs/"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_log_unauthenticated(client: TestClient):
    """POST /audit-logs/ without token returns HTTP 401 or 403."""
    response = client.post(
        AUDIT_LOGS_URL,
        json={"user_id": 1, "module": "test", "activity": "something"}
    )
    assert response.status_code in (401, 403)


def test_create_log_non_admin(client: TestClient, user_token: str):
    """POST /audit-logs/ as regular user returns HTTP 403."""
    response = client.post(
        AUDIT_LOGS_URL,
        json={"user_id": 1, "module": "test", "activity": "something"},
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 403


def test_create_log_admin(client: TestClient, admin_token: str, admin_user):
    """POST /audit-logs/ as admin returns HTTP 201."""
    payload = {
        "user_id": admin_user.id,
        "module": "security",
        "activity": "admin logged in",
        "ip_address": "127.0.0.1",
        "user_agent": "Mozilla/5.0"
    }
    response = client.post(
        AUDIT_LOGS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["module"] == "security"
    assert "id" in data


def test_get_log_by_id(client: TestClient, admin_token: str, user_token: str, admin_user):
    """GET /audit-logs/{log_id} returns HTTP 200 for authenticated user."""
    payload = {
        "user_id": admin_user.id,
        "module": "users",
        "activity": "created a user",
        "ip_address": "127.0.0.1"
    }
    create_resp = client.post(
        AUDIT_LOGS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert create_resp.status_code == 201
    log_id = create_resp.json()["id"]

    get_resp = client.get(
        f"{AUDIT_LOGS_URL}{log_id}",
        headers=_auth_headers(user_token)
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["activity"] == "created a user"


def test_get_log_not_found(client: TestClient, user_token: str):
    """GET /audit-logs/{log_id} with invalid id returns HTTP 404."""
    response = client.get(
        f"{AUDIT_LOGS_URL}99999",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 404


def test_get_logs_by_user(client: TestClient, admin_token: str, user_token: str, admin_user):
    """GET /audit-logs/user/{user_id} lists logs for that user."""
    payload = {
        "user_id": admin_user.id,
        "module": "audit_logs_test",
        "activity": "user filter activity"
    }
    client.post(
        AUDIT_LOGS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        f"{AUDIT_LOGS_URL}user/{admin_user.id}",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["user_id"] == admin_user.id


def test_get_logs_by_module(client: TestClient, admin_token: str, user_token: str, admin_user):
    """GET /audit-logs/module/{module} lists logs filtered by module."""
    payload = {
        "user_id": admin_user.id,
        "module": "unique_module_name",
        "activity": "module filter activity"
    }
    client.post(
        AUDIT_LOGS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        f"{AUDIT_LOGS_URL}module/unique_module_name",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["module"] == "unique_module_name"


def test_get_logs_by_date_range(client: TestClient, admin_token: str, user_token: str, admin_user):
    """GET /audit-logs/date-range/ filters log records by start_date and end_date."""
    payload = {
        "user_id": admin_user.id,
        "module": "date_range_module",
        "activity": "date filter activity"
    }
    client.post(
        AUDIT_LOGS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )

    # Pydantic/FastAPI query param parsing expects timezone-naive ISO format or a specific format depending on settings.
    # Replacing the timezone offset +00:00 with Z or dropping timezone to prevent 422 parser issues.
    start_date = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    end_date = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")

    response = client.get(
        f"{AUDIT_LOGS_URL}date-range/?start_date={start_date}&end_date={end_date}",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["module"] == "date_range_module"


def test_mutate_endpoints_return_method_not_allowed(client: TestClient, admin_token: str):
    """Verifies that PUT, PATCH, and DELETE endpoints do not exist on /audit-logs/ (methods not allowed / 404 or 405)."""
    # Try updating or deleting /audit-logs/
    resp_put = client.put(f"{AUDIT_LOGS_URL}1", json={"activity": "hack"}, headers=_auth_headers(admin_token))
    resp_delete = client.delete(f"{AUDIT_LOGS_URL}1", headers=_auth_headers(admin_token))

    assert resp_put.status_code in (404, 405)
    assert resp_delete.status_code in (404, 405)
