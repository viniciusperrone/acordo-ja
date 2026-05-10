import pytest

from decimal import Decimal

from users.models import User
from creditor.models import Creditor
from debtor.models import Debtor

from users.filters import UserFilter
from creditor.filters import CreditorFilter
from debtor.filters import DebtorFilter


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
