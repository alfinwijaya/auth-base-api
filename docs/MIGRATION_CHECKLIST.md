# RBAC Migration Checklist

Use this checklist to ensure a smooth migration to the new RBAC system.

## Pre-Migration

- [ ] **Backup your database** - Create a full backup before proceeding
- [ ] **Review documentation**
  - [ ] Read MIGRATION_GUIDE.md
  - [ ] Read RBAC_IMPLEMENTATION.md
  - [ ] Read PERMISSION_GUIDE.md
  - [ ] Read IMPLEMENTATION_SUMMARY.md
- [ ] **Check dependencies** - Ensure all required packages are installed
  ```bash
  pip install -r requirements.txt
  ```

## Database Preparation

- [ ] **Drop all existing tables** (as specified in requirements)
  ```sql
  -- Example for PostgreSQL
  DROP TABLE IF EXISTS password_reset_tokens CASCADE;
  DROP TABLE IF EXISTS users CASCADE;
  DROP TABLE IF EXISTS roles CASCADE;
  -- Add other tables if any
  ```

- [ ] **Verify database is empty**
  ```sql
  -- Check for remaining tables
  SELECT tablename FROM pg_tables WHERE schemaname = 'public';
  ```

## Alembic Setup

- [ ] **Initialize Alembic** (if not already done)
  ```bash
  alembic init alembic
  ```

- [ ] **Update alembic.ini**
  - [ ] Set correct `sqlalchemy.url`
  - [ ] Or ensure it's loaded from environment variables

- [ ] **Update alembic/env.py**
  - [ ] Copy the template from MIGRATION_GUIDE.md
  - [ ] Verify all models are imported
  - [ ] Verify database URL is correct

- [ ] **Test Alembic configuration**
  ```bash
  alembic current
  ```

## Create and Apply Migration

- [ ] **Create initial migration**
  ```bash
  alembic revision --autogenerate -m "Initial RBAC schema"
  ```

- [ ] **Review generated migration**
  - [ ] Check `alembic/versions/` for the new migration file
  - [ ] Verify all 7 tables are being created:
    - [ ] roles
    - [ ] users
    - [ ] menus
    - [ ] actions
    - [ ] role_permissions
    - [ ] audit_logs
    - [ ] password_reset_tokens
  - [ ] Verify foreign key constraints
  - [ ] Verify indexes

- [ ] **Apply migration**
  ```bash
  alembic upgrade head
  ```

- [ ] **Verify tables were created**
  ```sql
  -- Check all tables exist
  SELECT tablename FROM pg_tables WHERE schemaname = 'public';
  ```

## Seed Initial Data

- [ ] **Run seed script**
  ```bash
  python seed_data.py
  ```

- [ ] **Verify seeded data**
  ```sql
  -- Check roles
  SELECT * FROM roles;
  
  -- Check actions
  SELECT * FROM actions;
  
  -- Check menus
  SELECT * FROM menus;
  
  -- Check admin user
  SELECT * FROM users WHERE email = 'admin@example.com';
  
  -- Check admin permissions
  SELECT COUNT(*) FROM role_permissions WHERE role_id = 1;
  ```

## Test the Application

- [ ] **Start the application**
  ```bash
  uvicorn app.main:app --reload
  ```

- [ ] **Test authentication endpoints**
  - [ ] POST `/auth/register` with new fields
    ```json
    {
      "email": "test@example.com",
      "password": "test123",
      "name": "Test User",
      "role_id": 2,
      "phone": "+1234567890",
      "address": "Test Address"
    }
    ```
  - [ ] POST `/auth/login` with admin credentials
    ```json
    {
      "email": "admin@example.com",
      "password": "admin123"
    }
    ```
  - [ ] POST `/auth/refresh` with refresh token

- [ ] **Test user endpoints**
  - [ ] GET `/users/me` (should return full user object)
  - [ ] GET `/users/` (admin only)

- [ ] **Test role endpoints**
  - [ ] GET `/roles/` (list all roles)
  - [ ] POST `/roles/` (create new role)
  - [ ] GET `/roles/{role_id}` (get specific role)
  - [ ] PUT `/roles/{role_id}` (update role)

- [ ] **Test menu endpoints**
  - [ ] GET `/menus/` (list all menus)
  - [ ] GET `/menus/active/list` (list active menus)
  - [ ] POST `/menus/` (create new menu)

- [ ] **Test action endpoints**
  - [ ] GET `/actions/` (list all actions)
  - [ ] POST `/actions/` (create new action)

- [ ] **Test permission endpoints**
  - [ ] GET `/role-permissions/role/{role_id}` (get role permissions)
  - [ ] POST `/role-permissions/` (create permission)
  - [ ] POST `/role-permissions/bulk` (bulk create permissions)

- [ ] **Test audit log endpoints**
  - [ ] POST `/audit-logs/` (create audit log)
  - [ ] GET `/audit-logs/` (list all logs)
  - [ ] GET `/audit-logs/user/{user_id}` (get user logs)

## Security Configuration

- [ ] **Change default admin password**
  - [ ] Login as admin
  - [ ] Change password from "admin123" to a secure password
  - [ ] Document the new password securely

