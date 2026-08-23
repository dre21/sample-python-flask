"""
Order schemas — response serialization.
"""

from marshmallow import Schema, fields


class OrderProductSchema(Schema):
    """DTO for a product inside an order response."""

    id    = fields.Int(dump_only=True)
    name  = fields.Str()
    sku   = fields.Str()
    price = fields.Float()


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
    products = fields.List(fields.Nested(OrderProductSchema))

    def get_username(self, obj):
        """Resolve username from the user relationship."""
        return obj.user.username if obj.user else None
