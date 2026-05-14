# Database Migration Guide for RBAC System

## Overview
This guide will help you set up Alembic migrations for the new Role-Based Access Control (RBAC) system.

## Prerequisites
- All existing tables should be dropped
- Fresh Alembic initialization required

## Steps to Initialize Alembic

### 1. Initialize Alembic (if not already done)
```bash
alembic init alembic
```

### 2. Update alembic.ini
Make sure the `sqlalchemy.url` is set correctly in `alembic.ini`:
```ini
sqlalchemy.url = your_database_connection_string
```

### 3. Update alembic/env.py
Replace the content of `alembic/env.py` with the following:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.db.base import Base
from app.db.session import SQLALCHEMY_DATABASE_URL

# Import all models to ensure they are registered with Base.metadata
from app.models import (
    User, Role, Menu, Action, RolePermission, AuditLog, PasswordResetToken
)

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with the one from your app config
config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4. Create Initial Migration
```bash
alembic revision --autogenerate -m "Initial RBAC schema"
```

### 5. Review the Generated Migration
Check the generated migration file in `alembic/versions/` to ensure all tables are created correctly.

### 6. Apply the Migration
```bash
alembic upgrade head
```

## Database Schema

The RBAC system includes the following tables:

### 1. roles
- id (PK)
- role_name (unique)
- description
- created_at
- updated_at

### 2. users
- id (PK)
- role_id (FK -> roles.id)
- name
- email (unique)
- password
- phone
- address
- status (enum: active, inactive, suspended)
- created_at
- updated_at

### 3. menus
- id (PK)
- parent_id (FK -> menus.id, nullable)
- menu_name
- menu_slug (unique)
- menu_url
- icon
- sort_order
- is_active
- created_at
- updated_at

### 4. actions
- id (PK)
- action_name (unique)
- description
- created_at

### 5. role_permissions
- id (PK)
- role_id (FK -> roles.id)
- menu_id (FK -> menus.id)
- action_id (FK -> actions.id)
- created_at

### 6. audit_logs
- id (PK)
- user_id (FK -> users.id)
- module
- activity
- ip_address
- user_agent
- created_at

### 7. password_reset_tokens (existing)
- id (PK)
- user_id (FK -> users.id)
- token
- expires_at
- is_used

## Seeding Initial Data

After running migrations, you should seed initial data:

### 1. Create Default Roles
```python
from app.models.role import Role
from app.db.session import SessionLocal

db = SessionLocal()

roles = [
    Role(role_name="admin", description="Administrator with full access"),
    Role(role_name="user", description="Regular user with limited access"),
]

db.add_all(roles)
db.commit()
```

### 2. Create Default Actions
```python
from app.models.action import Action

actions = [
    Action(action_name="create", description="Create new records"),
    Action(action_name="read", description="View records"),
    Action(action_name="update", description="Modify existing records"),
    Action(action_name="delete", description="Remove records"),
]

db.add_all(actions)
db.commit()
```

### 3. Create Default Menus
```python
from app.models.menu import Menu

menus = [
    Menu(menu_name="Dashboard", menu_slug="dashboard", menu_url="/dashboard", icon="dashboard", sort_order=1),
    Menu(menu_name="Users", menu_slug="users", menu_url="/users", icon="people", sort_order=2),
    Menu(menu_name="Roles", menu_slug="roles", menu_url="/roles", icon="security", sort_order=3),
    Menu(menu_name="Settings", menu_slug="settings", menu_url="/settings", icon="settings", sort_order=4),
]

db.add_all(menus)
db.commit()
```

## API Endpoints

The following new endpoints are available:

### Roles
- POST /roles - Create a new role
- GET /roles - Get all roles
- GET /roles/{role_id} - Get a specific role
- PUT /roles/{role_id} - Update a role
- DELETE /roles/{role_id} - Delete a role

### Menus
- POST /menus - Create a new menu
- GET /menus - Get all menus
- GET /menus/{menu_id} - Get a specific menu
- GET /menus/active/list - Get all active menus
- PUT /menus/{menu_id} - Update a menu
- DELETE /menus/{menu_id} - Delete a menu

### Actions
- POST /actions - Create a new action
- GET /actions - Get all actions
- GET /actions/{action_id} - Get a specific action
- PUT /actions/{action_id} - Update an action
- DELETE /actions/{action_id} - Delete an action

### Role Permissions
- POST /role-permissions - Create a new permission
- POST /role-permissions/bulk - Create multiple permissions
- GET /role-permissions/{permission_id} - Get a specific permission
- GET /role-permissions/role/{role_id} - Get all permissions for a role
- GET /role-permissions/menu/{menu_id} - Get all permissions for a menu
- DELETE /role-permissions/{permission_id} - Delete a permission
- DELETE /role-permissions/role/{role_id} - Delete all permissions for a role

### Audit Logs
- POST /audit-logs - Create a new audit log
- GET /audit-logs - Get all audit logs
- GET /audit-logs/{log_id} - Get a specific audit log
- GET /audit-logs/user/{user_id} - Get all logs for a user
- GET /audit-logs/module/{module} - Get all logs for a module
- GET /audit-logs/date-range/ - Get logs within a date range

## Permission Checking

Use the `require_permission` dependency in your routes:

```python
from app.api.deps import require_permission

@router.post("/some-endpoint")
def some_endpoint(
    data: SomeSchema,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(menu_id=1, action_id=1))
):
    # Your endpoint logic
    pass
```

## Notes

- All timestamps use UTC timezone
- User status is an enum with values: active, inactive, suspended
- Menu parent_id can be null for top-level menus
- Audit logs are created automatically for important actions
- Password reset tokens remain unchanged from the previous implementation
