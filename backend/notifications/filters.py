from common.filters.base import BaseFilter
from notifications import Notification


class NotificationFilter(BaseFilter):
    model = Notification

    fields = {
        "is_read": ["exact"],
        "notification_type": ["exact", "in"],
    }

    ordering_fields = ('created_at',)
