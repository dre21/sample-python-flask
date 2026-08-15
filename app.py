from flask import Flask
from flasgger import Swagger
from routes import products_bp, users_bp, orders_bp
from utils import db
from models import Product, User, Category
from flask_migrate import Migrate

def init_app():
    print("Initializing Flask app...")
    app = Flask(__name__)


    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://andresta:Andre135@159.69.111.83/test_andre'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Swagger config
    app.config['SWAGGER'] = {
        'title': 'Simple Shops API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'A simple shop API with products, users, and orders',
    }

    # set up the database
    db.init_app(app)

    # set up Flask-Migrate
    migrate = Migrate(app, db)

    # set up Swagger
    swagger = Swagger(app)

    # register blueprints
    print("Registering blueprints...")
    app.register_blueprint(products_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(orders_bp)

    print("Flask app initialized successfully.")
    return app

app = init_app()


# if __name__ == '__main__':
#     app.run(debug=True)
