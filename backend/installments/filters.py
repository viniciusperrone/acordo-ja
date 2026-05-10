from common.filters.base import BaseFilter
from installments import Installments


class InstallmentFilter(BaseFilter):
    model = Installments

    fields = {
        "agreement_id": ["exact", "in"],
        "status": ["exact", "in"],
        "due_date": ["exact", "gte", "lte"],
        "value": ["exact", "gte", "lte"],
    }

    ordering_fields = [
        "installment_number",
        "due_date",
        "value",
        "created_at",
    ]
