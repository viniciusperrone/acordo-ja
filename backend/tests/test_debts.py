import pytest
import uuid
from datetime import date

from creditor import Creditor
from debtor import Debtor
from debts import Debt
from debts.exceptions import CreditorNotExistError, DebtorNotExistError

from debts.services import DebtService
from utils.enum import DebtStatus


def test_should_return_empty_list_when_no_debts(client):
    response = client.get("/debts/list")

    data = response.get_json()

    assert response.status_code == 200
    assert data["items"] == []
    assert data["total"] == 0

def test_should_return_paginated_debts(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()
    db_session.flush()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()
    db_session.flush()

    creditor_id = creditor.id
    debtor_id = debtor.id

    debt = Debt(
        debtor_id=debtor_id,
        creditor_id=creditor_id,
        original_value=1000,
        updated_value=1200,
        status=DebtStatus.OPEN,
        due_date=date(2025, 3, 26)
    )

    db_session.add(debt)
    db_session.commit()

    response = client.get("/debts/list")

    data = response.get_json()

    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["current_page"] == 1

def test_should_return_debt_detail(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()
    db_session.flush()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()
    db_session.flush()

    creditor_id = creditor.id
    debtor_id = debtor.id

    debt = Debt(
        debtor_id=debtor_id,
        creditor_id=creditor_id,
        original_value=1000,
        updated_value=1200,
        status=DebtStatus.OPEN,
        due_date=date(2025, 3, 26)
    )

    db_session.add(debt)
    db_session.commit()

    response = client.get(f"debts/{debt.id}/detail")

    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == str(debt.id)

def test_create_debt(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 201


def test_missing_creditor(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debt_data = {
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "debtor_id" in response.get_json()["errors"]

def test_missing_debtor(client, db_session):
    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "creditor_id" in response.get_json()["errors"]

def test_service_should_raise_when_creditor_not_exists(client, db_session):
    creditor_id = uuid.uuid4()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": creditor_id,
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    with pytest.raises(CreditorNotExistError):
        DebtService.create_debt(debt_data, db_session)

def test_service_should_raise_when_debtor_not_exists(client, db_session):
    debtor_id = uuid.uuid4()

    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor_id,
        "creditor_id": creditor.id,
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    with pytest.raises(DebtorNotExistError):
        DebtService.create_debt(debt_data, db_session)

def test_invalid_original_value_type(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": None,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "original_value" in response.get_json()["errors"]

def test_invalid_original_value_minimum_value(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": -1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "original_value" in response.get_json()["errors"]

def test_invalid_updated_value_type(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": None,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "updated_value" in response.get_json()["errors"]

def test_invalid_updated_value_minimum_value(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": -1200,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "updated_value" in response.get_json()["errors"]

def test_updated_value_less_than_original_value(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1200,
        "updated_value": 1000,
        "due_date": "2026-03-26",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "updated_value" in response.get_json()["errors"]

def test_invalid_due_date_format(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": -1200,
        "due_date": '15-10-2026',
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "due_date" in response.get_json()["errors"]

def test_empty_json(client):
    response = client.post("/debts/add", json={})

    assert response.status_code == 400

def test_no_json_body(client):
    response = client.post("/debts/add")

    assert response.status_code in [400, 500]

def test_unexpected_extra_field(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    debtor = Debtor(
        name="John Doe",
        document="12345678909",
        email="johndoe@hotmail.com",
        phone="5541974017213"
    )

    db_session.add(debtor)
    db_session.commit()

    debt_data = {
        "debtor_id": debtor.id,
        "creditor_id": str(creditor.id),
        "original_value": 1000,
        "updated_value": 1200,
        "due_date": "2026-03-26",
        "unexpected_field": "value",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
