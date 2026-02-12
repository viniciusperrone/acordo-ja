import re
from validate_docbr import CPF, CNPJ
from marshmallow import Schema, fields, validates, ValidationError


class DebtorSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    document = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("document")
    def validate_document(self, value, **kwargs):
        document = re.sub(r"\D", "", value)

        cpf = CPF()
        cnpj = CNPJ()

        is_valid_cpf = len(document) == 11 and cpf.validate(document)
        is_valid_cnpj = len(document) == 14 and cnpj.validate(document)

        if not (is_valid_cpf or is_valid_cnpj):
            raise ValidationError("CPF or CNPJ must be valid")

    class Meta:
        unknown = "raise"