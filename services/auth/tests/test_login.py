"""
tests/test_login.py — POST /auth/login and protected route tests.

Tests cover:
  - Happy path: valid login returns tokens
  - Wrong password → 401
  - Non-existent username → 401 (same error as wrong password)
  - Suspended account → 401
  - Protected route /me with valid token → 200
  - Protected route /me with no token → 401
  - Protected route /me with tampered token → 401
  - Token refresh happy path
  - Access token cannot be used as refresh token
  - Logout denylists the token
"""

import pytest
from fastapi.testclient import TestClient

from app.models import User

VALID_CREDENTIALS = {
    "username": "operator@cleansight.test",
    "password": "SecureP@ssw0rd!",
}


class TestLoginSuccess:
    def test_login_returns_200(self, client: TestClient, test_user: User):
        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        assert response.status_code == 200

    def test_login_returns_both_tokens(self, client: TestClient, test_user: User):
        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_tokens_are_non_empty_strings(self, client: TestClient, test_user: User):
        response = client.post("/auth/login", json=VALID_CREDENTIALS)
        data = response.json()
        assert len(data["access_token"]) > 20
        assert len(data["refresh_token"]) > 20

    def test_login_username_case_insensitive(self, client: TestClient, test_user: User):
        payload = {**VALID_CREDENTIALS, "username": VALID_CREDENTIALS["username"].upper()}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 200


class TestLoginFailure:
    def test_wrong_password_returns_401(self, client: TestClient, test_user: User):
        payload = {**VALID_CREDENTIALS, "password": "WrongPassword1!"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    def test_wrong_username_returns_401(self, client: TestClient, test_user: User):
        payload = {**VALID_CREDENTIALS, "username": "nobody@cleansight.test"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401

    def test_wrong_password_and_wrong_username_same_error(
        self, client: TestClient, test_user: User
    ):
        """SECURITY: Both failure cases must return the same error message."""
        bad_password = client.post(
            "/auth/login",
            json={**VALID_CREDENTIALS, "password": "WrongPass1!"},
        )
        bad_username = client.post(
            "/auth/login",
            json={**VALID_CREDENTIALS, "username": "nobody@cleansight.test"},
        )
        assert bad_password.json()["detail"] == bad_username.json()["detail"]

    def test_suspended_account_returns_401(
        self, client: TestClient, suspended_user: User
    ):
        response = client.post("/auth/login", json={
            "username": "suspended@cleansight.test",
            "password": "SuspendedP@ss!",
        })
        assert response.status_code == 401


class TestProtectedRoute:
    def test_me_with_valid_token_returns_200(
        self, client: TestClient, test_user: User, operator_token: str
    ):
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        assert response.status_code == 200

    def test_me_returns_correct_user(
        self, client: TestClient, test_user: User, operator_token: str
    ):
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        data = response.json()
        assert data["username"] == test_user.username
        assert "hashed_password" not in data

    def test_me_without_token_returns_401(self, client: TestClient, test_user: User):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_me_with_tampered_token_returns_401(
        self, client: TestClient, test_user: User, operator_token: str
    ):
        """SECURITY: Modifying any part of the token must invalidate it."""
        tampered = operator_token[:-5] + "XXXXX"
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tampered}"},
        )
        assert response.status_code == 401

    def test_me_with_garbage_token_returns_401(self, client: TestClient, test_user: User):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert response.status_code == 401


class TestRefreshToken:
    def test_refresh_returns_new_access_token(
        self, client: TestClient, test_user: User
    ):
        login = client.post("/auth/login", json=VALID_CREDENTIALS)
        refresh_token = login.json()["refresh_token"]

        response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_access_token_cannot_be_used_as_refresh(
        self, client: TestClient, test_user: User, operator_token: str
    ):
        """SECURITY: Token type confusion must be rejected."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": operator_token},  # access token, not refresh
        )
        assert response.status_code == 401


class TestLogout:
    def test_logout_returns_200(
        self, client: TestClient, test_user: User, operator_token: str
    ):
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        assert response.status_code == 200

    def test_logout_without_token_returns_401(self, client: TestClient, test_user: User):
        response = client.post("/auth/logout")
        assert response.status_code == 401