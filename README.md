# 🚀 AuthBase API

A reusable **FastAPI backend template** featuring JWT authentication, role-based access control, and production-ready structure.

---

## ✨ Features

- 🔐 JWT Authentication (Access + Refresh Token)
- 👤 Role-Based Access Control (Admin / User)
- 🧠 Clean Architecture (CRUD, schemas, dependencies)
- 🗃️ PostgreSQL + SQLAlchemy
- 🔄 Alembic Migrations
- 🚦 Rate Limiting (SlowAPI)
- 🐳 Docker Support
- ⚙️ Environment-based configuration

---

## 📂 Project Structure

```
auth-base-api/
├── app/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── alembic/
├── scripts/
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
```

---

## ⚙️ Setup

### 1. Clone Repository

```
git clone https://github.com/YOUR_USERNAME/auth-base-api.git
cd auth-base-api
```

---

### 2. Create Virtual Environment

Windows:
```
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```
pip install -r requirements.txt
```

---

## 🔧 Environment Variables

Create a `.env` file from `.env.example`

```
DATABASE_URL=postgresql://username:password@ep-abc123.us-east-1.aws.neon.tech/dbname?sslmode=require
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🗃️ Database Setup

### Run Migrations

```
alembic upgrade head
```

### Initialize Roles

```
python -m scripts.init_db
```

### Create Admin User

```
python -m scripts.create_admin
```

---

## ▶️ Run Server

```
uvicorn app.main:app --reload
```

---

## 📄 API Documentation

- Swagger UI → http://127.0.0.1:8000/docs  
- ReDoc → http://127.0.0.1:8000/redoc  

---

## 🔐 Authentication Flow

1. Register user → `/auth/register`
2. Login → `/auth/login`
3. Get `access_token`
4. Use token:

```
Authorization: Bearer <your_token>
```

---

## 🧪 Example Protected Route

```
GET /users/me
```

Requires valid JWT token.

---

## 🐳 Docker (Optional)

```
docker-compose up --build
```

---

## 🧠 Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Passlib (bcrypt)
- Python-JOSE
- SlowAPI

---

## 📌 Notes

- `.env` is ignored for security
- Use `.env.example` as template
- Do NOT expose secrets publicly

---

## 🚀 Future Improvements

- Email verification
- Password reset flow
- Token blacklist / logout
- Role & permission system
- Deployment (Railway / AWS)

---

## 👨‍💻 Author

Built as a backend template for learning and scaling projects.

---

## ⭐ If you find this useful

Give it a ⭐ on GitHub!
