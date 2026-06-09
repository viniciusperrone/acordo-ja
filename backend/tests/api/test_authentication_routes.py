import uuid

import pytest

from authentication.models import PasswordResetToken, TokenBlocklist


@pytest.mark.api
class TestAuthenticationRoutes:
    """
    Test suite for authentication API endpoints.

    Covers authentication workflows including login,
    password updates, password recovery, password reset,
    logout, and access control validation.
    """

    def test_login_success(self, client, admin_user):
        response = client.post(
            "/auth/login",
            json={
                "email": admin_user.email,
                "password": "AcordoJA@2026",
            }
        )

        assert response.status_code == 200

        data = response.json

        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_credentials(self, client, admin_user):
        response = client.post(
            "/auth/login",
            json={
                "email": admin_user.email,
                "password": "wrong-password",
            }
        )

        assert response.status_code == 401

    def test_update_password_success(self, client, admin_user, auth_headers_admin):
        response = client.patch(
            "/auth/me/update-password",
            headers=auth_headers_admin,
            json={
                "old_password": "AcordoJA@2026",
                "new_password": "NewPassword@2026",
                "confirm_password": "NewPassword@2026",
            }
        )

        assert response.status_code == 200

        assert (
            response.json["message"] == "Password changed successfully"
        )

    def test_update_password_requires_authentication(self, client):
        response = client.patch(
            "/auth/me/update-password",
            json={
                "old_password": "AcordoJA@2026",
                "new_password": "NewPassword@2026",
                "confirm_password": "NewPassword@2026",
            }
        )

        assert response.status_code == 401

    def test_update_password_invalid_old_password(self, client, auth_headers_admin):
        response = client.patch(
            "/auth/me/update-password",
            headers=auth_headers_admin,
            json={
                "old_password": "wrong-password",
                "new_password": "NewPassword@2026",
                "confirm_password": "NewPassword@2026",
            },
        )

        assert response.status_code == 400

    def test_forgot_password_success(self, client, admin_user, session):
        response = client.post(
            "/auth/forgot-password",
            json={
                "email": admin_user.email,
            }
        )

        assert response.status_code == 200

        token = (
            session.query(PasswordResetToken)
            .filter_by(user_id=admin_user.id)
            .first()
        )

        assert token is not None

    def test_forgot_password_user_not_found(self, client):
        response = client.post(
            "/auth/forgot-password",
            json={
                "email": "unknown@test.com",
            }
        )

        assert response.status_code in [400, 404]

    def test_reset_password_success(self, client, admin_user, session):
        response = client.post(
            "/auth/forgot-password",
            json={
                "email": admin_user.email
            }
        )

        assert response.status_code == 200

        token = (
            session.query(PasswordResetToken)
            .filter_by(user_id=admin_user.id)
            .first()
        )

        response = client.put(
            f"/auth/{token.token}/reset-password",
            json={
                "new_password": "ResetPassword@2026",
                "confirm_password": "ResetPassword@2026",
            },
        )

        assert response.status_code == 200

        session.refresh(token)

        assert token.is_used is True

    def test_reset_password_invalid_token(self, client):
        response = client.put(
            f"/auth/{uuid.uuid4()}/reset-password",
            json={
                "new_password": "ResetPassword@2026",
                "confirm_password": "ResetPassword@2026",
            }
        )

        assert response.status_code in [400, 404]

    def test_logout_success(self, client, session, auth_headers_admin):
        response = client.post(
            "/auth/logout",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200

        token = session.query(TokenBlocklist).first()

        assert token is not None

    def test_logout_requires_authentication(self, client):
        response = client.post("/auth/logout")

        assert response.status_code == 401
