from common.filters.base import BaseFilter
from payment import Payment


class PaymentFilter(BaseFilter):
    model = Payment

    fields = {
        "method": ["exact", "like"],
        "amount": ["exact", "gte", "lte"],
        "installment_id": ["exact", "in"],
        "paid_at": ["exact", "gte", "lte"],
        "created_at": ["exact", "gte", "lte"],
    }
