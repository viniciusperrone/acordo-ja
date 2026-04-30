import pytest
""
import uuid

from users.models import User
from users.services import UserService
from users.exceptions import UserNotFoundError

from utils.enum import UserRole


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
