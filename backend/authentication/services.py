from datetime import datetime

from flask_jwt_extended import create_access_token, create_refresh_token
from marshmallow import ValidationError

from users.exceptions import UserNotFoundError
from users.models import User
from authentication.models import PasswordResetToken
from authentication.exceptions import InvalidCredentials, InvalidPasswordResetToken


class AuthenticationService:

    @staticmethod
    def __generate_token():
        import secrets

        return secrets.token_urlsafe(32)

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

    @staticmethod
    def forgot_password(data, session):
        email = data["email"]

        if not email:
            raise ValidationError("Email is required")

        user = session.query(User).filter(User.email == email).first()

        if not user:
            raise UserNotFoundError

        password_reset_token = PasswordResetToken(
            user_id=user.id,
            token=AuthenticationService.__generate_token(),
        )

        session.add(password_reset_token)
        session.flush()

    @staticmethod
    def reset_password(url_safe, data, session):
        token = session.query(PasswordResetToken).filter(PasswordResetToken.token == url_safe).first()

        if not token:
            raise InvalidPasswordResetToken

        if token.is_expired:
            raise InvalidPasswordResetToken

        if token.is_used:
            raise InvalidPasswordResetToken

        if data["new_password"] != data["confirm_password"]:
            raise ValidationError("Password and Confirm Password are not equal")

        user = session.query(User).filter(User.id == token.user_id).first()

        if not user:
            raise UserNotFoundError

        user.set_password(data["new_password"])
        token.used_at = datetime.utcnow()

        session.flush()
