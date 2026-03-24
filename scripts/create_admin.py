from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.utils.hash import hash_password

def create_admin():
    db = SessionLocal()

    try:
        role = db.query(Role).filter(Role.name == "admin").first()

        user = User(
            email="admin@mail.com",
            password=hash_password("admin123"),
            role=role
        )

        db.add(user)
        db.commit()
        print("✅ Admin created")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()