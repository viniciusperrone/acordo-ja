import re
from validate_docbr import CPF, CNPJ
from marshmallow import Schema, fields, validates, ValidationError


class LeadSchema(Schema):
    id = fields.UUID(dump_only=True)
    name = fields.String(required=True)
    document = fields.String(required=True)
    email = fields.Email(required=True)
    phone = fields.String(required=True)

    created_at = fields.DateTime(dump_only=True)

    @validates("document")
    def validate_document(self, value, **kwargs):
        document = re.sub(r"\D", "", value)

        cpf = CPF()
        cnpj = CNPJ()

        is_valid_cpf = len(document) == 11 and cpf.validate(document)
        is_valid_cnpj = len(document) == 14 and cnpj.validate(document)

        if not (is_valid_cpf or is_valid_cnpj):
            raise ValidationError("CPF or CNPJ must be valid")

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        phone = re.sub(r"\D", "", value)

        if len(phone) not in (10, 11):
            raise ValidationError("Phone number must be 10 or 11")
