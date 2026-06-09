import pytest


@pytest.fixture
def auth_headers_admin(client, admin_user):
    response = client.post(
        "/auth/login",
        json={
            "email": admin_user.email,
            "password": "AcordoJA@2026",
        }
    )

    token = response.json["access_token"]

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

@pytest.fixture
def auth_headers_manager(client, manager_user):
    response = client.post(
        "/auth/login",
        json={
            "email": manager_user.email,
            "password": "AcordoJA@2026",
        }
    )

    token = response.json["access_token"]

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

@pytest.fixture
def auth_headers_agent(client, agent_user):
    response = client.post(
        "/auth/login",
        json={
            "email": agent_user.email,
            "password": "AcordoJA@2026",
        }
    )

    token = response.json["access_token"]

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
