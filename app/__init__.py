"""
Application factory — creates and configures the Flask app.
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Flask
from flasgger import Swagger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from app.config import Config
from app.models import Product, User, Category, Order, OrderProduct  # noqa: F401 — needed for Migrate
from app.controllers import products_bp, users_bp, orders_bp, auth_bp
from app.middleware.errors import register_error_handlers
from app.utils import db


def setup_logging(app):
    """
    Configure Python's logging system based on Config settings.

    Logs go to TWO places:
    1. Console (stdout) — so you can see them in the terminal
    2. File (logs/app.log) — rotated daily, keeps last 7 days

    The file is created automatically. Every day at midnight a new file
    is started, and old files get a date suffix like:
        logs/app.log            ← today's log
        logs/app.log.2026-08-26 ← yesterday
        logs/app.log.2026-08-25 ← two days ago
        (files older than 7 days are deleted automatically)
    """
    log_level = Config.get_log_level()
    formatter = logging.Formatter(Config.LOG_FORMAT, datefmt=Config.LOG_DATE_FORMAT)

    # ─── Console Handler (stdout) ──────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # ─── File Handler (daily rotation) ─────────────────────────────────────────
    # Create the logs/ directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'app.log')

    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when='midnight',       # Rotate at midnight every day
        interval=1,            # Every 1 day
        backupCount=7,         # Keep last 7 days of logs
        encoding='utf-8',
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    file_handler.suffix = '%Y-%m-%d'  # Date format for rotated file names

    # ─── Configure Root Logger ─────────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Remove any default handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Also set Flask's built-in logger to the same level
    app.logger.setLevel(log_level)

    # Log the active configuration
    app.logger.info("Logging configured — env=%s, level=%s, file=%s",
                    Config.FLASK_ENV, log_level, log_file)


def init_app(config_overrides=None):
    """Create and configure the Flask application."""
    application = Flask(__name__)

    # Load configuration
    application.config.from_object(Config)

    # Apply any overrides (e.g., test config) before initializing extensions
    if config_overrides:
        application.config.update(config_overrides)

    # Set up logging (replaces print statements)
    setup_logging(application)

    application.logger.info("Initializing Flask app...")

    # Set up the database
    db.init_app(application)

    # Set up Flask-Migrate
    Migrate(application, db)

    # Set up JWT
    JWTManager(application)

    # Set up Swagger with Bearer token authorization
    Swagger(application, template=Config.SWAGGER_TEMPLATE)

    # Register blueprints
    application.logger.debug("Registering blueprints...")
    application.register_blueprint(products_bp)
    application.register_blueprint(users_bp)
    application.register_blueprint(orders_bp)
    application.register_blueprint(auth_bp)

    # Register global error handlers (JSON responses)
    register_error_handlers(application)

    application.logger.info("Flask app initialized successfully.")
    return application