- [ ] **Configure environment variables**
  - [ ] Set `SECRET_KEY` to a secure random value
  - [ ] Set `DATABASE_URL` correctly
  - [ ] Set other required environment variables

- [ ] **Review permission assignments**
  - [ ] Verify admin has all permissions
  - [ ] Verify user role has appropriate limited permissions
  - [ ] Create additional roles as needed

## Frontend Integration

- [ ] **Update registration form**
  - [ ] Add "name" field (required)
  - [ ] Add "phone" field (optional)
  - [ ] Add "address" field (optional)
  - [ ] Add "role_id" field (if applicable)

- [ ] **Update user display**
  - [ ] Show user name
  - [ ] Show user status
  - [ ] Show additional fields

- [ ] **Implement permission checking**
  - [ ] Fetch user permissions on login
  - [ ] Store permissions in state/context
  - [ ] Hide/show UI elements based on permissions
  - [ ] Disable actions user doesn't have permission for

- [ ] **Add menu rendering**
  - [ ] Fetch active menus
  - [ ] Render hierarchical menu structure
  - [ ] Filter menus based on user permissions

## Production Deployment

- [ ] **Environment configuration**
  - [ ] Set production database URL
  - [ ] Set secure SECRET_KEY
  - [ ] Configure CORS settings
  - [ ] Set up SSL/TLS

- [ ] **Database backup strategy**
  - [ ] Set up automated backups
  - [ ] Test backup restoration
  - [ ] Document backup procedures

- [ ] **Monitoring setup**
  - [ ] Set up application monitoring
  - [ ] Set up database monitoring
  - [ ] Configure audit log retention policy

- [ ] **Security hardening**
  - [ ] Review and update all default passwords
  - [ ] Enable rate limiting
  - [ ] Configure security headers
  - [ ] Set up intrusion detection

## Documentation

- [ ] **Update API documentation**
  - [ ] Document new endpoints
  - [ ] Update request/response examples
  - [ ] Document breaking changes

- [ ] **Create user guides**
  - [ ] Admin guide for managing roles and permissions
  - [ ] User guide for new features
  - [ ] Developer guide for extending the system

- [ ] **Document custom configurations**
  - [ ] Custom roles created
  - [ ] Custom actions created
  - [ ] Custom menus created
  - [ ] Permission assignments

## Post-Migration Validation

- [ ] **Functional testing**
  - [ ] Test all CRUD operations
  - [ ] Test permission checking
  - [ ] Test audit logging
  - [ ] Test user status changes

- [ ] **Performance testing**
  - [ ] Test with multiple concurrent users
  - [ ] Check query performance
  - [ ] Verify index usage

- [ ] **Security testing**
  - [ ] Test permission bypass attempts
  - [ ] Test SQL injection protection
  - [ ] Test XSS protection
  - [ ] Test authentication bypass attempts

## Rollback Plan (If Needed)

- [ ] **Prepare rollback procedure**
  - [ ] Document steps to restore old schema
  - [ ] Keep backup of old codebase
  - [ ] Keep database backup

- [ ] **Test rollback procedure**
  - [ ] Test on staging environment
  - [ ] Document any issues
  - [ ] Update rollback documentation

## Final Steps

- [ ] **Team training**
  - [ ] Train team on new RBAC system
  - [ ] Explain permission model
  - [ ] Demonstrate admin features

- [ ] **User communication**
  - [ ] Notify users of new features
  - [ ] Provide user documentation
  - [ ] Set up support channels

- [ ] **Monitoring and maintenance**
  - [ ] Monitor error logs
  - [ ] Monitor audit logs
  - [ ] Set up alerts for issues
  - [ ] Schedule regular reviews

## Troubleshooting

### Common Issues

**Issue: Migration fails with foreign key error**
- Solution: Ensure all tables are dropped before migration
- Check: `alembic/env.py` has correct model imports

**Issue: Seed script fails**
- Solution: Ensure migration was successful
- Check: All tables exist in database
- Check: Database connection is working

**Issue: Permission checking not working**
- Solution: Verify role_permissions table has data
- Check: User has correct role_id
- Check: Menu and action IDs are correct

**Issue: Import errors**
- Solution: Ensure all dependencies are installed
- Check: Python path is correct
- Check: Virtual environment is activated

## Support Resources

- MIGRATION_GUIDE.md - Detailed migration instructions
- RBAC_IMPLEMENTATION.md - Implementation details
- PERMISSION_GUIDE.md - Permission system guide
- IMPLEMENTATION_SUMMARY.md - Overview of changes

## Sign-off

- [ ] **Development team sign-off**
  - [ ] Code review completed
  - [ ] Testing completed
  - [ ] Documentation reviewed

- [ ] **QA team sign-off**
  - [ ] All tests passed
  - [ ] Security review completed
  - [ ] Performance acceptable

- [ ] **Product owner sign-off**
  - [ ] Features meet requirements
  - [ ] Ready for production

---

**Migration Date:** _______________
**Completed By:** _______________
**Verified By:** _______________
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Completed | ⬜ Rolled Back
