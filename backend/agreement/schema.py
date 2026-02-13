from decimal import Decimal, ROUND_HALF_UP
from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class AgreementSchema(Schema):
    id = fields.UUID(dump_only=True)
    debt_id = fields.Int(required=True)

    total_traded = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal("0.01")))
    installment_value = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal("0.01")))
    installments_quantity = fields.Int(required=True, validate=validate.Range(min=1))

    entry_value = fields.Decimal(load_default=Decimal("0.00"), as_string=True, validate=validate.Range(min=Decimal("0.00")))
    discount_applied = fields.Decimal(load_default=Decimal("0.00"), as_string=True, validate=validate.Range(min=Decimal("0.00")))

    first_due_date = fields.Date(required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_rules(self, data, **kwargs):
        total = data.get('total_traded')
        installment_value = data.get('installment_value')
        installments_quantity = data.get('installments_quantity')
        entry_value = data.get('entry_value', Decimal('0.00'))
        discount_applied = data.get("discount_applied", Decimal("0.00"))

        if (
            total is not None
            and installment_value is not None
            and installments_quantity is not None
        ):

            gross_total = (
                  installment_value * installments_quantity
            ) + entry_value

            if discount_applied > gross_total:
                raise ValidationError({
                    "discount_applied": "Discount cannot exceed gross total."
                })

            calculated_total = gross_total - discount_applied

            total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            calculated_total = calculated_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if calculated_total <= Decimal("0.00"):
                raise ValidationError(
                    "Calculated total must be greater than zero."
                )

            if total != calculated_total:
                raise ValidationError(
                    "total_traded must be equal to "
                    "(installment_value * installments_quantity) "
                    "+ entry_value - discount_applied"
                )

    class Meta:
        unknown = "raise"
