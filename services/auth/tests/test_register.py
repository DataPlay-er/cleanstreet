"""
tests/test_register.py — POST /auth/register tests.

Tests cover:
  - Happy path: valid registration
  - Duplicate username rejection
  - Weak password rejection (multiple cases)
  - Invalid username rejection
  - Response shape (no hashed_password in response)
  - Case normalisation (username)
"""

import pytest
from fastapi.testclient import TestClient

VALID_PAYLOAD = {
    "username": "newuser@cleansight.test",
    "password": "Secur3P@ssword!",
}


class TestRegisterSuccess:
    def test_register_returns_201(self, client: TestClient):
        response = client.post("/auth/register", json=VALID_PAYLOAD)
        assert response.status_code == 201

    def test_register_returns_user_fields(self, client: TestClient):
        response = client.post("/auth/register", json=VALID_PAYLOAD)
        data = response.json()
        assert "id" in data
        assert data["username"] == VALID_PAYLOAD["username"]
        assert "role" in data
        assert "created_at" in data

    def test_register_never_returns_password(self, client: TestClient):
        """SECURITY: hashed_password must never appear in the response."""
        response = client.post("/auth/register", json=VALID_PAYLOAD)
        data = response.json()
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_default_role_is_operator(self, client: TestClient):
        response = client.post("/auth/register", json=VALID_PAYLOAD)
        assert response.json()["role"] == "operator"

    def test_register_normalises_username_to_lowercase(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "username": "UPPER@CleanSight.TEST"}
        response = client.post("/auth/register", json=payload)
        assert response.json()["username"] == "upper@cleansight.test"


class TestRegisterDuplicateusername:
    def test_duplicate_username_returns_409(self, client: TestClient):
        client.post("/auth/register", json=VALID_PAYLOAD)
        response = client.post("/auth/register", json=VALID_PAYLOAD)
        assert response.status_code == 409

    def test_duplicate_username_case_insensitive(self, client: TestClient):
        client.post("/auth/register", json=VALID_PAYLOAD)
        payload = {**VALID_PAYLOAD, "username": VALID_PAYLOAD["username"].upper()}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409


class TestRegisterPasswordValidation:
    def test_password_too_short_returns_422(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "password": "Short1!"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_password_no_uppercase_returns_422(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "password": "nouppercase123!"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_password_no_digit_returns_422(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "password": "NoDigitsHere!!!"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_password_no_special_char_returns_422(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "password": "NoSpecialChar1"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_invalid_username_returns_422(self, client: TestClient):
        payload = {**VALID_PAYLOAD, "username": "not-an-username"}
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422