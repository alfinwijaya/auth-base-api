"""
Tests for the /roles/* endpoints — RBAC guard enforcement.

Covers: unauthenticated access, non-admin access, admin access, duplicate
role creation, and authenticated GET.

Validates: Requirements 8.8, 8.9, 8.10, 8.11, 8.12
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


ROLES_URL = "/roles/"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Task 7.3 — 5 role route tests
# ---------------------------------------------------------------------------


def test_create_role_unauthenticated(client: TestClient, seed_roles):
    """
    POST /roles/ without an auth token must be rejected.
    Expects HTTP 401 or 403.  (Req 8.8)
    """
    response = client.post(ROLES_URL, json={"role_name": "noaccess"})
    assert response.status_code in (401, 403), (
        f"Expected 401 or 403 for unauthenticated request, got {response.status_code}: {response.text}"
    )


def test_create_role_as_user(client: TestClient, seed_roles, user_token: str):
    """
    POST /roles/ authenticated as a non-admin user must return HTTP 403.  (Req 8.9)
    """
    response = client.post(
        ROLES_URL,
        json={"role_name": "shouldfail"},
        headers=_auth_header(user_token),
    )
    assert response.status_code == 403, (
        f"Expected 403 for non-admin user, got {response.status_code}: {response.text}"
    )


def test_create_role_as_admin(client: TestClient, seed_roles, admin_token: str):
    """
    POST /roles/ with an admin token and a unique role name must return HTTP 201.  (Req 8.10)

    'seed_roles' already creates 'admin' and 'user', so we use a distinct name here.
    """
    response = client.post(
        ROLES_URL,
        json={"role_name": "manager"},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 201, (
        f"Expected 201 for admin creating role, got {response.status_code}: {response.text}"
    )


def test_duplicate_role_name(client: TestClient, seed_roles, admin_token: str):
    """
    POST /roles/ with the same name twice under an admin token must return HTTP 400
    on the second call.  (Req 8.11)
    """
    payload = {"role_name": "duplicate_role"}
    headers = _auth_header(admin_token)

    first = client.post(ROLES_URL, json=payload, headers=headers)
    assert first.status_code == 201, (
        f"First creation should succeed with 201, got {first.status_code}: {first.text}"
    )

    second = client.post(ROLES_URL, json=payload, headers=headers)
    assert second.status_code == 400, (
        f"Expected 400 for duplicate role name, got {second.status_code}: {second.text}"
    )


def test_get_roles_authenticated(client: TestClient, seed_roles, user_token: str):
    """
    GET /roles/ with a valid auth token must return HTTP 200.  (Req 8.12)
    """
    response = client.get(ROLES_URL, headers=_auth_header(user_token))
    assert response.status_code == 200, (
        f"Expected 200 for authenticated GET /roles/, got {response.status_code}: {response.text}"
    )
