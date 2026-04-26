from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from common.decorators import current_user, transactional, permission_roles
from config.rate_limit import limiter

from creditor.schemas import CreditorSchema
from creditor.models import Creditor
from creditor.services import CreditorService
from creditor.filters import CreditorFilter
from utils.enum import UserRole

creditor_bp = Blueprint('creditor', __name__, url_prefix='/creditors')

@jwt_required()
@creditor_bp.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
def list_creditors():
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

@creditor_bp.route('/<uuid:creditor_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_creditor(creditor_id, db):
    creditor = CreditorService.get(creditor_id, db.session)

    creditor_schema = CreditorSchema()
    result = creditor_schema.dump(creditor)

    return jsonify(result), 200


@creditor_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@permission_roles(UserRole.ADMIN)
@transactional
@current_user
def create_creditor(db):
    creditor_schema = CreditorSchema()

    data = creditor_schema.load(request.json)

    creditor = CreditorService.create_creditor(
        data=data,
        session=db.session
    )

    return jsonify(creditor_schema.dump(creditor)), 201
