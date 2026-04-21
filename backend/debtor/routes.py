from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from common.decorators import transactional
from config.rate_limit import limiter

from debtor.models import Debtor
from debtor.schemas import DebtorSchema
from debtor.filters import DebtorFilter

debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@debtor_bp.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
@jwt_required()
def list_debtors():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Debtor.query

        query = DebtorFilter(query, request.args).apply()

        pagination = query.paginate(
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
        current_app.logger.exception(
            "An error occurred while trying to list debtors",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@debtor_bp.route('/<int:debtor_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_debtor(debtor_id, db):
    try:
        debtor = db.session.get(Debtor, debtor_id)

        if not debtor:
            return jsonify({"message": "Debtor not found"}), 404

        debtor_schema = DebtorSchema()
        result = debtor_schema.dump(debtor)

        return jsonify(result), 200

    except Exception as err:
        current_app.log_exception(
            "An error occurred while trying to retrieve a debtor",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500

@debtor_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@transactional
def create_debtor(db):
    debtor_schema = DebtorSchema()

    try:
        data = debtor_schema.load(request.json)

        debt = Debtor(**data)

        db.session.add(debt)

        return jsonify({"message": "Successfully registered debtor"}), 201

    except ValidationError as err:
        return jsonify({"message": err.messages}), 400

    except Exception:
        current_app.logger.exception(
            "An error occurred while trying to register a debtor",
            extra={
                "endpoint": request.path,
                "method": request.method,
                "params": request.args.to_dict(),
                "request_id": getattr(g, "request_id", None)
            }
        )

        return jsonify({"message": "Internal Server Error"}), 500
