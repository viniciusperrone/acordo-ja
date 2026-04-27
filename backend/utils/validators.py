import re

from validate_docbr import CPF, CNPJ
from marshmallow import ValidationError


def validate_cnpj_or_cpf(document: str) -> str:
    document = re.sub(r"\D", "", document)

    cpf = CPF()
    cnpj = CNPJ()

    is_valid_cpf = len(document) == 11 and cpf.validate(document)
    is_valid_cnpj = len(document) == 14 and cnpj.validate(document)

    if not (is_valid_cpf or is_valid_cnpj):
        raise ValidationError("CPF or CNPJ must be valid")

    return document
