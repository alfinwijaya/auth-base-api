# Feature: authbase-hardening, Property 2: Refresh preserves role claim

"""
Property-based tests for RBAC / token behaviour.

Validates: Requirements 3.2
"""

from __future__ import annotations

import pytest

from hypothesis import given, settings as h_settings, HealthCheck
from hypothesis import strategies as st

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.role import Role
from app.models.user import User
from app.core.security import create_refresh_token
from app.core.config import settings as app_settings
from app.services.auth_service import AuthService
from jose import jwt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_session():
    """Return a fresh in-memory SQLite session with all tables created."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()


def _seed(db, role_name: str):
    """Insert a Role and a User with that role; return the user."""
    role = Role(role_name=role_name)
    db.add(role)
    db.flush()  # get role.id without committing

    user = User(
        email=f"test_{role_name}@example.com",
        password="hashed_pw_placeholder",
        name="Test User",
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Property 2: Refresh token preserves role claim for all users
# Validates: Requirements 3.2
# ---------------------------------------------------------------------------

@h_settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    role_name=st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(whitelist_categories=("L",)),
    )
)
def test_refresh_preserves_role_claim(role_name: str):
    """
    **Validates: Requirements 3.2**

    For any user with any role name, after calling `refresh_access_token`
    with a valid refresh token for that user, the decoded new access token
    payload SHALL contain a `"role"` key whose value equals `role_name`.
    """
    db = _make_session()
    try:
        user = _seed(db, role_name)

        # Build a valid refresh token for this user (same as login_user does)
        refresh_tok = create_refresh_token({"sub": user.email})

        # Call the service under test
        result = AuthService.refresh_access_token(refresh_tok, db)

        # Decode the newly issued access token (skip audience verification)
        payload = jwt.decode(
            result["access_token"],
            app_settings.SECRET_KEY,
            algorithms=[app_settings.ALGORITHM],
        )

        # The role claim must equal the seeded role name
        assert payload.get("role") == role_name, (
            f"Expected role claim '{role_name}', got '{payload.get('role')}'"
        )
    finally:
        db.close()
