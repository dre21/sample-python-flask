"""
Tests for /orders endpoints — get all orders and get order by ID.

Both endpoints require the 'user' role (or higher).
"""

import pytest


@pytest.mark.usefixtures("seed_orders")
class TestGetOrders:
    """Tests for GET /orders — list all orders (user role required)."""

    def test_get_orders_returns_200(self, client, user_token):
        """Should return 200 with a list of orders."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_get_orders_returns_all_seeded(self, client, user_token):
        """Should return all 2 seeded orders."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert len(data) == 2

    def test_get_orders_contains_expected_fields(self, client, user_token):
        """Each order in the list should have id, name, total, and status."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        order = data[0]
        assert "id" in order
        assert "name" in order  # username via Method field
        assert "total" in order
        assert "status" in order

    def test_get_orders_shows_username(self, client, user_token):
        """The 'name' field should contain the username of the order owner."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        # All seeded orders belong to user_id=2 (buyer_john)
        for order in data:
            assert order["name"] == "buyer_john"

    def test_get_orders_shows_status(self, client, user_token):
        """Should return the correct status for each order."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        statuses = {order["id"]: order["status"] for order in data}
        assert statuses[1] == "pending"
        assert statuses[2] == "completed"

    def test_get_orders_no_auth(self, client):
        """Should return 401 when no token is provided."""
        response = client.get("/orders")

        assert response.status_code == 401

    def test_get_orders_forbidden_role(self, client, seller_token):
        """Should return 403 when the user does not have the 'user' role."""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["error"] == "Forbidden"


@pytest.mark.usefixtures("seed_orders")
class TestGetOrderById:
    """Tests for GET /orders/<id> — get a single order by ID (user role required)."""

    def test_get_order_returns_200(self, client, user_token):
        """Should return 200 for an existing order."""
        response = client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 200

    def test_get_order_returns_correct_data(self, client, user_token):
        """Should return the correct order data."""
        response = client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert data["id"] == 1
        assert data["total"] == 119.98
        assert data["user_id"] == "buyer_john"  # username via Method field

    def test_get_order_includes_products(self, client, user_token):
        """Should include the list of products in the order."""
        response = client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert "products" in data
        assert len(data["products"]) == 2

        # Check product fields
        product = data["products"][0]
        assert "id" in product
        assert "name" in product
        assert "sku" in product
        assert "price" in product

    def test_get_order_products_match_seeded(self, client, user_token):
        """Order 1 should contain Wireless Mouse and Mechanical Keyboard."""
        response = client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        product_names = {p["name"] for p in data["products"]}
        assert "Wireless Mouse" in product_names
        assert "Mechanical Keyboard" in product_names

    def test_get_order_second_order(self, client, user_token):
        """Order 2 should contain Cotton T-Shirt."""
        response = client.get(
            "/orders/2",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        data = response.get_json()
        assert data["id"] == 2
        assert data["total"] == 15.00
        assert len(data["products"]) == 1
        assert data["products"][0]["name"] == "Cotton T-Shirt"

    def test_get_order_not_found(self, client, user_token):
        """Should return 404 when order does not exist."""
        response = client.get(
            "/orders/999",
            headers={"Authorization": f"Bearer {user_token}"},
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["message"] == "Order not found"
        assert data["status"] == "error"

    def test_get_order_no_auth(self, client):
        """Should return 401 when no token is provided."""
        response = client.get("/orders/1")

        assert response.status_code == 401

    def test_get_order_forbidden_role(self, client, seller_token):
        """Should return 403 when the user does not have the 'user' role."""
        response = client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {seller_token}"},
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["error"] == "Forbidden"
