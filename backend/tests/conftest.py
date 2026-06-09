import pytest

import os
import secrets
from sqlalchemy import event
from datetime import datetime, date, timedelta
from decimal import Decimal

from utils.enum import UserRole, DebtStatus

from app import initialize_app
from config.db import db as _db
from users.models import User
from debtor.models import Debtor
from creditor.models import Creditor
from debts.models import Debt
from agreement.models import Agreement


os.environ["TESTING"] = "True"


@pytest.fixture(scope="session")
def app():
    app = initialize_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": secrets.token_hex(32),
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False}
        }
    })

    yield app


@pytest.fixture(scope="session")
def db(app):

    with app.app_context():
        engine = _db.engine

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def session(db, app):
    from sqlalchemy.orm import sessionmaker, scoped_session

    with (app.app_context()):
        connection = db.engine.connect()
        transaction = connection.begin()

        session_factory = sessionmaker(bind=connection)
        session = scoped_session(session_factory)

        db.session = session

        yield session

        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(app, session):

    return app.test_client()

pytest_plugins = [
    "tests.fixtures.users",
    "tests.fixtures.auth",
    "tests.fixtures.creditors",
    "tests.fixtures.debtors",
    "tests.fixtures.debts",
    "tests.fixtures.agreements",
    "tests.fixtures.leads",
    "tests.fixtures.mock",
]
