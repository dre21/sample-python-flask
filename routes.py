from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from marshmallow import ValidationError
from models import Product, User, Category, Order
from utils import db
from sqlalchemy.exc import IntegrityError
from auth import hash_password, check_password, roles_required
from schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductListSchema,
    ProductDetailSchema,
    UserRegisterSchema,
    UserDetailSchema,
    LoginSchema,
    OrderListSchema,
    OrderDetailSchema,
)


# ─── Schema instances (reusable, stateless) ───────────────────────────────────

product_create_schema  = ProductCreateSchema()
product_update_schema  = ProductUpdateSchema()
product_list_schema    = ProductListSchema(many=True)
product_detail_schema  = ProductDetailSchema()
user_register_schema   = UserRegisterSchema()
user_detail_schema     = UserDetailSchema()
login_schema           = LoginSchema()
order_list_schema      = OrderListSchema(many=True)
order_detail_schema    = OrderDetailSchema()


# ─── Blueprints ───────────────────────────────────────────────────────────────

products_bp = Blueprint('products', __name__, url_prefix='/store')
users_bp = Blueprint('users', __name__, url_prefix='/users')
orders_bp = Blueprint('orders', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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
    query = Product.query

    if 'name' in request.args:
        name = request.args.get('name', type=str)
        query = query.filter(Product.name.icontains(name))

    if 'category_id' in request.args:
        category_id = request.args.get('category_id', type=int)
        query = query.filter_by(category_id=category_id)

    if 'max_price' in request.args:
        max_price = request.args.get('max_price', type=float)
        query = query.filter(Product.price <= max_price)

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

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

    # Validate and deserialize input using DTO schema
    try:
        validated = product_create_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Validate category exists if provided
    if validated.get('category_id') is not None:
        category = Category.query.get(validated['category_id'])
        if category is None:
            return jsonify({"error": f"Category with id {validated['category_id']} not found"}), 404

    # Create product from validated data
    try:
        product = Product(**validated)
        db.session.add(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error creating product", "details": str(e)}), 500

    # Serialize response using DTO schema
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
    product = Product.query.get(product_id)
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

    # Check category exists if provided
    if validated.get('category_id') is not None:
        category = Category.query.get(validated['category_id'])
        if category is None:
            return jsonify({"error": f"Category with id {validated['category_id']} not found"}), 404

    # Fetch product
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": f"Product {product_id} not found"}), 404

    # Partial update — only update fields present in validated data
    for key, value in validated.items():
        setattr(product, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error updating product", "details": str(e)}), 500

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
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404

    # Serialize before deleting (so we can return product details in response)
    product_data = product_detail_schema.dump(product)

    db.session.delete(product)
    db.session.commit()
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
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'products': product_list_schema.dump(category.products)
    }), 200


# ─── User Routes ──────────────────────────────────────────────────────────────


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

    try:
        user = User(
            username=validated['username'],
            email=validated['email'],
            password_hash=hash_password(validated['password_hash']),
            role=validated['role']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            "message": "User registered successfully",
            "user": user_detail_schema.dump(user),
            "status": "ok"
        }), 201
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
        return jsonify(user_detail_schema.dump(user)), 200
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({"message": "Error fetching user", "status": "error"}), 500


# ─── Order Routes ─────────────────────────────────────────────────────────────


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
    orders = Order.query.all()
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
    order = Order.query.get_or_404(order_id)
    return jsonify(order_detail_schema.dump(order)), 200


# ─── Auth Routes ──────────────────────────────────────────────────────────────


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

    user = User.query.filter_by(email=validated['email']).first()

    if user is None or not check_password(validated['password'], user.password_hash):
        return jsonify({'message': 'Invalid email or password', 'status': 'error'}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
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
    # get_jwt_identity() returns the identity (user id) from the refresh token
    current_user_id = get_jwt_identity()

    # Look up user to include role in new access token claims
    user = User.query.get(current_user_id)
    if user is None:
        return jsonify({"message": "User not found", "status": "error"}), 401

    new_access_token = create_access_token(
        identity=current_user_id,
        additional_claims={"role": user.role},
        fresh=False  # Refreshed tokens are not "fresh" (not from direct login)
    )

    return jsonify({"access_token": new_access_token}), 200
