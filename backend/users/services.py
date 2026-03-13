from users import User
from utils.enum import UserRole
from .exceptions import EmailAlreadyExists

class UserService:

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

        return user