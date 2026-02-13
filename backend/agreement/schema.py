from marshmallow import Schema, fields, validate


class AgreementSchema(Schema):
    id = fields.UUID(dump_only=True)
    debt_id = fields.Int(required=True)

    total_traded = fields.Decimal(required=True, as_string=True)
    installment_value = fields.Decimal(required=True, as_string=True)

    qtd_instalments = fields.Int(required=True, validate=validate.Range(min=1))

    entry_value = fields.Decimal(load_default=0, as_string=True)
    discount_applied = fields.Decimal(load_default=0, as_string=True)

    first_due_date = fields.Date(required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "raise"