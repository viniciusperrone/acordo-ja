

def test_create_debt(client):
    debt_data = {
        "cpf": "52998224725",
        "creditor": "001",
        "original_value": 160,
        "due_date": '2026-10-15',
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 201

def test_create_debt_success_only_required_fields(client):
    debt_data = {
        "cpf": "52998224725",
        "original_value": 200.0,
    }

    response = client.post("/debts/add", json=debt_data)

    assert response.status_code == 201

def test_invalid_cpf(client):
    debt_data = {
        "cpf": "12345678900",
        "creditor": "001",
        "original_value": 160,
        "due_date": '2026-10-15',
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )


    assert response.status_code == 400

    response_json = response.get_json()

    assert "errors" in response_json
    assert "cpf" in response_json["errors"]
    assert response_json["errors"]["cpf"][0] == "CPF is not valid"

def test_missing_cpf(client):
    debt_data = {
        "original_value": 160.0,
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "cpf" in response.get_json()["errors"]

def test_empty_cpf(client):
    debt_data = {
        "cpf": "",
        "original_value": 160.0,
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "cpf" in response.get_json()["errors"]

def test_invalid_creditor(client):
    debt_data = {
        "cpf": "52998224725",
        "creditor": "999",
        "original_value": 160.0,
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "creditor" in response.get_json()["errors"]

def test_invalid_original_value_type(client):
    debt_data = {
        "cpf": "52998224725",
        "original_value": None,
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400
    assert "original_value" in response.get_json()["errors"]

def test_invalid_due_date_format(client):
    debt_data = {
        "cpf": "52998224725",
        "original_value": 160.0,
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

def test_unexpected_extra_field(client):
    debt_data = {
        "cpf": "52998224725",
        "original_value": 160.0,
        "unexpected_field": "value",
    }

    response = client.post(
        "/debts/add",
        json=debt_data,
        content_type="application/json"
    )

    assert response.status_code == 400