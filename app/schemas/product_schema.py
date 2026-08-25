"""
Product schemas — request validation and response serialization.
"""

from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    """DTO for creating a product. All required fields must be present in the request body."""

    name        = fields.Str(required=True, validate=validate.Length(min=5, max=100))
    sku         = fields.Str(required=True, validate=validate.Length(min=5, max=50))
    description = fields.Str(load_default=None)
    price       = fields.Float(required=True, validate=validate.Range(min=0))
    stock_qty   = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))
    is_active   = fields.Bool(load_default=True)
    category_id = fields.Int(load_default=None)


class ProductUpdateSchema(Schema):
    """DTO for updating a product. All fields are optional — only provided fields get updated."""

    name        = fields.Str(validate=validate.Length(min=5, max=100))
    sku         = fields.Str(validate=validate.Length(min=5, max=50))
    description = fields.Str()
    price       = fields.Float(validate=validate.Range(min=0))
    stock_qty   = fields.Int(strict=True, validate=validate.Range(min=0))
    is_active   = fields.Bool()
    category_id = fields.Int()


class ProductListSchema(Schema):
    """DTO for product list responses."""

    id        = fields.Int(dump_only=True)
    name      = fields.Str()
    sku       = fields.Str()
    price     = fields.Float()
    stock_qty = fields.Int()
    category  = fields.Method("get_category_name")
    is_active = fields.Bool()

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class ProductDetailSchema(ProductListSchema):
    """DTO for single product responses with full detail including description and timestamps."""

    description = fields.Str()
    created_at  = fields.DateTime(format="iso")
