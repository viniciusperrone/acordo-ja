import datetime

from flask_jwt_extended import create_access_token, create_refresh_token

from users.models import User
from authentication.exceptions import InvalidCredentials


class AuthenticationService:

    @staticmethod
    def login(email, password, session):
        user = session.query(User).filter(User.email == email).first()

        if not user or not user.check_password(password):
            raise InvalidCredentials

        access_token = create_access_token(
            identity=user.id,
            expires_delta=datetime.timedelta(hours=6),
            additional_claims={
                "role": user.role.value
            }
        )

        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=datetime.timedelta(days=7)
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
