import pytest

import uuid
import random
from marshmallow import ValidationError
from decimal import Decimal
from datetime import date

import agreement
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

from debts.models import Debt
from debts.services import DebtService
from debts.exceptions import DebtNotFound

from agreement.models import Agreement
from agreement.services import AgreementService
from agreement.exceptions import AgreementNotFound, AgreementStatusError, PendingInstallmentsError

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

@pytest.mark.unit
class TestDebtService:

    def test_get_debt_by_id(self, session, debt):
        found_debt = DebtService.get(debt.id, session)

        assert isinstance(found_debt, Debt)
        assert found_debt.id == debt.id

    def test_debt_not_found(self, session):

        pytest.raises(DebtNotFound, lambda: DebtService.get(uuid.uuid4(), session))

    def test_search_document(self, session, debt):
        document = debt.debtor.document

        result = DebtService.search(document, session)

        dict_debt = dict(
            id=debt.id,
            amount=debt.original_value,
            due_date=debt.due_date,
            status=debt.status,
            creditor=debt.creditor.bank_name
        )

        assert isinstance(result, dict)
        assert result["document"] == document
        assert result["has_debts"] == True
        assert result["debts"] == [dict_debt]
        assert result["total_debts"] == 1
        assert result["total_amount"] == debt.original_value
        assert result["redirect_url"] == f"/leads/add?document={document}"

    def test_search_document_debt_empty(self, session):
        document = "52998224725"

        result = DebtService.search(document, session)

        assert isinstance(result, dict)
        assert result["document"] == document
        assert result["has_debts"] == False
        assert result["debts"] == []
        assert result["total_debts"] == 0
        assert result["total_amount"] == 0
        assert result["redirect_url"] is None

    def test_search_invalid_document(self, session):
        document = "99999999999"

        with pytest.raises(ValidationError) as err:
            DebtService.search(document, session)

            assert err.message == "CPF or CNPJ must be valid"

    def test_create_debt(self, creditor, debtor, manager_user, session):
        data = dict(
            creditor_id=creditor.id,
            debtor_id=debtor.id,
            original_value=Decimal("3000.00"),
            due_date=date(2026, 5, 6)
        )

        debt = DebtService.create(data, manager_user, session)

        session.commit()

        assert isinstance(debt, Debt)
        assert debt.creditor_id == creditor.id
        assert debt.debtor_id == debtor.id
        assert debt.original_value == data["original_value"]
        assert debt.due_date == data["due_date"]

    def test_create_debt_raise_creditor_not_found(self, debtor, manager_user, session):
        data = dict(
            creditor_id=uuid.uuid4(),
            debtor_id=debtor.id,
            original_value=Decimal("3000.00"),
            due_date=date(2026, 5, 6)
        )

        with pytest.raises(CreditorNotFound):
            DebtService.create(data, manager_user, session)

    def test_create_debt_raise_debtor_not_found(self, creditor, manager_user, session):
        data = dict(
            creditor_id=creditor.id,
            debtor_id=uuid.uuid4(),
            original_value=Decimal("3000.00"),
            due_date=date(2026, 5, 6)
        )

        with pytest.raises(DebtorNotFound):
            DebtService.create(data, manager_user, session)

@pytest.mark.unit
class TestAgreementService:

    def test_get_agreement_by_id(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("12000.00"),
            installments_quantity=10,
            installment_value=Decimal("1200.00"),
            first_due_date=date(2026, 5, 6)
        )

        session.add(agreement)
        session.commit()

        found_agreement = AgreementService.get(agreement.id, session)

        assert isinstance(found_agreement, Agreement)
        assert found_agreement.id == agreement.id
        assert found_agreement.total_traded == agreement.total_traded
        assert found_agreement.installments_quantity == agreement.installments_quantity
        assert found_agreement.installment_value == agreement.installment_value
        assert found_agreement.first_due_date == agreement.first_due_date

    def test_get_agreement_not_found(self, session):
        agreement_id = uuid.uuid4()

        pytest.raises(AgreementNotFound, lambda: AgreementService.get(agreement_id, session))

    def test_create_agreement_success(self, debt, session):
        data = dict(
            debt_id=debt.id,
            installments_quantity=10,
            first_due_date=date(2026, 5, 6)
        )

        agreement = AgreementService.create(data, session)

        assert isinstance(agreement, Agreement)
        assert agreement.debt_id == debt.id
        assert agreement.installments_quantity == data["installments_quantity"]
        assert agreement.first_due_date == data["first_due_date"]

    def test_create_agreement_debt_not_found(self, session):
        data = dict(
            debt_id=uuid.uuid4(),
            installments_quantity=10,
            first_due_date=date(2026, 5, 6)
        )

        with pytest.raises(DebtNotFound):
            AgreementService.create(data, session)

    def test_create_agreement_discount_greater_than_total_raises_error(self, debt, session):
        data = dict(
            debt_id=debt.id,
            installments_quantity=5,
            first_due_date=date(2026, 5, 6),
            discount_applied=Decimal("10000000000.00"),
        )

        with pytest.raises(ValueError) as err:
            AgreementService.create(data, session)

        assert "Discount cannot exceed total debt" in str(err.value)

    def test_create_agreement_discount_greater_than_limit_raises_error(self, debt, session):
        data = dict(
            debt_id=debt.id,
            installments_quantity=10,
            first_due_date=date(2026, 5, 6),
            discount_applied=Decimal("10.00")
        )

        with pytest.raises(ValueError) as err:
            AgreementService.create(data, session)

        assert "Discount cannot exceed" in str(err.value)
        assert "Discount cannot exceed total debt" is not str(err.value)

    def test_create_agreement_entry_greater_than_total_raises_error(self, debt, session):
        data = dict(
            debt_id=debt.id,
            installments_quantity=5,
            first_due_date=date(2026, 5, 6),
            discount_applied=Decimal("0.00"),
            entry_value=Decimal("999999.00"),
        )

        with pytest.raises(ValueError) as err:
            AgreementService.create(data, session)

        assert "Entry cannot exceed total after discount" in str(err.value)

    def test_create_agreement_installments_quantity_zero_raises_error(self, debt, session):
        data = dict(
            debt_id=debt.id,
            installments_quantity=0,
            first_due_date=date(2026, 5, 6),
        )

        with pytest.raises(ValueError) as err:
            AgreementService.create(data, session)

        assert "Installments quantity must be greater than zero" in str(err.value)
