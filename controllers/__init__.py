"""
controllers/ — Route handlers (thin controllers).

Each controller defines a Blueprint and delegates business logic to services.
All blueprints are exported here for easy registration in app.py.
"""

from controllers.product_controller import products_bp
from controllers.user_controller import users_bp
from controllers.order_controller import orders_bp
from controllers.auth_controller import auth_bp
