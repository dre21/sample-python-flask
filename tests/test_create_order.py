"""
Tests for POST /orders — create a new order (user role required).
"""

import pytest


@pytest.mark.usefixtures("seed_users", "seed_products")
class TestCreateOrder:
    """Tests for POST /orders — create order with product_id/quantity pairs."""

    def test_create_order_returns_201(self, client, user_token):
        """Should return 201 when order is created successfully."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 201

    def test_create_order_returns_correct_data(self, client, user_token):
        """Should return the order with correct total and status."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 2}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert data["total"] == 59.98  # 29.99 * 2
        assert data["status"] == "pending"
        assert data["user_id"] == "buyer_john"

    def test_create_order_multiple_items(self, client, user_token):
        """Should handle multiple products in a single order."""
        response = client.post(
            "/orders",
            json={
                "items": [
                    {"product_id": 1, "quantity": 1},
                    {"product_id": 2, "quantity": 2},
                ]
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert response.status_code == 201
        # 29.99 + (89.99 * 2) = 209.97
        assert data["total"] == 209.97
        assert len(data["products"]) == 2

    def test_create_order_includes_product_details(self, client, user_token):
        """Response should include product name, sku, price, and quantity."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 3}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        product = data["products"][0]
        assert product["id"] == 1
        assert product["name"] == "Wireless Mouse"
        assert product["sku"] == "ELEC-001"
        assert product["price"] == 29.99
        assert product["quantity"] == 3

    def test_create_order_assigns_to_authenticated_user(self, client, user_token):
        """Order should be assigned to the user from the JWT token."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 3, "quantity": 1}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        # user_token is identity="2" which is buyer_john
        assert data["user_id"] == "buyer_john"

    def test_create_order_product_not_found(self, client, user_token):
        """Should return 404 when a product_id does not exist."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 999, "quantity": 1}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert "not found" in data["message"]

    def test_create_order_inactive_product(self, client, user_token):
        """Should return 400 when a product is not active."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 4, "quantity": 1}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "not available" in data["message"]

    def test_create_order_empty_items(self, client, user_token):
        """Should return 400 when items list is empty."""
        response = client.post(
            "/orders",
            json={"items": []},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 400

    def test_create_order_missing_items(self, client, user_token):
        """Should return 400 when items field is missing."""
        response = client.post(
            "/orders",
            json={},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 400

    def test_create_order_invalid_quantity(self, client, user_token):
        """Should return 400 when quantity is less than 1."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 0}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 400

    def test_create_order_missing_product_id(self, client, user_token):
        """Should return 400 when product_id is missing from an item."""
        response = client.post(
            "/orders",
            json={"items": [{"quantity": 1}]},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 400

    def test_create_order_no_auth(self, client):
        """Should return 401 when no token is provided."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 1}]},
        )

        assert response.status_code == 401

    def test_create_order_forbidden_role(self, client, seller_token):
        """Should return 403 when the user does not have the 'user' role."""
        response = client.post(
            "/orders",
            json={"items": [{"product_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["error"] == "Forbidden"
