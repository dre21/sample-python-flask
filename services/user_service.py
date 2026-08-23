"""
User service — business logic for user registration and lookup.
"""

from sqlalchemy.exc import IntegrityError

from models import User
from utils import db
from middleware.auth import hash_password


def register_user(validated_data):
    """
    Create a new user from validated registration data.

    Args:
        validated_data: dict already validated by UserRegisterSchema

    Returns:
        (user, None) on success
        (None, error_dict) on failure
    """
    try:
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            password_hash=hash_password(validated_data['password_hash']),
            role=validated_data['role']
        )
        db.session.add(user)
        db.session.commit()
        return user, None
    except IntegrityError:
        db.session.rollback()
        return None, {
            "message": "Email already exists",
            "status_code": 409
        }
    except Exception as e:
        db.session.rollback()
        print(f"Error registering user: {e}")
        return None, {
            "message": "Error registering user",
            "status_code": 500
        }


def get_user_by_id(user_id):
    """Fetch a single user by ID. Returns None if not found."""
    return User.query.get(user_id)
