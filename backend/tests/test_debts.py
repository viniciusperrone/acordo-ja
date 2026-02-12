from datetime import datetime as dt


def test_create_debt(client):
    debt_data = {
        "cpf": "02780261250",
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
