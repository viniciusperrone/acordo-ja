from typing import Optional, List
from datetime import datetime

from notifications.models import Notification
from users.models import User
from utils.enum import NotificationType, UserRole


class NotificationService:

    @staticmethod
    def create_notification(
        notification_type: NotificationType,
        title: str,
        message: str,
        extra: Optional[dict] = None,
        user_id: Optional[str] = None,
        session=None,
    ) -> Notification:
        notification = Notification(
            type=notification_type,
            title=title,
            message=message,
            extra=extra,
            user_id=user_id,
        )

        session.add(notification)
        session.flush()

        return notification

    @staticmethod
    def create_notification_for_roles(
        notification_type: NotificationType,
        title: str,
        message: str,
        extra: Optional[dict] = None,
        roles: Optional[List[UserRole]] = None,
        session=None,
    ) -> List[Notification]:

        if roles is None:
            roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT]

        users = User.query.filter(
            User.is_active == True,
            User.role.in_(roles),
        ).all()

        notifications = []

        for user in users:
            notification = NotificationService.create_notification(
                notification_type=notification_type,
                title=title,
                message=message,
                extra=extra,
                user_id=user.id,
                session=session,
            )

            notifications.append(notification)

        if not users:
            notification = NotificationService.create_notification(
                notification_type=notification_type,
                title=title,
                message=message,
                extra=extra,
                session=session,
            )

            notifications.append(notification)

        return notifications

    @staticmethod
    def mark_as_read(notification_id: str, session=None):
        notification = session.get(Notification, notification_id)

        if notification:
            notification.mark_as_read()
            session.flush()

        return notification

    @staticmethod
    def mark_multiple_as_read(notification_ids: List[str], session=None) -> int:

        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.is_read == False,
        ).all()

        count = 0
        for notification in notifications:
            notification.mark_as_read()
            count += 1

        session.flush()
        return count

    @staticmethod
    def mark_all_read_for_user(user_id: str, session=None) -> int:
        notifications = Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).all()

        count = 0
        for notifications in notifications:
            notifications.mark_as_read()
            count += 1

        session.flush()
        return count

    @staticmethod
    def get_unread_count(user_id: str) -> int:
        return Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
        ).count()

    @staticmethod
    def delete_old_notifications(days: int = 30, session = None):
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_notifications = Notification.query.filter(
            Notification.is_read == True,
            Notification.read_at < cutoff_date,
        ).all()

        count = len(old_notifications)

        for notification in old_notifications:
            session.delete(notification)

        session.flush()
        return count
