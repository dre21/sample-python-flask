"""
schemas/ — Marshmallow DTO (Data Transfer Object) layer.

Handles:
- Request validation (load) — checks incoming JSON has correct types and required fields
- Response serialization (dump) — converts model objects into clean JSON responses
"""

from schemas.product_schema import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductListSchema,
    ProductDetailSchema,
)
from schemas.user_schema import UserRegisterSchema, UserDetailSchema
from schemas.order_schema import OrderProductSchema, OrderListSchema, OrderDetailSchema
from schemas.auth_schema import LoginSchema
