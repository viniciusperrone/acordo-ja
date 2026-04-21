from common.filters.base import BaseFilter
from debts.models import Debt


class DebtFilter(BaseFilter):
    model = Debt

    fields = {
        "id": ["exact", "in"],
        "debtor_id": ["exact", "in"],
        "creditor_id": ["exact", "in"],
        "original_value": ["exact", "gte", "lte"],
        "updated_value": ["exact", "gte", "lte"],
        "due_date": ["exact", "gte", "lte"],
        "status": ["exact", "in"],
        "renegotiation_count": ["exact", "gte", "lte"],
        "last_agreement_date": ["exact", "gte", "lte"],
        "created_at": ["exact", "gte", "lte"],
    }
