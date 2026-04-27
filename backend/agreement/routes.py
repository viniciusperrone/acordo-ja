from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required

from agreement.models import Agreement
from agreement.schemas import AgreementSchema
from agreement.services import AgreementService

from config import limiter
from common.decorators import transactional, current_user, permission_roles
from utils.enum import UserRole


agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreement')

@agreement_bp.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
@jwt_required()
def list_agreements():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Agreement.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    agreements_schema = AgreementSchema(many=True)

    result = agreements_schema.dump(pagination.items)

    return jsonify({
        "items": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page
    })

@agreement_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
@transactional
def create_agreement(db):
    agreement_schema = AgreementSchema()
    data = agreement_schema.load(request.json)

    agreement = AgreementService.create(data, db.session)
    result = agreement_schema.dump(agreement)

    return jsonify(result), 201

@agreement_bp.route('/<uuid:agreement_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_agreement(agreement_id, db):
    agreement = AgreementService.get(agreement_id, db.session)

    agreement_schema = AgreementSchema()
    result = agreement_schema.dump(agreement)

    return jsonify(result), 200

@agreement_bp.route('/<uuid:agreement_id>/activate', methods=['PATCH'])
@jwt_required()
@limiter.limit("3 per minute")
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
@transactional
@current_user
def activate_agreement(agreement_id, db):
    user = getattr(g, "current_user", None)

    agreement = AgreementService.get(agreement_id, db.session)

    AgreementService.activate(agreement, user, db.session)

    return jsonify(), 204

@agreement_bp.route('/<uuid:agreement_id>/cancel', methods=['POST'])
@jwt_required()
@limiter.limit("3 per minute")
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
@transactional
def cancel_agreement(agreement_id, db):
    agreement = AgreementService.get(agreement_id, db.session)

    AgreementService.cancel(agreement, db.session)

    return jsonify(), 204

@agreement_bp.route('/<uuid:agreement_id>/complete', methods=['POST'])
@limiter.limit("3 per minute")
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
@jwt_required()
@transactional
def complete_agreement(agreement_id, db):
    agreement = AgreementService.get(agreement_id, db.session)

    AgreementService.complete(agreement, db.session)

    return jsonify(), 204
