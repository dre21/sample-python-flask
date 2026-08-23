"""
Seeder script for simple-shops database.
Run from the project root:
    python -m helper.seed
"""

import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils import db
from models import Category, Product, User, Order, order_products
from middleware.auth import hash_password


def seed_categories():
    categories = [
        Category(name='Electronics'),
        Category(name='Clothing'),
        Category(name='Books'),
        Category(name='Home & Kitchen'),
        Category(name='Sports & Outdoors'),
        Category(name='Toys & Games'),
    ]
    db.session.add_all(categories)
    db.session.commit()
    print(f"  ✓ Seeded {len(categories)} categories")
    return categories


def seed_products(categories):
    # Map category names to objects for easy reference
    cat_map = {c.name: c for c in categories}

    products = [
        # Electronics
        Product(
            name='Wireless Mouse',
            sku='ELEC-001',
            description='Ergonomic wireless mouse with USB receiver',
            price=25.99,
            stock_qty=150,
            is_active=True,
            category_id=cat_map['Electronics'].id,
        ),
        Product(
            name='Mechanical Keyboard',
            sku='ELEC-002',
            description='RGB mechanical keyboard with blue switches',
            price=79.99,
            stock_qty=80,
            is_active=True,
            category_id=cat_map['Electronics'].id,
        ),
        Product(
            name='USB-C Hub',
            sku='ELEC-003',
            description='7-in-1 USB-C hub with HDMI and SD card reader',
            price=45.50,
            stock_qty=200,
            is_active=True,
            category_id=cat_map['Electronics'].id,
        ),
        Product(
            name='Bluetooth Speaker',
            sku='ELEC-004',
            description='Portable waterproof Bluetooth speaker',
            price=39.99,
            stock_qty=60,
            is_active=True,
            category_id=cat_map['Electronics'].id,
        ),
        # Clothing
        Product(
            name='Cotton T-Shirt',
            sku='CLTH-001',
            description='100% cotton crew neck t-shirt, unisex',
            price=15.00,
            stock_qty=300,
            is_active=True,
            category_id=cat_map['Clothing'].id,
        ),
        Product(
            name='Denim Jeans',
            sku='CLTH-002',
            description='Slim fit denim jeans, dark wash',
            price=49.99,
            stock_qty=120,
            is_active=True,
            category_id=cat_map['Clothing'].id,
        ),
        Product(
            name='Running Shoes',
            sku='CLTH-003',
            description='Lightweight running shoes with cushioned sole',
            price=89.99,
            stock_qty=75,
            is_active=True,
            category_id=cat_map['Clothing'].id,
        ),
        # Books
        Product(
            name='Python Crash Course',
            sku='BOOK-001',
            description='A hands-on, project-based introduction to programming',
            price=29.99,
            stock_qty=50,
            is_active=True,
            category_id=cat_map['Books'].id,
        ),
        Product(
            name='Clean Code',
            sku='BOOK-002',
            description='A handbook of agile software craftsmanship',
            price=34.99,
            stock_qty=40,
            is_active=True,
            category_id=cat_map['Books'].id,
        ),
        Product(
            name='The Pragmatic Programmer',
            sku='BOOK-003',
            description='Your journey to mastery, 20th anniversary edition',
            price=42.00,
            stock_qty=35,
            is_active=False,
            category_id=cat_map['Books'].id,
        ),
        # Home & Kitchen
        Product(
            name='Stainless Steel Water Bottle',
            sku='HOME-001',
            description='Insulated 750ml water bottle, keeps drinks cold 24h',
            price=22.50,
            stock_qty=200,
            is_active=True,
            category_id=cat_map['Home & Kitchen'].id,
        ),
        Product(
            name='Non-stick Frying Pan',
            sku='HOME-002',
            description='28cm ceramic non-stick frying pan',
            price=35.00,
            stock_qty=90,
            is_active=True,
            category_id=cat_map['Home & Kitchen'].id,
        ),
        # Sports & Outdoors
        Product(
            name='Yoga Mat',
            sku='SPRT-001',
            description='6mm thick non-slip yoga mat with carry strap',
            price=27.99,
            stock_qty=110,
            is_active=True,
            category_id=cat_map['Sports & Outdoors'].id,
        ),
        Product(
            name='Resistance Bands Set',
            sku='SPRT-002',
            description='Set of 5 resistance bands with varying tensions',
            price=18.99,
            stock_qty=180,
            is_active=True,
            category_id=cat_map['Sports & Outdoors'].id,
        ),
        # Toys & Games
        Product(
            name='Building Blocks Set',
            sku='TOYS-001',
            description='500-piece creative building blocks for ages 6+',
            price=32.99,
            stock_qty=65,
            is_active=True,
            category_id=cat_map['Toys & Games'].id,
        ),
        Product(
            name='Board Game Collection',
            sku='TOYS-002',
            description='Classic board game collection with 10 games',
            price=24.99,
            stock_qty=45,
            is_active=False,
            category_id=cat_map['Toys & Games'].id,
        ),
    ]
    db.session.add_all(products)
    db.session.commit()
    print(f"  ✓ Seeded {len(products)} products")
    return products


def seed_users():
    users = [
        User(
            username='admin',
            email='admin@simpleshops.com',
            password_hash=hash_password('Password1234'),
            role='admin',
        ),
        User(
            username='john_doe',
            email='john@example.com',
            password_hash=hash_password('Password1234'),
            role='user',
        ),
        User(
            username='jane_smith',
            email='jane@example.com',
            password_hash=hash_password('Password1234'),
            role='seller',
        ),
        User(
            username='bob_manager',
            email='bob@simpleshops.com',
            password_hash=hash_password('Password1234'),
            role='admin',
        ),
        User(
            username='alice_buyer',
            email='alice@example.com',
            password_hash=hash_password('Password1234'),
            role='user',
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    print(f"  ✓ Seeded {len(users)} users")
    return users


def seed_orders(users, products):
    """Seed orders with product associations and statuses."""
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
            'user': users[3],
            'products': [products[1], products[6], products[10]],
            'status': 'cancelled',
        },
        {
            'user': users[4],
            'products': products[12:16],
            'status': 'pending',
        },
        {
            'user': users[2],
            'products': products[1:4],
            'status': 'paid',
        },
        {
            'user': users[0],
            'products': [products[5], products[9]],
            'status': 'shipped',
        },
        {
            'user': users[3],
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


def run_seed():
    print("🌱 Starting database seeding...")
    with app.app_context():
        # Clear existing data (order matters due to foreign keys)
        db.session.execute(order_products.delete())
        Order.query.delete()
        Product.query.delete()
        Category.query.delete()
        User.query.delete()
        db.session.commit()
        print("  ✓ Cleared existing data")

        categories = seed_categories()
        products = seed_products(categories)
        users = seed_users()
        seed_orders(users, products)

    print("🌱 Seeding complete!")


if __name__ == '__main__':
    run_seed()
