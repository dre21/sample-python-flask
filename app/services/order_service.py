"""
Order service — business logic for orders.
"""

from app.utils import db
from app.models import Order, Product, OrderProduct


def get_all_orders():
    """Fetch all orders."""
    return Order.query.all()


def get_order_by_id(order_id):
    """Fetch a single order by ID. Returns None if not found."""
    return Order.query.get(order_id)


def create_order(user_id, items):
    """
    Create a new order for the given user.

    Args:
        user_id: ID of the authenticated user placing the order.
        items: list of dicts with 'product_id' and 'quantity'.

    Returns:
        (order, None) on success.
        (None, error_dict) on failure (e.g. product not found).
    """
    # Validate all products exist and calculate total
    total = 0.0
    order_items = []

    for item in items:
        product = Product.query.get(item['product_id'])
        if product is None:
            return None, {
                "message": f"Product with id {item['product_id']} not found",
                "status_code": 404,
            }

        if not product.is_active:
            return None, {
                "message": f"Product '{product.name}' is not available",
                "status_code": 400,
            }

        total += product.price * item['quantity']
        order_items.append({
            'product_id': product.id,
            'quantity': item['quantity'],
        })

    # Create the order
    try:
        order = Order(
            user_id=user_id,
            total=round(total, 2),
            status='pending',
        )
        db.session.add(order)
        db.session.flush()  # Get order.id for the OrderProduct rows

        # Create order items
        # TODO: Reduce product stock_qty here once inventory management is implemented
        for item_data in order_items:
            order_item = OrderProduct(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
            )
            db.session.add(order_item)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, {
            "message": f"Failed to create order: {str(e)}",
            "status_code": 500,
        }

    return order, None
