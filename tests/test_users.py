"""
Tests for the /users/* endpoints.

Covers: GET /users/me, GET /users/, DELETE /users/{user_id} with
authentication and authorization checks.

Validates: Requirements 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


USERS_ME_URL = "/users/me"
USERS_URL = "/users/"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# GET /users/me
# Validates: Requirements 8.2, 8.3
# ---------------------------------------------------------------------------

def test_get_me_authenticated(client: TestClient, admin_user, admin_token: str):
    """GET /users/me with a valid token returns HTTP 200. (Req 8.2)"""
    response = client.get(USERS_ME_URL, headers=_auth_headers(admin_token))
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )


def test_get_me_unauthenticated(client: TestClient):
    """GET /users/me without a token returns HTTP 401 or 403. (Req 8.3)"""
    response = client.get(USERS_ME_URL)
    assert response.status_code in (401, 403), (
        f"Expected 401 or 403, got {response.status_code}: {response.text}"
    )


# ---------------------------------------------------------------------------
# GET /users/
# Validates: Requirements 8.4, 8.5
# ---------------------------------------------------------------------------

def test_get_all_users_as_admin(client: TestClient, admin_user, admin_token: str):
    """GET /users/ with an admin token returns HTTP 200. (Req 8.4)"""
    response = client.get(USERS_URL, headers=_auth_headers(admin_token))
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )


def test_get_all_users_as_user(client: TestClient, regular_user, user_token: str):
    """GET /users/ with a non-admin user token returns HTTP 403. (Req 8.5)"""
    response = client.get(USERS_URL, headers=_auth_headers(user_token))
    assert response.status_code == 403, (
        f"Expected 403, got {response.status_code}: {response.text}"
    )


# ---------------------------------------------------------------------------
# DELETE /users/{user_id}
# Validates: Requirements 8.6, 8.7
# ---------------------------------------------------------------------------

def test_delete_user_as_admin(client: TestClient, admin_user, seed_roles, admin_token: str):
    """
    DELETE /users/{user_id} with an admin token returns HTTP 200. (Req 8.6)

    Registers a throwaway user so that deleting it does not invalidate
    the session-scoped regular_user fixture used by other tests.
    """
    # Register a throwaway user to be deleted
    reg = client.post(
        "/auth/register",
        json={"email": "todelete@example.com", "password": "pass123", "name": "To Delete"},
    )
    assert reg.status_code == 200, f"Registration failed: {reg.text}"
    # Retrieve the created user's id via GET /users/ (admin can list all users)
    users_resp = client.get(USERS_URL, headers=_auth_headers(admin_token))
    assert users_resp.status_code == 200
    created = next(
        (u for u in users_resp.json() if u["email"] == "todelete@example.com"),
        None,
    )
    assert created is not None, "Throwaway user not found in user list"

    response = client.delete(
        f"/users/{created['id']}",
        headers=_auth_headers(admin_token),
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )


def test_delete_user_as_user(client: TestClient, regular_user, user_token: str):
    """DELETE /users/{user_id} with a non-admin user token returns HTTP 403. (Req 8.7)"""
    # Attempt to delete the admin_user's record — the request should be
    # forbidden before any DB mutation occurs because the caller lacks the
    # 'admin' role.  Use a non-zero placeholder ID; the role check fires
    # before the DB lookup, so the exact ID doesn't matter.
    response = client.delete(
        f"/users/{regular_user.id}",
        headers=_auth_headers(user_token),
    )
    assert response.status_code == 403, (
        f"Expected 403, got {response.status_code}: {response.text}"
    )
