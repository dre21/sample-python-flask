"""
controllers/ — Route handlers (thin controllers).

Each controller defines a Blueprint and delegates business logic to services.
All blueprints are exported here for easy registration in app/__init__.py.
"""

from app.controllers.product_controller import products_bp
from app.controllers.user_controller import users_bp
from app.controllers.order_controller import orders_bp
from app.controllers.auth_controller import auth_bp
