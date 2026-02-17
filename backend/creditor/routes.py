from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db

from creditor.schemas import CreditorSchema
from creditor.models import Creditor


creditor_bp = Blueprint('creditor', __name__, url_prefix='/creditors')

@creditor_bp.route('/list', methods=['GET'])
def list_creditors():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = Creditor.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        creditors_schema = CreditorSchema(many=True)

        result = creditors_schema.dump(pagination.items)

        return jsonify({
            "items": result,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": page
        })

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

@creditor_bp.route('/<uuid:creditor_id>/detail', methods=['GET'])
def retrieve_creditor(creditor_id):
    try:
        creditor = Creditor.query.get(creditor_id)

        if not creditor:
            return jsonify({'message': 'Creditor not found'}), 404

        creditor_schema = CreditorSchema()
        result = creditor_schema.dump(creditor)

        return jsonify(result), 200

    except Exception as err:
        return jsonify({"message": "Internal Server Error"}), 500

@creditor_bp.route('/add', methods=['POST'])
def create_creditor():
    creditor_schema = CreditorSchema()

    try:
        data = creditor_schema.load(request.json)

        bank_code = data['bank_code']

        existing_creditor = Creditor.query.filter_by(bank_code=bank_code).first()

        if existing_creditor:
            return jsonify({'message': 'Creditor already exists'}), 400

        creditor = Creditor(**data)

        db.session.add(creditor)
        db.session.commit()

        return jsonify({'message': 'Successfully registered creditor'})

    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    except Exception as err:

        return jsonify({'message': "Internal Server Error"}), 500
