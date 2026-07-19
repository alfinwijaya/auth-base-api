# 🚀 AuthBase API - RBAC Edition

A comprehensive FastAPI-based authentication and authorization system with Role-Based Access Control (RBAC), JWT authentication, hierarchical menus, granular permissions, audit logging, and complete user management.

---

## ✨ Features

### Authentication & Authorization
- **JWT Authentication:** Access and refresh token generation.
- **Role-Based Access Control (RBAC):** Access restriction mapped to user roles.
- **Granular Permission Matrix:** 3D access control mapping **Role × Menu × Action**.
- **User Status Check:** Supports `active`, `inactive`, and `suspended` user states.
- **Password Reset:** Secure temporary reset token verification.

### RBAC System
- **Hierarchical Menus:** Parent-child menu tree relationships.
- **Flexible Actions:** Define custom operations (e.g. `create`, `read`, `update`, `delete`).
- **Audit Logging:** Append-only log capturing user context, IP address, and client details.
- **Bulk Permission Assignment:** Manage multiple mapping rules in a single transaction.

---

## 🗂️ Project Structure

```text
auth-base-api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── user.py           # User management
│   │   │   ├── role.py           # Role management
│   │   │   ├── menu.py           # Menu management
│   │   │   ├── action.py         # Action management
│   │   │   ├── role_permission.py # Permission management
│   │   │   └── audit_log.py      # Audit log endpoints
│   │   └── deps.py               # Dependencies & middleware
│   ├── core/                     # Config & security
│   ├── crud/                     # Database operations
│   ├── db/                       # Session & base models
│   ├── models/
│   │   ├── user.py               # User model
│   │   ├── role.py               # Role model
│   │   ├── menu.py               # Menu model
│   │   ├── action.py             # Action model
│   │   ├── role_permission.py    # Permission model
│   │   ├── audit_log.py          # Audit log model
│   │   └── password_reset.py     # Password reset tokens
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   └── main.py                   # FastAPI app
├── alembic/                      # Migrations
├── scripts/                      # Helper scripts
│   ├── seed_data.py              # Database seeding
│   └── validate_rbac.py          # Validation script
├── QUICK_START.md                # Quick start guide
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.8+
- SQLite, MySQL, or PostgreSQL
- Virtual environment tool (`venv`)

### 2. Install Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file at the root of the project:
```env
DB_TYPE=sqlite
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP for password reset
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_USE_TLS=true
```

### 4. Database Migration
```bash
alembic upgrade head
```

### 5. Seed Initial Data
```bash
python scripts/seed_data.py
```
This generates default roles (`admin`, `user`), default actions (`create`, `read`, `update`, `delete`), default menus (`Dashboard`, `Users`, etc.), permission mappings, and the default admin user:
- **Email:** `admin@example.com`
- **Password:** `Admin@1234!`

### 6. Verify System Health
Run the validation script to check database connections, tables, and seeded configurations:
```bash
python scripts/validate_rbac.py
```

### 7. Run the Application
```bash
uvicorn app.main:app --reload
```
- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc API Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📡 API Endpoint Reference

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user.
- `POST /auth/login` - Login, returning access and refresh JWT tokens.
- `POST /auth/refresh` - Refresh access token using a refresh token.
- `POST /auth/forgot-password` - Request a password reset token.
- `POST /auth/reset-password` - Reset password using the reset token.

### User Management (`/users`)
- `GET /users/me` - Retrieve current active user profile.
- `GET /users/` - List all users (Admin only).
- `DELETE /users/{user_id}` - Delete user (Admin only).

### Role Management (`/roles`)
- `POST /roles/` - Create a new role.
- `GET /roles/` - List all roles.
- `GET /roles/{role_id}` - Get a specific role.
- `PUT /roles/{role_id}` - Update a role.
- `DELETE /roles/{role_id}` - Delete a role.

### Menu Management (`/menus`)
- `POST /menus/` - Create a new menu.
- `GET /menus/` - List all menus.
- `GET /menus/{menu_id}` - Get a specific menu.
- `GET /menus/active/list` - Get active menus only (ordered by `sort_order`).
- `PUT /menus/{menu_id}` - Update a menu.
- `DELETE /menus/{menu_id}` - Delete a menu.

### Action Management (`/actions`)
- `POST /actions/` - Create a new action.
- `GET /actions/` - List all actions.
- `GET /actions/{action_id}` - Get a specific action.
- `PUT /actions/{action_id}` - Update an action.
- `DELETE /actions/{action_id}` - Delete an action.

### Role Permission Mapping (`/role-permissions`)
- `POST /role-permissions/` - Map single permission grant.
- `POST /role-permissions/bulk` - Map multiple permissions in a single call.
- `GET /role-permissions/{permission_id}` - Get specific permission grant details.
- `GET /role-permissions/role/{role_id}` - Get all permission mapping rules for a role.
- `GET /role-permissions/menu/{menu_id}` - Get all permission mapping rules for a menu.
- `DELETE /role-permissions/{permission_id}` - Revoke permission mapping.

### Audit Logs (`/audit-logs`)
- `POST /audit-logs/` - Create audit log entry.
- `GET /audit-logs/` - List all audit logs (supports pagination, user filtering, and module filtering).
- `GET /audit-logs/{log_id}` - Get specific audit log entry.
- `GET /audit-logs/user/{user_id}` - Get audit logs generated by a specific user.
- `GET /audit-logs/module/{module}` - Get audit logs for a specific module.
- `GET /audit-logs/date-range/` - Retrieve logs within a start and end datetime range.

---

## 🧪 Running Tests

Execute the test suite with:
```bash
pytest tests/ -v
```

---

## 🔒 Security Notes
1. Change default admin password after first login.
2. Use strong, randomly generated keys for `SECRET_KEY`.
3. In production, configure CORS settings and enforce TLS (HTTPS).
