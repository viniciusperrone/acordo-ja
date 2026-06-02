import pytest

from decimal import Decimal
from datetime import date, timedelta, datetime

from users.models import User
from creditor.models import Creditor
from debtor.models import Debtor
from debts.models import Debt
from agreement.models import Agreement
from installments.models import Installments
from payment.models import Payment
from notifications.models import Notification

from users.filters import UserFilter
from creditor.filters import CreditorFilter
from debtor.filters import DebtorFilter
from debts.filters import DebtFilter
from installments.filters import InstallmentFilter
from payment.filters import PaymentFilter
from notifications.filters import NotificationFilter

from utils.enum import (
    InstallmentStatus,
    MethodPayment,
    AgreementStatus,
    NotificationType
)


@pytest.mark.unit
class TestUserFilter:

    def test_should_filter_by_exact_name(
        self,
        session,
        manager_user,
        agent_user,
    ):
        query = session.query(User)

        params = {
            "name": manager_user.name
        }

        result = UserFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == manager_user.id

    def test_should_filter_by_like_name(
        self,
        session,
        manager_user,
        agent_user,
    ):
        query = session.query(User)

        params = {
            "name__like": "Manager"
        }

        result = UserFilter(query, params).apply().all()

        assert len(result) >= 1

        for user in result:
            assert "manager" in user.name.lower()

    def test_should_filter_by_exact_email(
        self,
        session,
        manager_user,
    ):
        query = session.query(User)

        params = {
            "email": manager_user.email
        }

        result = UserFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].email == manager_user.email

    def test_should_filter_by_role_in(
        self,
        session,
        manager_user,
        agent_user,
    ):
        query = session.query(User)

        params = {
            "role__in": f"{manager_user.role.value},{agent_user.role.value}"
        }

        result = UserFilter(query, params).apply().all()

        assert len(result) >= 2

    def test_should_ignore_invalid_field(
        self,
        session,
    ):
        query = session.query(User)

        params = {
            "invalid_field": "test"
        }

        result = UserFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(
        self,
        session,
    ):
        query = session.query(User)

        params = {
            "name__invalid": "test"
        }

        result = UserFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_order_by_name_ascending(
        self,
        session,
        manager_user,
        agent_user,
    ):
        query = session.query(User)

        params = {
            "ordering": "name"
        }

        result = UserFilter(query, params).apply().all()

        names = [user.name for user in result]

        assert names == sorted(names)

    def test_should_order_by_name_descending(
        self,
        session,
        manager_user,
        agent_user,
    ):
        query = session.query(User)

        params = {
            "ordering": "-name"
        }

        result = UserFilter(query, params).apply().all()

        names = [user.name for user in result]

        assert names == sorted(names, reverse=True)


