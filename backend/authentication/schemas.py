import re

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-])[A-Za-z\d@$!%*?&.#_\-]{8,}$"
)

password_validators = [
    validate.Length(min=8, error="Password must be at least 8 characters long."),
    validate.Regexp(
        PASSWORD_REGEX,
        error=(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one number and one special character."
        )
    )
]


class AuthenticationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
        unknown = "raise"

class UpdatePasswordSchema(Schema):
    old_password = fields.String(required=True, load_only=True)
    new_password = fields.String(
        required=True,
        load_only=True,
        validate=password_validators,
    )
    confirm_password = fields.String(
        required=True,
        load_only=True,
        validate=password_validators,
    )

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        if data.get("new_password") != data.get("confirm_password"):
            raise ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )
