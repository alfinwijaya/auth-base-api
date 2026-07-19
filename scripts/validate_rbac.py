#!/usr/bin/env python
"""
Validation script for auth-base-api.

Validates that:
1. The database connection is configured and live.
2. The required database tables exist.
3. The default roles ('admin', 'user') are seeded.
4. The default admin user exists.
5. Basic imports and application dependencies are healthy.
"""

import sys
import os
from sqlalchemy import inspect

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal, engine
from app.models.role import Role
from app.models.user import User
from app.models.menu import Menu
from app.models.action import Action
from app.models.role_permission import RolePermission
from app.models.audit_log import AuditLog
from app.models.password_reset import PasswordResetToken


def validate() -> bool:
    print("[INFO] Starting RBAC validation...")
    
    # 1. Test database connection
    try:
        db = SessionLocal()
        # Execute simple query to test connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        print("[SUCCESS] Database connection is live.")
    except Exception as e:
        print(f"[FAIL] Failed to connect to database: {e}")
        return False

    # 2. Verify all required tables exist
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        required_tables = [
            "users",
            "roles",
            "menus",
            "actions",
            "role_permissions",
            "audit_logs",
            "password_reset_tokens"
        ]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            print(f"[FAIL] Missing tables in database: {missing_tables}")
            print("Run migrations first: alembic upgrade head")
            return False
        
        print("[SUCCESS] All required tables exist in database.")
    except Exception as e:
        print(f"[FAIL] Error verifying database tables: {e}")
        return False

    # 3. Verify roles are seeded
    try:
        roles = db.query(Role).all()
        role_names = [r.role_name for r in roles]
        required_roles = ["admin", "user"]
        
        missing_roles = [r for r in required_roles if r not in role_names]
        if missing_roles:
            print(f"[FAIL] Missing seeded roles: {missing_roles}")
            print("Run seeding script first: python scripts/seed_data.py")
            return False
            
        print(f"[SUCCESS] Default roles seeded successfully. Found: {role_names}")
    except Exception as e:
        print(f"[FAIL] Error verifying roles: {e}")
        return False

    # 4. Verify admin user exists
    try:
        admin_role = db.query(Role).filter(Role.role_name == "admin").first()
        if not admin_role:
            print("[FAIL] Cannot verify admin user because admin role does not exist.")
            return False
            
        admin_user = db.query(User).filter(User.role_id == admin_role.id).first()
        if not admin_user:
            print("[FAIL] Default admin user does not exist in database.")
            print("Run seeding script first: python scripts/seed_data.py")
            return False
            
        print(f"[SUCCESS] Admin user exists. Active Admin: {admin_user.email}")
    except Exception as e:
        print(f"[FAIL] Error verifying admin user: {e}")
        return False

    # 5. Verify menus and actions are seeded
    try:
        menu_count = db.query(Menu).count()
        action_count = db.query(Action).count()
        perm_count = db.query(RolePermission).count()
        
        if menu_count == 0 or action_count == 0 or perm_count == 0:
            print(f"[FAIL] Missing menus ({menu_count}), actions ({action_count}), or permissions ({perm_count}).")
            print("Run seeding script first: python scripts/seed_data.py")
            return False
            
        print(f"[SUCCESS] Found {menu_count} menus, {action_count} actions, and {perm_count} permission mapping rules.")
    except Exception as e:
        print(f"[FAIL] Error verifying menus/actions/permissions: {e}")
        return False

    db.close()
    print("\n[SUCCESS] RBAC Validation Completed successfully! The repository base is healthy and ready.")
    return True


if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)
