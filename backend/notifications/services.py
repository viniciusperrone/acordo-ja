from typing import Optional, List
from datetime import datetime

from notifications.models import Notification
from users.models import User
from utils.enum import NotificationType, UserRole


class NotificationService:

    @staticmethod
    def create_notification(
        type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None,
        session=None,
    ) -> Notification:
        notification = Notification(
            type=type,
            title=title,
            message=message,
            metadata=metadata,
            user_id=user_id,
        )

        session.add(notification)
        session.flush()

        return notification