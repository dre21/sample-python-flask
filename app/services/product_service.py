"""
Product service — business logic for products and categories.
"""

import logging

from app.models import Product, Category
from app.utils import db

# Create a logger for this module
# The name will be 'app.services.product_service' — helpful for tracing
logger = logging.getLogger(__name__)


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
    logger.info("Fetching products — page=%d, per_page=%d", page, per_page)
    logger.debug("Applied filters: %s", filters)

    query = Product.query

    if filters.get('name'):
        query = query.filter(Product.name.icontains(filters['name']))
        logger.debug("Filter by name: '%s'", filters['name'])

    if filters.get('category_id') is not None:
        query = query.filter_by(category_id=filters['category_id'])
        logger.debug("Filter by category_id: %d", filters['category_id'])

    if filters.get('max_price') is not None:
        query = query.filter(Product.price <= filters['max_price'])
        logger.debug("Filter by max_price: %.2f", filters['max_price'])

    result = query.paginate(page=page, per_page=per_page, error_out=False)
    logger.info("Found %d products (page %d of %d)", result.total, result.page, result.pages)

    return result


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
            logger.warning("Create product failed — category_id=%d not found",
                           validated_data['category_id'])
            return None, {
                "message": f"Category with id {validated_data['category_id']} not found",
                "status_code": 404
            }

    try:
        product = Product(**validated_data)
        db.session.add(product)
        db.session.commit()
        logger.info("Product created — id=%d, name='%s'", product.id, product.name)
        return product, None
    except Exception as e:
        db.session.rollback()
        logger.error("Error creating product: %s", e, exc_info=True)
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
