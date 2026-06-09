import pytest

from debtor.models import Debtor


@pytest.fixture
def debtor(session):
    debtor = Debtor(
        name="João da Silva",
        document="52998224725",
        email="joao@test.com",
        phone="11999999999"
    )

    session.add(debtor)
    session.commit()

    return debtor
