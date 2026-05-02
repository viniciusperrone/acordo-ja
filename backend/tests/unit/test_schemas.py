import uuid

import pytest
from marshmallow import ValidationError

from users.schemas import UserSchema, UserUpdateSchema, UserResponseSchema
from leads.schemas import LeadSchema
from authentication.schemas import AuthenticationSchema, ResetPasswordSchema, UpdatePasswordSchema, ForgotPasswordSchema
from creditor.schemas import CreditorSchema
from debtor.schemas import DebtorSchema
from debts.schemas import DebtSchema, DebtHistorySchema, DebtSearchResponseSchema, DebtItemSchema
from agreement.schemas import AgreementSchema
from installments.schemas import InstallmentSchema
from payment.schemas import PaymentSchema

from utils.enum import UserRole


@pytest.mark.unit
class TestUserSchema:

    def test_user_schema_invalid_password(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": "weak"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "password" in err.value.messages

    def test_user_schema_unknown_field(self):
        schema = UserSchema()

        data = {
            "name": "João",
            "email": "joao@email.com",
            "password": "Strong@123",
            "unexpected": "field"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(data)

        assert "unexpected" in err.value.messages

    def test_dump_only_field_raises_error_on_load(self):
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

@pytest.mark.unit
class TestUserUpdateSchema:

    def test_user_update_partial(self):
        schema = UserUpdateSchema()

        data = {
            "name": "Novo Nome"
        }

        result = schema.load(data)

        assert result["name"] == "Novo Nome"

@pytest.mark.unit
class TestUserResponseSchema:

    def test_user_response_schema_dump(self):
        schema = UserResponseSchema()

        user = {
            "id": uuid.uuid4(),
            "name": "João",
            "email": "joao@email.com",
            "role": UserRole.ADMIN
        }

        result = schema.dump(user)

        assert result["name"] == "João"
        assert "password" not in result

@pytest.mark.unit
class TestLeadSchema:

    def test_lead_schema_invalid_document_raise_error(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "123456789",
            "email": "joao@test.gmail",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "document" in err.value.messages

    def test_lead_schema_invalid_id_parameter_raise_error(self):
        schema = LeadSchema()

        lead = {
            "id": uuid.uuid4(),
            "name": "João Silva",
            "document": "123456789",
            "email": "joao@test.gmail",
            "phone": "11999999999"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "id" in err.value.messages

    def test_lead_schema_invalid_phone_raise_error(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "email": "joao@test.gmail",
            "phone": "2132434"
        }

        with pytest.raises(ValidationError) as err:
            schema.load(lead)

        assert "phone" in err.value.messages

    def test_lead_schema_success(self):
        schema = LeadSchema()

        lead = {
            "name": "João Silva",
            "document": "52998224725",
            "email": "joao@test.gmail",
            "phone": "11999999999"
        }

        result = schema.dump(lead)

        assert result["name"] == lead["name"]
        assert result["document"] == lead["document"]
        assert result["email"] == lead["email"]
        assert result["phone"] == lead["phone"]

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

    def test_should_raise_error_when_email_has_invalid_typez(self):
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
