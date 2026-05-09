import pytest

from users.models import User

from users.filters import UserFilter

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
