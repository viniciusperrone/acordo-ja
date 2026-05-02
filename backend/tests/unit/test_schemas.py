import uuid

import pytest
from marshmallow import ValidationError

from users.schemas import UserSchema, UserUpdateSchema, UserResponseSchema
from leads.schemas import LeadSchema
from authentication.schemas import AuthenticationSchema, ResetPasswordSchema, UpdatePasswordSchema
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

