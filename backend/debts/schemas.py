from validate_docbr import CPF
from marshmallow import Schema, fields, validates, ValidationError

from utils.br_bank import BR_BANK_CHOICES


class DebtSchema(Schema):
    id = fields.UUID(dump_only=True)
    cpf = fields.Str(required=True)
    creditor = fields.Str(required=False)
    original_value = fields.Float(required=True)
    due_date = fields.Date(required=False)


    @validates("cpf")
    def validate_cpf(self, value, **kwargs):
        cpf = CPF()

        if not cpf.validate(value):
            raise ValidationError("CPF is not valid")

    @validates("creditor")
    def validate_creditor(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Creditor is required")

        if value.strip() in BR_BANK_CHOICES:
            raise ValidationError("Creditor is not valid in Brazil")
