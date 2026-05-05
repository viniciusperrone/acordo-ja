import pytest

import uuid
from decimal import Decimal
from datetime import datetime, date

from installments import Installments
from notifications import Notification
from payment import Payment
from users.models import User
from creditor.models import Creditor
from debtor.models import Debtor
from debts.models import Debt
from agreement.models import Agreement

from sqlalchemy.exc import IntegrityError

from utils.enum import UserRole, DebtStatus, AgreementStatus, InstallmentStatus, MethodPayment, NotificationType


@pytest.mark.unit
class TestUserModel:

    def test_create_user(self, session):
        user = User(
            name="Test User",
            email="test@test.com",
            role=UserRole.ADMIN,
        )

        user.set_password("123456")

        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.name == "Test User"
        assert user.is_active is True
        assert user.must_change_password is True
        assert user.password_hash is not None

    def test_password_hashing(self, session):
        user = User(
            name="Test User",
            email="test@test.com",
            role=UserRole.ADMIN,
        )
        user.set_password("123456")

        session.add(user)
        session.commit()

        assert user.password_hash != "123456"
        assert user.check_password("123456") is True
        assert user.check_password("wrong") is False


    def test_unique_email_constraint(self, session):
        user1 = User(
            name="User 1",
            email="unique@test.com",
            role=UserRole.AGENT,
        )

        user1.set_password("123456")

        session.add(user1)
        session.commit()

        user2 = User(
            name="User 2",
            email="unique@test.com",
            role=UserRole.AGENT,
        )

        user2.set_password("123456")

        session.add(user2)

        with pytest.raises(IntegrityError):
            session.commit()

@pytest.mark.unit
class TestCreditorModel:

    def test_create_creditor(self, session):
        creditor = Creditor(
            bank_code="033",
            interest_rate=Decimal("0.05"),
            fine_rate=Decimal("0.02"),
            discount_limit=Decimal("0.10")
        )

        session.add(creditor)
        session.commit()

        assert creditor.id is not None
        assert creditor.bank_code == "033"
        assert creditor.bank_name == "BCO SANTANDER (BRASIL) S.A."

        assert isinstance(creditor.interest_rate, Decimal)
        assert isinstance(creditor.fine_rate, Decimal)
        assert isinstance(creditor.discount_limit, Decimal)

        assert creditor.interest_rate == Decimal("0.05")
        assert creditor.fine_rate == Decimal("0.02")
        assert creditor.discount_limit == Decimal("0.10")

    def test_unique_bank_code(self, session):
        creditor1 = Creditor(
            bank_code="033",
            interest_rate=Decimal("0.05"),
            fine_rate=Decimal("0.02"),
            discount_limit=Decimal("0.10")
        )

        session.add(creditor1)
        session.commit()

        creditor2 = Creditor(
            bank_code="033",
            interest_rate=Decimal("0.05"),
            fine_rate=Decimal("0.02"),
            discount_limit=Decimal("0.20")
        )

        session.add(creditor2)

        with pytest.raises(IntegrityError):
            session.commit()

@pytest.mark.unit
class TestDebtorModel:

    def test_debtor_creation_persist_fields(self, session):
        debtor = Debtor(
            name="João da Silva",
            document="12345678900",
            email = "joao@test.com",
            phone = "11999999999"
        )

        session.add(debtor)
        session.commit()

        assert debtor.id is not None
        assert debtor.name == "João da Silva"
        assert debtor.document == "12345678900"
        assert debtor.email == "joao@test.com"
        assert debtor.phone == "11999999999"

    def test_debtor_document_must_be_unique(self, session):
        debtor1 = Debtor(
            name="João da Silva",
            document="12345678900",
            email="joao@test.com",
            phone="11999999999"
        )

        session.add(debtor1)
        session.commit()

        debtor2 = Debtor(
            name="José da Silva",
            document="12345678900",
            email="jose@test.com",
            phone="11999999999"
        )

        session.add(debtor2)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_debtor_optional_fields_default_to_none(self, session):
        debtor = Debtor(
            name="João da Silva",
            document="12345678900",
        )

        session.add(debtor)
        session.commit()

        assert debtor.id is not None
        assert debtor.email is None
        assert debtor.phone is None

