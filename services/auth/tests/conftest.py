"""
tests/conftest.py — Shared pytest fixtures for the auth service test suite.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
from unittest.mock import patch

from app.main import app
from app.database import get_db
from app.models import User, UserStatus
from app.auth import hash_password, create_access_token

# ─────────────────────────────────────────────────────────────────────────── #
# In-memory SQLite engine
# ─────────────────────────────────────────────────────────────────────────── #

SQLITE_URL = "sqlite://"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_db():
    # Return the same session that's being used by the test
    # This is set by the client fixture
    yield from _get_current_session()


# Global variable to track the current test session
_current_session = None


def _get_current_session():
    global _current_session
    if _current_session is None:
        _current_session = Session(engine)
    yield _current_session


# ─────────────────────────────────────────────────────────────────────────── #
# Session-scoped: create tables once, drop after all tests done
# ─────────────────────────────────────────────────────────────────────────── #

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


# ─────────────────────────────────────────────────────────────────────────── #
# Function-scoped: fresh DB session per test, rolls back after each
# ─────────────────────────────────────────────────────────────────────────── #

@pytest.fixture(scope="function")
def db_session():
    global _current_session
    # Create a new session for each test
    session = Session(engine)
    _current_session = session
    try:
        yield session
    finally:
        # Rollback any uncommitted changes
        session.rollback()
        # Delete all users to ensure test isolation
        session.exec(text("DELETE FROM users"))
        session.commit()
        session.close()
        _current_session = None


# ─────────────────────────────────────────────────────────────────────────── #
# Core client fixture
# ─────────────────────────────────────────────────────────────────────────── #

@pytest.fixture(scope="function")
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.router.is_rate_limited", return_value=False), \
         patch("app.router.record_failed_attempt", return_value=1), \
         patch("app.router.clear_failed_attempts", return_value=None), \
         patch("app.router.denylist_token", return_value=None):

        with TestClient(app, raise_server_exceptions=True) as test_client:
            yield test_client

    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────────────────────── #
# User fixtures — match exactly what test_login.py expects
# ─────────────────────────────────────────────────────────────────────────── #

# Credentials test_login.py hardcodes — fixtures must match these exactly
VALID_CREDENTIALS = {
    "username": "operator@cleansight.test",
    "password": "SecureP@ssw0rd!",
}

SUSPENDED_CREDENTIALS = {
    "username": "suspended@cleansight.test",
    "password": "SuspendedP@ss!",
}


@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    """
    Active user whose credentials match VALID_CREDENTIALS in test_login.py.
    Created directly in DB — does not depend on the register endpoint.
    """
    user = User(
        username=VALID_CREDENTIALS["username"],
        hashed_password=hash_password(VALID_CREDENTIALS["password"]),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def suspended_user(db_session) -> User:
    """
    Suspended user — login must return 401 even with correct password.
    """
    user = User(
        username=SUSPENDED_CREDENTIALS["username"],
        hashed_password=hash_password(SUSPENDED_CREDENTIALS["password"]),
        status=UserStatus.suspended,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def operator_token(test_user: User) -> str:
    """
    Valid access token for test_user.
    Generated directly — does not depend on the login endpoint.
    This means protected-route tests don't break if login is broken.
    """
    return create_access_token(test_user.id, test_user.role)


# ─────────────────────────────────────────────────────────────────────────── #
# Convenience fixture used by test_register.py indirectly
# ─────────────────────────────────────────────────────────────────────────── #

@pytest.fixture(scope="function")
def registered_user(db_session) -> dict:
    """
    Generic pre-existing user for tests that need one but don't care about
    the specific credentials.
    """
    plain_password = "TestPass123!"
    user = User(
        username="genericuser@cleansight.test",
        hashed_password=hash_password(plain_password),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"id": user.id, "username": user.username, "password": plain_password}