"""
Product & Category controllers — route handlers for /store endpoints.

These are thin: parse the request, call the service, return the response.
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.middleware.auth import roles_required
from app.schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductListSchema,
    ProductDetailSchema,
)
from app.services import product_service

# Create a logger for this module
logger = logging.getLogger(__name__)


# ─── Schema instances (reusable, stateless) ───────────────────────────────────

product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
product_list_schema   = ProductListSchema(many=True)
product_detail_schema = ProductDetailSchema()


# ─── Blueprint ────────────────────────────────────────────────────────────────

products_bp = Blueprint('products', __name__, url_prefix='/store')


# ─── Product Routes ───────────────────────────────────────────────────────────


@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products
    ---
    tags:
      - Products
    parameters:
      - in: query
        name: name
        type: string
        required: false
        description: Filter products by name (case-insensitive, partial match)
      - in: query
        name: category_id
        type: integer
        required: false
        description: Filter products by category ID
      - in: query
        name: max_price
        type: number
        required: false
        description: Filter products with price less than or equal to this value
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: Page number for pagination
      - in: query
        name: per_page
        type: integer
        required: false
        default: 10
        description: Number of items per page
    responses:
      200:
        description: A paginated list of products
        schema:
          type: object
          properties:
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
                  stock_qty:
                    type: integer
                  is_active:
                    type: boolean
            page:
              type: integer
            per_page:
              type: integer
            total:
              type: integer
            pages:
              type: integer
    """
    filters = {
        'name': request.args.get('name', type=str),
        'category_id': request.args.get('category_id', type=int),
        'max_price': request.args.get('max_price', type=float),
    }
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    logger.info("GET /store/products — page=%d, per_page=%d", page, per_page)
    logger.debug("Request args: %s", request.args.to_dict())

    pagination = product_service.get_products(filters, page, per_page)

    logger.debug("Returning %d items to client", len(pagination.items))

    return jsonify({
        "products": product_list_schema.dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages
    }), 200


@products_bp.route('/products', methods=['POST'])
@roles_required('seller')
def create_product():
    """Create a new product
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - sku
            - price
          properties:
            name:
              type: string
              example: "Widget"
            sku:
              type: string
              example: "WDG-001"
            description:
              type: string
              example: "A useful widget"
            price:
              type: number
              example: 19.99
            stock_qty:
              type: integer
              example: 100
            category_id:
              type: integer
              example: 1
    responses:
      201:
        description: Product created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden — seller role required
      404:
        description: Category not found
      500:
        description: Error creating product
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate input using DTO schema
    try:
        validated = product_create_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    product, error = product_service.create_product(validated)
    if error:
        response = {"error": error["message"]}
        if "details" in error:
            response["details"] = error["details"]
        return jsonify(response), error["status_code"]

    return jsonify(product_detail_schema.dump(product)), 201


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a product by ID
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The product ID
    responses:
      200:
        description: Product details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            sku:
              type: string
            description:
              type: string
            price:
              type: number
            stock_qty:
              type: integer
            is_active:
              type: boolean
            category:
              type: string
            created_at:
              type: string
              format: date-time
      404:
        description: Product not found
    """
    product = product_service.get_product_by_id(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404
    return jsonify(product_detail_schema.dump(product)), 200


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@roles_required('seller')
def update_product(product_id):
    """Update a product
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The product ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            sku:
              type: string
            description:
              type: string
            price:
              type: number
            stock_qty:
              type: integer
            category_id:
              type: integer
    responses:
      200:
        description: Product updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden — seller role required
      404:
        description: Product not found
      500:
        description: Error updating product
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate input using DTO schema (partial — all fields optional)
    try:
        validated = product_update_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    product, error = product_service.update_product(product_id, validated)
    if error:
        response = {"error": error["message"]}
        if "details" in error:
            response["details"] = error["details"]
        return jsonify(response), error["status_code"]

    return jsonify(product_detail_schema.dump(product)), 200


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@roles_required('admin')
def delete_product(product_id):
    """Delete a product
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        description: The product ID
    responses:
      200:
        description: Product deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden — admin role required
      404:
        description: Product not found
    """
    product = product_service.get_product_by_id(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404

    # Serialize before deleting (so we can return product details in response)
    product_data = product_detail_schema.dump(product)

    product_service.delete_product(product_id)

    return jsonify({
        "message": "Product deleted successfully",
        "product": product_data,
        "status": "ok"
    }), 200


# ─── Category Routes ──────────────────────────────────────────────────────────


@products_bp.route('/categories/<int:category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """Get a category with its products
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - in: path
        name: category_id
        type: integer
        required: true
        description: The category ID
    responses:
      200:
        description: Category with products
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
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
      401:
        description: Unauthorized
      404:
        description: Category not found
    """
    category = product_service.get_category_by_id(category_id)
    if category is None:
        return jsonify({"message": "Category not found", "status": "error"}), 404

    return jsonify({
        'id': category.id,
        'name': category.name,
        'products': product_list_schema.dump(category.products)
    }), 200
