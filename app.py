from flask import Flask
from flasgger import Swagger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import Product, User, Category, Order  # noqa: F401 — needed for Migrate to detect models
from controllers import products_bp, users_bp, orders_bp, auth_bp
from middleware.errors import register_error_handlers
from utils import db


def init_app():
    print("Initializing Flask app...")
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Set up the database
    db.init_app(app)

    # Set up Flask-Migrate
    migrate = Migrate(app, db)  # noqa: F841

    # Set up JWT
    jwt = JWTManager(app)  # noqa: F841

    # Set up Swagger with Bearer token authorization
    swagger = Swagger(app, template=Config.SWAGGER_TEMPLATE)  # noqa: F841

    # Register blueprints
    print("Registering blueprints...")
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)

    # Register global error handlers (JSON responses)
    register_error_handlers(app)

    print("Flask app initialized successfully.")
    return app


app = init_app()
