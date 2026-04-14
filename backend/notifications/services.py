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
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None,
        session=None,
    ) -> Notification:
        notification = Notification(
            type=notification_type,
            title=title,
            message=message,
            metadata=metadata,
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
        metadata: Optional[dict] = None,
        roles: Optional[List[UserRole]] = None,
        session=None,
    ) -> List[Notification]:

        if roles is None:
            roles = [UserRole.ADMIN, UserRole.MANAGER, UserRole.AGENT]

        users = User.query.filter(
            User.is_active == True,
            User.roles.in_(roles),
        ).all()

        notifications = []
        for user in users:
            notification = NotificationService.create_notification(
                notification_type=notification_type,
                title=title,
                message=message,
                metadata=metadata,
                user_id=user.id,
                session=session,
            )

            notifications.append(notification)

        return notifications