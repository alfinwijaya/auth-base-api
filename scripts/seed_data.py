"""
Seed script for auth-base-api.

Idempotent — safe to run multiple times. Each section checks for existing
records before inserting, so re-runs add only what is missing.

Usage (from the project root with the venv active):
    python -m scripts.seed_data
    # or
    python scripts/seed_data.py

Environment:
    Reads DATABASE_URL (via DB_TYPE) from .env automatically through
    app.core.config.settings.
"""

import sys
import os

# Ensure the project root is on sys.path when the script is run directly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine

# Import all models so Base.metadata is fully populated before create_all.
import app.models  # noqa: F401 – side-effect import registers all ORM classes

from app.models.role import Role
from app.models.action import Action
from app.models.menu import Menu
from app.models.role_permission import RolePermission
from app.models.user import User
from app.utils.hash import hash_password
from app.core.logger import logger


# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------

ROLES = [
    {"role_name": "admin", "description": "Full access — can manage all resources"},
    {"role_name": "user", "description": "Standard access — read-only on most resources"},
]

ACTIONS = [
    {"action_name": "create", "description": "Create a new resource"},
    {"action_name": "read", "description": "Read / list resources"},
    {"action_name": "update", "description": "Update an existing resource"},
    {"action_name": "delete", "description": "Delete a resource"},
]

# Menus are defined in (parent_slug, data) pairs so children are inserted
# after their parents.  parent_slug=None means a top-level menu.
MENUS = [
    # --- top-level entries ---
    (None, {
        "menu_name": "Dashboard",
        "menu_slug": "dashboard",
        "menu_url": "/dashboard",
        "icon": "dashboard",
        "sort_order": 1,
    }),
    (None, {
        "menu_name": "User Management",
        "menu_slug": "user-management",
        "menu_url": None,
        "icon": "people",
        "sort_order": 2,
    }),
    (None, {
        "menu_name": "Role Management",
        "menu_slug": "role-management",
        "menu_url": None,
        "icon": "shield",
        "sort_order": 3,
    }),
    (None, {
        "menu_name": "Permissions",
        "menu_slug": "permissions",
        "menu_url": None,
        "icon": "lock",
        "sort_order": 4,
    }),
    (None, {
        "menu_name": "Settings",
        "menu_slug": "settings",
        "menu_url": None,
        "icon": "settings",
        "sort_order": 5,
    }),
    # --- children of "User Management" ---
    ("user-management", {
        "menu_name": "Users",
        "menu_slug": "users",
        "menu_url": "/users",
        "icon": "person",
        "sort_order": 1,
    }),
    ("user-management", {
        "menu_name": "Audit Logs",
        "menu_slug": "audit-logs",
        "menu_url": "/audit-logs",
        "icon": "history",
        "sort_order": 2,
    }),
    # --- children of "Role Management" ---
    ("role-management", {
        "menu_name": "Roles",
        "menu_slug": "roles",
        "menu_url": "/roles",
        "icon": "badge",
        "sort_order": 1,
    }),
    # --- children of "Permissions" ---
    ("permissions", {
        "menu_name": "Menus",
        "menu_slug": "menus",
        "menu_url": "/menus",
        "icon": "menu",
        "sort_order": 1,
    }),
    ("permissions", {
        "menu_name": "Actions",
        "menu_slug": "actions",
        "menu_url": "/actions",
        "icon": "bolt",
        "sort_order": 2,
    }),
    ("permissions", {
        "menu_name": "Role Permissions",
        "menu_slug": "role-permissions",
        "menu_url": "/role-permissions",
        "icon": "key",
        "sort_order": 3,
    }),
    # --- children of "Settings" ---
    ("settings", {
        "menu_name": "Profile",
        "menu_slug": "profile",
        "menu_url": "/settings/profile",
        "icon": "account_circle",
        "sort_order": 1,
    }),
]

