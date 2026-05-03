import pytest
from marshmallow import ValidationError

from utils.validators import validate_cnpj_or_cpf


@pytest.mark.unit
class TestValidateCnpjOrCpf:

    def test_should_return_clean_document_when_valid_cpf(self):
        document = "529.982.247-25"

        result = validate_cnpj_or_cpf(document)

        assert result == "52998224725"

    def test_should_return_clean_document_when_valid_cnpj(self):
        document = "11.222.333/0001-81"

        result = validate_cnpj_or_cpf(document)

        assert result == "11222333000181"

    def test_should_raise_error_when_document_is_invalid(self):
        document = "12345678900"

        with pytest.raises(ValidationError) as err:
            validate_cnpj_or_cpf(document)

        assert str(err.value) == "CPF or CNPJ must be valid"

    def test_should_raise_error_when_document_has_invalid_length(self):
        document = "123"

        with pytest.raises(ValidationError) as err:
            validate_cnpj_or_cpf(document)

        assert str(err.value) == "CPF or CNPJ must be valid"

    def test_should_raise_error_when_document_is_empty(self):
        document = ""

        with pytest.raises(ValidationError) as err:
            validate_cnpj_or_cpf(document)

        assert str(err.value) == "CPF or CNPJ must be valid"

    def test_should_raise_error_when_document_has_only_non_numeric_chars(self):
        document = "abc.def-gh"

        with pytest.raises(ValidationError) as err:
            validate_cnpj_or_cpf(document)

        assert str(err.value) == "CPF or CNPJ must be valid"
