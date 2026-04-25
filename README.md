# 🚀 AuthBase API

A concise FastAPI-based authentication template with JWTs, role-based access control, password reset support, and migrations.

---

## ✨ Features

- JWT access + refresh tokens
- Role-based access (admin / user)
- Password reset via token + email
- Alembic migrations
- SlowAPI rate limiting
- Docker-compose support

---

## Project layout

```
auth-base-api/
├── app/                  # application package
│   ├── api/              # routes & dependencies
│   ├── core/             # config & security
│   ├── crud/             # DB operations
│   ├── db/               # session & base models
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── main.py           # FastAPI app
├── alembic/              # migrations
├── scripts/              # helper scripts (init_db, create_admin)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
```

---

## Setup

1. Clone:

```sh
git clone https://github.com/YOUR_USERNAME/auth-base-api.git
cd auth-base-api
```

2. Create virtualenv & activate

Windows (PowerShell):

```ps1
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

3. Install deps

```sh
pip install -r requirements.txt
```

---

## Environment

Create a `.env` file (see `.env.example`). Key names used by the code:

```
DB_TYPE=postgres
POSTGRES_DB_URL=postgresql://user:pass@host:port/dbname
MYSQL_DB_URL=mysql+pymysql://user:pass@host:port/dbname
SECRET_KEY=change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# SMTP for password reset emails
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user
SMTP_PASSWORD=pass
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_USE_TLS=true
```

The app selects `POSTGRES_DB_URL` or `MYSQL_DB_URL` depending on `DB_TYPE`.

---

## Database

Run migrations:

```sh
alembic upgrade head
```

Initialize roles and create an admin user:

```sh
python -m scripts.init_db
python -m scripts.create_admin
```

---

## Run (development)

```sh
uvicorn app.main:app --reload
```

API docs:

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## Important endpoints

Auth (prefix `/auth`):

- `POST /auth/register` — register (body: `email`, `password`)
- `POST /auth/login` — login (returns `access_token` and `refresh_token`; rate-limited `5/minute`)
- `POST /auth/refresh` — refresh tokens (body: `refresh_token`)
- `POST /auth/forgot-password` — request password reset (body: `email`)
- `POST /auth/reset-password` — reset password (body: `token`, `new_password`)

Users (prefix `/users`):

- `GET /users/me` — return current user (requires `Authorization: Bearer <token>`)
- `GET /users/` — admin only: list users
- `DELETE /users/{user_id}` — admin only: delete user

---

## Notes

- Login endpoint uses SlowAPI limiter (`5/minute`).
- Password reset sends emails via SMTP; ensure SMTP env vars are configured for that to work.
- Configuration is read via `pydantic-settings` from `.env`.

---

## Tech stack

- FastAPI
- SQLAlchemy
- Alembic
- SlowAPI
- Python-JOSE (JWT)

---

Author: template for learning and small projects.
