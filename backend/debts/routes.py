from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from debts.schemas import DebtSchema
from debts.services import DebtService
from debts.exceptions import DebtorNotExistError, CreditorNotExistError

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/add', methods=['POST'])
def create_debt():
    debt_schema = DebtSchema()

    try:
        data = debt_schema.load(request.json)

        DebtService.create_debt(
            data=data,
            session=db.session
        )

        db.session.commit()

        return jsonify({'message': 'Successfully registered debt'}), 201

    except ValidationError as err:
        db.session.rollback()
        return jsonify({"errors": err.messages}), 400
    except DebtorNotExistError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400
    except CreditorNotExistError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400
    except Exception as e:
        return jsonify({"message": "Internal Server Error"}), 500
