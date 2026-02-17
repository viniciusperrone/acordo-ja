from marshmallow import Schema, fields, validate

from debts.schemas import BANK_CODES


class CreditorSchema(Schema):
    id = fields.UUID(dump_only=True)
    bank_code = fields.Str(required=True, validate=validate.OneOf(BANK_CODES))
    interest_rate = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0, max=100)
    )
    fine_rate = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0, max=100)
    )
    discount_limit = fields.Decimal(
        required=True,
        as_string=True,
        validate=validate.Range(min=0, max=100)
    )
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "raise"
