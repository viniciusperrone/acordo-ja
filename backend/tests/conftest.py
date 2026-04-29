import pytest
from datetime import datetime, date
from decimal import Decimal
import os

from utils.enum import UserRole

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

@pytest.fixture(scope="session")
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

@pytest.fixture(scope="session")
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

@pytest.fixture(scope="session")
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
