"""
Tests for the /role-permissions/* endpoints.

Covers: create, bulk create, read, and delete permissions with auth/authorization boundaries.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


PERMISSIONS_URL = "/role-permissions/"


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def seeded_ids(client: TestClient, admin_token: str) -> dict:
    """Helper fixture to create a test role, menu, and action, returning their IDs."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    # Create role
    role_resp = client.post(
        "/roles/",
        json={"role_name": f"role_{uid}", "description": "test role desc"},
        headers=_auth_headers(admin_token)
    )
    role_id = role_resp.json()["id"]

    # Create menu
    menu_resp = client.post(
        "/menus/",
        json={"menu_name": f"menu_{uid}", "menu_slug": f"slug-{uid}"},
        headers=_auth_headers(admin_token)
    )
    menu_id = menu_resp.json()["id"]

    # Create action
    action_resp = client.post(
        "/actions/",
        json={"action_name": f"action_{uid}"},
        headers=_auth_headers(admin_token)
    )
    action_id = action_resp.json()["id"]

    return {"role_id": role_id, "menu_id": menu_id, "action_id": action_id}


def test_create_permission_unauthenticated(client: TestClient):
    """POST /role-permissions/ without token returns HTTP 401 or 403."""
    response = client.post(
        PERMISSIONS_URL,
        json={"role_id": 1, "menu_id": 1, "action_id": 1}
    )
    assert response.status_code in (401, 403)


def test_create_permission_non_admin(client: TestClient, user_token: str):
    """POST /role-permissions/ as regular user returns HTTP 403."""
    response = client.post(
        PERMISSIONS_URL,
        json={"role_id": 1, "menu_id": 1, "action_id": 1},
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 403


def test_create_permission_admin(client: TestClient, admin_token: str, seeded_ids: dict):
    """POST /role-permissions/ as admin returns HTTP 201."""
    payload = {
        "role_id": seeded_ids["role_id"],
        "menu_id": seeded_ids["menu_id"],
        "action_id": seeded_ids["action_id"]
    }
    response = client.post(
        PERMISSIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role_id"] == seeded_ids["role_id"]
    assert data["menu_id"] == seeded_ids["menu_id"]
    assert data["action_id"] == seeded_ids["action_id"]
    assert "id" in data


def test_bulk_create_permissions(client: TestClient, admin_token: str, seeded_ids: dict):
    """POST /role-permissions/bulk as admin returns HTTP 201 with list of permissions."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    # Create another menu for multiple items
    menu_resp = client.post(
        "/menus/",
        json={"menu_name": f"Bulk Menu {uid}", "menu_slug": f"bulk-menu-{uid}"},
        headers=_auth_headers(admin_token)
    )
    menu_id_2 = menu_resp.json()["id"]

    payload = [
        {
            "role_id": seeded_ids["role_id"],
            "menu_id": seeded_ids["menu_id"],
            "action_id": seeded_ids["action_id"]
        },
        {
            "role_id": seeded_ids["role_id"],
            "menu_id": menu_id_2,
            "action_id": seeded_ids["action_id"]
        }
    ]
    response = client.post(
        f"{PERMISSIONS_URL}bulk",
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["menu_id"] == seeded_ids["menu_id"]
    assert data[1]["menu_id"] == menu_id_2


def test_get_permission_by_id(client: TestClient, admin_token: str, user_token: str, seeded_ids: dict):
    """GET /role-permissions/{permission_id} returns HTTP 200 for authenticated user."""
    payload = {
        "role_id": seeded_ids["role_id"],
        "menu_id": seeded_ids["menu_id"],
        "action_id": seeded_ids["action_id"]
    }
    create_resp = client.post(
        PERMISSIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    assert create_resp.status_code == 201
    perm_id = create_resp.json()["id"]

    get_resp = client.get(
        f"{PERMISSIONS_URL}{perm_id}",
        headers=_auth_headers(user_token)
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["role_id"] == seeded_ids["role_id"]


def test_get_permissions_by_role(client: TestClient, admin_token: str, user_token: str, seeded_ids: dict):
    """GET /role-permissions/role/{role_id} returns all permissions assigned to a role."""
    payload = {
        "role_id": seeded_ids["role_id"],
        "menu_id": seeded_ids["menu_id"],
        "action_id": seeded_ids["action_id"]
    }
    client.post(
        PERMISSIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )

    response = client.get(
        f"{PERMISSIONS_URL}role/{seeded_ids['role_id']}",
        headers=_auth_headers(user_token)
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["role_id"] == seeded_ids["role_id"]


def test_delete_permission(client: TestClient, admin_token: str, seeded_ids: dict):
    """DELETE /role-permissions/{permission_id} removes permission successfully for admin."""
    payload = {
        "role_id": seeded_ids["role_id"],
        "menu_id": seeded_ids["menu_id"],
        "action_id": seeded_ids["action_id"]
    }
    create_resp = client.post(
        PERMISSIONS_URL,
        json=payload,
        headers=_auth_headers(admin_token)
    )
    perm_id = create_resp.json()["id"]

    del_resp = client.delete(
        f"{PERMISSIONS_URL}{perm_id}",
        headers=_auth_headers(admin_token)
    )
    assert del_resp.status_code == 204

    get_resp = client.get(
        f"{PERMISSIONS_URL}{perm_id}",
        headers=_auth_headers(admin_token)
    )
    assert get_resp.status_code == 404
