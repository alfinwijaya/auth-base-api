# Product Requirements Document
## Role-Based Access Control (RBAC) System
**Version:** 1.0 | **Date:** May 2026 | **Status:** Draft

---

| Field | Value | Field | Value |
|---|---|---|---|
| Document Owner | Product Team | Version | 1.0 |
| Status | Draft | Date | May 2026 |
| Reviewers | Engineering, Design, QA | Priority | High |

---

## 1. Executive Summary

This document defines the product requirements for a Role-Based Access Control (RBAC) system that manages users, roles, permissions, menus, and actions within an enterprise application. The system enforces who can access what, providing a granular, auditable, and scalable security model.

The RBAC system is a core infrastructure module. Every feature of the application depends on it for authentication boundaries and authorization rules. This PRD covers the database schema, functional requirements, business rules, and acceptance criteria for the initial release.

---

## 2. Background & Problem Statement

Organizations managing multiple users across different departments need a principled way to control access to application features. Without structured access control:

- Users may access data or functionality outside their authority
- Security audits become impossible without centralized logging
- Onboarding and offboarding users is slow and error-prone
- Feature rollouts cannot be limited to specific user segments

The RBAC system addresses these problems by associating each user with a role, and each role with fine-grained permissions over specific menus and actions. Every sensitive action is logged in a tamper-evident audit trail.

---

## 3. Goals & Non-Goals

### 3.1 Goals

- Assign users to roles and enforce access through role permissions
- Define hierarchical menus and associate them with allowable actions per role
- Log all user activity (module, action, IP, user agent) in an immutable audit trail
- Support soft activation/deactivation of users without deleting records
- Provide a self-referential menu structure supporting infinite nesting depth

### 3.2 Non-Goals

- **Multi-tenancy** – the current design assumes a single-tenant deployment
- **OAuth / SSO integration** – out of scope for v1; treated as future enhancement
- **Row-level security (RLS)** – permissions govern menus and actions, not individual data rows
- **Real-time permission sync without re-login** – cache invalidation strategy is a backend concern

---

## 4. User Stories

| ID | Story | Acceptance Criteria |
|---|---|---|
| US-01 | As an Admin, I can create a role with a name and description so that I can group users by their function. | Role is saved; name is unique; timestamps auto-set. |
| US-02 | As an Admin, I can assign a role to a user so that permissions are inherited automatically. | User record shows role_id FK; changing role takes effect on next login. |
| US-03 | As an Admin, I can activate or deactivate a user without deleting their record. | Status enum updated; deactivated user cannot log in. |
| US-04 | As an Admin, I can define hierarchical menus with parent-child relationships. | parent_id self-reference enforced; circular references rejected. |
| US-05 | As an Admin, I can grant a role access to a specific menu and action pair. | role_permissions row created; duplicate triplets rejected. |
| US-06 | As a Developer, I can query all permitted menus for a given role. | Efficient JOIN across roles, menus, actions returns correct set. |
| US-07 | As an Auditor, I can review all actions taken by a specific user including IP and browser details. | audit_logs filtered by user_id; no records can be deleted via API. |

---

## 5. Database Schema

The schema consists of six tables implementing the full RBAC + audit model. Each table is described below.

### 5.1 `roles`

Stores the named roles available in the system. Each role groups one or more users and is associated with a set of permissions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_name | VARCHAR(100) | NOT NULL, UNIQUE | Human-readable role label (e.g. Admin, Staff) |
| description | TEXT | NULLABLE | Optional explanation of the role's purpose |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.2 `users`

Stores all user accounts. Each user belongs to exactly one role, inherited at login for permission resolution.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_id | INT | FK → roles.id, NOT NULL | The role assigned to this user |
| name | VARCHAR(200) | NOT NULL | Full display name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Login identifier; must be valid email format |
| password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password; never stored plain |
| phone | VARCHAR(30) | NULLABLE | Contact phone number |
| address | TEXT | NULLABLE | Mailing or billing address |
| status | ENUM('active','inactive') | NOT NULL, DEFAULT 'active' | Account state; inactive users cannot authenticate |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.3 `menus`

Defines the application's navigation hierarchy. A menu item may reference a parent in the same table, enabling unlimited nesting.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| parent_id | INT | FK → menus.id, NULLABLE | NULL = top-level menu; otherwise the parent item |
| menu_name | VARCHAR(150) | NOT NULL | Display label shown in the UI |
| menu_slug | VARCHAR(150) | NOT NULL, UNIQUE | URL-safe identifier used in API routes |
| menu_url | VARCHAR(500) | NULLABLE | Absolute or relative path the item links to |
| icon | VARCHAR(100) | NULLABLE | Icon class or asset reference for sidebar rendering |
| sort_order | INT | NOT NULL, DEFAULT 0 | Ascending sort order within the same parent |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Hidden from navigation when FALSE |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| updated_at | DATETIME | NOT NULL, ON UPDATE NOW() | Last modification timestamp |

### 5.4 `actions`

Enumerates the atomic operations that can be performed within a menu (e.g. View, Create, Edit, Delete, Export). Actions have no `updated_at` since they are managed by the system, not users.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| action_name | VARCHAR(100) | NOT NULL, UNIQUE | Canonical name (e.g. 'view', 'create', 'delete') |
| description | TEXT | NULLABLE | Plain-language explanation of the action |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Record creation timestamp |

### 5.5 `role_permissions`

The pivot table linking a role to a menu-action pair. A single row grants the role permission to perform the given action on the given menu.

> **Business rule:** The combination `(role_id, menu_id, action_id)` must have a UNIQUE constraint to prevent duplicate grants.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| role_id | INT | FK → roles.id, NOT NULL | The role being granted permission |
| menu_id | INT | FK → menus.id, NOT NULL | The menu the permission applies to |
| action_id | INT | FK → actions.id, NOT NULL | The action being permitted |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | When the permission was granted |

