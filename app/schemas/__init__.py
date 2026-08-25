"""
schemas/ — Marshmallow DTO (Data Transfer Object) layer.

Handles:
- Request validation (load) — checks incoming JSON has correct types and required fields
- Response serialization (dump) — converts model objects into clean JSON responses
"""

from app.schemas.product_schema import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductListSchema,
    ProductDetailSchema,
)
from app.schemas.user_schema import UserRegisterSchema, UserDetailSchema
from app.schemas.order_schema import OrderProductSchema, OrderListSchema, OrderDetailSchema
from app.schemas.auth_schema import LoginSchema
