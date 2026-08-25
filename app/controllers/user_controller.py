"""
User controller — route handlers for /users endpoints.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.schemas import UserRegisterSchema, UserDetailSchema
from app.services import user_service


# ─── Schema instances ─────────────────────────────────────────────────────────

user_register_schema = UserRegisterSchema()
user_detail_schema   = UserDetailSchema()


# ─── Blueprint ────────────────────────────────────────────────────────────────

users_bp = Blueprint('users', __name__, url_prefix='/users')


# ─── Routes ───────────────────────────────────────────────────────────────────


@users_bp.route('/register', methods=['POST'])
def register_user():
    """Register a new user
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password_hash
            - role
          properties:
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              format: email
              example: "john@example.com"
            password_hash:
              type: string
              example: "securepassword123"
            role:
              type: string
              example: "user"
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Email already exists
      500:
        description: Error registering user
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate input using DTO schema
    try:
        validated = user_register_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user, error = user_service.register_user(validated)
    if error:
        return jsonify({"message": error["message"], "status": "error"}), error["status_code"]

    return jsonify({
        "message": "User registered successfully",
        "user": user_detail_schema.dump(user),
        "status": "ok"
    }), 201


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user by ID
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The user ID
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            role:
              type: string
            email:
              type: string
            created_at:
              type: string
              format: date-time
      404:
        description: User not found
      500:
        description: Error fetching user
    """
    try:
        user = user_service.get_user_by_id(user_id)
        if user is None:
            return jsonify({"message": "User not found", "status": "error"}), 404
        return jsonify(user_detail_schema.dump(user)), 200
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({"message": "Error fetching user", "status": "error"}), 500
