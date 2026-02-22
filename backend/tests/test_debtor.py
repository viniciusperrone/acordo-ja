import random

from debtor import Debtor


def test_should_return_empty_list_when_no_debtors(client):
    response = client.get('/debtor/list')

    data = response.get_json()

    assert response.status_code == 200
    assert data["items"] == []
    assert data["total"] == 0

def test_should_return_paginated_creditors(client, db_session):
    debtor = Debtor(
        name='João da Silva',
        email='joao.silva@email.com',
        document='52998224725',
        phone='11987654321'
    )

    db_session.add(debtor)
    db_session.commit()

    response = client.get('/debtor/list')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["current_page"] == 1

def test_should_return_debtor_detail(client, db_session):
    debtor = Debtor(
        name='João da Silva',
        email='joao.silva@email.com',
        document='52998224725',
        phone='11987654321'
    )

    db_session.add(debtor)
    db_session.commit()

    response = client.get('/debtor/{}/detail'.format(debtor.id))

    assert response.status_code == 200

def test_should_return_404_when_creditor_not_found(client):
    debtor_id = random.randint(1, 100)

    response = client.get('/debtor/{}/detail'.format(debtor_id))

    assert response.status_code == 404

def test_should_create_debtor_successfully(client):
    debtor = {
        "name": "João da Silva",
        "email": "joao.silva@email.com",
        "document": "52998224725",
        "phone": "11987654321"
    }

    response = client.post('/debtor/add', json=debtor, content_type='application/json')

    assert response.status_code == 201

def test_should_return_400_when_document_invalid(client):
    debtor = {
        "name": "João da Silva",
        "email": "joao.silva@email.com",
        "document": "99999999999",
        "phone": "11987654321"
    }

    response = client.post('/debtor/add', json=debtor, content_type='application/json')

    assert response.status_code == 400

def test_should_return_400_when_phone_invalid(client):
    debtor = {
        "name": "João da Silva",
        "email": "joao.silva@email.com",
        "document": "52998224725",
        "phone": "2123843892012"
    }

    response = client.post('/debtor/add', json=debtor, content_type='application/json')

    assert response.status_code == 400
