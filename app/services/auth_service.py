"""
Auth service — business logic for authentication.
"""

from flask_jwt_extended import create_access_token, create_refresh_token

from app.models import User
from app.middleware.auth import check_password


def authenticate_user(email, password):
    """
    Authenticate a user by email and password.

    Returns:
        (tokens_dict, user) on success — tokens_dict has 'access_token' and 'refresh_token'
        (None, None) on failure (invalid credentials)
    """
    user = User.query.filter_by(email=email).first()

    if user is None or not check_password(password, user.password_hash):
        return None, None

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
    }

    return tokens, user


def refresh_access_token(user_id):
    """
    Issue a new access token for the given user ID (from a valid refresh token).

    Returns:
        (access_token, None) on success
        (None, error_dict) on failure
    """
    user = User.query.get(user_id)
    if user is None:
        return None, {"message": "User not found", "status_code": 401}

    new_access_token = create_access_token(
        identity=user_id,
        additional_claims={"role": user.role},
        fresh=False  # Refreshed tokens are not "fresh" (not from direct login)
    )

    return new_access_token, None
