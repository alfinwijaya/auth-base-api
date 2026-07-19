"""
Tests for the /actions/* endpoints.

Covers: create, read, update, delete actions with authentication and authorization checks.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


ACTIONS_URL = "/actions/"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_action_unauthenticated(client: TestClient):
    """POST /actions/ without token returns HTTP 401 or 403."""
    response = client.post(
        ACTIONS_URL,
        json={"action_name": "view", "description": "view description"}
    )
    assert response.status_code in (401, 403)


def test_create_action_non_admin(client: TestClient, user_token: str):
    """POST /actions/ as regular user returns HTTP 403."""
    response = client.post(
        ACTIONS_URL,
        json={"action_name": "view", "description": "view description"},
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 403


def test_create_action_admin(client: TestClient, admin_token: str):
    """POST /actions/ as admin returns HTTP 201."""
    payload = {
        "action_name": "create",
        "description": "ability to create resources"
    }
    response = client.post(
        ACTIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["action_name"] == "create"
    assert "id" in data


def test_create_duplicate_action_name(client: TestClient, admin_token: str):
    """POST /actions/ with duplicate name returns HTTP 400."""
    payload = {
        "action_name": "duplicate",
        "description": "duplicate action"
    }
    response1 = client.post(
        ACTIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response1.status_code == 201

    response2 = client.post(
        ACTIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response2.status_code == 400


def test_get_action_by_id(client: TestClient, admin_token: str, user_token: str):
    """GET /actions/{action_id} returns HTTP 200 for authenticated user."""
    create_resp = client.post(
        ACTIONS_URL,
        json={"action_name": "read-only", "description": "read details"},
        headers=_auth_headers(admin_token)
    )
    assert create_resp.status_code == 201
    action_id = create_resp.json()["id"]

    get_resp = client.get(
        f"{ACTIONS_URL}{action_id}",
        headers=_auth_headers(user_token)
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["action_name"] == "read-only"


def test_get_action_not_found(client: TestClient, user_token: str):
    """GET /actions/{action_id} with invalid id returns HTTP 404."""
    response = client.get(
        f"{ACTIONS_URL}99999",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 404


def test_get_all_actions(client: TestClient, admin_token: str, user_token: str):
    """GET /actions/ lists all actions."""
    client.post(
        ACTIONS_URL,
        json={"action_name": "list-action", "description": "list action desc"},
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        ACTIONS_URL,
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_update_action(client: TestClient, admin_token: str):
    """PUT /actions/{action_id} updates fields successfully for admin."""
    create_resp = client.post(
        ACTIONS_URL,
        json={"action_name": "old-action", "description": "old desc"},
        headers=_auth_headers(admin_token)
    )
    action_id = create_resp.json()["id"]

    update_resp = client.put(
        f"{ACTIONS_URL}{action_id}",
        json={"action_name": "new-action", "description": "new desc"},
        headers=_auth_headers(admin_token)
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["action_name"] == "new-action"
    assert updated_data["description"] == "new desc"


def test_delete_action(client: TestClient, admin_token: str):
    """DELETE /actions/{action_id} removes action successfully for admin."""
    create_resp = client.post(
        ACTIONS_URL,
        json={"action_name": "delete-me", "description": "about to be deleted"},
        headers=_auth_headers(admin_token)
    )
    action_id = create_resp.json()["id"]

    del_resp = client.delete(
        f"{ACTIONS_URL}{action_id}",
        headers=_auth_headers(admin_token)
    )
    assert del_resp.status_code == 204

    get_resp = client.get(
        f"{ACTIONS_URL}{action_id}",
        headers=_auth_headers(admin_token)
    )
    assert get_resp.status_code == 404
