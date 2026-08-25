"""
User schemas — request validation and response serialization.
"""

from marshmallow import Schema, fields, validate


class UserRegisterSchema(Schema):
    """DTO for user registration."""

    username      = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    email         = fields.Email(required=True)
    password_hash = fields.Str(required=True, validate=validate.Length(min=6))
    role          = fields.Str(required=True, validate=validate.OneOf(["user", "seller", "admin"]))


class UserDetailSchema(Schema):
    """DTO for user responses, never exposes password_hash."""

    id         = fields.Int(dump_only=True)
    username   = fields.Str()
    role       = fields.Str()
    email      = fields.Email()
    created_at = fields.DateTime(format="iso")
