import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {
        'title': 'Simple Shops API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'A simple shop API with products, users, and orders',
    }
