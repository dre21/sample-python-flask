"""
Tests for GET /store/products and GET /store/products/<id> endpoints.
"""

import pytest


@pytest.mark.usefixtures("seed_products")
class TestGetProducts:
    """Tests for GET /store/products — list all products with pagination and filters."""

    def test_get_products_returns_200(self, client):
        """Should return 200 with a paginated list of products."""
        response = client.get("/store/products")

        assert response.status_code == 200

        data = response.get_json()
        assert "products" in data
        assert "page" in data
        assert "per_page" in data
        assert "total" in data
        assert "pages" in data

    def test_get_products_returns_all_seeded(self, client):
        """Should return all 4 seeded products."""
        response = client.get("/store/products")
        data = response.get_json()

        assert data["total"] == 4
        assert len(data["products"]) == 4

    def test_get_products_pagination_defaults(self, client):
        """Should default to page=1, per_page=10."""
        response = client.get("/store/products")
        data = response.get_json()

        assert data["page"] == 1
        assert data["per_page"] == 10

    def test_get_products_custom_pagination(self, client):
        """Should respect custom page and per_page params."""
        response = client.get("/store/products?page=1&per_page=2")
        data = response.get_json()

        assert data["page"] == 1
        assert data["per_page"] == 2
        assert len(data["products"]) == 2
        assert data["total"] == 4
        assert data["pages"] == 2

    def test_get_products_second_page(self, client):
        """Should return remaining products on page 2."""
        response = client.get("/store/products?page=2&per_page=2")
        data = response.get_json()

        assert data["page"] == 2
        assert len(data["products"]) == 2

    def test_get_products_filter_by_name(self, client):
        """Should filter products by name (case-insensitive partial match)."""
        response = client.get("/store/products?name=mouse")
        data = response.get_json()

        assert data["total"] == 1
        assert data["products"][0]["name"] == "Wireless Mouse"

    def test_get_products_filter_by_category_id(self, client):
        """Should filter products by category_id."""
        response = client.get("/store/products?category_id=1")
        data = response.get_json()

        # 3 electronics products (Mouse, Keyboard, Broken Headphones)
        assert data["total"] == 3

    def test_get_products_filter_by_max_price(self, client):
        """Should filter products with price <= max_price."""
        response = client.get("/store/products?max_price=30")
        data = response.get_json()

        # Wireless Mouse (29.99) and Cotton T-Shirt (15.00)
        assert data["total"] == 2
        for product in data["products"]:
            assert product["price"] <= 30

    def test_get_products_combined_filters(self, client):
        """Should support combining multiple filters."""
        response = client.get("/store/products?category_id=1&max_price=50")
        data = response.get_json()

        # Electronics under $50: Mouse (29.99), Broken Headphones (49.99)
        assert data["total"] == 2

    def test_get_products_no_match(self, client):
        """Should return empty list when no products match the filter."""
        response = client.get("/store/products?name=nonexistent")
        data = response.get_json()

        assert data["total"] == 0
        assert data["products"] == []

    def test_get_products_response_fields(self, client):
        """Each product in the list should have the expected fields."""
        response = client.get("/store/products")
        data = response.get_json()

        product = data["products"][0]
        expected_fields = {"id", "name", "sku", "price", "stock_qty", "is_active", "category"}
        assert expected_fields.issubset(set(product.keys()))


@pytest.mark.usefixtures("seed_products")
class TestGetProductById:
    """Tests for GET /store/products/<id> — get a single product by ID."""

    def test_get_product_returns_200(self, client):
        """Should return 200 for an existing product."""
        response = client.get("/store/products/1")

        assert response.status_code == 200

    def test_get_product_returns_correct_data(self, client):
        """Should return the correct product data."""
        response = client.get("/store/products/1")
        data = response.get_json()

        assert data["id"] == 1
        assert data["name"] == "Wireless Mouse"
        assert data["sku"] == "ELEC-001"
        assert data["price"] == 29.99
        assert data["stock_qty"] == 50
        assert data["is_active"] is True

    def test_get_product_includes_description(self, client):
        """Detail endpoint should include the description field."""
        response = client.get("/store/products/1")
        data = response.get_json()

        assert "description" in data
        assert data["description"] == "A comfortable wireless mouse"

    def test_get_product_includes_category_name(self, client):
        """Should include the category name (not just category_id)."""
        response = client.get("/store/products/1")
        data = response.get_json()

        assert data["category"] == "Electronics"

    def test_get_product_includes_created_at(self, client):
        """Detail endpoint should include created_at timestamp."""
        response = client.get("/store/products/1")
        data = response.get_json()

        assert "created_at" in data
        assert data["created_at"] is not None

    def test_get_product_not_found(self, client):
        """Should return 404 when product does not exist."""
        response = client.get("/store/products/999")

        assert response.status_code == 404

        data = response.get_json()
        assert data["message"] == "Product not found"
        assert data["status"] == "error"

    def test_get_product_inactive(self, client):
        """Should still return inactive products (no filtering by is_active on detail)."""
        response = client.get("/store/products/4")
        data = response.get_json()

        assert response.status_code == 200
        assert data["is_active"] is False
        assert data["name"] == "Broken Headphones"
