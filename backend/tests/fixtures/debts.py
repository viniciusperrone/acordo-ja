import pytest

from decimal import Decimal
from datetime import date, timedelta

from debts.models import Debt
from utils.enum import DebtStatus


@pytest.fixture
def debt(session, debtor, creditor):
    debt = Debt(
        debtor_id=debtor.id,
        creditor_id=creditor.id,
        original_value=Decimal("1000.00"),
        updated_value=None,
        due_date=date.today() + timedelta(days=30),
        status=DebtStatus.OPEN
    )

    session.add(debt)
    session.commit()

    return debt
