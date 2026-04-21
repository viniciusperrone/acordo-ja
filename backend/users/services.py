from users.models import User
from users.exceptions import EmailAlreadyExists

from common.exceptions.auth import UnauthorizedError
from utils.enum import UserRole

class UserService:

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