@pytest.mark.unit
class TestDebtModel:

    def test_debt_creation_persists_fields(self, session, debtor, creditor):
        debt = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("1000.00"),
            due_date=date(2026, 12, 31)
        )

        session.add(debt)
        session.commit()

        assert debt.id is not None
        assert debt.debtor_id == debtor.id
        assert debt.creditor_id == creditor.id
        assert debt.original_value == Decimal("1000.00")
        assert debt.updated_value is None
        assert debt.status == DebtStatus.OPEN
        assert debt.renegotiation_count == 0
        assert debt.created_at is not None

    def test_debt_has_debtor_and_creditor_relationships(self, session, debt):
        assert debt.debtor is not None
        assert debt.creditor is not None

    def test_debt_initial_agreements_is_empty(self, session, debt):
        assert debt.agreements == []

    def test_debt_defaults_are_correct(self, session, debtor, creditor):
        debt = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=1000.00,
            due_date="2024-01-15"
        )

        session.add(debt)
        session.commit()

        assert debt.updated_value is None
        assert debt.renegotiation_count == 0


@pytest.mark.unit
class TestAgreementModel:

    def test_agreement_creation_persists_fields(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("900.00"),
            discount_applied=Decimal("100.00"),
            installments_quantity=6,
            installment_value=Decimal("133.33"),
            entry_value=Decimal("0.00"),
            first_due_date=date(2024, 3, 2),
            status=AgreementStatus.ACTIVE
        )

        session.add(agreement)
        session.commit()

        assert agreement.id is not None
        assert agreement.debt_id == debt.id
        assert agreement.total_traded == Decimal("900.00")
        assert agreement.discount_applied == Decimal("100.00")
        assert agreement.installments_quantity == 6
        assert agreement.installment_value == Decimal("133.33")
        assert agreement.status == AgreementStatus.ACTIVE
        assert agreement.created_at is not None

    def test_agreement_defaults_to_draft_status(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 2),
        )

        session.add(agreement)
        session.commit()

        assert agreement.status == AgreementStatus.DRAFT

    def test_agreement_has_debt_relationship(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 2),
        )

        session.add(agreement)
        session.commit()

        assert agreement.debt is not None
        assert agreement.debt.id == debt.id

    def test_agreement_initial_installments_is_empty(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 2),
        )

        session.add(agreement)
        session.commit()

        assert agreement.installments == []

    def test_agreement_entry_and_discount_defaults(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 2),
        )

        session.add(agreement)
        session.commit()

        assert agreement.entry_value == Decimal("0.00")
        assert agreement.discount_applied == Decimal("0.00")

@pytest.mark.unit
class TestInstallmentsModel:

    def test_create_installment(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=10,
            first_due_date=date(2024, 3, 1)
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("100.00"),
            due_date=date(2024, 3, 1),
            status=InstallmentStatus.PENDING,
        )

        session.add(installment)
        session.commit()

        assert installment.id is not None
        assert installment.agreement_id == agreement.id
        assert installment.installment_number == 1
        assert installment.value == Decimal("100.00")
        assert installment.due_date == date(2024, 3, 1)
        assert installment.status == InstallmentStatus.PENDING

    def test_installment_status_transitions(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("300.00"),
            installments_quantity=2,
            installment_value=Decimal("150.00"),
            first_due_date=date(2024, 3, 1),
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("150.00"),
            due_date=date(2024, 3, 1),
            status=InstallmentStatus.PENDING,
        )

        session.add(installment)
        session.commit()

        assert installment.status == InstallmentStatus.PENDING

        installment.status = InstallmentStatus.PAID
        installment.payment_date = date.today()

        session.commit()

        assert installment.status == InstallmentStatus.PAID
        assert installment.payment_date is not None

        installment2 = Installments(
            agreement_id=agreement.id,
            installment_number=2,
            value=Decimal("150.00"),
            due_date=date(2024, 4, 1),
            status=InstallmentStatus.PENDING
        )

        session.add(installment2)
        session.commit()

        installment2.status = InstallmentStatus.OVERDUE
        session.commit()

        assert installment2.status == InstallmentStatus.OVERDUE

    def test_installment_relationship_with_agreement(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("500.00"),
            installments_quantity=5,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 1),
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("100.00"),
            due_date=date(2024, 3, 1),
        )

        session.add(installment)
        session.commit()

        assert installment.agreement is not None
        assert installment.agreement.id == agreement.id


