"""
Locust load-testing file for Simple Shops API.

Run with:
    locust -f locustfile.py --host=http://localhost:5000

Then open http://localhost:8089 in your browser to start the test.
"""

import random

from locust import HttpUser, task, between


class BrowsingUser(HttpUser):
    """Scenario 1: A casual visitor who browses products without logging in."""

    weight = 3  # 75% of users are casual browsers
    wait_time = between(1, 3)

    @task(3)
    def browse_all_products(self):
        """Browse the product listing page."""
        self.client.get("/store/products")

    @task(1)
    def view_single_product(self):
        """View a single product detail page."""
        product_id = random.randint(17, 32)
        self.client.get(f"/store/products/{product_id}", name="/store/products/<id>")


class BuyingUser(HttpUser):
    """Scenario 2: A logged-in buyer who browses, views, orders, and checks orders."""

    weight = 1  # 25% of users are buyers
    wait_time = between(2, 5)

    def on_start(self):
        """Login to get a JWT access token before running tasks."""
        response = self.client.post("/auth/login", json={
            "email": "john@example.com",
            "password": "Password1234"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.order_id = None  # Will be set after placing an order
        else:
            self.token = None
            self.order_id = None

    def auth_headers(self):
        """Helper to build the Authorization header."""
        return {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def browse_products(self):
        """Browse the product listing."""
        self.client.get("/store/products")

    @task(2)
    def view_product_detail(self):
        """View a single product's detail page."""
        product_id = random.randint(17, 32)
        self.client.get(f"/store/products/{product_id}", name="/store/products/<id>")

    @task(1)
    def place_order(self):
        """Place an order for some products."""
        if not self.token:
            return

        product_ids = random.sample(range(17, 33), 2)
        response = self.client.post(
            "/orders",
            json={
                "items": [
                    {"product_id": product_ids[0], "quantity": 1},
                    {"product_id": product_ids[1], "quantity": 2},
                ]
            },
            headers=self.auth_headers(),
        )

        # Save the order ID so we can look it up later
        if response.status_code == 201:
            self.order_id = response.json().get("id")

    @task(1)
    def get_order_detail(self):
        """View the detail of the last placed order."""
        if not self.token or not self.order_id:
            return

        self.client.get(
            f"/orders/{self.order_id}",
            headers=self.auth_headers(),
            name="/orders/<id>"
        )
