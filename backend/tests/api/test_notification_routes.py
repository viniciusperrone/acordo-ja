import pytest

import uuid

from notifications.models import Notification
from notifications.services import NotificationService
from tests.conftest import admin_user

from utils.enum import NotificationType


@pytest.mark.api
class TestNotificationRoutes:
    """
    Test suite for notification API endpoints

    Covers notification listing, unread counters, read operations,
    bulk actions, deletion, and authorization validation.
    """

    def test_list_notification_success(self, client, admin_user, session, auth_headers_admin):
        NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test",
            message="Test Notification",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.get(
            "/notifications/list",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        data = response.json

        assert "items" in data
        assert "total" in data
        assert "unread_count" in data

        assert data["total"] == 1
        assert data["unread_count"] == 1

    def test_get_unread_count_success(self, client, admin_user, session, auth_headers_admin):
        NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test",
            message="Test notification",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.get(
            "/notifications/unread-count",
            headers=auth_headers_admin,
        )

        assert response.status_code == 200
        assert response.json["unread_count"] == 1

    def test_mark_notification_as_read_success(self, client, admin_user, session, auth_headers_admin):
        notification = NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test",
            message="Test notification",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.patch(
            f"/notifications/{notification.id}/mark-read",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        session.refresh(notification)

        assert notification.is_read is True

    def test_mark_notification_as_read_not_found(self, client, auth_headers_admin):
        response = client.patch(
            f"/notifications/{uuid.uuid4()}/mark-read",
            headers=auth_headers_admin
        )

        assert response.status_code == 404

    def test_mark_notification_as_read_unauthorized(self, client, admin_user, agent_user, session, auth_headers_admin):
        notification = NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test",
            message="Test notification",
            user_id=agent_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.patch(
            f"/notifications/{notification.id}/mark-read",
            headers=auth_headers_admin
        )

        assert response.status_code == 401

    def test_mark_multiple_notifications_as_read_success(self, client, admin_user, session, auth_headers_admin):
        notification_1 = NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test 1",
            message="Test 1",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        notification_2 = NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test 2",
            message="Test 2",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.patch(
            "/notifications/mark-read-bulk",
            headers=auth_headers_admin,
            json={
                "notification_ids": [
                    str(notification_1.id),
                    str(notification_2.id),
                ]
            },
        )

        assert response.status_code == 200

        session.refresh(notification_1)
        session.refresh(notification_2)

        assert notification_1.is_read is True
        assert notification_2.is_read is True

    def test_mark_all_notifications_as_read_success(self, client, admin_user, session, auth_headers_admin):
        NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test 1",
            message="Test 1",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test 2",
            message="Test 2",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.patch(
            "/notifications/mark-all-read",
            headers=auth_headers_admin
        )

        assert response.status_code == 200

        unread_count = NotificationService.get_unread_count(admin_user.id, session)

        assert unread_count == 0

    def test_delete_notification_success(self, client, admin_user, session, auth_headers_admin):
        notification = NotificationService.create_notification(
            notification_type=NotificationType.GENERAL,
            title="Test",
            message="Message",
            user_id=admin_user.id,
            extra={},
            session=session
        )

        session.commit()

        response = client.delete(
            f"/notifications/{notification.id}",
            headers=auth_headers_admin
        )

        assert response.status_code == 204

        deleted = session.get(Notification, notification.id)

        assert deleted is None

    def test_delete_notification_not_found(self, client):
        response = client.delete(
            f"/notification/{uuid.uuid4()}/"
        )

        assert response.status_code == 404

    def test_list_notifications_requires_authentication(self, client):
        response = client.get("/notifications/list")

        assert response.status_code == 401