@pytest.mark.unit
class TestPaymentModel:

    def test_create_payment(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("300.00"),
            installments_quantity=1,
            installment_value=Decimal("300.00"),
            first_due_date=date(2024, 3, 1),
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("300.00"),
            due_date=date(2024, 3, 1),
        )

        session.add(installment)
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("100.00"),
            paid_at=datetime.utcnow(),
            method=MethodPayment.PIX
        )

        session.add(payment)
        session.commit()

        assert payment.id is not None
        assert payment.installment_id == installment.id
        assert payment.amount == Decimal("100.00")
        assert payment.method == MethodPayment.PIX
        assert payment.paid_at is not None
        assert payment.created_at is not None

    def test_payment_methods(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("500.00"),
            installments_quantity=5,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 1)
        )
        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("100.00"),
            due_date=date(2024, 3, 1)
        )
        session.add(installment)
        session.flush()

        methods = [
            MethodPayment.PIX,
            MethodPayment.BOLETO,
            MethodPayment.TED,
            MethodPayment.CARTAO,
            MethodPayment.DINHEIRO
        ]

        for method in methods:
            payment = Payment(
                installment_id=installment.id,
                amount=Decimal("100.00"),
                paid_at=datetime.utcnow(),
                method=method
            )
            session.add(payment)
            session.commit()

            assert payment.method == method

            session.delete(payment)
            session.commit()

    def test_payment_relationship_with_installment(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("200.00"),
            installments_quantity=2,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 1)
        )
        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("100.00"),
            due_date=date(2024, 3, 1)
        )
        session.add(installment)
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("100.00"),
            paid_at=datetime.utcnow(),
            method=MethodPayment.PIX
        )
        session.add(payment)
        session.commit()

        assert payment.installment is not None
        assert payment.installment.id == installment.id


