from common.filters.base import BaseFilter
from creditor import Creditor


class CreditorFilter(BaseFilter):
    model = Creditor

    ordering_fields = [
        "bank_code",
        "interest_rate",
        "fine_rate",
        "discount_limit",
        "created_at",
    ]

    fields = {
        "bank_code": ["exact", "in"],
        "interest_rate": ["exact", "lt", "gt"],
        "fine_rate": ["exact", "lt", "gt"],
        "discount_limit": ["exact", "lt", "gt"],
    }
