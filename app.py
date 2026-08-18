from flask import Flask
from flasgger import Swagger
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from models import Product, User, Category  # noqa: F401 — needed for Migrate to detect models
from routes import products_bp, users_bp, orders_bp, auth_bp
from utils import db


def init_app():
    print("Initializing Flask app...")
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Set up the database
    db.init_app(app)

    # Set up Flask-Migrate
    migrate = Migrate(app, db)

    # Set up JWT
    jwt = JWTManager(app)

    # Set up Swagger
    swagger = Swagger(app)

    # Register blueprints
    print("Registering blueprints...")
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(auth_bp)

    print("Flask app initialized successfully.")
    return app


app = init_app()


# if __name__ == '__main__':
#     app.run(debug=True)
