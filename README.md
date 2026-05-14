# 🚀 AuthBase API - RBAC Edition

A comprehensive FastAPI-based authentication and authorization system with Role-Based Access Control (RBAC), JWT authentication, hierarchical menus, granular permissions, audit logging, and complete user management.

---

## ⚠️ IMPORTANT: RBAC System Implemented

This codebase has been completely refactored to implement a comprehensive RBAC system. **All existing tables must be dropped and migrations must be run fresh.**

👉 **[GETTING_STARTED.md](GETTING_STARTED.md)** - Start here for quick overview and next steps

### 📚 Documentation

All documentation is organized in the **[docs/](docs/)** folder:

**Essential guides:**
- **[Quick Start](docs/QUICK_START.md)** - Get up and running in 10 minutes
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Step-by-step migration instructions
- **[Permission Guide](docs/PERMISSION_GUIDE.md)** - Permission system usage guide

**Complete index:** See **[docs/README.md](docs/README.md)** for all documentation

---

## ✨ Features

### Authentication & Authorization
- ✅ JWT access + refresh tokens
- ✅ Role-based access control (RBAC)
- ✅ Granular permission system (Role × Menu × Action)
- ✅ User status management (active, inactive, suspended)
- ✅ Password reset via token + email

### RBAC System
- ✅ **Hierarchical Menus** - Parent-child menu relationships
- ✅ **Flexible Actions** - Define custom actions (create, read, update, delete, export, import, etc.)
- ✅ **Role Permissions** - Fine-grained access control at Role × Menu × Action level
- ✅ **Audit Logging** - Track all user activities with IP and user agent
- ✅ **Bulk Operations** - Assign multiple permissions at once

### User Management
- ✅ Enhanced user profiles (name, phone, address)
- ✅ User status tracking
- ✅ Comprehensive user information
- ✅ Timestamp tracking (created_at, updated_at)

### Technical Features
- ✅ Alembic migrations
- ✅ SlowAPI rate limiting
- ✅ Docker-compose support
- ✅ Seed data script
- ✅ Validation script

---

## 🗂️ Project Structure

```
auth-base-api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── user.py           # User management
│   │   │   ├── role.py           # Role management (NEW)
│   │   │   ├── menu.py           # Menu management (NEW)
│   │   │   ├── action.py         # Action management (NEW)
│   │   │   ├── role_permission.py # Permission management (NEW)
│   │   │   └── audit_log.py      # Audit log endpoints (NEW)
│   │   └── deps.py               # Dependencies & middleware
│   ├── core/                     # Config & security
│   ├── crud/                     # Database operations
│   ├── db/                       # Session & base models
│   ├── models/
│   │   ├── user.py               # Enhanced user model
│   │   ├── role.py               # Enhanced role model
│   │   ├── menu.py               # Menu model (NEW)
│   │   ├── action.py             # Action model (NEW)
│   │   ├── role_permission.py    # Permission model (NEW)
│   │   ├── audit_log.py          # Audit log model (NEW)
│   │   └── password_reset.py     # Password reset tokens
│   ├── schemas/                  # Pydantic schemas (all updated/new)
│   ├── services/                 # Business logic (all updated/new)
│   └── main.py                   # FastAPI app
├── alembic/                      # Migrations
├── scripts/                      # Helper scripts
├── seed_data.py                  # Database seeding (NEW)
├── validate_rbac.py              # Validation script (NEW)
├── QUICK_START.md                # Quick start guide (NEW)
├── MIGRATION_GUIDE.md            # Migration instructions (NEW)
├── MIGRATION_CHECKLIST.md        # Migration checklist (NEW)
├── RBAC_IMPLEMENTATION.md        # Implementation details (NEW)
├── PERMISSION_GUIDE.md           # Permission guide (NEW)
├── IMPLEMENTATION_SUMMARY.md     # Summary of changes (NEW)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.8+
- PostgreSQL/MySQL/SQLite
- Virtual environment

### 2. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure Environment
Create `.env` file:
```env
DB_TYPE=postgres
POSTGRES_DB_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# SMTP for password reset
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_USE_TLS=true
```

### 4. Database Migration

⚠️ **IMPORTANT: Drop all existing tables first!**

```bash
# Initialize Alembic (if not done)
alembic init alembic

# Update alembic/env.py (see MIGRATION_GUIDE.md)

# Create migration
alembic revision --autogenerate -m "Initial RBAC schema"

