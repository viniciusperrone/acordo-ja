from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db

from debts import Debt
from debts.schemas import DebtSchema
from debts.services import DebtService
from debts.exceptions import DebtorNotExistError, CreditorNotExistError

debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/list', methods=['GET'])
def list_debts():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Debt.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        debts_schema = DebtSchema(many=True)

        result = debts_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page,
        }), 200

    except Exception as err:
        print(str(err))
        return jsonify({'message': 'Internal Server Error'}), 500

@debts_bp.route('/<uuid:debt_id>/detail', methods=['GET'])
def retrieve_debt(debt_id):
    try:
        debt = db.session.get(Debt, debt_id)

        if not debt:
            return jsonify({'message': 'Debt not found'}), 404

        debt_schema = DebtSchema()
        result = debt_schema.dump(debt)

        return jsonify(result), 200
    except Exception as err:
        print(str(err))
        return jsonify({'message': 'Internal Server Error'}), 500


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
