# Quick Start & Migration Guide

This guide will help you install, configure, migrate, seed, and run the FastAPI AuthBase API.

---

## 1. Quick Setup (Local Run)

### Prerequisites
* Python 3.8+ installed.
* Database engine (PostgreSQL, MySQL, or SQLite).
* Virtual environment utility (`venv`).

### Setup Steps
1. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file at the root of the project using the following template:
   ```env
   DB_TYPE=postgres
   POSTGRES_DB_URL=postgresql://user:password@localhost:5432/dbname
   MYSQL_DB_URL=mysql+pymysql://user:password@localhost:3306/dbname
   SECRET_KEY=generate-a-secure-random-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   REFRESH_TOKEN_EXPIRE_DAYS=7

   # SMTP Configuration (For Password Reset)
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   SMTP_USERNAME=smtp-user
   SMTP_PASSWORD=smtp-pass
   SMTP_FROM_EMAIL=noreply@example.com
   SMTP_USE_TLS=true
   ```

---

## 2. Database Migrations (Alembic)

The codebase consolidates all tables into a unified Alembic migration script. Follow these steps to build the schema:

1. **Clear Legacy Tables (If present):**
   * **PostgreSQL:** `DROP SCHEMA public CASCADE; CREATE SCHEMA public;`
   * **MySQL:** `DROP DATABASE dbname; CREATE DATABASE dbname;`
   * **SQLite:** Remove the SQLite database file if migrating locally to standard SQLite.

2. **Run Schema Migration:**
   Apply the migrations to build the tables:
   ```bash
   alembic upgrade head
   ```

---

## 3. Database Seeding

After applying the migrations, run the seeding script to populate the initial roles, menus, actions, permissions, and create the default admin account:

```bash
python scripts/seed_data.py
```

### Seed Data Reference
* **Roles:**
  * `admin` (id: 1) - Full CRUD permissions.
  * `user` (id: 2) - Read-only dashboard permissions.
* **Actions:**
  * `create` (id: 1), `read` (id: 2), `update` (id: 3), `delete` (id: 4).
* **Menus:**
  * `Dashboard` (id: 1), `Users` (id: 2), `Roles` (id: 3), `Menus` (id: 4), `Permissions` (id: 5), `Audit Logs` (id: 6), `Settings` (id: 7).
* **Default Credentials:**
  * **Email:** `admin@example.com`
  * **Password:** `Admin@1234!`
  * ⚠️ *Change these credentials immediately after setup.*

---

## 4. Run the API

Start the local server using Uvicorn:
```bash
uvicorn app.main:app --reload
```

* **Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 5. API Endpoint Summary

### Auth Services (`/auth`)
* `POST /auth/register` - Registers a user. Requires `email`, `password`, `name`.
* `POST /auth/login` - Performs authentication. Returns Access & Refresh tokens.
* `POST /auth/refresh` - Validates Refresh token, returning a new Access token.
* `POST /auth/forgot-password` - Sends password reset link.
* `POST /auth/reset-password` - Resets password with valid token.

### User Services (`/users`)
* `GET /users/me` - Profile information of current logged-in user.
* `GET /users` - Lists all users (Admin only).
* `DELETE /users/{user_id}` - Deletes a user (Admin only).

### RBAC Management (Admin Only)
* **Roles (`/roles`):** GET (list, retrieve), POST (create), PUT (update), DELETE (remove).
* **Menus (`/menus`):** GET (list, active tree retrieval), POST (create), PUT (update), DELETE (remove).
* **Actions (`/actions`):** GET (list), POST (create), PUT (update), DELETE (remove).
* **Role Permissions (`/role-permissions`):**
  * `POST /role-permissions` - Maps custom action.
  * `POST /role-permissions/bulk` - Assigns multiple permission sets.
  * `GET /role-permissions/role/{role_id}` - Retrieve permissions matching a role.
  * `DELETE /role-permissions/{permission_id}` - Delete mapping.

### Compliance & Auditing (`/audit-logs`)
* `GET /audit-logs` - Query logs (supports filters for `user_id`, `module`, `date-range`).
