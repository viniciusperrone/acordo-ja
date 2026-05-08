import pytest
from unittest.mock import patch

import uuid
import random
from marshmallow import ValidationError
from decimal import Decimal
from datetime import date

from leads.models import Lead
from leads.services import LeadService

from users.models import User
from users.services import UserService
from users.exceptions import UserNotFoundError, EmailAlreadyExists

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
from agreement.exceptions import AgreementNotFound, AgreementStatusError

from installments.models import Installments
from installments.services import InstallmentService
from installments.exceptions import InstallmentNotFound

from payment.models import Payment
from payment.services import PaymentService
from payment.exception import PaymentError

from utils.enum import UserRole, AgreementStatus, InstallmentStatus, MethodPayment


@pytest.mark.unit
class TestLeadService:

    @patch("leads.services.NotificationEvents.on_lead_created")
    def test_should_create_lead_successfully(self, mock_on_lead_created, session):
        data = {
            "name": "Lead Test",
            "email": "lead@test.com",
            "phone": "1199999999",
            "document": "52998224725"
        }

        lead = LeadService.create(data, session)

        assert isinstance(lead, Lead)

        assert lead.id is not None
        assert lead.name == data["name"]
        assert lead.email == data["email"]
        assert lead.phone == data["phone"]
        assert lead.document == data["document"]

        persisted_lead = session.get(Lead, lead.id)

        assert persisted_lead is not None
        assert persisted_lead.id == lead.id

        mock_on_lead_created.assert_called_once_with(
            lead,
            session,
        )

@pytest.mark.unit
class TestUserService:

    def test_should_return_user_when_user_exists(self, session, agent_user):
        found_user = UserService.get(agent_user.id, session)

        assert found_user is not None
        assert found_user.id == agent_user.id

    def test_should_raise_user_not_found_error_when_user_does_not_exist(self, session):
        with pytest.raises(UserNotFoundError):
            UserService.get(uuid.uuid4(), session)

    def test_should_create_user_successfully(self, session):
        data = {
            "name": "Test User",
            "email": "user@test.com",
            "password": "Teste@2026"
        }

        user = UserService.create_user(data, session)

        assert isinstance(user, User)

        assert user.id is not None
        assert user.name == data["name"]
        assert user.email == data["email"]
        assert user.role == UserRole.AGENT

        assert user.check_password(data["password"])

    def test_should_persist_user_after_creation(self, session):
        data = {
            "name": "Test User",
            "email": "user@test.com",
            "password": "Teste@2026"
        }

        user = UserService.create_user(data, session)

        persisted_user = session.get(User, user.id)

        assert persisted_user is not None
        assert persisted_user.id == user.id
        assert persisted_user.email == data["email"]

    def test_should_raise_email_already_exists_when_updating_to_existing_email(
        self,
        agent_user,
        session
    ):
        data = {
            "name": "Another User",
            "email": agent_user.email,
            "password": "Teste@2026",
        }

        with pytest.raises(EmailAlreadyExists) as err:
            UserService.create_user(data, session)

        assert str(err.value) == "Email already exists"

    def test_should_update_user_name_successfully(self, session, agent_user):
        data = {
            "name": "Updated User"
        }

        updated_user = UserService.update(
            agent_user.id,
            data,
            session
        )

        assert updated_user.name == data["name"]

    def test_should_updated_user_email_successfully(self, session, agent_user):
        data = {
            "email": "updated@test,com"
        }

        updated_user = UserService.update(
            agent_user.id,
            data,
            session,
        )

        assert updated_user.email == data["email"]

    def test_should_update_user_role_successfully(
        self,
        session,
        agent_user,
    ):
        data = {
            "role": UserRole.ADMIN.value,
        }

        updated_user = UserService.update(
            agent_user.id,
            data,
            session,
        )

        assert updated_user.role == UserRole.ADMIN

    def test_should_raise_email_already_exists_when_updating_to_existing_email(
            self,
            session,
            agent_user,
    ):
        another_user = User(
            name="Another User",
            email="another@test.com",
            role=UserRole.AGENT,
        )

        another_user.set_password("Teste@2026")

        session.add(another_user)
        session.flush()

        data = {
            "email": another_user.email,
        }

        with pytest.raises(EmailAlreadyExists) as err:
            UserService.update(
                agent_user.id,
                data,
                session,
            )

        assert str(err.value) == "Email already exists"

    def test_should_delete_user_successfully(self, session, agent_user):
        UserService.delete(agent_user.id, session)

        deleted_user = session.get(User, agent_user.id)

        assert deleted_user is None

