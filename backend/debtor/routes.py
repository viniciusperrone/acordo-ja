from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from common.decorators import transactional, permission_roles
from config.rate_limit import limiter

from debtor.models import Debtor
from debtor.schemas import DebtorSchema
from debtor.filters import DebtorFilter
from debtor.services import DebtorService
from utils.enum import UserRole

debtor_bp = Blueprint('debtor', __name__, url_prefix='/debtor')

@debtor_bp.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
@jwt_required()
def list_debtors():
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

@debtor_bp.route('/<int:debtor_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_debtor(debtor_id, db):
    debtor = DebtorService.get(debtor_id, db.session)

    debtor_schema = DebtorSchema()
    result = debtor_schema.dump(debtor)

    return jsonify(result), 200

@debtor_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
@transactional
def create_debtor(db):
    debtor_schema = DebtorSchema()
    data = debtor_schema.load(request.json)

    debtor = DebtorService.create(data, db.session)

    return jsonify(debtor_schema.dump(debtor)), 201
