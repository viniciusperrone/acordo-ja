import pytest

from decimal import Decimal

from users.models import User
from creditor.models import Creditor

from users.filters import UserFilter
from creditor.filters import CreditorFilter


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
