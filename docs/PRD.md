# Product Requirements Document
## Role-Based Access Control (RBAC) System
**Version:** 1.0 | **Date:** July 2026 | **Status:** Approved

---

| Field | Value | Field | Value |
|---|---|---|---|
| Document Owner | Product Team | Version | 1.0 |
| Status | Approved | Date | July 2026 |
| Reviewers | Engineering, Design, QA | Priority | High |

---

## 1. Executive Summary

This document defines the product requirements for the Role-Based Access Control (RBAC) system that manages users, roles, permissions, menus, and actions within the application. The system enforces access boundaries, providing a granular, auditable, and scalable security model.

The RBAC system is a core infrastructure module. Every feature of the application depends on it for authentication boundaries and authorization rules. This PRD covers the database schema, functional requirements, business rules, and acceptance criteria for the implementation.

---

## 2. Background & Problem Statement

Organizations managing multiple users across different departments need a principled way to control access to application features. Without structured access control:

- Users may access data or functionality outside their authority.
- Security audits are impossible without centralized logging.
- Onboarding and offboarding users is slow and error-prone.
- Feature rollouts cannot be limited to specific user segments.

The RBAC system addresses these problems by associating each user with a role, and each role with fine-grained permissions over specific menus and actions. Every sensitive action is logged in an immutable audit trail.

---

## 3. Goals & Non-Goals

### 3.1 Goals

- Assign users to roles and enforce access through role permissions.
- Define hierarchical menus and associate them with allowable actions per role.
- Log all user activity (module, action, IP, user agent) in an immutable audit trail.
- Support soft activation/deactivation of users without deleting records (via `status` field supporting `active`, `inactive`, and `suspended`).
- Provide a self-referential menu structure supporting nesting hierarchy.
- Provide bulk operations to assign multiple permissions at once.
- Provide password reset capability using secure reset tokens.

### 3.2 Non-Goals

- **Multi-tenancy** – the current design assumes a single-tenant deployment.
- **OAuth / SSO integration** – out of scope for the current phase.
- **Row-level security (RLS)** – permissions govern menus and actions, not individual data rows.
- **Real-time permission sync without token regeneration** – cache invalidation strategy is a backend concern.

---

## 4. User Stories

| ID | Story | Acceptance Criteria |
|---|---|---|
| 1 | As an Admin, I can create a role with a name and description so that I can group users by their function. | Role is saved; `role_name` is unique; timestamps are auto-set. |
| 2 | As an Admin, I can assign a role to a user so that permissions are inherited automatically. | User record shows `role_id` FK; changing role takes effect when a new access token is generated. |
| 3 | As an Admin, I can activate, deactivate, or suspend a user without deleting their record. | Status enum updated (`active`, `inactive`, `suspended`); non-active users cannot log in or refresh tokens. |
| 4 | As an Admin, I can define hierarchical menus with parent-child relationships. | `parent_id` self-reference is enforced. |
| 5 | As an Admin, I can grant a role access to a specific menu and action pair. | `role_permissions` row created; duplicate triplets are rejected. |
| 6 | As a Developer, I can query all permitted menus for a given role. | JOIN across roles, menus, actions returns the correct permission set. |
| 7 | As an Auditor, I can review all actions taken by a specific user including IP and browser details. | `audit_logs` can be filtered by user, module, or date range; no records can be deleted or updated. |

---

## 5. Database Schema

The schema consists of seven tables implementing the full RBAC, user, and security model.

### 5.1 `roles`

Stores the named roles available in the system.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_name | VARCHAR(100) | NOT NULL, UNIQUE | Human-readable role label (e.g. admin, user) |
| description | VARCHAR(255) | NULLABLE | Optional explanation of the role's purpose |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.2 `users`

Stores all user accounts. Each user belongs to exactly one role.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_id | INT | FK → roles.id, NOT NULL | The role assigned to this user |
| name | VARCHAR(255) | NOT NULL | Full display name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Login identifier; must be valid email format |
| password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| phone | VARCHAR(20) | NULLABLE | Contact phone number |
| address | TEXT | NULLABLE | Physical address details |
| status | ENUM('active','inactive','suspended') | NOT NULL, DEFAULT 'active' | Account state |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.3 `menus`

