from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from common.decorators import transactional, current_user, permission_roles
from config.rate_limit import limiter

from users.models import User
from users.services import UserService
from users.schemas import UserSchema, UserUpdateSchema, UserResponseSchema
from users.filters import UserFilter
from utils.enum import UserRole

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/list', methods=['GET'])
@limiter.limit("30 per minute")
@jwt_required()
@transactional
def list_users(db):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = UserFilter(User.query, request.args).apply()

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    users_schema = UserSchema(many=True)

    result = users_schema.dump(pagination.items)

    return jsonify({
        "items": result,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
    })

@user_bp.route('/<uuid:user_id>/detail', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
@transactional
def retrieve_user(user_id, db):
    user = UserService.get(user_id=user_id, session=db.session)

    user_schema = UserSchema()
    result = user_schema.dump(user)

    return jsonify(result), 200

@user_bp.route('/add', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
@transactional
@current_user
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
def create_user(db):
    user_schema = UserSchema()

    data = user_schema.load(request.json)

    user = UserService.create_user(data=data, session=db.session)

    return jsonify(user_schema.dump(user)), 201

@user_bp.route('/<uuid:user_id>/update', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per minute")
@transactional
@current_user
@permission_roles(UserRole.ADMIN, UserRole.MANAGER)
def update_user(user_id, db):
    schema = UserUpdateSchema()
    response_schema = UserResponseSchema()

    data = schema.load(request.json)

    user = UserService.update(
        user_id=user_id,
        data=data,
        session=db.session
    )

    return jsonify(response_schema.dump(user)), 200
