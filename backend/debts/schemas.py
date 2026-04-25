import re

from marshmallow import Schema, fields, validates, validates_schema, ValidationError
from validate_docbr import CPF, CNPJ

from utils.enum import DebtStatus, DebtHistoryType


class DebtSchema(Schema):
    id = fields.UUID(dump_only=True)

    debtor_id = fields.Int(required=True)
    creditor_id = fields.UUID(required=True)

    original_value = fields.Decimal(as_string=True, required=True)
    updated_value = fields.Decimal(as_string=True, required=False)

    due_date = fields.Date(required=True)
    last_agreement_date = fields.DateTime(dump_only=True)

    status = fields.Enum(
        DebtStatus,
        by_value=True,
        dump_only=True
    )

    renegotiation_count = fields.Int(dump_only=True)

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = "raise"

class DebtSearchByDocumentSchema(Schema):
    document = fields.String(required=True)

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

class DebtHistorySchema(Schema):
    id = fields.UUID()
    event_type = fields.Enum(DebtHistoryType, by_value=True, dump_only=True)

    old_status = fields.Enum(DebtStatus, by_value=True, dump_only=True)
    new_status = fields.Enum(DebtStatus, by_value=True, dump_only=True)

    old_value = fields.Decimal(as_string=True)
    new_value = fields.Decimal(as_string=True)

    changed_at = fields.DateTime()
    reason = fields.String()
    extra = fields.Dict()

    class Meta:
        unknown = "raise"
