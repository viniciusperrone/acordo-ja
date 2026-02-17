from uuid import uuid4
from creditor import Creditor
from debts.schemas import BANK_CODES
from config.db import db


def test_should_return_empty_list_when_no_creditors(client):
    response = client.get('/creditors/list')

    data = response.get_json()

    assert response.status_code == 200
    assert data["items"] == []
    assert data["total"] == 0

def test_should_return_paginated_creditors(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )
    db_session.add(creditor)
    db_session.commit()

    response = client.get('/creditors/list')

    data = response.get_json()

    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["current_page"] == 1

def test_should_paginate_creditors(client, db_session):
    for bank_code in BANK_CODES[:15]:
        db_session.add(Creditor(
            bank_code=bank_code,
            interest_rate=0.1,
            fine_rate=0.1,
            discount_limit=0.1
        ))

    db_session.commit()

    response = client.get('/creditors/list?per_page=10&page=1')

    data = response.get_json()

    assert response.status_code == 200
    assert len(data["items"]) == 10
    assert data["pages"] == 2

def test_should_return_creditor_detail(client, db_session):
    creditor = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(creditor)
    db_session.commit()

    response = client.get(f'/creditors/{creditor.id}/detail')

    data = response.get_json()

    assert response.status_code == 200
    assert data["bank_code"] == "001"

def test_should_create_creditor_successfully(client):
    creditor_data = {
        "bank_code": "001",
        "interest_rate": 0.1,
        "fine_rate": 0.1,
        "discount_limit": 0.1
    }

    response = client.post('/creditors/add', json=creditor_data, content_type='application/json')

    assert response.status_code == 201

def test_should_return_404_when_creditor_not_found(client):
    random_id = uuid4()

    response = client.get(f'/creditors/{random_id}/detail')

    data = response.get_json()

    assert response.status_code == 404
    assert data["message"] == "Creditor not found"


def test_should_return_400_when_creditor_already_exist(client, db_session):
    already_creditor_data = Creditor(
        bank_code="001",
        interest_rate=0.1,
        fine_rate=0.1,
        discount_limit=0.1
    )

    db_session.add(already_creditor_data)
    db_session.commit()

    creditor_data = {
        "bank_code": "001",
        "interest_rate": 0.1,
        "fine_rate": 0.1,
        "discount_limit": 0.1
    }

    response = client.post('/creditors/add', json=creditor_data, content_type='application/json')

    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json['message'] == 'Creditor already exists'

def test_should_return_400_when_bank_code_is_missing(client):
    creditor_data = {
        "interest_rate": 0.1,
        "fine_rate": 0.1,
        "discount_limit": 0.1
    }

    response = client.post('/creditors/add', json=creditor_data, content_type='application/json')

    assert response.status_code == 400

def test_should_return_400_when_bank_code_is_invalid(client):
    creditor_data = {
        "bank_code": "999",
        "interest_rate": 0.1,
        "fine_rate": 0.1,
        "discount_limit": 0.1
    }

    response = client.post('/creditors/add', json=creditor_data, content_type='application/json')

    assert response.status_code == 400

def test_should_return_400_when_interest_rate_is_negative(client):
    response = client.post('/creditors/add', json={
        "bank_code": "001",
        "interest_rate": -1,
        "fine_rate": 0.1,
        "discount_limit": 0.1
    })

    assert response.status_code == 400

def test_should_return_400_when_fine_rate_is_greater_than_100(client):
    response = client.post('/creditors/add', json={
        "bank_code": "001",
        "interest_rate": 0.1,
        "fine_rate": 200,
        "discount_limit": 0.1
    })

    assert response.status_code == 400

def test_should_return_400_when_unknown_field_is_sent(client):
    creditor_data = {
        "bank_code": "001",
        "interest_rate": 0.1,
        "fine_rate": 0.1,
        "discount_limit": 0.1,
        "unexpected_field": "error"
    }

    response = client.post('/creditors/add', json=creditor_data, content_type='application/json')

    assert response.status_code == 400
