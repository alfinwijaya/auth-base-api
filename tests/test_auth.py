"""
Tests for the /auth/* endpoints.

Covers: registration, login, and token refresh flows.

Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
REFRESH_URL = "/auth/refresh"

# A valid UserCreate body is required by /auth/login (uses UserCreate schema)
# which requires: email, password, name, role_id
def _login_payload(email: str, password: str, name: str = "Test User") -> dict:
    return {"email": email, "password": password, "name": name, "role_id": 1}


def _register_payload(email: str, password: str, name: str = "Test User") -> dict:
    return {"email": email, "password": password, "name": name}


# ---------------------------------------------------------------------------
# Task 2.3 – role_id is ignored during public registration
# Validates: Requirements 4.2, 4.3
# ---------------------------------------------------------------------------

def test_register_ignores_role_id(client: TestClient, seed_roles):
    """
    POST /auth/register with a body that includes role_id must:
    - Return HTTP 200  (the UserRegister schema has no role_id field, so
      Pydantic ignores the extra key rather than raising a validation error)
    - Create the user with the default 'user' role, not the supplied role_id=99

    The role assignment is verified by logging in with the registered credentials
    and decoding the JWT access token to confirm the 'role' claim equals 'user'.
    """
    payload = {
        "email": "newuser@example.com",
        "password": "pass123",
        "name": "Test User",
        "role_id": 99,  # arbitrary value — no matching Role row exists
    }

    response = client.post(REGISTER_URL, json=payload)

    # 1. Registration must succeed despite the extra role_id field
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    # 2. Log in with the same credentials to obtain a JWT.
    # The /auth/login endpoint uses UserCreate schema which requires name and role_id.
    login_resp = client.post(
        LOGIN_URL,
        json={
            "email": "newuser@example.com",
            "password": "pass123",
            "name": "Test User",
            "role_id": 1,
        },
    )
    assert login_resp.status_code == 200, (
        f"Login after registration failed ({login_resp.status_code}): {login_resp.text}"
    )

    # 3. Decode the access token and assert the role claim is 'user'
    access_token = login_resp.json()["access_token"]
    decoded = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert decoded.get("role") == "user", (
        f"Expected role claim 'user', got '{decoded.get('role')}'. "
        "The supplied role_id=99 must have been ignored."
    )


# ---------------------------------------------------------------------------
# Task 6.4 – 7 auth flow tests
# Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8
# ---------------------------------------------------------------------------

def test_register_success(client: TestClient, seed_roles):
    """POST /auth/register with unique email returns HTTP 200. (Req 7.2)"""
    response = client.post(REGISTER_URL, json=_register_payload("unique@example.com", "secret123"))
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    assert response.json()  # non-empty body


def test_register_duplicate_email(client: TestClient, seed_roles):
    """POST /auth/register twice with the same email → 400 on second call. (Req 7.3)"""
    payload = _register_payload("dup@example.com", "secret123")
    first = client.post(REGISTER_URL, json=payload)
    assert first.status_code == 200, f"First registration failed: {first.text}"

    second = client.post(REGISTER_URL, json=payload)
    assert second.status_code == 400, (
        f"Expected 400 on duplicate registration, got {second.status_code}: {second.text}"
    )


def test_login_success(client: TestClient, seed_roles):
    """
    Register then POST /auth/login → 200 with access_token, refresh_token,
    and token_type == 'bearer'. (Req 7.4)
    """
    email, password = "loginok@example.com", "mypassword"
    reg = client.post(REGISTER_URL, json=_register_payload(email, password))
    assert reg.status_code == 200, f"Registration failed: {reg.text}"

    resp = client.post(LOGIN_URL, json=_login_payload(email, password))
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    body = resp.json()
    assert "access_token" in body, "Response missing 'access_token'"
    assert "refresh_token" in body, "Response missing 'refresh_token'"
    assert body.get("token_type") == "bearer", (
        f"Expected token_type='bearer', got '{body.get('token_type')}'"
    )


def test_login_wrong_password(client: TestClient, seed_roles):
    """POST /auth/login with wrong password → HTTP 401. (Req 7.5)"""
    email, password = "wrongpw@example.com", "correctpassword"
    reg = client.post(REGISTER_URL, json=_register_payload(email, password))
    assert reg.status_code == 200, f"Registration failed: {reg.text}"

    resp = client.post(LOGIN_URL, json=_login_payload(email, "WRONGPASSWORD"))
    assert resp.status_code == 401, (
        f"Expected 401 for wrong password, got {resp.status_code}: {resp.text}"
    )


def test_login_unknown_email(client: TestClient, seed_roles):
    """POST /auth/login with an unregistered email → HTTP 401. (Req 7.6)"""
    resp = client.post(LOGIN_URL, json=_login_payload("nobody@example.com", "anypassword"))
    assert resp.status_code == 401, (
        f"Expected 401 for unknown email, got {resp.status_code}: {resp.text}"
    )


def test_refresh_token_success(client: TestClient, seed_roles):
    """
    Login, take refresh_token, POST /auth/refresh → 200.
    Decoded access_token must contain a 'role' claim. (Req 7.7)
    """
    email, password = "refreshme@example.com", "refreshpass"
    reg = client.post(REGISTER_URL, json=_register_payload(email, password))
    assert reg.status_code == 200, f"Registration failed: {reg.text}"

    login_resp = client.post(LOGIN_URL, json=_login_payload(email, password))
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    refresh_token = login_resp.json()["refresh_token"]

    resp = client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert resp.status_code == 200, (
        f"Expected 200 from /auth/refresh, got {resp.status_code}: {resp.text}"
    )

    new_access_token = resp.json().get("access_token")
    assert new_access_token, "Response missing 'access_token' after refresh"

    decoded = jwt.decode(
        new_access_token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert "role" in decoded, (
        f"Expected 'role' claim in refreshed access token, got claims: {list(decoded.keys())}"
    )


def test_refresh_token_invalid(client: TestClient, seed_roles):
    """POST /auth/refresh with a garbage token string → HTTP 401. (Req 7.8)"""
    resp = client.post(REFRESH_URL, json={"refresh_token": "this.is.garbage"})
    assert resp.status_code == 401, (
        f"Expected 401 for invalid refresh token, got {resp.status_code}: {resp.text}"
    )
