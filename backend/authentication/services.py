import datetime

from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

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

    @staticmethod
    def update_password(user, data, session):
        old_password = data["old_password"]

        if not old_password:
            raise ValidationError("Old Password is required")

        old_password_is_valid = user.check_password(old_password)

        if not old_password_is_valid:
            raise ValidationError("Old Password is invalid")

        if not data["new_password"] or not data["confirm_password"]:
            raise ValidationError("New Password and Confirm Password are required")

        if data["new_password"] != data["confirm_password"]:
            raise ValidationError("Password and Confirm Password are not equal")

        user.set_password(data["new_password"])

        session.flush

        return user
