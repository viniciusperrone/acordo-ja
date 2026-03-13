import re

from marshmallow import Schema, fields, validate


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-])[A-Za-z\d@$!%*?&.#_\-]{8,}$"
)

class AuthenticationSchema(Schema):
    email = fields.Email(required=True)
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
