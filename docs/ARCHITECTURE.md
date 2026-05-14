# RBAC System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         RBAC System                             │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│  │  Users   │───▶│  Roles   │───▶│   Role   │───▶│  Menus   │   │
│  │          │    │          │    │Permission│    │          │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘   │
│       │               │                │                │       │
│       │               │                │                │       │
│       ▼               │                ▼                │       │
│  ┌──────────┐         │          ┌──────────┐           │       │
│  │  Audit   │         │          │ Actions  │           │       │
│  │   Logs   │         │          │          │           │       │
│  └──────────┘         │          └──────────┘           │       │
│                       │                                 │       │
│                       └─────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────┐
│     roles       │
├─────────────────┤
│ id (PK)         │
│ role_name       │◀────────┐
│ description     │         │
│ created_at      │         │
│ updated_at      │         │
└─────────────────┘         │
                            │
┌─────────────────┐         │
│     users       │         │
├─────────────────┤         │
│ id (PK)         │         │
│ role_id (FK)    │─────────┘
│ name            │
│ email           │
│ password        │
│ phone           │
│ address         │
│ status          │
│ created_at      │
│ updated_at      │
└─────────────────┘
        │
        │
        ▼
┌─────────────────┐
│   audit_logs    │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ module          │
│ activity        │
│ ip_address      │
│ user_agent      │
│ created_at      │
└─────────────────┘

┌─────────────────┐
│     menus       │
├─────────────────┤
│ id (PK)         │◀────────┐
│ parent_id (FK)  │─────────┘
│ menu_name       │
│ menu_slug       │
│ menu_url        │
│ icon            │
│ sort_order      │
│ is_active       │
│ created_at      │
│ updated_at      │
└─────────────────┘
        │
        │
        ▼
┌─────────────────┐
│    actions      │
├─────────────────┤
│ id (PK)         │
│ action_name     │
│ description     │
│ created_at      │
└─────────────────┘
        │
        │
        ▼
┌─────────────────┐
│role_permissions │
├─────────────────┤
│ id (PK)         │
│ role_id (FK)    │───┐
│ menu_id (FK)    │───┼───▶ Permission = Role × Menu × Action
│ action_id (FK)  │───┘
│ created_at      │
└─────────────────┘
```

## Permission Flow

```
┌──────────┐
│  User    │
│ Logs In  │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Get User's Role  │
└────┬─────────────┘
     │
     ▼
┌────────────────────────┐
│ Fetch Role Permissions │
│ (Role × Menu × Action) │
└────┬───────────────────┘
     │
     ▼
┌──────────────────────┐
│ User Accesses Route  │
└────┬─────────────────┘
     │
     ▼
┌────────────────────────┐
│ Check Permission       │
│ require_permission(    │
│   menu_id=2,           │
│   action_id=1          │
│ )                      │
└────┬───────────────────┘
     │
     ├─── Has Permission ──▶ ✅ Allow Access
     │
     └─── No Permission ───▶ ❌ 403 Forbidden
```

## API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Routes                        │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ /auth          │ Authentication & Registration       │   │
│  │ /users         │ User Management                     │   |
│  │ /roles         │ Role Management                     │   │
│  │ /menus         │ Menu Management                     │   │
│  │ /actions       │ Action Management                   │   │
│  │ /role-permissions │ Permission Management            │   │
│  │ /audit-logs    │ Audit Log Queries                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Dependencies                        │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ get_db()            │ Database Session               │   │
│  │ get_current_user()  │ JWT Authentication             │   │
│  │ require_role()      │ Role-Based Check               │   │
│  │ require_permission()│ Permission Check               │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Services                          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ AuthService        │ Authentication Logic            │   │
│  │ UserService        │ User Operations                 │   │
│  │ RoleService        │ Role Operations                 │   │
│  │ MenuService        │ Menu Operations                 │   │
│  │ ActionService      │ Action Operations               │   │
│  │ RolePermissionService │ Permission Operations        │   │
│  │ AuditLogService    │ Audit Log Operations            │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                     Models                           │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │ User, Role, Menu, Action, RolePermission, AuditLog   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Database                          │   │
│  │              PostgreSQL / MySQL / SQLite             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow Example

```
1. User Login
   ┌──────────────────────────────────────────────────┐
   │ POST /auth/login                                 │
   │ Body: { email, password }                        │
   └────┬─────────────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────────────────┐
   │ AuthService.login_user()                         │
   │ - Verify credentials                             │
   │ - Generate JWT tokens                            │
   └────┬─────────────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────────────────┐
   │ Return: { access_token, refresh_token }          │
   └──────────────────────────────────────────────────┘

2. Protected Request
   ┌──────────────────────────────────────────────────┐
   │ POST /users/                                     │
   │ Headers: Authorization: Bearer <token>           │
   │ Dependencies: require_permission(2, 1)           │
   └────┬─────────────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────────────────┐
   │ get_current_user()                               │
   │ - Decode JWT                                     │
   │ - Fetch user from DB                             │
   └────┬─────────────────────────────────────────────┘
        │
        ▼
   ┌──────────────────────────────────────────────────┐
   │ require_permission(menu_id=2, action_id=1)       │
   │ - Check role_permissions table                   │
   │ - Verify: role_id + menu_id + action_id exists   │
   └────┬─────────────────────────────────────────────┘
        │
        ├─── Permission Granted ──▶ Execute Handler
        │
        └─── Permission Denied ───▶ 403 Forbidden
