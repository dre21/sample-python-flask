"""
Seeder script for Order model.
Run from the project root:
    python -m helper.seed_order
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils import db
from models import Order, Product, User


def seed_orders():
    print("🌱 Starting order seeding...")

    with app.app_context():
        # Fetch existing users and products
        users = User.query.all()
        products = Product.query.all()

        if not users:
            print("  ✗ No users found. Run `python -m helper.seed` first.")
            return
        if not products:
            print("  ✗ No products found. Run `python -m helper.seed` first.")
            return

        # Clear existing orders and association data
        # Need to clear the association table via raw SQL since it's not a model
        db.session.execute(db.text("DELETE FROM order_products"))
        Order.query.delete()
        db.session.commit()
        print("  ✓ Cleared existing orders")

        # Create orders with different product combinations
        orders_data = [
            {
                'user': users[0],
                'products': products[0:3],   # first 3 products
            },
            {
                'user': users[1],
                'products': products[2:5],   # products 3-5
            },
            {
                'user': users[1],
                'products': products[5:7],   # products 6-7
            },
            {
                'user': users[2],
                'products': [products[0], products[4], products[7]],
            },
            {
                'user': users[0],
                'products': products[8:12],  # products 9-12
            },
            {
                'user': users[3] if len(users) > 3 else users[0],
                'products': [products[1], products[6], products[10]] if len(products) > 10 else products[0:2],
            },
            {
                'user': users[4] if len(users) > 4 else users[0],
                'products': products[12:16] if len(products) > 12 else products[0:3],
            },
        ]

        created = 0
        for data in orders_data:
            order_products = data['products']
            total = sum(p.price for p in order_products)

            order = Order(
                total=round(total, 2),
                user_id=data['user'].id,
            )
            order.products = order_products
            db.session.add(order)
            created += 1

        db.session.commit()
        print(f"  ✓ Seeded {created} orders with products")

    print("🌱 Order seeding complete!")


if __name__ == '__main__':
    seed_orders()
