"""
Configuration class — reads settings from environment variables.

Logging levels per environment:
- local       → DEBUG   (shows everything, great for development)
- development → INFO    (server dev — shows info + warnings + errors)
- production  → WARNING (server prod — only warnings and errors, less noise)
"""

import os
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()


class Config:
    """Base configuration shared across all environments."""

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

    # ─── Logging Configuration ─────────────────────────────────────────────────

    # FLASK_ENV controls which log level is used:
    #   "local"       → DEBUG
    #   "development" → INFO
    #   "production"  → WARNING
    FLASK_ENV = os.getenv('FLASK_ENV', 'local')

    # You can also override the log level directly (takes priority over FLASK_ENV)
    LOG_LEVEL = os.getenv('LOG_LEVEL', None)

    # Log format — includes timestamp, level, logger name, and message
    LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # Map environment names to log levels
    LOG_LEVEL_MAP = {
        'local': 'DEBUG',
        'development': 'INFO',
        'production': 'WARNING',
    }

    @classmethod
    def get_log_level(cls):
        """
        Determine the log level to use.

        Priority:
        1. LOG_LEVEL env var (explicit override)
        2. FLASK_ENV mapped to a level via LOG_LEVEL_MAP
        3. Default: DEBUG
        """
        if cls.LOG_LEVEL:
            return cls.LOG_LEVEL.upper()
        return cls.LOG_LEVEL_MAP.get(cls.FLASK_ENV, 'DEBUG')