```

## Data Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP Request
       │
       ▼
┌─────────────┐
│  FastAPI    │
│   Router    │
└──────┬──────┘
       │
       │ Route Handler
       │
       ▼
┌─────────────┐
│ Dependencies│
│  - Auth     │
│  - Perms    │
└──────┬──────┘
       │
       │ Validated Request
       │
       ▼
┌─────────────┐
│  Service    │
│   Layer     │
└──────┬──────┘
       │
       │ Business Logic
       │
       ▼
┌─────────────┐
│   Model     │
│   Layer     │
└──────┬──────┘
       │
       │ SQL Query
       │
       ▼
┌─────────────┐
│  Database   │
└──────┬──────┘
       │
       │ Result
       │
       ▼
┌─────────────┐
│  Response   │
│   (JSON)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Client    │
└─────────────┘
```

## Permission Matrix Example

```
Role: Editor
┌──────────────┬────────┬──────┬────────┬────────┬────────┬────────┐
│ Menu         │ Create │ Read │ Update │ Delete │ Export │ Import │
├──────────────┼────────┼──────┼────────┼────────┼────────┼────────┤
│ Dashboard    │   ❌   │  ✅  │   ❌   │   ❌   │   ❌  │   ❌   │
│ Users        │   ❌   │  ✅  │   ✅   │   ❌   │   ❌  │   ❌   │
│ Roles        │   ❌   │  ✅  │   ❌   │   ❌   │   ❌  │   ❌   │
│ Menus        │   ❌   │  ✅  │   ❌   │   ❌   │   ❌  │   ❌   │
│ Permissions  │   ❌   │  ✅  │   ❌   │   ❌   │   ❌  │   ❌   │
│ Audit Logs   │   ❌   │  ✅  │   ❌   │   ❌   │   ✅  │   ❌   │
│ Settings     │   ❌   │  ✅  │   ✅   │   ❌   │   ❌  │   ❌   │
└──────────────┴────────┴──────┴────────┴────────┴────────┴────────┘

Role: Admin
┌──────────────┬────────┬──────┬────────┬────────┬────────┬────────┐
│ Menu         │ Create │ Read │ Update │ Delete │ Export │ Import │
├──────────────┼────────┼──────┼────────┼────────┼────────┼────────┤
│ Dashboard    │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Users        │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Roles        │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Menus        │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Permissions  │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Audit Logs   │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
│ Settings     │   ✅   │  ✅  │   ✅   │   ✅   │   ✅  │   ✅   │
└──────────────┴────────┴──────┴────────┴────────┴────────┴────────┘
```

## Hierarchical Menu Structure

```
Dashboard (id: 1)
│
Users (id: 2)
│
Roles (id: 3)
│
Menus (id: 4)
│
Permissions (id: 5)
│
Audit Logs (id: 6)
│
Settings (id: 7)
├── Profile Settings (parent_id: 7)
├── System Settings (parent_id: 7)
│   ├── Email Settings (parent_id: 8)
│   └── Security Settings (parent_id: 8)
└── Appearance (parent_id: 7)
```

## Audit Log Flow

```
┌─────────────────┐
│  User Action    │
│  (Any CRUD)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create AuditLog │
│ - user_id       │
│ - module        │
│ - activity      │
│ - ip_address    │
│ - user_agent    │
│ - timestamp     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Store in DB     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Logs      │
│ - By user       │
│ - By module     │
│ - By date range │
└─────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Authentication (JWT)                          │
│  ├─ Valid token required                                │
│  ├─ Token expiration check                              │
│  └─ User existence verification                         │
│                                                         │
│  Layer 2: Role-Based Access                             │
│  ├─ User must have valid role                           │
│  └─ Role must be active                                 │
│                                                         │
│  Layer 3: Permission-Based Access                       │
│  ├─ Check role_permissions table                        │
│  ├─ Verify: role_id + menu_id + action_id               │
│  └─ Grant/Deny access                                   │
│                                                         │
│  Layer 4: User Status Check                             │
│  ├─ User must be "active"                               │
│  └─ Suspended/Inactive users denied                     │
│                                                         │
│  Layer 5: Audit Logging                                 │
│  ├─ Log all actions                                     │
│  ├─ Track IP and user agent                             │
│  └─ Timestamp all activities                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Component Relationships

```
┌──────────┐
│   User   │
└────┬─────┘
     │ has one
     ▼
┌──────────┐
│   Role   │
└────┬─────┘
     │ has many
     ▼
┌───────────────┐
│ RolePermission│
└────┬──────────┘
     │ references
     ├──────────────┐
     │              │
     ▼              ▼
┌──────────┐  ┌──────────┐
│   Menu   │  │  Action  │
└──────────┘  └──────────┘
```

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Scalable permission system
- ✅ Comprehensive audit trail
- ✅ Flexible role management
- ✅ Hierarchical menu structure
- ✅ Multiple security layers
