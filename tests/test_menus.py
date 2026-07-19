"""
Tests for the /menus/* endpoints.

Covers: create, read, update, delete menus, including active list and hierarchy checks.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


MENUS_URL = "/menus/"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_create_menu_unauthenticated(client: TestClient):
    """POST /menus/ without token returns HTTP 401 or 403."""
    response = client.post(
        MENUS_URL,
        json={"menu_name": "Test", "menu_slug": "test"}
    )
    assert response.status_code in (401, 403)


def test_create_menu_non_admin(client: TestClient, user_token: str):
    """POST /menus/ as a regular user returns HTTP 403."""
    response = client.post(
        MENUS_URL,
        json={"menu_name": "Test", "menu_slug": "test"},
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 403


def test_create_menu_admin(client: TestClient, admin_token: str):
    """POST /menus/ as admin returns HTTP 201."""
    payload = {
        "menu_name": "Dashboard",
        "menu_slug": "dashboard",
        "menu_url": "/dashboard",
        "icon": "dashboard-icon",
        "sort_order": 1,
        "is_active": True
    }
    response = client.post(
        MENUS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["menu_slug"] == "dashboard"
    assert "id" in data


def test_create_duplicate_menu_slug(client: TestClient, admin_token: str):
    """POST /menus/ with duplicate slug returns HTTP 400."""
    payload = {
        "menu_name": "Unique Menu",
        "menu_slug": "unique",
    }
    response = client.post(
        MENUS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201

    response_dup = client.post(
        MENUS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response_dup.status_code == 400


def test_get_menu_by_id(client: TestClient, admin_token: str, user_token: str):
    """GET /menus/{menu_id} returns HTTP 200 for authenticated user."""
    payload = {
        "menu_name": "Item To Get",
        "menu_slug": "get-item",
    }
    create_resp = client.post(
        MENUS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert create_resp.status_code == 201
    menu_id = create_resp.json()["id"]

    # Accessible by a regular user as long as they are authenticated
    get_resp = client.get(
        f"{MENUS_URL}{menu_id}",
        headers=_auth_headers(user_token)
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["menu_slug"] == "get-item"


def test_get_menu_not_found(client: TestClient, user_token: str):
    """GET /menus/{menu_id} with invalid id returns HTTP 404."""
    response = client.get(
        f"{MENUS_URL}99999",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 404


def test_get_all_menus(client: TestClient, admin_token: str, user_token: str):
    """GET /menus/ lists all menus."""
    # Seed at least one menu
    client.post(
        MENUS_URL,
        json={"menu_name": "List Item", "menu_slug": "list-item"},
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        MENUS_URL,
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_active_menus(client: TestClient, admin_token: str, user_token: str):
    """GET /menus/active/list returns only active menus ordered by sort_order."""
    client.post(
        MENUS_URL,
        json={"menu_name": "Active A", "menu_slug": "active-a", "is_active": True, "sort_order": 10},
        headers=_auth_headers(admin_token)
    )
    client.post(
        MENUS_URL,
        json={"menu_name": "Active B", "menu_slug": "active-b", "is_active": True, "sort_order": 5},
        headers=_auth_headers(admin_token)
    )
    client.post(
        MENUS_URL,
        json={"menu_name": "Inactive C", "menu_slug": "inactive-c", "is_active": False, "sort_order": 1},
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        f"{MENUS_URL}active/list",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Check that inactive-c is not in active list
    slugs = [item["menu_slug"] for item in data]
    assert "inactive-c" not in slugs
    assert "active-a" in slugs
    assert "active-b" in slugs

    # Assert sort order: active-b (5) comes before active-a (10)
    idx_a = slugs.index("active-a")
    idx_b = slugs.index("active-b")
    assert idx_b < idx_a


def test_update_menu(client: TestClient, admin_token: str):
    """PUT /menus/{menu_id} updates fields successfully for admin."""
    create_resp = client.post(
        MENUS_URL,
        json={"menu_name": "Old Name", "menu_slug": "old-slug"},
        headers=_auth_headers(admin_token)
    )
    menu_id = create_resp.json()["id"]

    update_payload = {
        "menu_name": "New Name",
        "menu_slug": "new-slug",
        "is_active": False
    }
    update_resp = client.put(
        f"{MENUS_URL}{menu_id}",
        json=update_payload,
        headers=_auth_headers(admin_token)
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["menu_name"] == "New Name"
    assert updated_data["menu_slug"] == "new-slug"
    assert updated_data["is_active"] is False


def test_delete_menu(client: TestClient, admin_token: str):
    """DELETE /menus/{menu_id} removes menu successfully for admin."""
    create_resp = client.post(
        MENUS_URL,
        json={"menu_name": "Delete Me", "menu_slug": "delete-me"},
        headers=_auth_headers(admin_token)
    )
    menu_id = create_resp.json()["id"]

    del_resp = client.delete(
        f"{MENUS_URL}{menu_id}",
        headers=_auth_headers(admin_token)
    )
    assert del_resp.status_code == 204

    # Verify not found after delete
    get_resp = client.get(
        f"{MENUS_URL}{menu_id}",
        headers=_auth_headers(admin_token)
    )
    assert get_resp.status_code == 404
