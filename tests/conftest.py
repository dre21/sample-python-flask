"""
Shared test fixtures — creates an in-memory SQLite app for fast, isolated tests.
"""

import pytest
from flask_jwt_extended import create_access_token
from app import init_app
from utils import db as _db
from models import Product, Category, User, Order


@pytest.fixture(scope='class')
def app():
    """Create a Flask application configured for testing (in-memory SQLite)."""
    
    config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
    }
    app = init_app(config)

    # Create all tables in the in-memory database
    with app.app_context():
        _db.create_all()

    yield app

    # Cleanup — drop all tables after the test
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='class')
def client(app):
    """A Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='class')
def seed_products(app):
    """Seed the database with sample categories and products for testing."""
    with app.app_context():
        # Create categories
        cat_electronics = Category(id=1, name="Electronics")
        cat_clothing = Category(id=2, name="Clothing")
        _db.session.add_all([cat_electronics, cat_clothing])
        _db.session.commit()

        # Create products
        products = [
            Product(
                name="Wireless Mouse",
                sku="ELEC-001",
                description="A comfortable wireless mouse",
                price=29.99,
                stock_qty=50,
                is_active=True,
                category_id=1,
            ),
            Product(
                name="Mechanical Keyboard",
                sku="ELEC-002",
                description="RGB mechanical keyboard",
                price=89.99,
                stock_qty=30,
                is_active=True,
                category_id=1,
            ),
            Product(
                name="Cotton T-Shirt",
                sku="CLTH-001",
                description="Soft cotton t-shirt",
                price=15.00,
                stock_qty=100,
                is_active=True,
                category_id=2,
            ),
            Product(
                name="Broken Headphones",
                sku="ELEC-003",
                description="These are discontinued",
                price=49.99,
                stock_qty=0,
                is_active=False,
                category_id=1,
            ),
        ]
        _db.session.add_all(products)
        _db.session.commit()


@pytest.fixture(scope='class')
def seed_users(app):
    """Seed the database with sample users for testing."""
    with app.app_context():
        from middleware.auth import hash_password

        users = [
            User(
                id=1,
                username="seller_jane",
                email="jane@example.com",
                password_hash=hash_password("password123"),
                role="seller",
            ),
            User(
                id=2,
                username="buyer_john",
                email="john@example.com",
                password_hash=hash_password("password123"),
                role="user",
            ),
            User(
                id=3,
                username="admin_bob",
                email="bob@example.com",
                password_hash=hash_password("adminpass1"),
                role="admin",
            ),
        ]
        _db.session.add_all(users)
        _db.session.commit()


@pytest.fixture(scope='class')
def seed_orders(app, seed_users, seed_products):
    """Seed the database with sample orders for testing. Requires users and products."""
    with app.app_context():
        order1 = Order(id=1, total=119.98, status="pending", user_id=2)
        order2 = Order(id=2, total=15.00, status="completed", user_id=2)
        _db.session.add_all([order1, order2])
        _db.session.commit()

        # Attach products to orders via the association table
        product1 = Product.query.get(1)  # Wireless Mouse
        product2 = Product.query.get(2)  # Mechanical Keyboard
        product3 = Product.query.get(3)  # Cotton T-Shirt

        order1.products.append(product1)
        order1.products.append(product2)
        order2.products.append(product3)
        _db.session.commit()


@pytest.fixture(scope='class')
def seller_token(app):
    """Generate a JWT access token with the 'seller' role for testing."""
    with app.app_context():
        token = create_access_token(
            identity="1",
            additional_claims={"role": "seller"}
        )
        return token


@pytest.fixture(scope='class')
def user_token(app):
    """Generate a JWT access token with the default 'user' role for testing."""
    with app.app_context():
        token = create_access_token(
            identity="2",
            additional_claims={"role": "user"}
        )
        return token


@pytest.fixture(scope='class')
def admin_token(app):
    """Generate a JWT access token with the 'admin' role for testing."""
    with app.app_context():
        token = create_access_token(
            identity="3",
            additional_claims={"role": "admin"}
        )
        return token
