from utils.enum import UserRole
from common.exceptions.auth import UnauthorizedError

from users.models import User
from users.exceptions import EmailAlreadyExists, UserNotFoundError


class UserService:

    @staticmethod
    def get(user_id, session):
        user = session.get(User, user_id)

        if not user:
            raise UserNotFoundError

        return user

    @staticmethod
    def create_user(data, staff, session):
        if staff.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise UnauthorizedError(message="User does not have permission to create users")

        existing_user = (
            session.query(User)
            .filter(
                User.email == data['email'],
            )
            .first()
        )

        if existing_user:
            raise EmailAlreadyExists("Email already exists")

        user = User(
            name=data['name'],
            email=data['email'],
            role=UserRole.AGENT,
        )

        user.set_password(data['password'])

        session.add(user)
        session.flush()

        return user
