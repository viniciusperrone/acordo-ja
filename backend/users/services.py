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
    def create_user(data, session):
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

    @staticmethod
    def update(user_id, data, session):
        user = UserService.get(user_id, session)

        if 'email' in data:
            existing_user = (
                session.query(User)
                .filter(
                    User.email == data['email'],
                    User.id != user_id
                )
                .first()
            )

            if existing_user:
                raise EmailAlreadyExists("Email already exists")

            user.email = data['email']

        if 'name' in data:
            user.name = data['name']
        if 'role' in data:
            user.role = UserRole(data['role'])

        session.flush()

        return user

    @staticmethod
    def delete(user_id, session):
        user = UserService.get(user_id, session)

        session.delete(user)
        session.flush()