@pytest.mark.unit
class TestCreditorService:

    def test_should_return_creditor_when_creditor_exist(self, session, creditor):
        found_creditor = CreditorService.get(
            creditor.id,
            session,
        )

        assert isinstance(found_creditor, Creditor)
        assert found_creditor.id == creditor.id

    def test_should_raise_creditor_not_found_when_creditor_does_not_exist(self, session):
        with pytest.raises(CreditorNotFound):
            CreditorService.get(uuid.uuid4(), session)

    def test_should_create_creditor_successfully(self, session):
        data = {
            "bank_code": "001",
            "interest_rate": Decimal("5.00"),
            "fine_rate": Decimal("2.00"),
            "discount_limit": Decimal("20.00"),
        }

        creditor = CreditorService.create_creditor(
            data,
            session,
        )

        assert isinstance(creditor, Creditor)

        assert creditor.id is not None
        assert creditor.bank_code == data["bank_code"]
        assert creditor.interest_rate == data["interest_rate"]
        assert creditor.fine_rate == data["fine_rate"]
        assert creditor.discount_limit == data["discount_limit"]

    def test_should_persist_creditor_after_creation(self, session):
        data = {
            "bank_code": "001",
            "interest_rate": Decimal("5.00"),
            "fine_rate": Decimal("2.00"),
            "discount_limit": Decimal("20.00"),
        }

        creditor = CreditorService.create_creditor(
            data,
            session,
        )

        persisted_creditor = session.get(
            Creditor,
            creditor.id,
        )

        assert persisted_creditor is not None
        assert persisted_creditor.id == creditor.id
        assert persisted_creditor.bank_code == data["bank_code"]

    def test_should_raise_creditor_already_exists_when_bank_code_is_duplicated(self, session, creditor):
        data = {
            "bank_code": creditor.bank_code,
            "interest_rate": Decimal("5.00"),
            "fine_rate": Decimal("2.00"),
            "discount_limit": Decimal("20.00"),
        }

        with pytest.raises(CreditorAlreadyExistsError):
            CreditorService.create_creditor(
                data,
                session,
            )

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

    def test_cancel_agreement_updates_status_to_cancelled(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6)
        )

        session.add(agreement)
        session.commit()

        assert agreement.status is not AgreementStatus.CANCELLED

        AgreementService.cancel(agreement, session)

        agreement = session.get(Agreement, agreement.id)

        assert agreement.status == AgreementStatus.CANCELLED

    def test_cancel_completed_agreement_raises_error(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.COMPLETED
        )

        session.add(agreement)
        session.commit()

        assert agreement.status is not AgreementStatus.CANCELLED

        with pytest.raises(AgreementStatusError) as err:
            AgreementService.cancel(agreement, session)

        assert str(err.value) == "Cannot cancel a completed agreement"

    def test_cancel_already_cancelled_agreement_raises_error(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.CANCELLED
        )

        session.add(agreement)
        session.commit()

        with pytest.raises(AgreementStatusError) as err:
            AgreementService.cancel(agreement, session)

        assert str(err.value) == "Agreement already cancelled"

    def test_complete_agreement_updates_status_to_completed(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.commit()

        assert agreement.status is not AgreementStatus.COMPLETED

        AgreementService.complete(agreement, session)

        session.commit()

        agreement = session.get(Agreement, agreement.id)

        assert agreement.status == AgreementStatus.COMPLETED

    def test_complete_already_completed_agreement_raises_error(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.COMPLETED
        )

        session.add(agreement)
        session.commit()

        assert agreement.status is not AgreementStatus.CANCELLED

        with pytest.raises(AgreementStatusError) as err:
            AgreementService.complete(agreement, session)

        assert str(err.value) == "Agreement already completed"

    def test_complete_cancelled_agreement_raises_error(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.CANCELLED
        )

        session.add(agreement)
        session.commit()

        assert agreement.status == AgreementStatus.CANCELLED

        with pytest.raises(AgreementStatusError) as err:
            AgreementService.complete(agreement, session)

        assert str(err.value) == "Agreement is cancelled"

    def test_complete_draft_agreement_raises_error(self, debt, manager_user, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6)
        )

        session.add(agreement)
        session.commit()

        assert agreement.status == AgreementStatus.DRAFT

        with pytest.raises(AgreementStatusError) as err:
            AgreementService.complete(agreement, session)

        assert str(err.value) == "Draft agreement cannot be completed"

class TestInstallmentService:

    def test_get_installment_by_id_success(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6)
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        found_installment = InstallmentService.get(installment.id, session)

        assert found_installment.id == installment.id
        assert found_installment.agreement_id == agreement.id

    def test_get_installment_by_id_raises_error(self, session):
        installment_id = random.randint(1, 999999999)

        with pytest.raises(InstallmentNotFound) as err:
            InstallmentService.get(installment_id, session)

@pytest.mark.init
class TestPaymentService:

    def test_payment_installment_success(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        payment = PaymentService.process_installment_payment(
            installment=installment,
            amount=Decimal("100.00"),
            method=MethodPayment.PIX,
            session=session
        )

        assert isinstance(payment, Payment)
        assert payment.installment_id == installment.id
        assert payment.amount == installment.value
        assert payment.paid_at is not None
        assert payment.method == MethodPayment.PIX

    def test_payment_installment_invalid_method_raises_error(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        with pytest.raises(PaymentError):
            PaymentService.process_installment_payment(
                installment=installment,
                amount=Decimal("100.00"),
                method="INVALID_METHOD",
                session=session
            )


    def test_payment_paid_installment_raises_error(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        with pytest.raises(PaymentError) as err:
            PaymentService.process_installment_payment(
                installment=installment,
                amount=Decimal("100.00"),
                method="INVALID_METHOD",
                session=session
            )

    def test_payment_invalid_amount_raises_error(self, debt, session):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        with pytest.raises(PaymentError) as err:
            PaymentService.process_installment_payment(
                installment=installment,
                amount=Decimal("200.00"),
                method=MethodPayment.PIX,
                session=session
            )
