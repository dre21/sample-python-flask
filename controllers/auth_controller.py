"""
Auth controller — route handlers for login and token refresh.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from schemas import LoginSchema, UserDetailSchema
from services import auth_service


# ─── Schema instances ─────────────────────────────────────────────────────────

login_schema       = LoginSchema()
user_detail_schema = UserDetailSchema()


# ─── Blueprint ────────────────────────────────────────────────────────────────

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ─── Routes ───────────────────────────────────────────────────────────────────


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and get a JWT token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: "john@example.com"
            password:
              type: string
              example: "securepassword123"
    responses:
      200:
        description: Login successful, returns access and refresh tokens
        schema:
          type: object
          properties:
            message:
              type: string
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate input using DTO schema
    try:
        validated = login_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    tokens, user = auth_service.authenticate_user(validated['email'], validated['password'])
    if tokens is None:
        return jsonify({'message': 'Invalid email or password', 'status': 'error'}), 401

    return jsonify({
        'message': 'Login successful',
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': user_detail_schema.dump(user)
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Get a new access token using a refresh token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    description: >
      Send the refresh token in the Authorization header as "Bearer <refresh_token>".
      Returns a new access token. The refresh token itself is not rotated.
    responses:
      200:
        description: New access token issued
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()

    access_token, error = auth_service.refresh_access_token(current_user_id)
    if error:
        return jsonify({"message": error["message"], "status": "error"}), error["status_code"]

    return jsonify({"access_token": access_token}), 200
