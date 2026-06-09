import pytest

from users.models import User

from utils.enum import UserRole


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
