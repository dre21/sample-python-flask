"""
Authentication and authorization helpers.

- hash_password / check_password: bcrypt-based password hashing
- roles_required: decorator that enforces role-based access control via JWT claims
"""

from functools import wraps

import bcrypt
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def hash_password(plain_password):
    """Hash a plain text password using bcrypt."""
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(plain_password, hashed_password):
    """Verify a plain text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def roles_required(*allowed_roles):
    """
    Decorator that checks if the current user has one of the allowed roles.

    Usage:
        @roles_required('admin', 'seller')
        def my_route():
            ...

    How it works:
        1. Verifies the JWT is present and valid (like @jwt_required())
        2. Reads the 'role' claim from the JWT payload
        3. Returns 403 if the user's role is not in the allowed list
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "user")

            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Access denied. Required role(s): {', '.join(allowed_roles)}"
                }), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
