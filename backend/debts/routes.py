from flask import Blueprint, request, jsonify

from config.db import db
from debts import Debt
from debts.schemas import DebtSchema

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/add', methods=['POST'])
def create_debt():
    data = request.json
    debt_schema = DebtSchema()

    errors = debt_schema.validate(data)

    if errors:
        return jsonify({"errors": errors}), 400


    debt = Debt(**data)

    try:
        db.session.add(debt)
        db.session.commit()

        return jsonify({'message': 'Successfully registered debt'})
    except Exception:

        return jsonify({"message": "Internal Server Error"}), 500
