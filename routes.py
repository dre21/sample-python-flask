from flask import Blueprint, jsonify, request
from models import Product, User, Category, Order
from utils import db
from sqlalchemy.exc import IntegrityError


products_bp = Blueprint('products', __name__, url_prefix='/store')
users_bp = Blueprint('users', __name__, url_prefix='/users')
orders_bp = Blueprint('orders', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    # TODO: Query all products, return as JSON list
    products = Product.query.all()
    return jsonify([product.show_list() for product in products]), 200


@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    print(data)

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
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"message": "Product not found", "status": "error"}), 404
    return jsonify(product.show_detail()), 200


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
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
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'products' :[
            p.show_list() for p in category.products
        ]
    }), 200



# POST /users/register
@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    # TODO: Validate required fields: username, email, password_hash
    # TODO: Create User, add to session, commit
    # TODO: Handle IntegrityError (duplicate email) → return 409
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

# GET /users/<id>
@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # TODO: Fetch user by ID, return 404 if not found
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"message": "User not found", "status": "error"}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        print(f"Error fetching user: {e}")
        return jsonify({"message": "Error fetching user", "status": "error"}), 500


# GET /orders/<id>
@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify({
        "id": order.id,
        "user_id": order.user.username,
        "total": order.total,
        "products": [
            p.show_list() for p in order.products
        ]
    }), 200

