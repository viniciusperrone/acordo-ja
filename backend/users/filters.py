from common.filters.base import BaseFilter
from users import User


class UserFilter(BaseFilter):
    model = User

    ordering_fields = [
        "name",
        "email",
        "created_at",
    ]

    fields = {
        'id': ['exact', 'in'],
        'name': ['exact', 'like'],
        'email': ['exact', 'like'],
        'is_active': ['exact'],
        'role': ['exact', 'in'],
        'created_at': ['exact', 'lte', 'gte'],
    }
