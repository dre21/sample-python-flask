"""
Order schemas — request validation and response serialization.
"""

from marshmallow import Schema, fields, validate


# ─── Request Schemas (load) ───────────────────────────────────────────────────


class OrderItemCreateSchema(Schema):
    """DTO for a single item in a create order request."""

    product_id = fields.Int(required=True)
    quantity   = fields.Int(required=True, validate=validate.Range(min=1))


class OrderCreateSchema(Schema):
    """DTO for creating an order. Expects a list of product_id + quantity pairs."""

    items = fields.List(
        fields.Nested(OrderItemCreateSchema),
        required=True,
        validate=validate.Length(min=1),
    )


# ─── Response Schemas (dump) ──────────────────────────────────────────────────


class OrderProductSchema(Schema):
    """DTO for a product inside an order response."""

    id       = fields.Method("get_product_id")
    name     = fields.Method("get_name")
    sku      = fields.Method("get_sku")
    price    = fields.Method("get_price")
    quantity = fields.Int()

    def get_product_id(self, obj):
        return obj.product_id

    def get_name(self, obj):
        return obj.product.name if obj.product else None

    def get_sku(self, obj):
        return obj.product.sku if obj.product else None

    def get_price(self, obj):
        return obj.product.price if obj.product else None


class OrderListSchema(Schema):
    """DTO for order list responses."""

    id     = fields.Int(dump_only=True)
    name   = fields.Method("get_username")
    total  = fields.Float()
    status = fields.Str()

    def get_username(self, obj):
        return obj.user.username if obj.user else None


class OrderDetailSchema(Schema):
    """DTO for single order response, full detail with products."""

    id       = fields.Int(dump_only=True)
    user_id  = fields.Method("get_username")
    total    = fields.Float()
    status   = fields.Str()
    products = fields.List(fields.Nested(OrderProductSchema), attribute='order_items')

    def get_username(self, obj):
        """Resolve username from the user relationship."""
        return obj.user.username if obj.user else None
