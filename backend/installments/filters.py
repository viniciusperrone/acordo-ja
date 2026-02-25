from common.filters.base import BaseFilter
from installments import Installments


class InstallmentFilter(BaseFilter):
    model = Installments

    fields = {
        "status": ["exact", "in"],
        "agreement_id": ["exact"],
        "due_date": ["exact", "gte", "lte"],
        "value": ["exact", "gte", "lte"],
    }

    ordering_fields = [
        "due_date",
        "value",
        "created_at",
    ]
