"""
Order service — business logic for orders.
"""

from app.models import Order


def get_all_orders():
    """Fetch all orders."""
    return Order.query.all()


def get_order_by_id(order_id):
    """Fetch a single order by ID. Returns None if not found."""
    return Order.query.get(order_id)
