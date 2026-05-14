# Permission System Quick Reference

## Overview
The RBAC system uses a three-dimensional permission model: **Role × Menu × Action**

## Core Concepts

### 1. Roles
Define user groups with specific access levels.
- Examples: admin, user, manager, editor

### 2. Menus
Represent application features or modules.
- Examples: Dashboard, Users, Reports, Settings

### 3. Actions
Define what operations can be performed.
- Standard actions: create, read, update, delete
- Custom actions: export, import, approve, publish

### 4. Permissions
A permission grants a specific **Role** the ability to perform an **Action** on a **Menu**.

## Permission Flow

```
User → Has Role → Role has Permissions → Permission = (Menu + Action)
```

## Using Permissions in Code

### Method 1: Using `require_permission` Dependency

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_permission

router = APIRouter()

@router.post("/users/")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(menu_id=2, action_id=1))
):
    # Only users with permission to CREATE on USERS menu can access this
    # menu_id=2 (Users menu), action_id=1 (Create action)
    pass
```

### Method 2: Manual Permission Check

```python
from app.services.role_permission_service import RolePermissionService

def some_function(db: Session, current_user: User):
    has_permission = RolePermissionService.check_permission(
        db,
        role_id=current_user.role_id,
        menu_id=2,  # Users menu
        action_id=3  # Update action
    )
    
    if not has_permission:
        raise HTTPException(403, "Permission denied")
    
    # Proceed with operation
```

## Common Permission Patterns

### 1. Full CRUD Access
Grant all four basic actions on a menu:

```python
from app.schemas.role_permission import RolePermissionCreate

permissions = [
    RolePermissionCreate(role_id=role_id, menu_id=menu_id, action_id=1),  # Create
    RolePermissionCreate(role_id=role_id, menu_id=menu_id, action_id=2),  # Read
    RolePermissionCreate(role_id=role_id, menu_id=menu_id, action_id=3),  # Update
    RolePermissionCreate(role_id=role_id, menu_id=menu_id, action_id=4),  # Delete
]

RolePermissionService.bulk_create_permissions(db, permissions)
```

### 2. Read-Only Access
Grant only read permission:

```python
permission = RolePermissionCreate(
    role_id=user_role_id,
    menu_id=dashboard_menu_id,
    action_id=2  # Read action only
)

RolePermissionService.create_permission(db, permission)
```

### 3. Admin Full Access
Grant admin access to everything:

```python
admin_role = db.query(Role).filter(Role.role_name == "admin").first()
menus = db.query(Menu).all()
actions = db.query(Action).all()

permissions = []
for menu in menus:
    for action in actions:
        permissions.append(
            RolePermissionCreate(
                role_id=admin_role.id,
                menu_id=menu.id,
                action_id=action.id
            )
        )

RolePermissionService.bulk_create_permissions(db, permissions)
```

## Menu and Action IDs Reference

After running `seed_data.py`, you'll have these default IDs:

### Default Actions
| ID | Action Name | Description |
|----|-------------|-------------|
| 1  | create      | Create new records |
| 2  | read        | View and read records |
| 3  | update      | Modify existing records |
| 4  | delete      | Remove records |
| 5  | export      | Export data |
| 6  | import      | Import data |

### Default Menus
| ID | Menu Name    | Slug          | URL                |
|----|--------------|---------------|--------------------|
| 1  | Dashboard    | dashboard     | /dashboard         |
| 2  | Users        | users         | /users             |
| 3  | Roles        | roles         | /roles             |
| 4  | Menus        | menus         | /menus             |
| 5  | Permissions  | permissions   | /role-permissions  |
| 6  | Audit Logs   | audit-logs    | /audit-logs        |
| 7  | Settings     | settings      | /settings          |

## API Endpoints for Permission Management

### Get All Permissions for a Role
```http
GET /role-permissions/role/{role_id}
```

### Get All Permissions for a Menu
```http
GET /role-permissions/menu/{menu_id}
```

### Create Single Permission
```http
POST /role-permissions/
Content-Type: application/json

{
  "role_id": 2,
  "menu_id": 1,
  "action_id": 2
}
```

### Create Multiple Permissions (Bulk)
```http
POST /role-permissions/bulk
Content-Type: application/json

[
  {
    "role_id": 2,
    "menu_id": 1,
    "action_id": 2
  },
  {
    "role_id": 2,
    "menu_id": 2,
    "action_id": 2
  }
]
```

### Delete Permission
```http
DELETE /role-permissions/{permission_id}
```

### Delete All Permissions for a Role
```http
DELETE /role-permissions/role/{role_id}
```

## Best Practices

### 1. Use Descriptive Action Names
```python
# Good
Action(action_name="approve_invoice", description="Approve pending invoices")
Action(action_name="publish_article", description="Publish draft articles")

