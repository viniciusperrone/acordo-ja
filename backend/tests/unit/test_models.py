import pytest

from decimal import Decimal
from datetime import date

from users.models import User
from creditor.models import Creditor
from debtor.models import Debtor
from debts.models import Debt
from agreement.models import Agreement

from sqlalchemy.exc import IntegrityError

from utils.enum import UserRole, DebtStatus, AgreementStatus


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

    def test_create_debtor(self, session):
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


    def test_unique_document(self, session):
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

    def test_optional_fields(self, session):
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

    def test_create_debt(self, session, debtor, creditor):
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

    def test_relationships(self, session, debt):
        assert debt.debtor is not None
        assert debt.creditor is not None

@pytest.mark.unit
class TestAgreementModel:

    def test_create_agreement(self, session, debt):
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

    def test_agreement_default_status(self, session, debt):
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

    def test_agreement_relationship_with_debt(self, session, debt):
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
