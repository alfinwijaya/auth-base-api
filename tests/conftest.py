"""
Core pytest fixtures for the AuthBase API test suite.

Provides an in-memory SQLite database, a FastAPI TestClient with the get_db
dependency overridden, seed roles, and (for RBAC tests) admin/regular user
fixtures with pre-generated JWT tokens.

Validates: Requirements 7.1, 8.1
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

from app.db.base import Base
# Import all models so every table is registered with Base.metadata before
# create_all runs.  The __init__.py re-exports every model class.
import app.models  # noqa: F401

from app.models.role import Role
from app.models.user import User
from app.api.deps import get_db
from app.main import app
from app.core.security import create_access_token
from app.utils.hash import hash_password


# ---------------------------------------------------------------------------
# In-memory SQLite engine — shared across the whole test session
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine():
    """
    Create a single in-memory SQLite engine for the entire test session.

    StaticPool ensures all connections (including those made from inside the
    FastAPI dependency injection chain) share the same in-memory database
    instance — without it each new connection would get a blank database.
    """
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(_engine)
    yield _engine
    Base.metadata.drop_all(_engine)
    _engine.dispose()


# ---------------------------------------------------------------------------
# Per-test database session with automatic rollback
# ---------------------------------------------------------------------------

@pytest.fixture()
def db(engine) -> Session: # type: ignore
    """
    Yield a SQLAlchemy session bound to the in-memory engine.

    Rolls back and closes after each test so tests remain independent.
    """
    TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient with get_db override
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db: Session):
    """
    TestClient whose get_db dependency is overridden to use the test session.

    The override is cleaned up after each test to prevent state leaking
    between tests.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Seed default roles
# ---------------------------------------------------------------------------

@pytest.fixture()
def seed_roles(db: Session):
    """
    Ensure the two default roles ('admin' and 'user') exist in the test database.

    Uses get-or-create semantics so that tests sharing the same session-scoped
    engine do not collide on the UNIQUE constraint for role_name.

    autouse=False — tests that need these roles must request this fixture
    explicitly (or depend on a fixture that does).
    """
    from sqlalchemy import select

    admin_role = db.execute(select(Role).where(Role.role_name == "admin")).scalar_one_or_none()
    if admin_role is None:
        admin_role = Role(role_name="admin")
        db.add(admin_role)

    user_role = db.execute(select(Role).where(Role.role_name == "user")).scalar_one_or_none()
    if user_role is None:
        user_role = Role(role_name="user")
        db.add(user_role)

    db.commit()
    db.refresh(admin_role)
    db.refresh(user_role)
    return {"admin": admin_role, "user": user_role}


# ---------------------------------------------------------------------------
# User fixtures (depend on seed_roles)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def admin_user(engine):
    """
    Create a User assigned the 'admin' role in the test database.

    Session-scoped so the row is inserted exactly once and shared across all
    tests that need an admin user, avoiding UNIQUE constraint collisions that
    arise when the per-test 'db' fixture rolls back its connection state.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker as _sm

    Session_ = _sm(bind=engine, autoflush=False, autocommit=False)
    session = Session_()
    try:
        # Ensure admin role exists
        admin_role = session.execute(select(Role).where(Role.role_name == "admin")).scalar_one_or_none()
        if admin_role is None:
            admin_role = Role(role_name="admin")
            session.add(admin_role)
            session.commit()
            session.refresh(admin_role)

        existing = session.execute(select(User).where(User.email == "admin@test.com")).scalar_one_or_none()
        if existing is not None:
            return existing

        user = User(
            name="Admin User",
            email="admin@test.com",
            password=hash_password("adminpass123"),
            role_id=admin_role.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


@pytest.fixture(scope="session")
def regular_user(engine):
    """
    Create a User assigned the 'user' role in the test database.

    Session-scoped for the same reason as admin_user.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker as _sm

    Session_ = _sm(bind=engine, autoflush=False, autocommit=False)
    session = Session_()
    try:
        # Ensure user role exists
        user_role = session.execute(select(Role).where(Role.role_name == "user")).scalar_one_or_none()
        if user_role is None:
            user_role = Role(role_name="user")
            session.add(user_role)
            session.commit()
            session.refresh(user_role)

        existing = session.execute(select(User).where(User.email == "user@test.com")).scalar_one_or_none()
        if existing is not None:
            return existing

        user = User(
            name="Regular User",
            email="user@test.com",
            password=hash_password("userpass123"),
            role_id=user_role.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


# ---------------------------------------------------------------------------
# JWT token fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def admin_token(admin_user: User) -> str:
    """Return a valid JWT access token for the admin user."""
    return create_access_token({"sub": admin_user.email, "role": "admin"})


@pytest.fixture()
def user_token(regular_user: User) -> str:
    """Return a valid JWT access token for the regular user."""
    return create_access_token({"sub": regular_user.email, "role": "user"})