@pytest.mark.unit
class TestNotificationModel:

    def test_create_notification(self, session, admin_user):
        lead_id = uuid.uuid4()

        notification = Notification(
            type=NotificationType.NEW_LEAD,
            title="Novo Lead Criado",
            message="Um novo lead foi registrado",
            user_id=admin_user.id,
            extra={"lead_id": str(lead_id)},
            is_read=False
        )

        session.add(notification)
        session.commit()

        assert notification.id is not None
        assert notification.type == NotificationType.NEW_LEAD
        assert notification.title == "Novo Lead Criado"
        assert notification.message == "Um novo lead foi registrado"
        assert notification.user_id == admin_user.id
        assert notification.is_read is False
        assert notification.read_at is None
        assert notification.created_at is not None

    def test_notification_mark_as_read(self, session, admin_user):
        notification = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Pagamento Recebido",
            message="Pagamento de R$ 100,00 recebido",
            user_id=admin_user.id,
            is_read=False,
            extra={}
        )

        session.add(notification)
        session.commit()

        notification.mark_as_read()
        session.commit()

        assert notification.is_read is True
        assert notification.read_at is not None
        assert isinstance(notification.read_at, datetime)

    def test_notification_to_dict(self, session, admin_user):
        notification = Notification(
            type=NotificationType.AGREEMENT_CREATED,
            title="Acordo Criado",
            message="Novo acordo de 6 parcelas",
            user_id=admin_user.id,
            extra={"agreement_id": "abc123"}
        )

        session.add(notification)
        session.commit()

        data = notification.to_dict()

        assert isinstance(data, dict)
        assert 'id' in data
        assert 'notification_type' in data
        assert data['notification_type'] == 'AGREEMENT_CREATED'
        assert data['title'] == "Acordo Criado"
        assert data['is_read'] is False
        assert 'extra' in data
        assert data['extra']['agreement_id'] == "abc123"

    def test_notification_types(self, session, admin_user):
        types = [
            NotificationType.NEW_LEAD,
            NotificationType.PAYMENT_RECEIVED,
            NotificationType.INSTALLMENT_OVERDUE,
            NotificationType.AGREEMENT_CREATED,
            NotificationType.AGREEMENT_COMPLETED,
            NotificationType.DEBT_PAID,
            NotificationType.GENERAL
        ]

        for notif_type in types:
            notification = Notification(
                type=notif_type,
                title=f"Test {notif_type.value}",
                message="Test message",
                user_id=admin_user.id,
                is_read=False,
                extra={}
            )
            session.add(notification)
            session.commit()

            assert notification.type == notif_type
            session.delete(notification)
            session.commit()

    def test_notification_relationships(self, session, admin_user):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="General",
            message="Test message",
            user_id=admin_user.id,
            is_read=False,
            extra={}
        )

        session.add(notification)
        session.commit()

        assert notification.user is not None
        assert notification.user.id == admin_user.id
        assert notification.user.email == "admin@test.com"

    def test_notification_optional_user(self, session):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="Manutenção Programada",
            message="Sistema entrará em manutenção",
            user_id=None,
            is_read=False,
            extra={}
        )

        session.add(notification)
        session.commit()

        assert notification.user_id is None
        assert notification.user is None

    def test_notification_metadata_json(self, session, admin_user):
        complex_metadata = {
            "lead_id": "abc123",
            "lead_name": "João Silva",
            "lead_document": "12345678900",
            "nested": {
                "key1": "value1",
                "key2": 123
            },
            "list": [1, 2, 3]
        }

        notification = Notification(
            type=NotificationType.NEW_LEAD,
            title="Test",
            message="Test",
            user_id=admin_user.id,
            extra=complex_metadata
        )

        session.add(notification)
        session.commit()

        session.refresh(notification)

        assert notification.extra is not None
        assert notification.extra["lead_id"] == "abc123"
        assert notification.extra["nested"]["key1"] == "value1"
        assert notification.extra["list"] == [1, 2, 3]

@pytest.mark.unit()
class TestModelRelationships:

    def test_delete_debtor_with_debts_raises_error(self, session, debtor, creditor):
        debt = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("1000.00"),
            due_date=date(2024, 1, 1)
        )

        session.add(debt)
        session.commit()

        session.delete(debtor)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_delete_creditor_with_debts_raises_error(self, session, debtor, creditor):
        debt = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("1000.00"),
            due_date=date(2024, 1, 1)
        )

        session.add(debt)
        session.commit()

        session.delete(creditor)

        with pytest.raises(IntegrityError):
            session.commit()

    def test_cascade_delete_debt_agreements(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("500.00"),
            installment_value=Decimal("100.00"),
            installments_quantity=5,
            first_due_date=date(2024, 3, 1)
        )

        session.add(agreement)
        session.commit()

        agreement_id = agreement.id

        session.delete(debt)
        session.commit()

        deleted_agreement = session.get(Agreement, agreement_id)

        assert deleted_agreement is None

    def test_full_chain_relationship(self, session, debtor, creditor):

        debt = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("1200.00"),
            due_date=date(2024, 1, 1)
        )

        session.add(debt)
        session.flush()

        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1200.00"),
            installments_quantity=12,
            installment_value=Decimal("100.00"),
            first_due_date=date(2024, 3, 1)
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            agreement_id=agreement.id,
            installment_number=1,
            value=Decimal("100.00"),
            due_date=date(2024, 3, 1)
        )
        session.add(installment)
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("100.00"),
            paid_at=datetime.utcnow(),
            method=MethodPayment.PIX
        )
        session.add(payment)
        session.commit()

        assert payment.installment.id == installment.id
        assert installment.agreement.id == agreement.id
        assert agreement.debt.id == debt.id
        assert debt.debtor.id == debtor.id
        assert debt.creditor.id == creditor.id
