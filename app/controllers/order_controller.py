"""
Order controller — route handlers for /orders endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError

from app.middleware.auth import roles_required
from app.schemas import OrderListSchema, OrderDetailSchema, OrderCreateSchema
from app.services import order_service


# ─── Schema instances ─────────────────────────────────────────────────────────

order_list_schema   = OrderListSchema(many=True)
order_detail_schema = OrderDetailSchema()
order_create_schema = OrderCreateSchema()


# ─── Blueprint ────────────────────────────────────────────────────────────────

orders_bp = Blueprint('orders', __name__)


# ─── Routes ───────────────────────────────────────────────────────────────────


@orders_bp.route('/orders', methods=['GET'])
@roles_required('user')
def get_orders():
    """Get all orders
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: A list of all orders
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              total:
                type: number
              status:
                type: string
      401:
        description: Unauthorized
      403:
        description: Forbidden
    """
    orders = order_service.get_all_orders()
    return jsonify(order_list_schema.dump(orders)), 200


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@roles_required('user')
def get_order_by_id(order_id):
    """Get an order by ID
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
        description: The order ID
    responses:
      200:
        description: Order details
        schema:
          type: object
          properties:
            id:
              type: integer
            user_id:
              type: string
              description: Username of the order owner
            total:
              type: number
            products:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  sku:
                    type: string
                  price:
                    type: number
                  quantity:
                    type: integer
      401:
        description: Unauthorized
      403:
        description: Forbidden
      404:
        description: Order not found
    """
    order = order_service.get_order_by_id(order_id)
    if order is None:
        return jsonify({"message": "Order not found", "status": "error"}), 404
    return jsonify(order_detail_schema.dump(order)), 200


@orders_bp.route('/orders', methods=['POST'])
@roles_required('user')
def create_order():
    """Create a new order
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - items
          properties:
            items:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - quantity
                properties:
                  product_id:
                    type: integer
                    description: ID of the product to order
                  quantity:
                    type: integer
                    minimum: 1
                    description: Quantity to order
    responses:
      201:
        description: Order created successfully
        schema:
          type: object
          properties:
            id:
              type: integer
            user_id:
              type: string
            total:
              type: number
            status:
              type: string
            products:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  sku:
                    type: string
                  price:
                    type: number
                  quantity:
                    type: integer
      400:
        description: Validation error or product unavailable
      401:
        description: Unauthorized
      403:
        description: Forbidden
      404:
        description: Product not found
    """
    # Validate request body
    try:
        data = order_create_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"message": "Validation error", "errors": err.messages}), 400

    # Get the current user's ID from the JWT token
    user_id = int(get_jwt_identity())

    # Create the order (assigned to the authenticated user)
    order, error = order_service.create_order(user_id, data['items'])

    if error:
        status_code = error.pop('status_code', 400)
        return jsonify(error), status_code

    return jsonify(order_detail_schema.dump(order)), 201
