import pytest

from decimal import Decimal

from users.models import User
from creditor.models import Creditor
from debtor.models import Debtor
from debts.models import Debt
from agreement.models import Agreement

from sqlalchemy.exc import IntegrityError

from utils.enum import UserRole


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