Defines the application's navigation hierarchy. A menu item may reference a parent in the same table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| parent_id | INT | FK → menus.id, NULLABLE | NULL = top-level menu |
| menu_name | VARCHAR(100) | NOT NULL | Display label shown in the UI |
| menu_slug | VARCHAR(100) | NOT NULL, UNIQUE | URL-safe identifier used in API routes |
| menu_url | VARCHAR(255) | NULLABLE | Path the item links to |
| icon | VARCHAR(100) | NULLABLE | Icon class or asset reference for UI rendering |
| sort_order | INT | NOT NULL, DEFAULT 0 | Sort order within the same parent |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Hidden from navigation when FALSE |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.4 `actions`

Enumerates the atomic operations that can be performed within a menu (e.g. create, read, update, delete).

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| action_name | VARCHAR(100) | NOT NULL, UNIQUE | Canonical name (e.g. 'create', 'read', 'update', 'delete') |
| description | VARCHAR(255) | NULLABLE | Plain-language explanation of the action |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |

### 5.5 `role_permissions`

The pivot table linking a role to a menu-action pair.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_id | INT | FK → roles.id, NOT NULL | The role being granted permission |
| menu_id | INT | FK → menus.id, NOT NULL | The menu the permission applies to |
| action_id | INT | FK → actions.id, NOT NULL | The action being permitted |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | When the permission was granted |

### 5.6 `audit_logs`

Append-only table recording every significant user action.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| user_id | INT | FK → users.id, NOT NULL | The actor performing the logged action |
| module | VARCHAR(100) | NOT NULL | Application module name (e.g. 'auth', 'user') |
| activity | TEXT | NOT NULL | Detailed description of what was done |
| ip_address | VARCHAR(45) | NULLABLE | IPv4 or IPv6 address of the client |
| user_agent | VARCHAR(255) | NULLABLE | Browser or client User-Agent header |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Timestamp the event was recorded |

### 5.7 `password_reset_tokens`

Stores secure temporary tokens for password reset operations.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| email | VARCHAR(255) | NOT NULL | The recipient email address |
| token | VARCHAR(255) | NOT NULL, UNIQUE | The cryptographically secure token |
| expires_at | DATETIME | NOT NULL | Token expiration timestamp |
| is_used | BOOLEAN | NOT NULL, DEFAULT FALSE | State flag preventing token reuse |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |

---

## 6. Functional Requirements

### 6.1 Role Management
- The system allows creating, reading, updating, and deleting roles.
- `role_name` must be unique across the system.
- Standard roles include `admin` and `user`.

### 6.2 User Management & Authentication
- Users are assigned exactly one role. JWT access tokens embed the user's role claim.
- Refreshing an access token preserves the user's role claim.
- User status must be `active`, `inactive`, or `suspended`. Non-active users are barred from logging in or refreshing tokens.
- Passwords must be hashed using bcrypt before persistence.
- Registrations require email format validation, password validation, and a name.

### 6.3 Menu & Action Management
- Menus support self-referential relationships through `parent_id`.
- The active menu list returns only active menus (`is_active = true`) sorted by `sort_order` in ascending order.
- Action names are unique.

### 6.4 Permission Management
- Access checks are based on a three-dimensional mapping: **Role × Menu × Action**.
- Endpoints allow bulk permission creation (`POST /role-permissions/bulk`) to map multiple sets in a single transaction.
- Query endpoints support looking up permissions by a specific role or menu.

### 6.5 Audit Logging
- Audit logs capture state-changing operations and security events.
- Client metadata such as `ip_address` and `user_agent` are parsed and stored.
- Audit logs can be queried by date ranges, user ID, or module.
- Mutating operations (PUT, PATCH, DELETE) are explicitly forbidden on audit logs.

---

## 7. Non-Functional Requirements

- **Security:** SQL injection mitigation through ORM parameterization. All passwords stored as bcrypt hashes.
- **Maintainability:** All database updates applied using Alembic migration version control.
- **Data Integrity:** Database foreign keys and unique constraints are strictly enforced at the database schema engine level.

---

## 8. Acceptance Criteria

1. All seven tables are verified to exist with correct column mappings and relationships.
2. Unique constraints are verified on `roles.role_name`, `users.email`, `menus.menu_slug`, `actions.action_name`, `password_reset_tokens.token`, and the triplet `(role_id, menu_id, action_id)` in `role_permissions`.
3. Inactive or suspended users cannot successfully authenticate or refresh access tokens.
4. Mutation attempts on audit logs via the API must be rejected.
5. All tests run and pass without errors.
