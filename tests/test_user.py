"""
Tests for /users endpoints — user registration and get user by ID.
"""

import pytest


@pytest.mark.usefixtures("seed_users")
class TestRegisterUser:
    """Tests for POST /users/register — create a new user account."""

    def test_register_user_returns_201(self, client):
        """Should return 201 when registering with valid data."""
        response = client.post(
            "/users/register",
            json={
                "username": "new_user",
                "email": "newuser@example.com",
                "password_hash": "securepass123",
                "role": "user",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "User registered successfully"
        assert data["status"] == "ok"
        assert data["user"]["username"] == "new_user"
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "user"
        # Password should never be in the response
        assert "password_hash" not in data["user"]

    def test_register_user_seller_role(self, client):
        """Should allow registering with the seller role."""
        response = client.post(
            "/users/register",
            json={
                "username": "new_seller",
                "email": "seller@newshop.com",
                "password_hash": "sellerpass1",
                "role": "seller",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["role"] == "seller"

    def test_register_user_admin_role(self, client):
        """Should allow registering with the admin role."""
        response = client.post(
            "/users/register",
            json={
                "username": "new_admin",
                "email": "admin@newshop.com",
                "password_hash": "adminpass1",
                "role": "admin",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["user"]["role"] == "admin"

    def test_register_user_missing_username(self, client):
        """Should return 400 when username is missing."""
        response = client.post(
            "/users/register",
            json={
                "email": "noname@example.com",
                "password_hash": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "username" in data["errors"]

    def test_register_user_missing_email(self, client):
        """Should return 400 when email is missing."""
        response = client.post(
            "/users/register",
            json={
                "username": "no_email_user",
                "password_hash": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "email" in data["errors"]

    def test_register_user_missing_password(self, client):
        """Should return 400 when password_hash is missing."""
        response = client.post(
            "/users/register",
            json={
                "username": "no_pass_user",
                "email": "nopass@example.com",
                "role": "user",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "password_hash" in data["errors"]

    def test_register_user_missing_role(self, client):
        """Should return 400 when role is missing."""
        response = client.post(
            "/users/register",
            json={
                "username": "no_role_user",
                "email": "norole@example.com",
                "password_hash": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "role" in data["errors"]

    def test_register_user_invalid_email(self, client):
        """Should return 400 when email format is invalid."""
        response = client.post(
            "/users/register",
            json={
                "username": "bad_email_user",
                "email": "not-an-email",
                "password_hash": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "email" in data["errors"]

    def test_register_user_invalid_role(self, client):
        """Should return 400 when role is not one of user/seller/admin."""
        response = client.post(
            "/users/register",
            json={
                "username": "bad_role_user",
                "email": "badrole@example.com",
                "password_hash": "password123",
                "role": "superadmin",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "role" in data["errors"]

    def test_register_user_password_too_short(self, client):
        """Should return 400 when password is shorter than 6 characters."""
        response = client.post(
            "/users/register",
            json={
                "username": "short_pass",
                "email": "shortpass@example.com",
                "password_hash": "abc",
                "role": "user",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "errors" in data
        assert "password_hash" in data["errors"]

    def test_register_user_duplicate_email(self, client):
        """Should return 409 when email already exists."""
        response = client.post(
            "/users/register",
            json={
                "username": "duplicate_user",
                "email": "jane@example.com",  # Already seeded
                "password_hash": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["status"] == "error"
        assert "already exists" in data["message"].lower()

    def test_register_user_empty_body(self, client):
        """Should return 400 or 415 when request body is not JSON."""
        response = client.post(
            "/users/register",
            data="not json",
            content_type="text/plain",
        )

        assert response.status_code in (400, 415)

    def test_register_user_includes_created_at(self, client):
        """Should include created_at in the response."""
        response = client.post(
            "/users/register",
            json={
                "username": "timestamped",
                "email": "timestamp@example.com",
                "password_hash": "password123",
                "role": "user",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "created_at" in data["user"]
        assert data["user"]["created_at"] is not None


@pytest.mark.usefixtures("seed_users")
class TestGetUser:
    """Tests for GET /users/<id> — get a user by ID."""

    def test_get_user_returns_200(self, client):
        """Should return 200 for an existing user."""
        response = client.get("/users/1")

        assert response.status_code == 200

    def test_get_user_returns_correct_data(self, client):
        """Should return the correct user data."""
        response = client.get("/users/1")
        data = response.get_json()

        assert data["id"] == 1
        assert data["username"] == "seller_jane"
        assert data["email"] == "jane@example.com"
        assert data["role"] == "seller"

    def test_get_user_does_not_expose_password(self, client):
        """Should never expose password_hash in the response."""
        response = client.get("/users/1")
        data = response.get_json()

        assert "password_hash" not in data
        assert "password" not in data

    def test_get_user_includes_created_at(self, client):
        """Should include created_at timestamp."""
        response = client.get("/users/1")
        data = response.get_json()

        assert "created_at" in data
        assert data["created_at"] is not None

    def test_get_user_not_found(self, client):
        """Should return 404 when user does not exist."""
        response = client.get("/users/999")

        assert response.status_code == 404
        data = response.get_json()
        assert data["message"] == "User not found"
        assert data["status"] == "error"

    def test_get_user_different_roles(self, client):
        """Should return correct role for different users."""
        # Check buyer
        response = client.get("/users/2")
        data = response.get_json()
        assert data["role"] == "user"

        # Check admin
        response = client.get("/users/3")
        data = response.get_json()
        assert data["role"] == "admin"
