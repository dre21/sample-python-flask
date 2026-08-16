from flask import Blueprint, jsonify, request
from models import Product, User, Category, Order
from utils import db
from sqlalchemy.exc import IntegrityError


products_bp = Blueprint('products', __name__, url_prefix='/store')
users_bp = Blueprint('users', __name__, url_prefix='/users')
orders_bp = Blueprint('orders', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of products
        schema:
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
    """
    query = Product.query

    print(f"arguments: {request.args}")

    if 'name' in request.args:
        print("filter by name")
        name = request.args.get('name', type=str)
        query = query.filter(Product.name.icontains(name))
        
    if 'category_id' in request.args:
        print("filter by category")
        category_id = request.args.get('category_id', type=int)
        query = query.filter_by(category_id=category_id)

    if 'max_price' in request.args:
        print("filter by max price")
        max_price = request.args.get('max_price', type=float)
        query = query.filter(Product.price <= max_price)

    products = query.all()
    return jsonify([product.show_list() for product in products]), 200


@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product
    ---
    tags:
      - Products
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
      500:
        description: Error creating product
    """
    data = request.get_json()

    try:
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product created successfully",
                        "product": product.show_detail(),
                        "status": "ok"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating product", "status": "error"}), 500


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
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404
    return jsonify(product.show_detail()), 200


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product
    ---
    tags:
      - Products
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
      404:
        description: Product not found
      500:
        description: Error updating product
    """
    data = request.get_json()
    try:
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({"message": "Product not found", "status": "error"}), 404

        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        db.session.commit()
        return jsonify({"message": "Product updated successfully", "product": product.show_detail(), "status": "ok"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product: {e}")
        return jsonify({"message": "Error updating product", "status": "error"}), 500


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product
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
        description: Product deleted successfully
      404:
        description: Product not found
    """
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully",
                    "product": product.show_detail(),
                    "status": "ok"}), 200


@products_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get a category with its products
    ---
    tags:
      - Categories
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
      404:
        description: Category not found
    """
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'products': [
            p.show_list() for p in category.products
        ]
    }), 200


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
              example: "hashed_password_123"
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing required field
      409:
        description: Email already exists
      500:
        description: Error registering user
    """
    data = request.get_json()
    try:
        for field in ['username', 'email', 'password_hash']:
            if field not in data:
                return jsonify({"message": f"Missing required field: {field}", "status": "error"}), 400
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully",
                        "user": user.to_dict(),
                        "status": "ok"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already exists", "status": "error"}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Error registering user: {e}")
        return jsonify({"message": "Error registering user", "status": "error"}), 500


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
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"message": "User not found", "status": "error"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({"message": "Error fetching user", "status": "error"}), 500


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """Get an order by ID
    ---
    tags:
      - Orders
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
      404:
        description: Order not found
    """
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "id": order.id,
        "user_id": order.user.username,
        "total": order.total,
        "products": [
            p.show_list() for p in order.products
        ]
    }), 200
