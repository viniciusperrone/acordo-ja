import pytest

from decimal import Decimal
from datetime import date, timedelta

from agreement.models import Agreement

@pytest.fixture
def agreement(session, debt):
    agreement = Agreement(
        debt_id=debt.id,
        total_traded=Decimal("12000.00"),
        installments_quantity=10,
        installment_value=Decimal("1200.00"),
        first_due_date=date.today() + timedelta(days=30),
    )

    session.add(agreement)
    session.commit()

    return agreement
