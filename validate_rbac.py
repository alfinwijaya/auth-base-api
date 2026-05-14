"""
Validation script to check if all models and imports are working correctly
Run this before running migrations to catch any import or syntax errors
"""

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test model imports
        from app.models.user import User, UserStatus
        from app.models.role import Role
        from app.models.menu import Menu
        from app.models.action import Action
        from app.models.role_permission import RolePermission
        from app.models.audit_log import AuditLog
        from app.models.password_reset import PasswordResetToken
        print("✓ All models imported successfully")
        
        # Test schema imports
        from app.schemas.user import UserCreate, UserUpdate, UserOut, UserStatusEnum
        from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
        from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse
        from app.schemas.action import ActionCreate, ActionUpdate, ActionResponse
        from app.schemas.role_permission import RolePermissionCreate, RolePermissionResponse
        from app.schemas.audit_log import AuditLogCreate, AuditLogResponse
        print("✓ All schemas imported successfully")
        
        # Test service imports
        from app.services.user_service import get_all_users_service, delete_user_service
        from app.services.auth_service import register_user, login_user, refresh_access_token
        from app.services.role_service import RoleService
        from app.services.menu_service import MenuService
        from app.services.action_service import ActionService
        from app.services.role_permission_service import RolePermissionService
        from app.services.audit_log_service import AuditLogService
        print("✓ All services imported successfully")
        
        # Test route imports
        from app.api.routes import auth, user, role, menu, action, role_permission, audit_log
        print("✓ All routes imported successfully")
        
        # Test deps imports
        from app.api.deps import get_db, get_current_user, require_role, require_permission
        print("✓ All dependencies imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_model_relationships():
    """Test if model relationships are properly defined"""
    print("\nTesting model relationships...")
    
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.menu import Menu
        from app.models.action import Action
        from app.models.role_permission import RolePermission
        from app.models.audit_log import AuditLog
        
        # Check if relationships exist
        assert hasattr(User, 'role'), "User should have 'role' relationship"
        assert hasattr(User, 'audit_logs'), "User should have 'audit_logs' relationship"
        assert hasattr(Role, 'users'), "Role should have 'users' relationship"
        assert hasattr(Role, 'role_permissions'), "Role should have 'role_permissions' relationship"
        assert hasattr(Menu, 'parent'), "Menu should have 'parent' relationship"
        assert hasattr(Menu, 'role_permissions'), "Menu should have 'role_permissions' relationship"
        assert hasattr(Action, 'role_permissions'), "Action should have 'role_permissions' relationship"
        assert hasattr(RolePermission, 'role'), "RolePermission should have 'role' relationship"
        assert hasattr(RolePermission, 'menu'), "RolePermission should have 'menu' relationship"
        assert hasattr(RolePermission, 'action'), "RolePermission should have 'action' relationship"
        assert hasattr(AuditLog, 'user'), "AuditLog should have 'user' relationship"
        
        print("✓ All model relationships are properly defined")
        return True
        
    except AssertionError as e:
        print(f"✗ Relationship error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_enum_definitions():
    """Test if enums are properly defined"""
    print("\nTesting enum definitions...")
    
    try:
        from app.models.user import UserStatus
        from app.schemas.user import UserStatusEnum
        
        # Check UserStatus enum
        assert hasattr(UserStatus, 'active'), "UserStatus should have 'active' value"
        assert hasattr(UserStatus, 'inactive'), "UserStatus should have 'inactive' value"
        assert hasattr(UserStatus, 'suspended'), "UserStatus should have 'suspended' value"
        
        # Check UserStatusEnum
        assert hasattr(UserStatusEnum, 'active'), "UserStatusEnum should have 'active' value"
        assert hasattr(UserStatusEnum, 'inactive'), "UserStatusEnum should have 'inactive' value"
        assert hasattr(UserStatusEnum, 'suspended'), "UserStatusEnum should have 'suspended' value"
        
        print("✓ All enums are properly defined")
        return True
        
    except AssertionError as e:
        print(f"✗ Enum error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_main_app():
    """Test if main app can be imported"""
    print("\nTesting main application...")
    
    try:
        from app.main import app
        
        # Check if all routers are included
        routes = [route.path for route in app.routes]
        
        print(f"✓ Main application imported successfully")
        print(f"  Total routes registered: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Main app error: {str(e)}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("RBAC System Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Model Relationships", test_model_relationships()))
    results.append(("Enum Definitions", test_enum_definitions()))
    results.append(("Main Application", test_main_app()))
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All validation tests passed!")
        print("You can now proceed with database migrations.")
    else:
        print("❌ Some validation tests failed!")
        print("Please fix the errors before proceeding with migrations.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
