"""
Configuration class — reads settings from environment variables.
"""

import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    SWAGGER = {
        'title': 'Simple Shops API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'A simple shop API with products, users, and orders',
    }

    SWAGGER_TEMPLATE = {
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT token. Enter: **Bearer <your-token>**"
            }
        },
        "security": [
            {"Bearer": []}
        ]
    }
