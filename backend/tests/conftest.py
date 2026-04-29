import pytest
from datetime import datetime, date
from decimal import Decimal
import os

from utils.enum import UserRole, DebtStatus

os.environ["TESTING"] = "True"

from app import initialize_app
from config.db import db as _db
from users.models import User
from debtor.models import Debtor
from creditor.models import Creditor
from debts.models import Debt


@pytest.fixture(scope="session")
def app():
    app = initialize_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI":  "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY")
    })

    yield app

@pytest.fixture(scope="session")
def db(app):

    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope="function")
def session(db, app):

    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session

        yield session

        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(app):

    return app.test_client()

@pytest.fixture
def admin_user(session):
    user = User(
        name="Admin User",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True,
    )

    user.set_password("AcordoJA@2026")

    session.add(user)
    session.commit()

    return user

@pytest.fixture
def manager_user(session):
    user = User(
        name="Manager User",
        email="manager@test.com",
        role=UserRole.MANAGER,
        is_active=True,
    )

    user.set_password("AcordoJA@2026")

    session.add(user)
    session.commit()

    return user

@pytest.fixture
def agent_user(session):
    user = User(
        name="Agent User",
        email="agent@test.com",
        role=UserRole.AGENT,
        is_active=True,
    )

    user.set_password("AcordoJA@2026")

    session.add(user)
    session.commit()

    return user

@pytest.fixture
def auth_headers_admin(client, admin_user):
    response = client.post('/auth/login', json={
        'email': 'admin@test.com',
        'password': 'AcordoJA@2026'
    })

    token = response.json.get('access_token')

    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

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

@pytest.fixture
def debtor(session):
    debtor = Debtor(
        name="João da Silva",
        document="12345678900",
        email="joao@test.com",
        phone="11999999999"
    )

    session.add(debtor)
    session.commit()

    return debtor

@pytest.fixture
def debt(session, debtor, creditor):
    debt = Debt(
        debtor_id=debtor.id,
        creditor_id=creditor.id,
        original_value=Decimal("1000.00"),
        updated_value=None,
        due_date=date(2024, 1, 15),
        status=DebtStatus.OPEN
    )

    session.add(debt)
    session.commit()

    return debt

@pytest.fixture
def lead(session):
    from leads.models import Lead

    lead = Lead(
        name="Maria Santos",
        document="98765432100",
        email="maria@test.com",
        phone="11988888888"
    )

    session.add(lead)
    session.commit()

    return lead

@pytest.fixture
def sample_debt_data(debtor, creditor):
    return {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": "1500.00",
        "due_date": "2024-06-01"
    }

@pytest.fixture
def sample_creditor_data(creditor, debtor):
    return {
        "debt_id": str(debt.id),
        "installments_quantity": 6,
        "discount_applied": 0,
        "entry_value": 0,
        "first_due_date": "2024-03-01"
    }

@pytest.fixture
def mock_datetime(monkeypatch):

    class MockDateTime:

        @staticmethod
        def utcnow():
            return datetime(2024, 2, 15, 10, 30, 0)

        @staticmethod
        def now():
            return datetime(2024, 2, 15, 10, 30, 0)

    monkeypatch.setattr("datetime.datetime", MockDateTime)
    return MockDateTime
