"""
Auth schemas — login request validation.
"""

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    """DTO for login request."""

    email    = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
