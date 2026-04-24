import re

from marshmallow import Schema, fields, validate

from utils.enum import UserRole


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-])[A-Za-z\d@$!%*?&.#_\-]{8,}$"
)

class UserSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    email = fields.Email(required=True)
    role = fields.Enum(UserRole, dump_only=True)
    must_change_password = fields.Boolean(dump_only=True)

    password = fields.String(
        required=True,
        load_only=True,
        validate=[
            validate.Length(min=8, error="Password must be at least 8 characters long."),
            validate.Regexp(
                PASSWORD_REGEX,
                error=(
                    "Password must contain at least one uppercase letter, "
                    "one lowercase letter, one number and one special character."
                ),
            ),
        ],
    )

    class Meta:
        unknown = "raise"

class UserUpdateSchema(Schema):
    name = fields.String(required=False)
    email = fields.Email(required=False)
    role = fields.Enum(UserRole, required=False)

    class Meta:
        unknown = "raise"

class UserResponseSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    email = fields.Email()
    role = fields.Enum(UserRole)
