from flask import Blueprint, request, jsonify, current_app, g
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

    except Exception:
        current_app.logger.exception(
            "An error occured while trying to list creditors",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

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

    except Exception:
        current_app.logger.exception(
            "An error occured while trying to retrieve creditor",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500


@creditor_bp.route('/add', methods=['POST'])
@jwt_required()
@transactional
@current_app
def create_creditor(db):
    creditor_schema = CreditorSchema()

    try:
        data = creditor_schema.load(request.json)

        CreditorService.create_creditor(
            data=data,
            session=db.session
        )

        user = g.current_user

        current_app.logger.info(
            "Creditor successfully added",
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, "value", None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({'message': 'Successfully registered creditor'}), 201

    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    except CreditorAlreadyExistsError as err:
        current_app.logger.warning(
            "Creditor already exists",
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, "value", None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            })

        return jsonify({'message': str(err)}), 400
    except Exception:
        current_app.logger.exception(
            "An error occured while trying to register creditor",
            extra={
                "user_id": user.id,
                "user_role": getattr(user.role, "value", None),
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({'message': "Internal Server Error"}), 500
