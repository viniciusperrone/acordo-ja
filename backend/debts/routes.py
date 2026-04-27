from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required

from common.decorators import current_user, permission_roles
from common.decorators.transactional import transactional
from config.rate_limit import limiter
from utils.enum import UserRole

from debts.models import Debt
from debts.services import DebtService
from debts.filters import DebtFilter
from debts.schemas import (
    DebtSchema,
    DebtSearchByDocumentSchema,
    DebtHistorySchema,
    DebtSearchResponseSchema
)


debts_bp = Blueprint('debts', __name__, url_prefix='/debts')

@debts_bp.route('/search', methods=['GET'])
@limiter.limit("30 per minute")
@transactional
def search_debt(db):
    debt_schema = DebtSearchByDocumentSchema()
    data = debt_schema.load(request.args)

    result = DebtService.search(document=data["document"], session=db.session)

    result_schema = DebtSearchResponseSchema()

    return jsonify(result_schema.dump(result)), 200

@debts_bp.route('/list', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def list_debts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Debt.query

    query = DebtFilter(query, request.args).apply()

    pagination = query.paginate(
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

@debts_bp.route('/<uuid:debt_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_debt(debt_id, db):
    debt = DebtService.get(debt_id, db.session)

    debt_schema = DebtSchema()
    result = debt_schema.dump(debt)

    return jsonify(result), 200

@debts_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@transactional
@permission_roles(UserRole.MANAGER, UserRole.ADMIN)
@current_user
def create_debt(db):
    user = g.current_user

    debt_schema = DebtSchema()
    data = debt_schema.load(request.json)

    debt = DebtService.create(
        data=data,
        user=user,
        session=db.session
    )

    return jsonify(debt_schema.dump(debt)), 201

@debts_bp.route("/<uuid:debt_id>/timeline")
@jwt_required()
@limiter.limit("30 per minute")
@transactional
def get_debt_timeline(debt_id, db):
    debt = DebtService.get(debt_id, db.session)
    schema = DebtHistorySchema(many=True)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = DebtService.get_timeline(debt, db.session).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    result = schema.dump(pagination.items)

    return jsonify({
        "items": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    }), 200
