# Quick Start Guide - RBAC System

This guide will get you up and running with the new RBAC system in 10 minutes.

## Prerequisites

- Python 3.8+
- PostgreSQL/MySQL/SQLite database
- All dependencies installed (`pip install -r requirements.txt`)

## Step-by-Step Setup

### 1. Drop Existing Tables (⚠️ WARNING: This will delete all data)

```sql
-- For PostgreSQL
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- For MySQL
DROP DATABASE your_database_name;
CREATE DATABASE your_database_name;

-- For SQLite
-- Just delete the database file
```

### 2. Initialize Alembic

```bash
# If alembic directory doesn't exist
alembic init alembic
```

### 3. Configure Alembic

Create or update `alembic/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.base import Base
from app.db.session import SQLALCHEMY_DATABASE_URL

# Import all models
from app.models import (
    User, Role, Menu, Action, RolePermission, AuditLog, PasswordResetToken
)

config = context.config
config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4. Create and Apply Migration

```bash
# Create migration
alembic revision --autogenerate -m "Initial RBAC schema"

# Apply migration
alembic upgrade head
```

### 5. Seed Initial Data

```bash
python seed_data.py
```

You should see:
```
🌱 Starting database seeding...

✓ Roles seeded successfully
✓ Actions seeded successfully
✓ Menus seeded successfully
✓ Admin permissions seeded successfully
✓ User permissions seeded successfully
✓ Admin user created successfully
  Email: admin@example.com
  Password: admin123
  ⚠️  IMPORTANT: Change this password immediately in production!

✅ Database seeding completed successfully!
```

### 6. Start the Application

```bash
uvicorn app.main:app --reload
```

### 7. Test the API

#### Login as Admin
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Get All Roles
```bash
curl -X GET "http://localhost:8000/roles/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get All Menus
```bash
curl -X GET "http://localhost:8000/menus/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Admin Permissions
```bash
curl -X GET "http://localhost:8000/role-permissions/role/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Default Data After Seeding

### Roles
1. **admin** - Full access to everything
2. **user** - Limited access (read-only dashboard)
3. **manager** - Team management access

### Actions
1. **create** - Create new records
2. **read** - View records
3. **update** - Modify records
4. **delete** - Remove records
5. **export** - Export data
6. **import** - Import data

### Menus
1. **Dashboard** (id: 1)
2. **Users** (id: 2)
3. **Roles** (id: 3)
4. **Menus** (id: 4)
5. **Permissions** (id: 5)
6. **Audit Logs** (id: 6)
7. **Settings** (id: 7)

### Default Admin User
- **Email:** admin@example.com
- **Password:** admin123 (⚠️ Change this!)
- **Role:** admin
- **Permissions:** All menus × All actions

## Common Tasks

### Create a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "name": "New User",
    "role_id": 2,
    "phone": "+1234567890",
    "address": "123 Main St"
  }'
```

### Create a New Role

```bash
curl -X POST "http://localhost:8000/roles/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "editor",
    "description": "Content editor with limited access"
  }'
```

### Assign Permission to Role

```bash
curl -X POST "http://localhost:8000/role-permissions/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 2,
    "menu_id": 1,
    "action_id": 2
  }'
```

### Bulk Assign Permissions

```bash
curl -X POST "http://localhost:8000/role-permissions/bulk" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"role_id": 2, "menu_id": 1, "action_id": 2},
    {"role_id": 2, "menu_id": 2, "action_id": 2},
    {"role_id": 2, "menu_id": 3, "action_id": 2}
  ]'
```

### Create Audit Log

```bash
curl -X POST "http://localhost:8000/audit-logs/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "module": "users",
    "activity": "Created new user",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  }'
```

## Using Permissions in Your Code

### Protect a Route with Permission

```python
from fastapi import APIRouter, Depends
from app.api.deps import require_permission, get_db

router = APIRouter()

@router.post("/users/")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_permission(menu_id=2, action_id=1))
):
    # Only users with CREATE permission on USERS menu can access
    # menu_id=2 (Users), action_id=1 (Create)
    return create_user_logic(db, user_data)
```

### Check Permission Manually

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
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sqlalchemy'"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "alembic.util.exc.CommandError: Can't locate revision identified by..."
**Solution:** Drop all tables and start fresh
```bash
# Drop all tables
# Then run migrations again
alembic upgrade head
```

### Issue: "Seed script fails"
**Solution:** Ensure migration completed successfully
```bash
# Check if tables exist
alembic current
# Should show the latest migration
```

### Issue: "Permission denied" when accessing endpoints
**Solution:** Check if user has the required permission
```bash
# Get user's role permissions
curl -X GET "http://localhost:8000/role-permissions/role/{role_id}" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Next Steps

1. **Change admin password** - Login and change from "admin123"
2. **Create custom roles** - Define roles for your use case
3. **Assign permissions** - Grant appropriate permissions to roles
4. **Create users** - Add users with appropriate roles
5. **Implement audit logging** - Add audit logs to critical operations
6. **Update frontend** - Integrate permission checking in UI

## Important Security Notes

⚠️ **Before going to production:**
1. Change the default admin password
2. Set a secure `SECRET_KEY` in environment variables
3. Use HTTPS in production
4. Enable rate limiting
5. Review and adjust permission assignments
6. Set up proper database backups
7. Configure CORS properly
8. Enable security headers

## Support

For detailed information, see:
- **MIGRATION_GUIDE.md** - Complete migration instructions
- **RBAC_IMPLEMENTATION.md** - Implementation details
- **PERMISSION_GUIDE.md** - Permission system reference
- **MIGRATION_CHECKLIST.md** - Detailed checklist

---

**You're all set!** 🎉

The RBAC system is now ready to use. Start by logging in as admin and exploring the new endpoints.
