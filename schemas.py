"""
schemas.py — DTO (Data Transfer Object) layer using Marshmallow.

Handles:
- Request validation (load) — checks incoming JSON has correct types and required fields
- Response serialization (dump) — converts model objects into clean JSON responses

Each resource has separate schemas for input (Create/Update) and output (Response/List).
"""

from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    # DTO for creating a product. All required fields must be present in the request body.

    name        = fields.Str(required=True, validate=validate.Length(min=5, max=100))
    sku         = fields.Str(required=True, validate=validate.Length(min=5, max=50))
    description = fields.Str(load_default=None)
    price       = fields.Float(required=True, validate=validate.Range(min=0))
    stock_qty   = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))
    is_active   = fields.Bool(load_default=True)
    category_id = fields.Int(load_default=None)


class ProductUpdateSchema(Schema):
    # DTO for updating a product. All fields are optional — only provided fields get updated."""

    name        = fields.Str(validate=validate.Length(min=5, max=100))
    sku         = fields.Str(validate=validate.Length(min=5, max=50))
    description = fields.Str()
    price       = fields.Float(validate=validate.Range(min=0))
    stock_qty   = fields.Int(strict=True, validate=validate.Range(min=0))
    is_active   = fields.Bool()
    category_id = fields.Int()


class ProductListSchema(Schema):
    # DTO for product list responses.

    id         = fields.Int(dump_only=True)
    name       = fields.Str()
    sku        = fields.Str()
    price      = fields.Float()
    stock_qty  = fields.Int()
    category   = fields.Method("get_category_name")
    is_active  = fields.Bool()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class ProductDetailSchema(ProductListSchema):
    # DTO for single product responses with full detail including description and timestamps.

    description = fields.Str()
    created_at  = fields.DateTime(format="iso")


class UserRegisterSchema(Schema):
    # DTO for user registration.

    username      = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    email         = fields.Email(required=True)
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    role          = fields.Str(required=True, validate=validate.OneOf(["user", "seller", "admin"]))


class UserDetailSchema(Schema):
    # DTO for user responses, never exposes password_hash.

    id         = fields.Int(dump_only=True)
    username   = fields.Str()
    role       = fields.Str()
    email      = fields.Email()
    created_at = fields.DateTime(format="iso")


class LoginSchema(Schema):
    # DTO for login request.

    email    = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))



class OrderProductSchema(Schema):
    # DTO for a product inside an order response.

    id    = fields.Int(dump_only=True)
    name  = fields.Str()
    sku   = fields.Str()
    price = fields.Float()


class OrderListSchema(Schema):
    # DTO for order list responses.

    id     = fields.Int(dump_only=True)
    name   = fields.Method("get_username")
    total  = fields.Float()
    status = fields.Str()

    def get_username(self, obj):
        return obj.user.username if obj.user else None


class OrderDetailSchema(Schema):
    # DTO for single order response, full detail with products.

    id       = fields.Int(dump_only=True)
    user_id  = fields.Method("get_username")
    total    = fields.Float()
    products = fields.List(fields.Nested(OrderProductSchema))

    def get_username(self, obj):
        """Resolve username from the user relationship."""
        return obj.user.username if obj.user else None
