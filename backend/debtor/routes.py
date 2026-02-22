from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db
from debtor.models import Debtor
from debtor.schemas import DebtorSchema


debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@debtor_bp.route('/list', methods=['GET'])
def list_debtors():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Debtor.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        debtors_schema = DebtorSchema(many=True)

        result = debtors_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        }), 200

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

@debtor_bp.route('/<int:debtor_id>/detail', methods=['GET'])
def retrieve_debtor(debtor_id):
    try:
        debtor = db.session.get(Debtor, debtor_id)

        if not debtor:
            return jsonify({"message": "Debtor not found"}), 404

        debtor_schema = DebtorSchema()
        result = debtor_schema.dump(debtor)

        return jsonify(result), 200

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

@debtor_bp.route('/add', methods=['POST'])
def create_debtor():
    debtor_schema = DebtorSchema()

    try:
        data = debtor_schema.load(request.json)

        debt = Debtor(**data)

        db.session.add(debt)
        db.session.commit()

        return jsonify({"message": "Successfully registered debtor"}), 201

    except ValidationError as err:
        return jsonify({"message": err.messages}), 400

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500
