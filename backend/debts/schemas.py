from validate_docbr import CPF
from marshmallow import Schema, fields, validates, ValidationError, validate

from utils.br_bank import BR_BANK_CHOICES


BANK_CODES = [code for code, _ in BR_BANK_CHOICES]

class DebtSchema(Schema):
    id = fields.Int(dump_only=True)
    cpf = fields.Str(required=True)
    creditor = fields.Str(required=False, validate=validate.OneOf(BANK_CODES))
    original_value = fields.Float(required=True)
    due_date = fields.Date(required=False)


    @validates("cpf")
    def validate_cpf(self, value, **kwargs):
        cpf = CPF()

        if not cpf.validate(value):
            raise ValidationError("CPF is not valid")


    class Meta:
        unknown = "raise"