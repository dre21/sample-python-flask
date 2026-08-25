"""
Seeder script for Order model only.
Seeds orders using existing users and products in the database.

Run from the project root:
    python -m app.helper.seed_order

Note: Run `python -m app.helper.seed` first to ensure users and products exist.
"""

from app import init_app
from app.utils import db
from app.models import Order, Product, User, order_products


def seed_orders():
    print("🌱 Starting order seeding...")

    app = init_app()
    with app.app_context():
        # Fetch existing users and products
        users = User.query.all()
        products = Product.query.all()

        if not users:
            print("  ✗ No users found. Run `python -m app.helper.seed` first.")
            return
        if not products:
            print("  ✗ No products found. Run `python -m app.helper.seed` first.")
            return

        # Clear existing orders and association data
        db.session.execute(order_products.delete())
        Order.query.delete()
        db.session.commit()
        print("  ✓ Cleared existing orders")

        # Create orders with different product combinations and statuses
        orders_data = [
            {
                'user': users[0],
                'products': products[0:3],
                'status': 'paid',
            },
            {
                'user': users[1],
                'products': products[2:5],
                'status': 'pending',
            },
            {
                'user': users[1],
                'products': products[5:7],
                'status': 'shipped',
            },
            {
                'user': users[2],
                'products': [products[0], products[4], products[7]],
                'status': 'delivered',
            },
            {
                'user': users[0],
                'products': products[8:12],
                'status': 'paid',
            },
            {
                'user': users[3] if len(users) > 3 else users[0],
                'products': [products[1], products[6], products[10]] if len(products) > 10 else products[0:2],
                'status': 'cancelled',
            },
            {
                'user': users[4] if len(users) > 4 else users[0],
                'products': products[12:16] if len(products) > 12 else products[0:3],
                'status': 'pending',
            },
            {
                'user': users[2],
                'products': products[1:4],
                'status': 'paid',
            },
            {
                'user': users[0],
                'products': [products[5], products[9]] if len(products) > 9 else products[0:2],
                'status': 'shipped',
            },
            {
                'user': users[3] if len(users) > 3 else users[1],
                'products': products[3:6],
                'status': 'delivered',
            },
        ]

        created = 0
        for data in orders_data:
            order_products_list = data['products']
            total = sum(p.price for p in order_products_list)

            order = Order(
                total=round(total, 2),
                user_id=data['user'].id,
                status=data['status'],
            )
            order.products = order_products_list
            db.session.add(order)
            created += 1

        db.session.commit()
        print(f"  ✓ Seeded {created} orders with products")

    print("🌱 Order seeding complete!")


if __name__ == '__main__':
    seed_orders()
