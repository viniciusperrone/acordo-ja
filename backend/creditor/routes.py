from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from common.decorators.transactional import transactional

from creditor.schemas import CreditorSchema
from creditor.models import Creditor
from creditor.services import CreditorService
from creditor.exceptions import CreditorAlreadyExistsError
from creditor.filters import CreditorFilter


creditor_bp = Blueprint('creditor', __name__, url_prefix='/creditors')

@jwt_required()
@creditor_bp.route('/list', methods=['GET'])
def list_creditors():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Creditor.query

        query = CreditorFilter(query, request.args).apply()

        pagination = query.paginate(
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
        }), 200

    except Exception as err:
        print(str(err))
        return jsonify({"message": "Internal Server Error"}), 500

@creditor_bp.route('/<uuid:creditor_id>/detail', methods=['GET'])
@jwt_required()
@transactional
def retrieve_creditor(creditor_id, db):
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
@jwt_required()
@transactional
def create_creditor(db):
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
