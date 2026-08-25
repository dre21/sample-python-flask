"""
Application factory — creates and configures the Flask app.
"""

from flask import Flask
from flasgger import Swagger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from app.config import Config
from app.models import Product, User, Category, Order  # noqa: F401 — needed for Migrate
from app.controllers import products_bp, users_bp, orders_bp, auth_bp
from app.middleware.errors import register_error_handlers
from app.utils import db


def init_app(config_overrides=None):
    """Create and configure the Flask application."""
    print("Initializing Flask app...")
    application = Flask(__name__)

    # Load configuration
    application.config.from_object(Config)

    # Apply any overrides (e.g., test config) before initializing extensions
    if config_overrides:
        application.config.update(config_overrides)

    # Set up the database
    db.init_app(application)

    # Set up Flask-Migrate
    Migrate(application, db)

    # Set up JWT
    JWTManager(application)

    # Set up Swagger with Bearer token authorization
    Swagger(application, template=Config.SWAGGER_TEMPLATE)

    # Register blueprints
    print("Registering blueprints...")
    application.register_blueprint(products_bp)
    application.register_blueprint(users_bp)
    application.register_blueprint(orders_bp)
    application.register_blueprint(auth_bp)

    # Register global error handlers (JSON responses)
    register_error_handlers(application)

    print("Flask app initialized successfully.")
    return application
