from marshmallow import Schema, fields, validate
from utils.enum import MethodPayment


class PaymentSchema(Schema):
    id = fields.UUID(dump_only=True)
    amount = fields.Decimal(required=True, as_string=True)
    method = fields.Enum(
        MethodPayment,
        by_value=True,
        required=True
    )
    installment_id = fields.Integer(dump_only=True)
    paid_at = fields.DateTime(required=False)

    class Meta:
        unknown = "raise"
