"""
Seed script to populate initial data for RBAC system
Run this after creating the database tables with alembic
"""
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.action import Action
from app.models.menu import Menu
from app.models.role_permission import RolePermission
from app.models.user import User, UserStatus
from app.utils.hash import hash_password
from datetime import datetime, timezone

def seed_roles(db):
    """Create default roles"""
    roles = [
        Role(
            role_name="admin",
            description="Administrator with full access to all features",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Role(
            role_name="user",
            description="Regular user with limited access",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
        Role(
            role_name="manager",
            description="Manager with access to team management features",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        ),
    ]
    
    for role in roles:
        existing = db.query(Role).filter(Role.role_name == role.role_name).first()
        if not existing:
            db.add(role)
    
    db.commit()
    print("✓ Roles seeded successfully")

def seed_actions(db):
    """Create default actions"""
    actions = [
        Action(action_name="create", description="Create new records"),
        Action(action_name="read", description="View and read records"),
        Action(action_name="update", description="Modify existing records"),
        Action(action_name="delete", description="Remove records"),
        Action(action_name="export", description="Export data"),
        Action(action_name="import", description="Import data"),
    ]
    
    for action in actions:
        existing = db.query(Action).filter(Action.action_name == action.action_name).first()
        if not existing:
            db.add(action)
    
    db.commit()
    print("✓ Actions seeded successfully")

def seed_menus(db):
    """Create default menus"""
    menus = [
        Menu(
            menu_name="Dashboard",
            menu_slug="dashboard",
            menu_url="/dashboard",
            icon="dashboard",
            sort_order=1,
            is_active=True
        ),
        Menu(
            menu_name="Users",
            menu_slug="users",
            menu_url="/users",
            icon="people",
            sort_order=2,
            is_active=True
        ),
        Menu(
            menu_name="Roles",
            menu_slug="roles",
            menu_url="/roles",
            icon="security",
            sort_order=3,
            is_active=True
        ),
        Menu(
            menu_name="Menus",
            menu_slug="menus",
            menu_url="/menus",
            icon="menu",
            sort_order=4,
            is_active=True
        ),
        Menu(
            menu_name="Permissions",
            menu_slug="permissions",
            menu_url="/role-permissions",
            icon="lock",
            sort_order=5,
            is_active=True
        ),
        Menu(
            menu_name="Audit Logs",
            menu_slug="audit-logs",
            menu_url="/audit-logs",
            icon="history",
            sort_order=6,
            is_active=True
        ),
        Menu(
            menu_name="Settings",
            menu_slug="settings",
            menu_url="/settings",
            icon="settings",
            sort_order=7,
            is_active=True
        ),
    ]
    
    for menu in menus:
        existing = db.query(Menu).filter(Menu.menu_slug == menu.menu_slug).first()
        if not existing:
            db.add(menu)
    
    db.commit()
    print("✓ Menus seeded successfully")

def seed_admin_permissions(db):
    """Grant admin role full permissions to all menus and actions"""
    admin_role = db.query(Role).filter(Role.role_name == "admin").first()
    if not admin_role:
        print("✗ Admin role not found")
        return
    
    menus = db.query(Menu).all()
    actions = db.query(Action).all()
    
    for menu in menus:
        for action in actions:
            existing = db.query(RolePermission).filter(
                RolePermission.role_id == admin_role.id,
                RolePermission.menu_id == menu.id,
                RolePermission.action_id == action.id
            ).first()
            
            if not existing:
                permission = RolePermission(
                    role_id=admin_role.id,
                    menu_id=menu.id,
                    action_id=action.id
                )
                db.add(permission)
    
    db.commit()
    print("✓ Admin permissions seeded successfully")

def seed_user_permissions(db):
    """Grant user role read-only permissions to dashboard"""
    user_role = db.query(Role).filter(Role.role_name == "user").first()
    if not user_role:
        print("✗ User role not found")
        return
    
    dashboard_menu = db.query(Menu).filter(Menu.menu_slug == "dashboard").first()
    read_action = db.query(Action).filter(Action.action_name == "read").first()
    
    if dashboard_menu and read_action:
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == user_role.id,
            RolePermission.menu_id == dashboard_menu.id,
            RolePermission.action_id == read_action.id
        ).first()
        
        if not existing:
            permission = RolePermission(
                role_id=user_role.id,
                menu_id=dashboard_menu.id,
                action_id=read_action.id
            )
            db.add(permission)
            db.commit()
    
    print("✓ User permissions seeded successfully")

def seed_admin_user(db):
    """Create default admin user"""
    admin_role = db.query(Role).filter(Role.role_name == "admin").first()
    if not admin_role:
        print("✗ Admin role not found")
        return
    
    existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not existing_admin:
        admin_user = User(
            role_id=admin_role.id,
            name="System Administrator",
            email="admin@example.com",
            password=hash_password("admin123"),  # Change this password in production!
            phone="+1234567890",
            address="System",
            status=UserStatus.active,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(admin_user)
        db.commit()
        print("✓ Admin user created successfully")
        print("  Email: admin@example.com")
        print("  Password: admin123")
        print("  ⚠️  IMPORTANT: Change this password immediately in production!")
    else:
        print("✓ Admin user already exists")

def main():
    """Run all seed functions"""
    print("\n🌱 Starting database seeding...\n")
    
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_actions(db)
        seed_menus(db)
        seed_admin_permissions(db)
        seed_user_permissions(db)
        seed_admin_user(db)
        
        print("\n✅ Database seeding completed successfully!\n")
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}\n")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
