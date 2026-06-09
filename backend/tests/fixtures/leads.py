import pytest

from leads.models import Lead


@pytest.fixture
def lead(session):
    lead = Lead(
        name="Maria Santos",
        document="98765432100",
        email="maria@test.com",
        phone="11988888888"
    )

    session.add(lead)
    session.commit()

    return lead
