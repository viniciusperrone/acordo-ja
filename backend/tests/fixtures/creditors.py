import pytest

from decimal import Decimal

from creditor.models import Creditor


@pytest.fixture
def creditor(session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=Decimal("0.05"),
        fine_rate=Decimal("0.02"),
        discount_limit=Decimal("0.20")
    )

    session.add(creditor)
    session.commit()

    return creditor
