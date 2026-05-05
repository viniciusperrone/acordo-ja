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

    def test_user_persists_correctly(self, session):
        user = User(
            name="John Doe",
            email="john@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            must_change_password=True,
        )
        user.set_password("password123")

        session.add(user)
        session.commit()

        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@test.com"
        assert user.role == UserRole.ADMIN
        assert user.is_active is True
        assert user.must_change_password is True
        assert user.password_hash is not None

    def test_user_email_must_be_unique(self, session):
        user1 = User(
            name="User One",
            email="same@test.com",
            role=UserRole.AGENT
        )
        user1.set_password("password")

        user2 = User(
            name="User Two",
            email="same@test.com",
            role=UserRole.MANAGER
        )
        user2.set_password("password")

        session.add(user1)
        session.commit()

        session.add(user2)

        with pytest.raises(Exception):
            session.commit()

    def test_user_password_hashing_and_verification(self, session):
        user = User(
            name="Secure User",
            email="secure@test.com",
            role=UserRole.ADMIN
        )

        user.set_password("secret123")

        assert user.password_hash != "secret123"
        assert user.check_password("secret123") is True
        assert user.check_password("wrong") is False

    def test_user_defaults(self, session):
        user = User(
            name="Default User",
            email="default@test.com",
            role=UserRole.AGENT
        )
        user.set_password("password")

        session.add(user)
        session.commit()

        assert user.is_active is True
        assert user.must_change_password is True

@pytest.mark.unit
class TestCreditorModel:

    def test_creditor_persists_correctly(self, session):
        creditor = Creditor(
            bank_code="001",
            interest_rate=5.00,
            fine_rate=2.00,
            discount_limit=20.00
        )

        session.add(creditor)
        session.commit()

        assert creditor.id is not None
        assert creditor.bank_code == "001"
        assert creditor.interest_rate == 5.00
        assert creditor.fine_rate == 2.00
        assert creditor.discount_limit == 20.00

    def test_creditor_bank_name_property(self, session):
        creditor = Creditor(
            bank_code="001",
            interest_rate=5.00,
            fine_rate=2.00,
            discount_limit=20.00
        )

        session.add(creditor)
        session.commit()

        assert creditor.bank_name is not None

    def test_creditor_has_debts_relationship(self, session, creditor):
        assert creditor.debts == []

    def test_creditor_bank_code_must_be_unique(self, session):
        c1 = Creditor(
            bank_code="001",
            interest_rate=5.00,
            fine_rate=2.00,
            discount_limit=20.00
        )

        c2 = Creditor(
            bank_code="001",
            interest_rate=3.00,
            fine_rate=1.00,
            discount_limit=10.00
        )

        session.add(c1)
        session.commit()

        session.add(c2)

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

    def test_installment_persists_correctly(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=10,
            installment_value=Decimal("100.00"),
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

@pytest.mark.unit
class TestPaymentModel:

    def test_payment_persists_correctly(self, session, debt):
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

    def test_payment_has_installment_relationship(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("200.00"),
            installments_quantity=2,
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

    def test_payment_method_is_persisted_correctly(self, session, debt):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("100.00"),
            installments_quantity=1,
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
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("100.00"),
            paid_at=datetime.utcnow(),
            method=MethodPayment.PIX
        )

        session.add(payment)
        session.commit()

        assert payment.method == MethodPayment.PIX

@pytest.mark.unit
class TestNotificationModel:

    def test_notification_persists_with_valid_data(self, session, admin_user):
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

    def test_notification_mark_as_read_updates_flags(self, session, admin_user):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="Test",
            message="Test",
            user_id=admin_user.id,
            extra={}
        )

        session.add(notification)
        session.commit()

        notification.mark_as_read()
        session.commit()

        assert notification.is_read is True
        assert notification.read_at is not None
        assert isinstance(notification.read_at, datetime)

    def test_notification_mark_as_read_is_idempotent(self, session, admin_user):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="Test",
            message="Test",
            user_id=admin_user.id,
            extra={}
        )

        session.add(notification)
        session.commit()

        notification.mark_as_read()
        first_read_at = notification.created_at

        notification.mark_as_read()
        session.commit()

        assert notification.is_read is True
        assert notification.read_at >= first_read_at

    def test_notification_to_dict_serializes_fields(self, session, admin_user):
        notification = Notification(
            type=NotificationType.AGREEMENT_CREATED,
            title="Acordo Criado",
            message="Novo criado",
            user_id=admin_user.id,
            extra={"agreement_id": "abc123"}
        )

        session.add(notification)
        session.commit()

        data = notification.to_dict()

        assert isinstance(data, dict)
        assert isinstance(data["id"], str)
        assert data["notification_type"] == "AGREEMENT_CREATED"
        assert data["title"] == "Acordo Criado"
        assert data["message"] == "Novo criado"
        assert data["is_read"] is False
        assert data["read_at"] is None
        assert isinstance(data["created_at"], str)
        assert data["extra"]["agreement_id"] == "abc123"

    def test_notification_accepts_all_enum_types(self, session, admin_user):
        for notif_type in NotificationType:
            notification = Notification(
                type=notif_type,
                title=f"Test {notif_type}",
                message="Test message",
                user_id=admin_user.id,
                extra={}
            )

            session.add(notification)

        session.commit()

        notifications = session.query(Notification).all()

        assert len(notifications) == len(NotificationType)

        for notification in notifications:
            assert notification.type in NotificationType

    def test_notification_belongs_to_user(self, session, admin_user):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="Test",
            message="Test",
            user_id=admin_user.id,
            extra={}
        )

        session.add(notification)
        session.commit()

        assert notification.user is not None
        assert notification.user.id == admin_user.id

    def test_notification_allows_null_user(self, session):
        notification = Notification(
            type=NotificationType.GENERAL,
            title="System",
            message="System message",
            user_id=None,
            extra={}
        )

        session.add(notification)
        session.commit()

        assert notification.user_id is None
        assert notification.user is None

    def test_notification_persists_json_extra(self, session, admin_user):
        payload = {
            "lead_id": "abc123",
            "nested": {"key": "value"},
            "list": [1, 2, 3]
        }

        notification = Notification(
            type=NotificationType.NEW_LEAD,
            title="Test",
            message="Test",
            user_id=admin_user.id,
            extra=payload
        )

        session.add(notification)
        session.commit()
        session.refresh(notification)

        assert notification.extra == payload
        assert notification.extra["nested"]["key"] == "value"
        assert notification.extra["list"] == [1, 2, 3]

    def test_notification_rejects_null_extra(self, session, admin_user):
        with pytest.raises(ValueError) as err:
            notification = Notification(
                type=NotificationType.GENERAL,
                title="Test",
                message="Test",
                user_id=admin_user.id,
                extra=None
            )
            session.add(notification)
            session.commit()

        assert "extra cannot be None" in str(err.value)

@pytest.mark.unit
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
