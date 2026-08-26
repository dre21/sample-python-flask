"""
Order schemas — response serialization.
"""

from marshmallow import Schema, fields


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
    products = fields.List(fields.Nested(OrderProductSchema), attribute='order_items')

    def get_username(self, obj):
        """Resolve username from the user relationship."""
        return obj.user.username if obj.user else None