### 5.6 `audit_logs`

Append-only table recording every significant user action. No records may be deleted or updated via the application API.

| Column | Type | Constraints | Description |
|---|---|---|---|
| id | INT | PK, AUTO_INCREMENT | Surrogate primary key |
| user_id | INT | FK → users.id, NOT NULL | The actor performing the logged action |
| module | VARCHAR(150) | NOT NULL | Application module name (e.g. 'Users', 'Reports') |
| activity | VARCHAR(500) | NOT NULL | Human-readable description of what was done |
| ip_address | VARCHAR(45) | NOT NULL | IPv4 or IPv6 address of the client |
| user_agent | TEXT | NULLABLE | Browser or client User-Agent header |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | Timestamp the event was recorded |

---

## 6. Functional Requirements

### 6.1 Role Management

- The system must allow creating, reading, updating, and soft-deleting roles.
- `role_name` must be unique across the system; duplicate names must be rejected with a 422 error.
- A role cannot be deleted while users are assigned to it.

### 6.2 User Management

- Users are assigned exactly one role; role changes take effect on the user's next authenticated session.
- User `status` must be either `'active'` or `'inactive'`. Inactive users are rejected at login without revealing the reason to the client.
- Passwords must be hashed using bcrypt (cost factor >= 12) before persistence.
- Email addresses must be validated for format and uniqueness at the database and API layer.

### 6.3 Menu Management

- Menus support arbitrary nesting via the `parent_id` self-reference. The UI must render up to four levels of nesting; deeper levels are collapsed by default.
- Circular parent references (e.g. A → B → A) must be rejected at the API layer.
- `sort_order` within a parent group determines display sequence; ties are broken alphabetically by `menu_name`.
- `is_active = FALSE` hides the item from navigation but does not cascade to children automatically.

### 6.4 Permission Management

- A permission grant requires a valid `(role_id, menu_id, action_id)` triplet with no nulls.
- Duplicate grants must be silently ignored (upsert semantics) or rejected with a 409 conflict.
- Revoking a permission deletes the `role_permissions` row; affected users lose access on next request.
- An API endpoint `GET /roles/{id}/permissions` must return all menus and actions for the role, structured hierarchically by menu parent.

### 6.5 Audit Logging

- Every state-changing API call (POST, PUT, PATCH, DELETE) must produce an `audit_logs` record before the response is returned.
- The IP address must be extracted from `X-Forwarded-For` or `REMOTE_ADDR`; both IPv4 and IPv6 formats must be supported (up to 45 characters).
- The audit log API must support filtering by `user_id`, `module`, date range, and keyword search on `activity`.
- No DELETE or UPDATE endpoint may exist for `audit_logs`.

---

## 7. Non-Functional Requirements

| Category | Metric | Requirement |
|---|---|---|
| Performance | Permission check latency | < 50 ms at p95 under 500 concurrent users |
| Performance | Audit log write | Async or < 20 ms; must not block the main request |
| Scalability | User records | Support >= 100,000 users without index degradation |
| Security | Password storage | bcrypt, cost >= 12; no plain-text or MD5/SHA1 hashes |
| Security | SQL injection | All queries use parameterized statements or ORM |
| Availability | Uptime | 99.5% monthly SLA excluding scheduled maintenance |
| Maintainability | Migration | All schema changes delivered as versioned migration files |
| Compliance | Data retention | Audit logs retained for minimum 2 years; GDPR-compatible |

---

## 8. Entity Relationship Summary

| From | Cardinality | To | Description |
|---|---|---|---|
| roles | 1 → N | users | One role is assigned to many users |
| roles | 1 → N | role_permissions | One role may have many permission grants |
| menus | 1 → N | role_permissions | One menu appears in many permission grants |
| actions | 1 → N | role_permissions | One action appears in many permission grants |
| menus | 1 → N | menus (self) | A menu item may contain many child menu items |
| users | 1 → N | audit_logs | One user generates many audit log entries |

---

## 9. Acceptance Criteria

1. All six tables are created with the specified columns, types, and constraints.
2. Unique constraints are enforced on: `roles.role_name`, `users.email`, `menus.menu_slug`, `actions.action_name`, and the triplet `(role_id, menu_id, action_id)` in `role_permissions`.
3. Foreign key constraints are enforced by the database engine, not only at the application layer.
4. A user with `status='inactive'` cannot obtain an authentication token.
5. Deleting or updating an `audit_log` record via the API returns HTTP 405.
6. A role assigned to one or more users cannot be deleted; the API returns HTTP 409.
7. The permission resolution query for a role returns results within 50 ms under load test conditions.
8. All state-changing operations produce an `audit_logs` record with a non-null `ip_address`.

---

## 10. Open Questions & Decisions

| # | Question | Owner / ETA |
|---|---|---|
| Q1 | Should role assignment be multi-role (many-to-many users-roles) in a future version? | Product Lead – Sprint 3 |
| Q2 | Is column-level permission granularity needed, or is menu+action sufficient? | Architect – Sprint 2 |
| Q3 | How should permission changes propagate to active sessions (invalidate JWT, or lazy re-check)? | Backend Lead – Sprint 2 |
| Q4 | Should audit_logs be written to a separate database or data lake for long-term retention? | DevOps – Sprint 4 |

---

## 11. Out of Scope (v1)

- OAuth 2.0 / OpenID Connect integration
- Single Sign-On (SAML / LDAP)
- Multi-tenant isolation (separate schemas or databases)
- Row-level data security per user
- Real-time WebSocket permission sync
- Self-service user registration without admin approval

---

## 12. Revision History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0 | May 2026 | Product Team | Initial draft based on RBAC schema |
