import random

import pytest

import uuid
from marshmallow import ValidationError

from leads.models import Lead
from leads.services import LeadService

from users.models import User
from users.services import UserService
from users.exceptions import UserNotFoundError

from debtor.models import Debtor
from debtor.services import DebtorService
from debtor.exceptions import DebtorNotFound, DuplicateDocumentDebtor

from creditor.models import Creditor
from creditor.services import CreditorService
from creditor.exceptions import CreditorAlreadyExistsError, CreditorNotFound

from utils.enum import UserRole


@pytest.mark.unit
class TestLeadService:

    def test_create_lead(self, session):
        document = "52998224725"
        data = {
            "name": "Lead Test",
            "email": "lead@test.com",
            "phone": "1199999999"
        }

        lead = LeadService.create(data, document, session)

        assert isinstance(lead, Lead)

    def test_invalid_document(self, session):
        document = "99999999999"
        data = {
            "name": "Lead Test",
            "email": "lead@test.com",
            "phone": "1199999999"
        }

        with pytest.raises(ValidationError) as err:
            LeadService.create(data, document, session)

            assert err.message == "CPF or CNPJ must be valid"

    def test_missing_document(self, session):
        data = {
            "name": "Lead Test",
            "email": "lead@test.com",
            "phone": "1199999999"
        }

        with pytest.raises(ValidationError) as err:
            LeadService.create(data, None, session)

            assert err.message == "Lead must have a document"

@pytest.mark.unit
class TestUserService:

    def test_get_user_by_id(self, session, agent_user):
        found_user = UserService.get(agent_user.id, session)

        assert found_user.id is not None
        assert found_user.id == agent_user.id

    def test_user_not_found(self, session):

        pytest.raises(UserNotFoundError, lambda: UserService.get(uuid.uuid4(), session))

    def test_create_user_success(self, session):
        data = {
            "name": "Test User",
            "email": "user@test.com",
            "password": "Teste@2026"
        }

        user = UserService.create_user(data, session)

        assert isinstance(user, User)
        assert user.name == data["name"]
        assert user.email == data["email"]
        assert user.role == UserRole.AGENT
        assert user.check_password(data["password"])

    def test_update_user(self, session, agent_user):
        data = {
            "name": "Teste User"
        }

        updated_user = UserService.update(agent_user.id, data, session)

        assert isinstance(updated_user, User)
        assert updated_user.name == data["name"]

    def test_delete_user(self, session, agent_user):
        UserService.delete(agent_user.id, session)
        session.commit()

        deleted_user = session.get(User, agent_user.id)
        assert deleted_user is None

@pytest.mark.unit
class TestDebtorService:

    def test_get_debtor_by_id(self, session, debtor):
        found_debtor = DebtorService.get(debtor.id, session)

        assert isinstance(found_debtor, Debtor)
        assert found_debtor.id == debtor.id

    def test_debtor_not_found(self, session):
        debtor_id = random.randint(1, 999999999)

        pytest.raises(DebtorNotFound, lambda: DebtorService.get(debtor_id, session))

    def test_create_debtor(self, session):
        data = {
            "name": "Test Debtor",
            "document": "12345678970",
            "email": "debtor@test.com",
            "phone": "11999999999"
        }

        debtor = DebtorService.create(data, session)

        assert isinstance(debtor, Debtor)
        assert debtor.name == data["name"]
        assert debtor.document == data["document"]
        assert debtor.email == data["email"]
        assert debtor.phone == data["phone"]

    def test_create_existing_debtor(self, session, debtor):
        data = {
            "name": "Test Debtor",
            "document": debtor.document,
            "email": "debtor@test.com",
            "phone": "11999999999"
        }

        with pytest.raises(DuplicateDocumentDebtor):
            DebtorService.create(data, session)

@pytest.mark.unit
class TestCreditorService:

    def test_get_creditor_by_id(self, session, creditor):
        found_creditor = CreditorService.get(creditor.id, session)

        assert isinstance(found_creditor, Creditor)
        assert found_creditor.id == creditor.id

    def test_creditor_not_found(self, session):

        pytest.raises(CreditorNotFound, lambda: CreditorService.get(uuid.uuid4(), session))

    def test_create_creditor(self, session):
        data = {
            "bank_code": "001",
            "interest_rate": "0.05",
            "fine_rate":  "0.02",
            "discount_limit":  "0.20"
        }

        creditor = CreditorService.create_creditor(data, session)

        assert isinstance(creditor, Creditor)
        assert creditor.bank_code == data["bank_code"]
        assert creditor.interest_rate == data["interest_rate"]
        assert creditor.fine_rate == data["fine_rate"]
        assert creditor.discount_limit == data["discount_limit"]

    def test_create_existing_creditor(self, session, creditor):
        data = {
            "bank_code": creditor.bank_code,
            "interest_rate": "0.05",
            "fine_rate": "0.02",
            "discount_limit": "0.20"
        }

        with pytest.raises(CreditorAlreadyExistsError):
            CreditorService.create_creditor(data, session)
