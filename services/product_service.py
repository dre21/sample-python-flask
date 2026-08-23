"""
Product service — business logic for products and categories.
"""

from models import Product, Category
from utils import db


def get_products(filters, page, per_page):
    """
    Query products with optional filters and pagination.

    Args:
        filters: dict with optional keys 'name', 'category_id', 'max_price'
        page: current page number
        per_page: items per page

    Returns:
        SQLAlchemy Pagination object
    """
    query = Product.query

    if filters.get('name'):
        query = query.filter(Product.name.icontains(filters['name']))

    if filters.get('category_id') is not None:
        query = query.filter_by(category_id=filters['category_id'])

    if filters.get('max_price') is not None:
        query = query.filter(Product.price <= filters['max_price'])

    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_product_by_id(product_id):
    """Fetch a single product by ID. Returns None if not found."""
    return Product.query.get(product_id)


def create_product(validated_data):
    """
    Create a new product from validated data.

    Args:
        validated_data: dict already validated by ProductCreateSchema

    Returns:
        (product, None) on success
        (None, error_dict) on failure — error_dict has 'message' and 'status_code'
    """
    # Validate category exists if provided
    if validated_data.get('category_id') is not None:
        category = Category.query.get(validated_data['category_id'])
        if category is None:
            return None, {
                "message": f"Category with id {validated_data['category_id']} not found",
                "status_code": 404
            }

    try:
        product = Product(**validated_data)
        db.session.add(product)
        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, {
            "message": "Error creating product",
            "details": str(e),
            "status_code": 500
        }


def update_product(product_id, validated_data):
    """
    Update an existing product with validated data.

    Args:
        product_id: ID of the product to update
        validated_data: dict already validated by ProductUpdateSchema

    Returns:
        (product, None) on success
        (None, error_dict) on failure
    """
    # Validate category exists if provided
    if validated_data.get('category_id') is not None:
        category = Category.query.get(validated_data['category_id'])
        if category is None:
            return None, {
                "message": f"Category with id {validated_data['category_id']} not found",
                "status_code": 404
            }

    product = Product.query.get(product_id)
    if product is None:
        return None, {
            "message": f"Product {product_id} not found",
            "status_code": 404
        }

    # Partial update — only update fields present in validated data
    for key, value in validated_data.items():
        setattr(product, key, value)

    try:
        db.session.commit()
        return product, None
    except Exception as e:
        db.session.rollback()
        return None, {
            "message": "Error updating product",
            "details": str(e),
            "status_code": 500
        }


def delete_product(product_id):
    """
    Delete a product by ID.

    Returns:
        (product, None) on success — product is the deleted object (before commit)
        (None, error_dict) on failure
    """
    product = Product.query.get(product_id)
    if product is None:
        return None, {
            "message": "Product not found",
            "status_code": 404
        }

    db.session.delete(product)
    db.session.commit()
    return product, None


def get_category_by_id(category_id):
    """Fetch a single category by ID. Returns None if not found."""
    return Category.query.get(category_id)
