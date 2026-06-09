import pytest

from decimal import Decimal

from installments.models import Installments
from utils.enum import InstallmentStatus


@pytest.fixture
def installment(session, agreement):
    installment = Installments(
        installment_number=1,
        due_date=agreement.first_due_date,
        value=Decimal("1200.00"),
        status=InstallmentStatus.PENDING,
        agreement_id=agreement.id,
    )

    session.add(installment)
    session.commit()

    return installment
