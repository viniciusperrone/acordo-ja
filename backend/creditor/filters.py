from common.filters.base import BaseFilter
from creditor import Creditor


class CreditorFilter(BaseFilter):
    model = Creditor
    fields = {
        "bank_code": ["exact", "in"],
        "interest_rate": ["exact", "lt", "gt"],
        "fine_rate": ["exact", "lt", "gt"],
        "discount_limit": ["exact", "lt", "gt"],
    }