@pytest.mark.unit
class TestCreditorFilter:

    def test_should_filter_by_exact_bank_code(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "bank_code": creditor.bank_code
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == creditor.id

    def test_should_filter_by_bank_code_in(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "bank_code__in": creditor.bank_code
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_interest_rate_gt(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "interest_rate__gt": Decimal("0.01")
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.interest_rate > Decimal("0.01")

    def test_should_filter_interest_rate_lt(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "interest_rate__lt": Decimal("1.00")
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.interest_rate < Decimal("1.00")

    def test_should_filter_fine_rate_gt(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "fine_rate__gt": Decimal("0.01")
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_discount_limit_gt(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "discount_limit__gt": Decimal("0.01")
        }

        result = CreditorFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_ignore_invalid_field(self, creditor, session):
        query = session.query(Creditor)

        params = {
            "invalid_field": "test"
        }

        result = CreditorFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(
        self,
        session,
    ):
        query = session.query(Creditor)

        params = {
            "bank_code__invalid": "001"
        }

        result = CreditorFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_order_by_interest_rate_ascending(self, session):
        creditor_1 = Creditor(
            bank_code="001",
            interest_rate=Decimal("0.10"),
            fine_rate=Decimal("0.02"),
            discount_limit=Decimal("0.20"),
        )

        creditor_2 = Creditor(
            bank_code="237",
            interest_rate=Decimal("0.05"),
            fine_rate=Decimal("0.02"),
            discount_limit=Decimal("0.20"),
        )

        session.add_all([creditor_1, creditor_2])
        session.commit()

        query = session.query(Creditor)

        params = {
            "ordering": "interest_rate"
        }

        result = CreditorFilter(query, params).apply().all()

        rates = [item.interest_rate for item in result]

        assert rates == sorted(rates)

    def test_should_order_by_interest_rate_descending(self, session):
        query = session.query(Creditor)

        params = {
            "ordering": "-interest_rate"
        }

        result = CreditorFilter(query, params).apply().all()

        rates = [item.interest_rate for item in result]

        assert rates == sorted(rates, reverse=True)


@pytest.mark.unit
class TestDebtorFilter:

    def test_should_filter_by_exact_name(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "name": debtor.name
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == debtor.id

    def test_should_filter_by_like_name(self, debtor, session):
        query = session.query(Debtor)

        partial_name = debtor.name[:4]

        params = {
            "name__like": partial_name
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert partial_name.lower() in item.name.lower()

    def test_should_filter_by_exact_document(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "document": debtor.document
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == debtor.id

    def test_should_filter_by_like_document(self, debtor, session):
        query = session.query(Debtor)

        partial_document = debtor.document[:5]

        params = {
            "document__like": partial_document
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert partial_document in item.document

    def test_should_filter_by_exact_email(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "email": debtor.email
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].email == debtor.email

    def test_should_filter_by_like_email(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "email__like": "@"
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_by_exact_phone(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "phone": debtor.phone
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].phone == debtor.phone

    def test_should_filter_by_like_phone(self, debtor, session):
        query = session.query(Debtor)

        partial_phone = debtor.phone[:4]

        params = {
            "phone__like": partial_phone
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert partial_phone in item.phone

    def test_should_filter_id_in(self, debtor, session):
        query = session.query(Debtor)

        params = {
            "id__in": str(debtor.id)
        }

        result = DebtorFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_ignore_invalid_field(self, session):
        query = session.query(Debtor)

        params = {
            "invalid_field": "test"
        }

        result = DebtorFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(self, session):
        query = session.query(Debtor)

        params = {
            "name__invalid": "test"
        }

        result = DebtorFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_order_by_name_ascending(self, session):
        debtor_1 = Debtor(
            name="Zulu",
            document="52998224725",
            email="zulu@test.com",
            phone="11999999999",
        )

        debtor_2 = Debtor(
            name="Alpha",
            document="39053344705",
            email="alpha@test.com",
            phone="11888888888",
        )

        session.add_all([debtor_1, debtor_2])
        session.commit()

        query = session.query(Debtor)

        params = {
            "ordering": "name"
        }

        result = DebtorFilter(query, params).apply().all()

        names = [item.name for item in result]

        assert names == sorted(names)

    def test_should_order_by_name_descending(self, session):
        query = session.query(Debtor)

        params = {
            "ordering": "-name"
        }

        result = DebtorFilter(query, params).apply().all()

        names = [item.name for item in result]

        assert names == sorted(names, reverse=True)


@pytest.mark.unit
class TestDebtFilter:

    def test_should_filter_by_exact_id(self, debt, session):
        query = session.query(Debt)

        params = {
            "id": debt.id
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == debt.id

    def test_should_filter_by_id_in(self, debt, session):
        query = session.query(Debt)

        params = {
            "id__in": f"{debt.id}"
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_by_exact_debtor_id(self, debt, session):
        query = session.query(Debt)

        params = {
            "debtor_id": debt.debtor_id
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.debtor_id == debt.debtor_id

    def test_should_filter_by_exact_creditor_id(self, debt, session):
        query = session.query(Debt)

        params = {
            "creditor_id": debt.creditor_id
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.creditor_id == debt.creditor_id

    def test_should_filter_by_original_value_gte(self, debt, session):
        query = session.query(Debt)

        params = {
            "original_value__gte": Decimal("1000.00")
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.original_value >= Decimal("1000.00")

    def test_should_filter_by_original_value_lte(self, debt, session):
        query = session.query(Debt)

        params = {
            "original_value__lte": Decimal("999999.00")
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.original_value <= Decimal("999999.00")

    def test_should_filter_by_updated_value_exact(self, debt, session):
        debt.updated_value = Decimal("3500.00")
        session.commit()

        query = session.query(Debt)

        params = {
            "updated_value": Decimal("3500.00")
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.updated_value == Decimal("3500.00")

    def test_should_filter_by_due_date_exact(self, debt, session):
        query = session.query(Debt)

        params = {
            "due_date": str(debt.due_date)
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.due_date == debt.due_date

    def test_should_filter_by_status_exact(self, debt, session):
        query = session.query(Debt)

        params = {
            "status": debt.status.value
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.status == debt.status

    def test_should_filter_by_status_in(self, debt, session):
        query = session.query(Debt)

        params = {
            "status__in": debt.status.value
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_by_renegotiation_count_gte(self, debt, session):
        debt.renegotiation_count = 2
        session.commit()

        query = session.query(Debt)

        params = {
            "renegotiation_count__gte": 1
        }

        result = DebtFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.renegotiation_count >= 1

    def test_should_ignore_invalid_field(self, session):
        query = session.query(Debt)

        params = {
            "invalid_field": "test"
        }

        result = DebtFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(self, session):
        query = session.query(Debt)

        params = {
            "status__invalid": "OPEN"
        }

        result = DebtFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_order_by_original_value_ascending(self, creditor, debtor, session):
        debt_1 = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("5000.00"),
            due_date=date(2026, 5, 10),
        )

        debt_2 = Debt(
            debtor_id=debtor.id,
            creditor_id=creditor.id,
            original_value=Decimal("1000.00"),
            due_date=date(2026, 5, 10),
        )

        session.add_all([debt_1, debt_2])
        session.commit()

        query = session.query(Debt)

        params = {
            "ordering": "original_value"
        }

        result = DebtFilter(query, params).apply().all()

        values = [item.original_value for item in result]

        assert values == sorted(values)

    def test_should_order_by_original_value_descending(self, session):
        query = session.query(Debt)

        params = {
            "ordering": "-original_value"
        }

        result = DebtFilter(query, params).apply().all()

        values = [item.original_value for item in result]

        assert values == sorted(values, reverse=True)


@pytest.mark.unit
class TestInstallmentFilter:

    def test_should_filter_by_exact_agreement_id(
        self,
        session,
        agreement,
    ):
        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        query = session.query(Installments)

        params = {
            "agreement_id": agreement.id
        }

        result = InstallmentFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == installment.id

    def test_should_filter_by_status_exact(
        self,
        session,
        agreement,
    ):
        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.commit()

        query = session.query(Installments)

        params = {
            "status": InstallmentStatus.PENDING.value
        }

        result = InstallmentFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.status == InstallmentStatus.PENDING

    def test_should_filter_by_status_in(
        self,
        session,
        agreement,
    ):
        pending_installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        paid_installment = Installments(
            installment_number=2,
            due_date=date(2026, 6, 6),
            value=Decimal("200.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add_all([
            pending_installment,
            paid_installment,
        ])
        session.commit()

        query = session.query(Installments)

        params = {
            "status__in": (
                f"{InstallmentStatus.PENDING.value},"
                f"{InstallmentStatus.PAID.value}"
            )
        }

        result = InstallmentFilter(query, params).apply().all()

        assert len(result) >= 2

    def test_should_filter_by_due_date_gte(
        self,
        session,
        agreement,
    ):
        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 7, 6),
            value=Decimal("200.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.commit()

        query = session.query(Installments)

        params = {
            "due_date__gte": "2026-06-01"
        }

        result = InstallmentFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == installment_2.id

    def test_should_filter_by_value_lte(
        self,
        session,
        agreement,
    ):
        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 6, 6),
            value=Decimal("500.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.commit()

        query = session.query(Installments)

        params = {
            "value__lte": "200.00"
        }

        result = InstallmentFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == installment_1.id

    def test_should_order_by_due_date_ascending(
        self,
        session,
        agreement,
    ):
        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 7, 6),
            value=Decimal("300.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.commit()

        query = session.query(Installments)

        params = {
            "ordering": "due_date"
        }

        result = InstallmentFilter(query, params).apply().all()

        due_dates = [item.due_date for item in result]

        assert due_dates == sorted(due_dates)

    def test_should_order_by_value_descending(
        self,
        session,
        agreement,
    ):
        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("100.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 6, 6),
            value=Decimal("500.00"),
            status=InstallmentStatus.PENDING,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.commit()

        query = session.query(Installments)

        params = {
            "ordering": "-value"
        }

        result = InstallmentFilter(query, params).apply().all()

        values = [item.value for item in result]

        assert values == sorted(values, reverse=True)

    def test_should_ignore_invalid_field(
        self,
        session,
    ):
        query = session.query(Installments)

        params = {
            "invalid_field": "test"
        }

        result = InstallmentFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(
        self,
        session,
    ):
        query = session.query(Installments)

        params = {
            "value__invalid": "100"
        }

        result = InstallmentFilter(query, params).apply().all()

        assert isinstance(result, list)


@pytest.mark.unit
class TestPaymentFilter:

    def test_should_filter_by_exact_method(
        self,
        session,
        debt,
    ):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=1,
            installment_value=Decimal("1000.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE,
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("1000.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("1000.00"),
            method=MethodPayment.PIX,
            paid_at=datetime.utcnow(),
        )

        session.add(payment)
        session.commit()

        query = session.query(Payment)

        params = {
            "method": MethodPayment.PIX.value
        }

        result = PaymentFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.method == MethodPayment.PIX

    def test_should_filter_by_method_like(
        self,
        session,
        debt,
    ):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("500.00"),
            installments_quantity=1,
            installment_value=Decimal("500.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE,
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("500.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.flush()

        payment = Payment(
            installment_id=installment.id,
            amount=Decimal("500.00"),
            method=MethodPayment.PIX,
            paid_at=datetime.utcnow(),
        )

        session.add(payment)
        session.commit()

        query = session.query(Payment)

        params = {
            "method__like": "PI"
        }

        result = PaymentFilter(query, params).apply().all()

        assert len(result) >= 1

    def test_should_filter_by_amount_gte(
        self,
        session,
        debt,
    ):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1500.00"),
            installments_quantity=2,
            installment_value=Decimal("750.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE,
        )

        session.add(agreement)
        session.flush()

        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("300.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 6, 6),
            value=Decimal("900.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.flush()

        payment_1 = Payment(
            installment_id=installment_1.id,
            amount=Decimal("300.00"),
            method=MethodPayment.PIX,
            paid_at=datetime.utcnow(),
        )

        payment_2 = Payment(
            installment_id=installment_2.id,
            amount=Decimal("900.00"),
            method=MethodPayment.BOLETO,
            paid_at=datetime.utcnow(),
        )

        session.add_all([payment_1, payment_2])
        session.commit()

        query = session.query(Payment)

        params = {
            "amount__gte": "500.00"
        }

        result = PaymentFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == payment_2.id

    def test_should_filter_by_installment_id_in(
        self,
        session,
        debt,
    ):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("2000.00"),
            installments_quantity=2,
            installment_value=Decimal("1000.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE,
        )

        session.add(agreement)
        session.flush()

        installment_1 = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("1000.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        installment_2 = Installments(
            installment_number=2,
            due_date=date(2026, 6, 6),
            value=Decimal("1000.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add_all([installment_1, installment_2])
        session.flush()

        payment_1 = Payment(
            installment_id=installment_1.id,
            amount=Decimal("1000.00"),
            method=MethodPayment.PIX,
            paid_at=datetime.utcnow(),
        )

        payment_2 = Payment(
            installment_id=installment_2.id,
            amount=Decimal("1000.00"),
            method=MethodPayment.CARTAO,
            paid_at=datetime.utcnow(),
        )

        session.add_all([payment_1, payment_2])
        session.commit()

        query = session.query(Payment)

        params = {
            "installment_id__in": (
                f"{installment_1.id},{installment_2.id}"
            )
        }

        result = PaymentFilter(query, params).apply().all()

        assert len(result) >= 2

    def test_should_filter_by_paid_at_lte(
        self,
        session,
        debt,
    ):
        agreement = Agreement(
            debt_id=debt.id,
            total_traded=Decimal("1000.00"),
            installments_quantity=1,
            installment_value=Decimal("1000.00"),
            first_due_date=date(2026, 5, 6),
            status=AgreementStatus.ACTIVE,
        )

        session.add(agreement)
        session.flush()

        installment = Installments(
            installment_number=1,
            due_date=date(2026, 5, 6),
            value=Decimal("1000.00"),
            status=InstallmentStatus.PAID,
            agreement_id=agreement.id,
        )

        session.add(installment)
        session.flush()

        old_payment = Payment(
            installment_id=installment.id,
            amount=Decimal("300.00"),
            method=MethodPayment.PIX,
            paid_at=datetime.utcnow() - timedelta(days=10),
        )

        recent_payment = Payment(
            installment_id=installment.id,
            amount=Decimal("700.00"),
            method=MethodPayment.BOLETO,
            paid_at=datetime.utcnow(),
        )

        session.add_all([old_payment, recent_payment])
        session.commit()

        query = session.query(Payment)

        cutoff_date = (
            datetime.utcnow() - timedelta(days=5)
        ).isoformat()

        params = {
            "paid_at__lte": cutoff_date
        }

        result = PaymentFilter(query, params).apply().all()

        assert len(result) == 1
        assert result[0].id == old_payment.id

    def test_should_ignore_invalid_field(
        self,
        session,
    ):
        query = session.query(Payment)

        params = {
            "invalid_field": "test"
        }

        result = PaymentFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(
        self,
        session,
    ):
        query = session.query(Payment)

        params = {
            "amount__invalid": "100"
        }

        result = PaymentFilter(query, params).apply().all()

        assert isinstance(result, list)


@pytest.mark.unit
class TestNotificationFilter:

    def test_should_filter_by_is_read(
        self,
        session,
        manager_user,
    ):
        notification = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Payment received",
            message="A payment has been received",
            extra={"payment_id": "123"},
            user_id=manager_user.id,
            is_read=True,
        )

        session.add(notification)
        session.commit()

        query = session.query(Notification)

        params = {
            "is_read": True
        }

        result = NotificationFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.is_read is True

    def test_should_filter_by_notification_type_exact(
        self,
        session,
        manager_user,
    ):
        notification = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Payment received",
            message="A payment has been received",
            extra={"payment_id": "123"},
            user_id=manager_user.id,
        )

        session.add(notification)
        session.commit()

        query = session.query(Notification)

        params = {
            "notification_type": NotificationType.PAYMENT_RECEIVED.value
        }

        result = NotificationFilter(query, params).apply().all()

        assert len(result) >= 1

        for item in result:
            assert item.type == NotificationType.PAYMENT_RECEIVED

    def test_should_filter_by_notification_type_in(
        self,
        session,
        manager_user,
    ):
        notification_1 = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Payment received",
            message="Payment processed",
            extra={"payment_id": "123"},
            user_id=manager_user.id,
        )

        notification_2 = Notification(
            type=NotificationType.AGREEMENT_CREATED,
            title="Agreement created",
            message="Agreement successfully created",
            extra={"agreement_id": "456"},
            user_id=manager_user.id,
        )

        session.add_all([
            notification_1,
            notification_2,
        ])
        session.commit()

        query = session.query(Notification)

        params = {
            "notification_type__in": (
                f"{NotificationType.PAYMENT_RECEIVED.value},"
                f"{NotificationType.AGREEMENT_CREATED.value}"
            )
        }

        result = NotificationFilter(query, params).apply().all()

        assert len(result) >= 2

    def test_should_order_by_created_at_ascending(
        self,
        session,
        manager_user,
    ):
        notification_1 = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Older notification",
            message="Old message",
            extra={"id": 1},
            user_id=manager_user.id,
            created_at=datetime.utcnow() - timedelta(days=1),
        )

        notification_2 = Notification(
            type=NotificationType.AGREEMENT_CREATED,
            title="Newer notification",
            message="New message",
            extra={"id": 2},
            user_id=manager_user.id,
            created_at=datetime.utcnow(),
        )

        session.add_all([
            notification_1,
            notification_2,
        ])
        session.commit()

        query = session.query(Notification)

        params = {
            "ordering": "created_at"
        }

        result = NotificationFilter(query, params).apply().all()

        created_dates = [item.created_at for item in result]

        assert created_dates == sorted(created_dates)

    def test_should_order_by_created_at_descending(
        self,
        session,
        manager_user,
    ):
        notification_1 = Notification(
            type=NotificationType.PAYMENT_RECEIVED,
            title="Older notification",
            message="Old message",
            extra={"id": 1},
            user_id=manager_user.id,
            created_at=datetime.utcnow() - timedelta(days=1),
        )

        notification_2 = Notification(
            type=NotificationType.AGREEMENT_CREATED,
            title="Newer notification",
            message="New message",
            extra={"id": 2},
            user_id=manager_user.id,
            created_at=datetime.utcnow(),
        )

        session.add_all([
            notification_1,
            notification_2,
        ])
        session.commit()

        query = session.query(Notification)

        params = {
            "ordering": "-created_at"
        }

        result = NotificationFilter(query, params).apply().all()

        created_dates = [item.created_at for item in result]

        assert created_dates == sorted(created_dates, reverse=True)

    def test_should_ignore_invalid_field(
        self,
        session,
    ):
        query = session.query(Notification)

        params = {
            "invalid_field": "test"
        }

        result = NotificationFilter(query, params).apply().all()

        assert isinstance(result, list)

    def test_should_ignore_invalid_operator(
        self,
        session,
    ):
        query = session.query(Notification)

        params = {
            "notification_type__invalid": "PAYMENT_RECEIVED"
        }

        result = NotificationFilter(query, params).apply().all()

        assert isinstance(result, list)
