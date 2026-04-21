import re
from validate_docbr import CPF, CNPJ
from marshmallow import Schema, fields, validates, pre_load, ValidationError


class DebtorSchema(Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    document = fields.String(required=True)
    email = fields.Email(required=True)
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

    @validates("phone")
    def validate_phone(self, value, **kwargs):
        phone = re.sub(r"\D", "", value)

        if len(phone) not in (10, 11):
            raise ValidationError("Phone number must be 10 or 11")

    @pre_load
    def normalize_fields(self, data, **kwargs):
        if "document" in data:
            data["document"] = re.sub(r"\D", "", data["document"])

        if "phone" in data:
            data["phone"] = re.sub(r"\D", "", data["phone"])

        return data

    class Meta:
        unknown = "raise"