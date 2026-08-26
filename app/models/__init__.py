"""
models/ — SQLAlchemy model definitions.

All models are imported here so other parts of the app can do:
    from app.models import Product, Category, User, Order, OrderProduct
"""

from app.models.category import Category
from app.models.product import Product, OrderProduct
from app.models.user import User
from app.models.order import Order
