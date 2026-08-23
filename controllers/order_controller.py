"""
Order controller — route handlers for /orders endpoints.
"""

from flask import Blueprint, jsonify

from middleware.auth import roles_required
from schemas import OrderListSchema, OrderDetailSchema
from services import order_service


# ─── Schema instances ─────────────────────────────────────────────────────────

order_list_schema   = OrderListSchema(many=True)
order_detail_schema = OrderDetailSchema()


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
