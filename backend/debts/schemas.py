from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from utils.enum import DebtStatus


class DebtSchema(Schema):
    id = fields.UUID(dump_only=True)

    debtor_id = fields.Int(required=True)
    creditor_id = fields.UUID(required=True)

    original_value = fields.Decimal(as_string=True, required=True)
    updated_value = fields.Decimal(as_string=True, required=True)

    due_date = fields.Date(required=True)
    last_agreement_date = fields.DateTime(dump_only=True)

    status = fields.Str(
        validate=validate.OneOf([status.name for status in DebtStatus]),
        dump_only=True
    )

    renegotiation_count = fields.Int(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_values(self, data, **kwargs):
        original_value = data.get("original_value")
        updated_value = data.get("updated_value")

        if original_value is not None and original_value <= 0:
            raise ValidationError("Original value must be greater than 0", field_name="original_value")

        if updated_value is not None:
            if updated_value <= 0:
                raise ValidationError("Updated value must be greater than 0", field_name="updated_value")

            if original_value is not None and updated_value < original_value:
                raise ValidationError(
                    "Updated value must be greater than or equal to original value",
                    field_name="updated_value"
                )


    class Meta:
        unknown = "raise"