# Avoid
Action(action_name="action1", description="Does something")
```

### 2. Organize Menus Hierarchically
```python
# Parent menu
reports_menu = Menu(
    menu_name="Reports",
    menu_slug="reports",
    parent_id=None,
    sort_order=1
)

# Child menu
sales_reports = Menu(
    menu_name="Sales Reports",
    menu_slug="sales-reports",
    parent_id=reports_menu.id,
    sort_order=1
)
```

### 3. Check Permissions Early
```python
# Check permission at the route level
@router.post("/", dependencies=[Depends(require_permission(menu_id=2, action_id=1))])
def create_resource(...):
    # Permission already verified
    pass
```

### 4. Log Permission Denials
```python
from app.services.audit_log_service import AuditLogService

try:
    if not has_permission:
        # Log the denial
        AuditLogService.create_log(db, AuditLogCreate(
            user_id=current_user.id,
            module="permissions",
            activity=f"Permission denied: menu_id={menu_id}, action_id={action_id}",
            ip_address=request.client.host
        ))
        raise HTTPException(403, "Permission denied")
except Exception as e:
    # Handle error
    pass
```

### 5. Use Role-Based Defaults
```python
# Define permission templates for common roles
ROLE_TEMPLATES = {
    "viewer": [
        (menu_id, 2)  # Read-only on all menus
        for menu_id in range(1, 8)
    ],
    "editor": [
        (menu_id, action_id)
        for menu_id in range(1, 8)
        for action_id in [2, 3]  # Read and Update
    ],
    "admin": [
        (menu_id, action_id)
        for menu_id in range(1, 8)
        for action_id in range(1, 7)  # All actions
    ]
}
```

## Troubleshooting

### Permission Not Working?

1. **Check if permission exists:**
   ```python
   has_perm = RolePermissionService.check_permission(db, role_id, menu_id, action_id)
   print(f"Permission exists: {has_perm}")
   ```

2. **Verify user's role:**
   ```python
   print(f"User role: {current_user.role.role_name}")
   print(f"User role_id: {current_user.role_id}")
   ```

3. **Check menu and action IDs:**
   ```python
   menu = db.query(Menu).filter(Menu.menu_slug == "users").first()
   action = db.query(Action).filter(Action.action_name == "create").first()
   print(f"Menu ID: {menu.id}, Action ID: {action.id}")
   ```

4. **List all permissions for a role:**
   ```python
   perms = RolePermissionService.get_permissions_by_role(db, role_id)
   for perm in perms:
       print(f"Menu: {perm.menu_id}, Action: {perm.action_id}")
   ```

## Example: Complete Permission Setup

```python
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.menu import Menu
from app.models.action import Action
from app.services.role_permission_service import RolePermissionService
from app.schemas.role_permission import RolePermissionCreate

db = SessionLocal()

# Get entities
editor_role = db.query(Role).filter(Role.role_name == "editor").first()
users_menu = db.query(Menu).filter(Menu.menu_slug == "users").first()
read_action = db.query(Action).filter(Action.action_name == "read").first()
update_action = db.query(Action).filter(Action.action_name == "update").first()

# Grant permissions
permissions = [
    RolePermissionCreate(
        role_id=editor_role.id,
        menu_id=users_menu.id,
        action_id=read_action.id
    ),
    RolePermissionCreate(
        role_id=editor_role.id,
        menu_id=users_menu.id,
        action_id=update_action.id
    )
]

RolePermissionService.bulk_create_permissions(db, permissions)
print("✓ Editor can now read and update users")

db.close()
```

## Frontend Integration

### Checking Permissions in Frontend

Your frontend should request the user's permissions on login:

```javascript
// After login, fetch user permissions
const response = await fetch(`/role-permissions/role/${user.role_id}`);
const permissions = await response.json();

// Store in state/context
const userPermissions = permissions.map(p => ({
  menuId: p.menu_id,
  actionId: p.action_id
}));

// Check permission before showing UI elements
function hasPermission(menuId, actionId) {
  return userPermissions.some(
    p => p.menuId === menuId && p.actionId === actionId
  );
}

// Example: Show "Create User" button only if user has permission
{hasPermission(2, 1) && <CreateUserButton />}
```

## Summary

The permission system provides fine-grained access control by combining:
- **Roles** (who)
- **Menus** (where)
- **Actions** (what)

This allows you to precisely control what each user can do in your application.
