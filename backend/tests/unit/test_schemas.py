import pytest

import uuid
from decimal import Decimal
from datetime import datetime, date
from marshmallow import ValidationError

from users.schemas import UserSchema, UserUpdateSchema, UserResponseSchema
from leads.schemas import LeadSchema
from authentication.schemas import AuthenticationSchema, ResetPasswordSchema, UpdatePasswordSchema, ForgotPasswordSchema
from creditor.schemas import CreditorSchema
from debtor.schemas import DebtorSchema
from debts.schemas import DebtSchema, DebtSearchResponseSchema, DebtHistorySchema, DebtSearchByDocumentSchema
from agreement.schemas import AgreementSchema
from installments.schemas import InstallmentSchema
from payment.schemas import PaymentSchema

from utils.enum import UserRole, MethodPayment, InstallmentStatus, DebtStatus, DebtHistoryType


@pytest.mark.unit
class TestUserSchema:

    def test_should_load_valid_user_data(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": "Strong@123"
        }

        result = schema.load(data)

        assert result["name"] == data["name"]
        assert result["email"] == data["email"]
        assert result["password"] == data["password"]

    def test_should_raise_validation_error_when_required_fields_are_missing(self):
        schema = UserSchema()

        with pytest.raises(ValidationError) as err:
            schema.load({})

        assert "name" in err.value.messages
        assert "email" in err.value.messages
        assert "password" in err.value.messages

    def test_should_raise_validation_error_when_email_is_invalid(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "invalid-email",
            "password": "Strong@123",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_validation_error_when_password_is_too_short(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": "Aa1@",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "password" in err.value.messages
        assert (
            err.value.messages["password"][0]
            == "Password must be at least 8 characters long."
        )

    @pytest.mark.parametrize(
        "password",
        [
            "lowercase123@",
            "UPPERCASE123@",
            "NoNumber@",
            "NoSpecial123",
        ]
    )
    def test_should_raise_validation_error_when_password_does_not_match_regex(self, password):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": password,
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "password" in err.value.messages
        assert (
            err.value.messages["password"][0]
            == (
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number and one special character."
            )
        )

    def test_should_raise_validation_error_when_unknown_field_is_provided(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": "Strong@123",
            "unknown": "unexpected field"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown" in err.value.messages

    def test_should_raise_validation_error_when_dump_only_field_is_provided(self):
        schema = UserSchema()

        data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "João",
            "email": "joao@email.com",
            "password": "Strong@123"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "id" in err.value.messages

    def test_should_not_include_password_in_dump(self):
        schema = UserSchema()

        user = {
            "id": uuid.uuid4(),
            "name": "João",
            "email": "joao@email.com",
            "password": "Strong@123",
            "role": UserRole.ADMIN,
            "must_change_password": False,
        }

        result = schema.dump(user)

        assert "password" not in result

@pytest.mark.unit
class TestUserUpdateSchema:

    def test_should_load_partial_user_update_data(self):
        schema = UserUpdateSchema()

        data = {
            "name": "Novo Nome"
        }

        result = schema.load(data)

        assert result["name"] == "Novo Nome"

    def test_should_raise_validation_error_when_email_is_invalid(self):
        schema = UserUpdateSchema()

        data = {
            "email": "invalid-email"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_validation_error_when_role_is_invalid(self):
        schema = UserUpdateSchema()

        data = {
            "role": "INVALID_ROLE"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "role" in err.value.messages

@pytest.mark.unit
class TestUserResponseSchema:

    def test_should_dump_user_response_schema_correctly(self):
        schema = UserResponseSchema()

        user = {
            "id": uuid.uuid4(),
            "name": "João",
            "email": "joao@email.com",
            "role": UserRole.ADMIN
        }

        result = schema.dump(user)

        assert result["name"] == "João"
        assert result["email"] == "joao@email.com"
        assert result["role"] == UserRole.ADMIN.value
        assert "password" not in result

@pytest.mark.unit
class TestLeadSchema:

    def test_should_load_valid_lead_data(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.com",
            "phone": "11999999999",
        }

        result = schema.load(lead)

        assert result["name"] == lead["name"]
        assert result["document"] == lead["document"]
        assert result["email"] == lead["email"]
        assert result["phone"] == lead["phone"]

    def test_should_raise_validation_error_when_required_fields_are_missing(
        self,
    ):
        schema = LeadSchema()

        with pytest.raises(ValidationError) as err:
            schema.load({})

        assert "name" in err.value.messages
        assert "email" in err.value.messages
        assert "phone" in err.value.messages

    def test_should_raise_validation_error_when_document_is_invalid(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "123456789",
            "email": "joao@test.com",
            "phone": "11999999999",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "document" in err.value.messages
        assert (
            err.value.messages["document"][0]
            == "CPF or CNPJ must be valid"
        )

    @pytest.mark.parametrize(
        "document",
        [
            "52998224725",
            "04.252.011/0001-10",
        ],
    )
    def test_should_accept_valid_cpf_and_cnpj_documents(
        self,
        document,
    ):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": document,
            "email": "joao@test.com",
            "phone": "11999999999",
        }

        result = schema.load(lead)

        assert result["document"] == document

    @pytest.mark.parametrize(
        "phone",
        [
            "2132434",
            "123",
            "999999999999",
        ],
    )
    def test_should_raise_validation_error_when_phone_is_invalid(
        self,
        phone,
    ):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.com",
            "phone": phone,
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "phone" in err.value.messages
        assert (
            err.value.messages["phone"][0]
            == "Phone number must be 10 or 11"
        )

    def test_should_raise_validation_error_when_email_is_invalid(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "invalid-email",
            "phone": "11999999999",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "email" in err.value.messages

    def test_should_raise_validation_error_when_unknown_field_is_provided(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.com",
            "phone": "11999999999",
            "unexpected": "field",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "unexpected" in err.value.messages

    def test_should_raise_validation_error_when_dump_only_id_is_provided(self):
        schema = LeadSchema()

        lead = {
            "id": str(uuid.uuid4()),
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.com",
            "phone": "11999999999",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "id" in err.value.messages

    def test_should_not_include_dump_only_fields_in_load_result(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.com",
            "phone": "11999999999",
        }

        result = schema.load(lead)

        assert "id" not in result
        assert "created_at" not in result

@pytest.mark.unit
class TestAuthenticationSchema:

    def test_should_raise_error_when_password_is_missing(self):
        schema = AuthenticationSchema()

        data = {
            "email": "test@gmail.com"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "password" in err.value.messages

    def test_should_raise_error_when_email_is_missing(self):
        schema = AuthenticationSchema()

        data = {
            "password": "AcordoJA@2026"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_error_when_email_is_invalid(self):
        schema = AuthenticationSchema()

        data = {
            "email": "joao.silva",
            "password": "AcordoJA@2026"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = AuthenticationSchema()

        data = {
            "email": "joao.silva@gmail.com",
            "password": "AcordoJA@2026"
        }

        result = schema.load(data)

        assert result["email"] == data["email"]
        assert result["password"] == data["password"]

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = AuthenticationSchema()

        data = {
            "email": "joao.silva@gmail.com",
            "password": "AcordoJA@2026",
            "extra": "campo_invalido"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "extra" in err.value.messages

    def test_should_raise_error_when_email_is_not_string(self):
        schema = AuthenticationSchema()

        data = {
            "email": 123,
            "password": "AcordoJA@2026"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_error_when_password_is_not_string(self):
        schema = AuthenticationSchema()

        data = {
            "email": "joao.silva@gmail.com",
            "password": True
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "password" in err.value.messages

@pytest.mark.unit
class TestUpdatePasswordSchema:

    def test_should_raise_error_when_old_password_is_missing(self):
        schema = UpdatePasswordSchema()

        data = {
            "new_password": "AcordoJA@2026",
            "confirm_password": "AcordoJA@2026",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "old_password" in err.value.messages

    def test_should_raise_error_when_new_password_is_missing(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2026",
            "confirm_password": "AcordoJA@2026",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "new_password" in err.value.messages

    def test_should_raise_error_when_confirm_password_is_missing(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2026",
            "new_password": "AcordoJA@2026",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "confirm_password" in err.value.messages

    def test_should_raise_error_when_data_has_invalid_type(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": 123,
            "new_password": 123,
            "confirm_password": 123
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "old_password" in err.value.messages
        assert "new_password" in err.value.messages
        assert "confirm_password" in err.value.messages

    def test_should_raise_error_when_new_password_is_invalid_format(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2025",
            "new_password": "abc",
            "confirm_password": "AcordoJA@2026",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "new_password" in err.value.messages

    def test_should_raise_error_when_confirm_password_is_invalid_format(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2025",
            "new_password": "AcordoJA@2026",
            "confirm_password": "abc",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "confirm_password" in err.value.messages

    def test_should_raise_error_when_password_does_not_match(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2025",
            "new_password": "AcordoJA@2026",
            "confirm_password": "AcordoJA@2025",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "confirm_password" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = UpdatePasswordSchema()

        data = {
            "old_password": "AcordoJA@2025",
            "new_password": "AcordoJA@2026",
            "confirm_password": "AcordoJA@2026",
        }

        result = schema.load(data)

        assert result["old_password"] == "AcordoJA@2025"
        assert result["new_password"] == "AcordoJA@2026"
        assert result["confirm_password"] == "AcordoJA@2026"


@pytest.mark.unit
class TestForgotPasswordSchema:

    def test_should_raise_error_when_email_is_missing(self):
        schema = ForgotPasswordSchema()

        data = {}

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_error_when_email_has_invalid_format(self):
        schema = ForgotPasswordSchema()

        data = {
            "email": "joao.silva"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_error_when_email_has_invalid_type(self):
        schema = ForgotPasswordSchema()

        data = {
            "email": 123
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = ForgotPasswordSchema()

        data = {
            "email": "joao.silva@gmail.com"
        }

        result = schema.load(data)

        assert result["email"] == data["email"]


@pytest.mark.unit
class TestResetPasswordSchema:

    def test_should_raise_error_when_data_has_invalid_format(self):
        schema = ResetPasswordSchema()

        data = {
            "new_password": 123,
            "confirm_password": 123,
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "new_password" in err.value.messages
        assert "confirm_password" in err.value.messages

    def test_should_raise_error_when_passwords_does_not_match(self):
        schema = ResetPasswordSchema()

        data = {
            "new_password": "AcordoJA@2025",
            "confirm_password": "AcordoJA@2026",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "confirm_password" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = ResetPasswordSchema()

        data = {
            "new_password": "AcordoJA@2026",
            "confirm_password": "AcordoJA@2026",
        }

        result = schema.load(data)

        assert result["new_password"] == "AcordoJA@2026"
        assert result["confirm_password"] == "AcordoJA@2026"

@pytest.mark.unit
class TestCreditorSchema:

    def test_should_raise_error_when_bank_code_is_missing(self):
        schema = CreditorSchema()

        data = {
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "bank_code" in err.value.messages

    def test_should_raise_error_when_interest_rate_is_missing(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "interest_rate" in err.value.messages

    def test_should_raise_error_when_fine_rate_is_missing(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "discount_limit": Decimal("15.00"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "fine_rate" in err.value.messages

    def test_should_raise_error_when_discount_limit_is_missing(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "discount_limit" in err.value.messages

    def test_should_raise_error_when_interest_rate_is_out_of_range(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("150.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "interest_rate" in err.value.messages
        assert "Must be greater than or equal to 0 and less than or equal to 100" in str(err.value)

    def test_should_raise_error_when_fine_rate_is_out_of_range(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("-5.00"),
            "discount_limit": Decimal("15.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "fine_rate" in err.value.messages
        assert "Must be greater than or equal to 0 and less than or equal to 100." in str(err.value)

    def test_should_raise_error_when_discount_limit_is_out_of_range(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("150.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "discount_limit" in err.value.messages
        assert "Must be greater than or equal to 0 and less than or equal to 100." in str(err.value)

    def test_should_raise_error_when_bank_code_is_invalid(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "999",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "bank_code" in err.value.messages
        assert "Must be one of" in str(err.value)

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00"),
            "extra_field": "unexpected_value"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "extra_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00")
        }

        result = schema.load(data)

        assert result["bank_code"] == data["bank_code"]
        assert result["interest_rate"] == data["interest_rate"]
        assert result["fine_rate"] == data["fine_rate"]
        assert result["discount_limit"] == data["discount_limit"]

    def test_should_dump_successfully_with_valid_data(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("10.00"),
            "fine_rate": Decimal("5.00"),
            "discount_limit": Decimal("15.00")
        }

        result = schema.dump(data)

        assert result["bank_code"] == data["bank_code"]
        assert result["interest_rate"] == str(data["interest_rate"])
        assert result["fine_rate"] == str(data["fine_rate"])
        assert result["discount_limit"] == str(data["discount_limit"])

@pytest.mark.unit
class TestDebtorSchema:

    def test_should_raise_error_when_name_is_missing(self):
        schema = DebtorSchema()

        data = {
            "document": "12345678901",
            "email": "test@gmail.com",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "name" in err.value.messages

    def test_should_raise_error_when_document_is_missing(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "email": "test@gmail.com",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages

    def test_should_raise_when_email_is_missing(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678901",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "email" in err.value.messages

    def test_should_raise_error_when_phone_is_missing(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678901",
            "email": "test@gmail.com"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "phone" in err.value.messages

    def test_should_raise_error_document_is_invalid_cpf(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678900",
            "email": "test@gmail.com",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "CPF or CNPJ must be valid" in str(err.value)

    def test_should_raise_error_when_document_is_invalid_cnpj(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "99999999999999",
            "email": "test@gmail.com",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "CPF or CNPJ must be valid" in str(err.value)

    def test_should_raise_error_when_phone_is_invalid_length(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678901",
            "email": "test@gmail.com",
            "phone": "12345"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "Phone number must be 10 or 11" in str(err.value)

    def test_should_raise_error_when_phone_is_invalid_length_too_long(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678901",
            "email": "test@gmail.com",
            "phone": "123456789012"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "Phone number must be 10 or 11" in str(err.value)

    def test_should_normalize_document_and_phone_on_pre_load(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "529.982.247-25",
            "email": "test@gmail.com",
            "phone": "(11) 99999-9999"
        }

        normalized_data = schema.load(data)

        assert normalized_data["document"] == "52998224725"
        assert normalized_data["phone"] == "11999999999"

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = DebtorSchema()

        data = {
            "name": "João Silva",
            "document": "12345678901",
            "email": "test@gmail.com",
            "phone": "11999999999",
            "unknown_field": "some_value"  # Campo não esperado
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = CreditorSchema()

        data = {
            "bank_code": "001",
            "interest_rate": Decimal("5.00"),
            "fine_rate": Decimal("2.00"),
            "discount_limit": Decimal("10.00")
        }

        result = schema.load(data)

        assert result["bank_code"] == data["bank_code"]
        assert result["interest_rate"] == data["interest_rate"]
        assert result["fine_rate"] == data["fine_rate"]
        assert result["discount_limit"] == data["discount_limit"]

    def test_should_dump_successfully_with_valid_data(self):
        schema = CreditorSchema()

        creditor = {
            "bank_code": "001",
            "interest_rate": Decimal("5.00"),
            "fine_rate": Decimal("2.00"),
            "discount_limit": Decimal("10.00")
        }

        result = schema.dump(creditor)

        assert result["bank_code"] == creditor["bank_code"]
        assert result["interest_rate"] == str(creditor["interest_rate"])
        assert result["fine_rate"] == str(creditor["fine_rate"])
        assert result["discount_limit"] == str(creditor["discount_limit"])

@pytest.mark.unit
class TestDebtSchema:

    def test_should_raise_error_when_debtor_id_is_missing(self):
        schema = DebtSchema()

        data = {
            "creditor_id": uuid.uuid4(),
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00"),
            "due_date": "2026-12-01"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "debtor_id" in err.value.messages

    def test_should_raise_error_when_creditor_id_is_missing(self):
        schema = DebtSchema()

        data = {
            "debtor_id": 1,
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00"),
            "due_date": "2026-12-01"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "creditor_id" in err.value.messages

    def test_should_raise_error_when_original_value_is_missing(self):
        schema = DebtSchema()

        data = {
            "debtor_id": 1,
            "creditor_id": uuid.uuid4(),
            "updated_value": Decimal("5000.00"),
            "due_date": "2026-12-01"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "original_value" in err.value.messages

    def test_should_raise_error_when_due_date_is_missing(self):
        schema = DebtSchema()

        data = {
            "debtor_id": 1,
            "creditor_id": uuid.uuid4(),
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "due_date" in err.value.messages

    def test_should_raise_error_when_data_has_invalid_type(self):
        schema = DebtSchema()

        data = {
            "debtor_id": "invalid_type",
            "creditor_id": "invalid_type",
            "original_value": "invalid_type",
            "updated_value": "invalid_type",
            "due_date": "invalid_type",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "debtor_id" in err.value.messages
        assert "creditor_id" in err.value.messages
        assert "original_value" in err.value.messages
        assert "updated_value" in err.value.messages
        assert "due_date" in err.value.messages

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = DebtSchema()

        data = {
            "debtor_id": 1,
            "creditor_id": uuid.uuid4(),
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00"),
            "due_date": "2026-12-01",
            "unknown_field": "unexpected_value"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = DebtSchema()

        data = {
            "debtor_id": 1,
            "creditor_id": uuid.uuid4(),
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00"),
            "due_date": "2026-12-01"
        }

        result = schema.load(data)

        assert result["debtor_id"] == data["debtor_id"]
        assert result["creditor_id"] == data["creditor_id"]
        assert result["original_value"] == data["original_value"]
        assert result["updated_value"] == data["updated_value"]
        assert result["due_date"] == date(2026, 12, 1)

    def test_should_dump_successfully_with_valid_data(self):
        schema = DebtSchema()

        data = {
            "id": uuid.uuid4(),
            "debtor_id": 1,
            "creditor_id": uuid.uuid4(),
            "original_value": Decimal("5000.00"),
            "updated_value": Decimal("5000.00"),
            "due_date": date(2026, 12, 1),
            "last_agreement_date": datetime.utcnow(),
            "status": DebtStatus.OPEN,
            "renegotiation_count": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = schema.dump(data)

        assert result["id"] == str(data["id"])
        assert result["debtor_id"] == data["debtor_id"]
        assert result["creditor_id"] == str(data["creditor_id"])
        assert result["original_value"] == str(data["original_value"])
        assert result["updated_value"] == str(data["updated_value"])
        assert result["due_date"] == str(data["due_date"])
        assert result["last_agreement_date"] == data["last_agreement_date"].isoformat()
        assert result["status"] == data["status"].value
        assert result["renegotiation_count"] == data["renegotiation_count"]
        assert result["created_at"] == data["created_at"].isoformat()
        assert result["updated_at"] == data["updated_at"].isoformat()

@pytest.mark.unit
class TestDebtSearchByDocumentSchema:

    def test_should_raise_error_when_document_is_missing(self):
        schema = DebtSearchByDocumentSchema()

        data = {}

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages

    def test_should_raise_error_when_document_is_invalid(self):
        schema = DebtSearchByDocumentSchema()

        data = {
            "document": "12345678900"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages

    def test_should_load_successfully_with_valid_cpf(self):
        schema = DebtSearchByDocumentSchema()

        data = {
            "document": "52998224725"
        }

        result = schema.load(data)

        assert result["document"] == data["document"]

    def test_should_load_successfully_with_valid_cnpj(self):
        schema = DebtSearchByDocumentSchema()

        data = {
            "document": "11222333000181"
        }

        result = schema.load(data)

        assert result["document"] == data["document"]

    def test_should_accept_formatted_document(self):
        schema = DebtSearchByDocumentSchema()

        data = {
            "document": "529.982.247-25"
        }

        result = schema.load(data)

        assert result["document"] == data["document"]

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = DebtSearchByDocumentSchema()

        data = {
            "document": "52998224725",
            "unexpected": "value"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unexpected" in err.value.messages

@pytest.mark.unit
class TestDebtSearchResponseSchema:

    def test_should_raise_error_when_document_is_missing(self):
        schema = DebtSearchResponseSchema()

        data = {
            "has_debts": True,
            "debts": [],
            "total_debts": 0,
            "total_amount": Decimal("0.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages

    def test_should_raise_error_when_has_debts_is_missing(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "debts": [],
            "total_debts": 0,
            "total_amount": Decimal("0.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "has_debts" in err.value.messages

    def test_should_raise_error_when_debts_is_missing(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "total_debts": 0,
            "total_amount": Decimal("0.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "debts" in err.value.messages

    def test_should_raise_error_when_total_debts_is_missing(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_amount": Decimal("0.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "total_debts" in err.value.messages

    def test_should_raise_error_when_total_amount_is_missing(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_debts": 0
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "total_amount" in err.value.messages

    def test_should_raise_error_when_document_is_invalid(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "12345678900",
            "has_debts": True,
            "debts": [],
            "total_debts": 0,
            "total_amount": Decimal("0.00")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages

    def test_should_raise_error_when_data_has_invalid_type(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": 123,
            "has_debts": "invalid",
            "debts": "invalid",
            "total_debts": "invalid",
            "total_amount": "invalid"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "document" in err.value.messages
        assert "has_debts" in err.value.messages
        assert "debts" in err.value.messages
        assert "total_debts" in err.value.messages
        assert "total_amount" in err.value.messages

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_debts": 0,
            "total_amount": Decimal("0.00"),
            "unknown_field": "unexpected"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_debts": 0,
            "total_amount": Decimal("0.00"),
            "redirect_url": "https://example.com"
        }

        result = schema.load(data)

        assert result["document"] == data["document"]
        assert result["has_debts"] == data["has_debts"]
        assert result["debts"] == data["debts"]
        assert result["total_debts"] == data["total_debts"]
        assert result["total_amount"] == Decimal("0.00")
        assert result["redirect_url"] == data["redirect_url"]

    def test_should_load_successfully_without_optional_redirect_url(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_debts": 0,
            "total_amount": "0.00"
        }

        result = schema.load(data)

        assert "redirect_url" not in result

    def test_should_dump_successfully_with_valid_data(self):
        schema = DebtSearchResponseSchema()

        data = {
            "document": "52998224725",
            "has_debts": True,
            "debts": [],
            "total_debts": 1,
            "total_amount": Decimal("123.45"),
            "redirect_url": "/leads/add?document=52998224725"
        }

        result = schema.dump(data)

        assert result["document"] == data["document"]
        assert result["has_debts"] == data["has_debts"]
        assert result["debts"] == data["debts"]
        assert result["total_debts"] == data["total_debts"]
        assert result["total_amount"] == "123.45"
        assert result["redirect_url"] == data["redirect_url"]

@pytest.mark.unit
class TestDebtHistorySchema:

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = DebtHistorySchema()

        data = {
            "id": str(uuid.uuid4()),
            "unknown": "value"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = DebtHistorySchema()

        data = {
            "id": str(uuid.uuid4()),
            "old_value": "100.00",
            "new_value": "150.00",
            "changed_at": datetime.utcnow().isoformat(),
            "reason": "update",
            "extra": {"key": "value"}
        }

        result = schema.load(data)

        assert result["id"] is not None
        assert result["old_value"] == Decimal("100.00")
        assert result["new_value"] == Decimal("150.00")
        assert result["reason"] == data["reason"]
        assert result["extra"] == data["extra"]

    def test_should_raise_error_when_invalid_types_are_provided(self):
        schema = DebtHistorySchema()

        data = {
            "id": "invalid_uuid",
            "old_value": "invalid",
            "new_value": "invalid",
            "changed_at": "invalid",
            "extra": "invalid"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        errors = err.value.messages

        assert "id" in errors
        assert "old_value" in errors
        assert "new_value" in errors
        assert "changed_at" in errors
        assert "extra" in errors

    def test_should_dump_successfully_with_valid_data(self):
        schema = DebtHistorySchema()

        data = {
            "id": uuid.uuid4(),
            "event_type": DebtHistoryType.UPDATED,
            "old_status": DebtStatus.OPEN,
            "new_status": DebtStatus.PAID,
            "old_value": Decimal("100.00"),
            "new_value": Decimal("150.00"),
            "changed_at": datetime.utcnow(),
            "reason": "update",
            "extra": {"key": "value"}
        }

        result = schema.dump(data)

        assert result["id"] == str(data["id"])
        assert result["event_type"] == data["event_type"].value
        assert result["old_status"] == data["old_status"].value
        assert result["new_status"] == data["new_status"].value
        assert result["old_value"] == "100.00"
        assert result["new_value"] == "150.00"
        assert result["changed_at"] == data["changed_at"].isoformat()
        assert result["reason"] == data["reason"]
        assert result["extra"] == data["extra"]

@pytest.mark.unit
class TestAgreementSchema:
    """
        id (dump), debt_id, status (dump), total_traded (dump),
        installment_value (dump), installment_quantity,
        entry_value (optional), discount_applied (optional)
        first_due_date, created_at (dump), updated_at (dump)
    """

    def test_should_raise_error_when_debt_id_is_missing(self):
        schema = AgreementSchema()

        data = {
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6)
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "debt_id" in err.value.messages

    def test_should_raise_error_when_first_due_date_is_missing(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "first_due_date" in err.value.messages

    def test_should_raise_error_when_installment_quantity_is_missing(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05")
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "first_due_date" in err.value.messages

    def test_should_raise_error_when_installment_quantity_is_zero_or_negative(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": -1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6)
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "installments_quantity" in err.value.messages
        assert "Must be greater than or equal to 1." in str(err.value)

    def test_should_raise_error_when_installment_quantity_is_zero(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": 0,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6)
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "installments_quantity" in err.value.messages
        assert "Must be greater than or equal to 1." in str(err.value)

    def test_should_raise_when_data_has_invalid_type(self):
        schema = AgreementSchema()

        data = {
            "debt_id": 123456,
            "installments_quantity": "invalid_type",
            "entry_value": "invalid_type",
            "discount_applied": "invalid_type",
            "first_due_date": 123456
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "debt_id" in err.value.messages
        assert "installments_quantity" in err.value.messages
        assert "entry_value" in err.value.messages
        assert "discount_applied" in err.value.messages
        assert "first_due_date" in err.value.messages

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6),
            "unknown_field": "unexpected_value"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = AgreementSchema()

        data = {
            "debt_id": uuid.uuid4(),
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6),
        }

        result = schema.load(data)

        assert result["debt_id"] == data["debt_id"]
        assert result["installments_quantity"] == data["installments_quantity"]
        assert result["entry_value"] == data["entry_value"]
        assert result["discount_applied"] == data["discount_applied"]
        assert result["first_due_date"] == data["first_due_date"]

    def test_should_dump_successfully_with_valid_data(self):
        schema = AgreementSchema()

        data = {
            "id": uuid.uuid4(),
            "debt_id": uuid.uuid4(),
            "installments_quantity": 1,
            "entry_value": Decimal("150.00"),
            "discount_applied": Decimal("0.05"),
            "first_due_date": date(2026, 5, 6),
            "total_traded": Decimal("200.00"),
            "installment_value": Decimal("50.00")
        }

        result = schema.dump(data)

        assert result["id"] == str(data["id"])
        assert result["debt_id"] == str(data["debt_id"])
        assert result["installments_quantity"] == data["installments_quantity"]
        assert result["entry_value"] == str(data["entry_value"])
        assert result["discount_applied"] == str(data["discount_applied"])
        assert result["first_due_date"] == data["first_due_date"].isoformat()
        assert result["total_traded"] == data["total_traded"]
        assert result["installment_value"] == data["installment_value"]

@pytest.mark.unit
class TestInstallmentSchema:

    def test_should_raise_error_when_installment_number_is_missing(self):
        schema = InstallmentSchema()

        data = {
            "due_date": "2026-12-01",
            "value": Decimal("150.00"),
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "installment_number" in err.value.messages

    def test_should_raise_error_when_due_date_is_missing(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "value": Decimal("150.00"),
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "due_date" in err.value.messages

    def test_should_raise_error_when_value_is_zero_or_negative(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": "2026-12-01",
            "value": Decimal("-50.00"),
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "Installment value must be greater than zero." in str(err.value)

    def test_should_raise_error_when_value_is_zero(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": "2026-12-01",
            "value": Decimal("0.00"),
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "Installment value must be greater than zero." in str(err.value)

    def test_should_raise_error_when_installment_number_is_invalid_type(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": "invalid_string",
            "due_date": "2026-12-01",
            "value": Decimal("150.00"),
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "installment_number" in err.value.messages

    def test_should_raise_error_when_value_is_invalid_type(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": "2026-12-01",
            "value": "invalid_value",
            "agreement_id": uuid.uuid4(),
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "value" in err.value.messages

    def test_should_raise_error_when_unknown_field_is_provided(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": "2026-12-01",
            "value": Decimal("150.00"),
            "agreement_id": uuid.uuid4(),
            "extra_field": "unexpected_value",
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "extra_field" in err.value.messages

    def test_should_load_successfully_with_valid_data(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": "2026-12-01",
            "value": Decimal("150.00"),
            "agreement_id": uuid.uuid4()
        }

        result = schema.load(data)

        assert result["installment_number"] == data["installment_number"]
        assert result["due_date"] == date(2026, 12, 1)
        assert result["value"] == data["value"]
        assert result["agreement_id"] == data["agreement_id"]

    def test_should_dump_successfully_with_valid_data(self):
        schema = InstallmentSchema()

        data = {
            "installment_number": 1,
            "due_date": date(2026, 12, 1),
            "value": Decimal("150.00"),
            "status": InstallmentStatus.PENDING,  # Status "PENDING"
            "agreement_id": uuid.uuid4()
        }

        result = schema.dump(data)

        assert result["installment_number"] == data["installment_number"]
        assert result["due_date"] == "2026-12-01"
        assert result["value"] == data["value"]
        assert result["status"] == data["status"].value
        assert result["agreement_id"] == str(data["agreement_id"])

@pytest.mark.unit
class TestPaymentSchema:

    def test_invalid_payment_method_raises_error(self):
        schema = PaymentSchema()

        data = {
            "amount": Decimal("200.00"),
            "method": "INVALID_METHOD",
            "paid_at": datetime.utcnow()
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "method" in err.value.messages


    def test_invalid_data_type_raises_error(self):
        schema = PaymentSchema()

        data = {
            "amount": "invalid_amount",
            "method": 123456,
            "paid_at": 12345
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "amount" in err.value.messages
        assert "method" in err.value.messages
        assert "paid_at" in err.value.messages

    def test_unknown_field_raises_error(self):
        schema = PaymentSchema()

        data = {
            "amount": Decimal("200.00"),
            "method": MethodPayment.PIX,
            "paid_at": datetime.utcnow(),
            "unknown_field": 12345
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unknown_field" in err.value.messages

    def test_loads_with_valid_data(self):
        schema = PaymentSchema()

        data = {
            "amount": Decimal("200.00"),
            "method": MethodPayment.PIX,
            "paid_at": datetime.utcnow()
        }

        result = schema.load(data)

        assert result["amount"] == data["amount"]
        assert result["method"] == data["method"]
        assert result["paid_at"] == data["paid_at"]

    def test_dumps_with_valid_data(self):
        schema = PaymentSchema()

        data = {
            "amount": Decimal("200.00"),
            "method": MethodPayment.PIX,
            "paid_at": datetime.utcnow()
        }

        result = schema.dump(data)

        assert result["amount"] == str(data["amount"])
        assert result["method"] == data["method"].value
        assert result["paid_at"] == data["paid_at"].isoformat()
