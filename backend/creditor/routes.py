from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config.db import db

from creditor.schemas import CreditorSchema
from creditor.models import Creditor
from creditor.services import CreditorService, CreditorAlreadyExistsError

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
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500

@creditor_bp.route('/<uuid:creditor_id>/detail', methods=['GET'])
def retrieve_creditor(creditor_id):
    try:
        creditor = db.session.get(Creditor, creditor_id)

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

        CreditorService.create_creditor(
            data=data,
            session=db.session
        )

        db.session.commit()

        return jsonify({'message': 'Successfully registered creditor'}), 201

    except ValidationError as err:
        db.session.rollback()
        return jsonify({'message': err.messages}), 400

    except CreditorAlreadyExistsError as err:
        db.session.rollback()
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        db.session.rollback()
        return jsonify({'message': "Internal Server Error"}), 500