# Admin seed credentials — override via env vars in production.
ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "Admin@1234!")
ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "System Administrator")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _upsert_roles(db) -> dict[str, Role]:
    """Insert missing roles and return a {role_name: Role} mapping."""
    role_map: dict[str, Role] = {}
    for data in ROLES:
        role = db.query(Role).filter(Role.role_name == data["role_name"]).first()
        if role is None:
            role = Role(**data)
            db.add(role)
            db.flush()
            logger.info(f"Seeded role: {data['role_name']}")
        else:
            logger.debug(f"Role already exists, skipping: {data['role_name']}")
        role_map[role.role_name] = role
    return role_map


def _upsert_actions(db) -> dict[str, Action]:
    """Insert missing actions and return a {action_name: Action} mapping."""
    action_map: dict[str, Action] = {}
    for data in ACTIONS:
        action = db.query(Action).filter(Action.action_name == data["action_name"]).first()
        if action is None:
            action = Action(**data)
            db.add(action)
            db.flush()
            logger.info(f"Seeded action: {data['action_name']}")
        else:
            logger.debug(f"Action already exists, skipping: {data['action_name']}")
        action_map[action.action_name] = action
    return action_map


def _upsert_menus(db) -> dict[str, Menu]:
    """Insert missing menus (in order) and return a {menu_slug: Menu} mapping."""
    menu_map: dict[str, Menu] = {}

    # First pass: load any already-existing menus into the map.
    for existing in db.query(Menu).all():
        menu_map[existing.menu_slug] = existing

    for parent_slug, data in MENUS:
        if data["menu_slug"] in menu_map:
            logger.debug(f"Menu already exists, skipping: {data['menu_slug']}")
            continue

        parent_id = menu_map[parent_slug].id if parent_slug else None
        menu = Menu(parent_id=parent_id, **data)
        db.add(menu)
        db.flush()
        menu_map[menu.menu_slug] = menu
        logger.info(f"Seeded menu: {data['menu_slug']}")

    return menu_map


def _upsert_role_permissions(db, role_map, menu_map, action_map) -> None:
    """
    Grant permissions:
      - admin  → all actions on every menu
      - user   → "read" action on every menu
    """
    admin_role = role_map["admin"]
    user_role = role_map["user"]
    read_action = action_map["read"]

    all_menus = list(menu_map.values())
    all_actions = list(action_map.values())

    def _permission_exists(role_id: int, menu_id: int, action_id: int) -> bool:
        return (
            db.query(RolePermission)
            .filter_by(role_id=role_id, menu_id=menu_id, action_id=action_id)
            .first()
            is not None
        )

    # Admin: full CRUD on every menu
    for menu in all_menus:
        for action in all_actions:
            if not _permission_exists(admin_role.id, menu.id, action.id):
                db.add(RolePermission(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    action_id=action.id,
                ))
                logger.info(
                    f"Seeded permission: admin → {menu.menu_slug} → {action.action_name}"
                )

    # User: read-only on every menu
    for menu in all_menus:
        if not _permission_exists(user_role.id, menu.id, read_action.id):
            db.add(RolePermission(
                role_id=user_role.id,
                menu_id=menu.id,
                action_id=read_action.id,
            ))
            logger.info(f"Seeded permission: user → {menu.menu_slug} → read")

    db.flush()


def _upsert_admin_user(db, role_map) -> None:
    """Create the default admin user if it does not already exist."""
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        logger.debug(f"Admin user already exists, skipping: {ADMIN_EMAIL}")
        return

    admin_role = role_map["admin"]
    user = User(
        email=ADMIN_EMAIL,
        password=hash_password(ADMIN_PASSWORD),
        name=ADMIN_NAME,
        role_id=admin_role.id,
    )
    db.add(user)
    db.flush()
    logger.info(f"Seeded admin user: {ADMIN_EMAIL}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def seed() -> None:
    """Run all seed steps inside a single transaction."""
    logger.info("Starting database seed...")
    db = SessionLocal()
    try:
        role_map = _upsert_roles(db)
        action_map = _upsert_actions(db)
        menu_map = _upsert_menus(db)
        _upsert_role_permissions(db, role_map, menu_map, action_map)
        _upsert_admin_user(db, role_map)

        db.commit()
        logger.info("Database seed completed successfully.")
    except Exception:
        db.rollback()
        logger.exception("Seed failed — rolled back all changes.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
