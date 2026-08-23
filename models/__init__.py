"""
models/ — SQLAlchemy model definitions.

All models are imported here so other parts of the app can do:
    from models import Product, Category, User, Order, order_products
"""

from models.category import Category
from models.product import Product, order_products
from models.user import User
from models.order import Order
