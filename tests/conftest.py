"""
Shared test fixtures — creates an in-memory SQLite app for fast, isolated tests.
"""

import pytest
from app import init_app
from utils import db as _db
from models import Product, Category


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
