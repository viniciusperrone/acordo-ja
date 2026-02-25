from marshmallow import Schema, fields, validate, validates, ValidationError

from utils.enum import InstallmentStatus


class InstallmentSchema(Schema):
    id = fields.Int(dump_only=True)

    installment_number = fields.Int(required=True)
    due_date = fields.Date(required=True)
    payment_date = fields.Date(required=False, allow_none=True)
    value = fields.Float(required=True)
    status = fields.Enum(InstallmentStatus, dump_only=True)
    agreement_id = fields.UUID(required=True)


    class Meta:
        unknown = "raise"

    @validates("value")
    def validate_value(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Installment value must be greater than zero.")