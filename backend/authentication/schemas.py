import re

from marshmallow import Schema, fields, validate


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.#_\-])[A-Za-z\d@$!%*?&.#_\-]{8,}$"
)

class AuthenticationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

    class Meta:
        unknown = "raise"
