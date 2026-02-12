from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from debts import Debt
from debts.schemas import DebtSchema

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/add', methods=['POST'])
def create_debt():
    debt_schema = DebtSchema()

    try:
        data = debt_schema.load(request.json)

        debt = Debt(**data)

        db.session.add(debt)
        db.session.commit()

        return jsonify({'message': 'Successfully registered debt'}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as e:

        return jsonify({"message": "Internal Server Error"}), 500
