from common.filters.base import BaseFilter
from debtor import Debtor


class DebtorFilter(BaseFilter):
    model = Debtor

    ordering_fields = [
        "name",
        "document",
        "email",
        "created_at",
    ]

    fields = {
        "id": ["exact", "in"],
        "name": ["exact", "like"],
        "document": ["exact", "like"],
        "email": ["exact", "like"],
        "phone": ["exact", "like"],
        "debt_id": ["exact", "in"],
    }
