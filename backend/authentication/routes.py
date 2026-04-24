from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required

from authentication.schemas import AuthenticationSchema, UpdatePasswordSchema
from authentication.services import AuthenticationService
from common.decorators import current_user, transactional
from config.rate_limit import limiter


authentication_bp = Blueprint("authentication", __name__, url_prefix="/auth")

@authentication_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
@transactional
def login(db):
    authentication_schema = AuthenticationSchema()

    data = authentication_schema.load(request.get_json())

    tokens = AuthenticationService.login(email=data["email"], password=data["password"], session=db.session)

    return jsonify(tokens), 200


@authentication_bp.route("/me/update-password", methods=["PATCH"])
@jwt_required()
@transactional
@current_user
def update_password(db):
    user = getattr(g, "current_user")
    schema = UpdatePasswordSchema()
    data = schema.load(request.json)

    AuthenticationService.update_password(
        user=user,
        data=data,
        session=db.session
    )

    return jsonify({"message": "Password changed successfully"}), 200
