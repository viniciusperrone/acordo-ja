from marshmallow import Schema, fields, validate

from utils.choices import INSTALLMENT_STATUS_CHOICES


class InstallmentSchema(Schema):
    id = fields.Int(dump_only=True)

    installment_number = fields.Int(required=True)
    due_date = fields.Date(required=True)
    payment_date = fields.Date(required=False, allow_none=True)
    value = fields.Float(required=True)
    status = fields.Str(required=True,
                        validate=validate.OneOf(INSTALLMENT_STATUS_CHOICES))
    agreement_id = fields.UUID(required=True)


    class Meta:
        unknown = "raise"
