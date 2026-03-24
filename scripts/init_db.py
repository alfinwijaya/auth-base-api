from app.db.session import SessionLocal
from app.models.role import Role

def init_roles():
    db = SessionLocal()

    roles = ["admin", "user"]

    for r in roles:
        existing = db.query(Role).filter(Role.name == r).first()
        if not existing:
            db.add(Role(name=r))

    db.commit()
    db.close()


if __name__ == "__main__":
    init_roles()