# Apply migration
alembic upgrade head
```

### 5. Seed Initial Data
```bash
python seed_data.py
```

This creates:
- Default roles (admin, user, manager)
- Default actions (create, read, update, delete, export, import)
- Default menus (Dashboard, Users, Roles, Menus, Permissions, Audit Logs, Settings)
- Admin user (email: admin@example.com, password: admin123)
- Default permissions

### 6. Run the Application
```bash
uvicorn app.main:app --reload
```

Visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📡 API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user (requires: email, password, name, role_id)
- `POST /auth/login` - Login (returns access & refresh tokens)
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Users (`/users`)
- `GET /users/me` - Get current user profile
- `GET /users/` - List all users (admin only)
- `DELETE /users/{user_id}` - Delete user (admin only)

### Roles (`/roles`) 🆕
- `POST /roles/` - Create new role
- `GET /roles/` - List all roles
- `GET /roles/{role_id}` - Get specific role
- `PUT /roles/{role_id}` - Update role
- `DELETE /roles/{role_id}` - Delete role

### Menus (`/menus`) 🆕
- `POST /menus/` - Create new menu
- `GET /menus/` - List all menus
- `GET /menus/{menu_id}` - Get specific menu
- `GET /menus/active/list` - Get active menus only
- `PUT /menus/{menu_id}` - Update menu
- `DELETE /menus/{menu_id}` - Delete menu

### Actions (`/actions`) 🆕
- `POST /actions/` - Create new action
- `GET /actions/` - List all actions
- `GET /actions/{action_id}` - Get specific action
- `PUT /actions/{action_id}` - Update action
- `DELETE /actions/{action_id}` - Delete action

### Role Permissions (`/role-permissions`) 🆕
- `POST /role-permissions/` - Create single permission
- `POST /role-permissions/bulk` - Create multiple permissions
- `GET /role-permissions/{permission_id}` - Get specific permission
- `GET /role-permissions/role/{role_id}` - Get all permissions for a role
- `GET /role-permissions/menu/{menu_id}` - Get all permissions for a menu
- `DELETE /role-permissions/{permission_id}` - Delete permission
- `DELETE /role-permissions/role/{role_id}` - Delete all permissions for a role

### Audit Logs (`/audit-logs`) 🆕
- `POST /audit-logs/` - Create audit log entry
- `GET /audit-logs/` - List all audit logs
- `GET /audit-logs/{log_id}` - Get specific log
- `GET /audit-logs/user/{user_id}` - Get logs by user
- `GET /audit-logs/module/{module}` - Get logs by module
- `GET /audit-logs/date-range/` - Get logs by date range

---

## 🔐 Permission System

The RBAC system uses a three-dimensional permission model:

**Permission = Role × Menu × Action**

### Example: Protecting a Route
```python
from fastapi import APIRouter, Depends
from app.api.deps import require_permission

router = APIRouter()

@router.post("/users/")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(menu_id=2, action_id=1))
):
    # Only users with CREATE permission on USERS menu can access
    # menu_id=2 (Users menu), action_id=1 (Create action)
    return create_user_logic(db, user_data)
```

See **[PERMISSION_GUIDE.md](PERMISSION_GUIDE.md)** for complete usage guide.

---

## 🔄 Breaking Changes

### User Registration
**Before:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**After:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "role_id": 2,
  "phone": "+1234567890",
  "address": "123 Main St"
}
```

### Role Field Name
- `role.name` → `role.role_name`

### User Response
Now includes: `name`, `phone`, `address`, `status`, `created_at`, `updated_at`

---

## 🛠️ Tech Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Python-JOSE** - JWT handling
- **SlowAPI** - Rate limiting
- **PostgreSQL/MySQL/SQLite** - Database

---

## 📊 Default Data (After Seeding)

### Roles
- **admin** - Full access to all features
- **user** - Limited access (read-only dashboard)
- **manager** - Team management access

### Actions
- create, read, update, delete, export, import

### Menus
- Dashboard, Users, Roles, Menus, Permissions, Audit Logs, Settings

### Default Admin
- **Email:** admin@example.com
- **Password:** admin123
- ⚠️ **Change this immediately in production!**

---

## 🔒 Security Notes

Before production:
1. ✅ Change default admin password
2. ✅ Set secure `SECRET_KEY`
3. ✅ Use HTTPS
4. ✅ Enable rate limiting
5. ✅ Configure CORS properly
6. ✅ Set up database backups
7. ✅ Review permission assignments
8. ✅ Enable security headers

---

## 📖 Documentation

For complete documentation, see the **[docs/](docs/)** folder:
- **[Getting Started](GETTING_STARTED.md)** - Quick overview and next steps
- **[Quick Start Guide](docs/QUICK_START.md)** - Get started in 10 minutes
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Complete migration instructions
- **[Permission Guide](docs/PERMISSION_GUIDE.md)** - Permission system reference
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture diagrams
- **[Full Documentation Index](docs/README.md)** - Complete documentation index

---

## 🤝 Contributing

This is a template project for learning and small projects. Feel free to fork and customize for your needs.

---

## 📝 License

MIT License - Feel free to use this template for your projects.

---

## 🎉 What's New in RBAC Edition

- ✅ Complete RBAC implementation
- ✅ Hierarchical menu system
- ✅ Granular permission control
- ✅ Comprehensive audit logging
- ✅ Enhanced user management
- ✅ Bulk permission operations
- ✅ User status tracking
- ✅ Complete documentation
- ✅ Seed data script
- ✅ Validation tools

---

**Ready to get started?** Check out **[GETTING_STARTED.md](GETTING_STARTED.md)** or jump straight to **[docs/QUICK_START.md](docs/QUICK_START.md)**!
